import random
import pygame
import math
import numpy as np
import sys
#from nn import NeuralNetwork
from nn2 import NeuralNetwork

(width, height) = (800, 800)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Insects simulation')

def renormalize(n, range1, range2):
    delta1 = range1[1] - range1[0]
    delta2 = range2[1] - range2[0]
    return (delta2 * (n - range1[0]) / delta1) + range2[0]

class Insect:
    def __init__(self):
        self.id = random.randint(0, 999999999)
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.orientation = 2 * math.pi * random.random()
        self.size = 10
        self.health = 300
        self.cntrLived = 0
        self.isAlive = True
        self.cntrFood = 0
        self.brain = NeuralNetwork(2, 2, 4)

    def think(self, target):
        target_orientation = math.atan2(target['food'].y - self.y, target['food'].x - self.x)
        target_orientation += math.pi 
        target_orientation = renormalize(target_orientation, [0,  2 * math.pi], [0, 1])
        distance = renormalize(target['distance'], [0, 1131], [0, 1])
        inp_vec = [target_orientation, distance]
        result = self.brain.run(inp_vec)
#        print('inp', inp_vec, 'result', result)
        gas = result[0]
        steer = result[1]
        gas = renormalize(gas, [0, 1], [0, 15])
        steer = renormalize(steer, [0, 1], [-3, 3]) 
        return (gas, steer)

    def update(self):
        self.health -= 1
        if self.health <= 0:
            self.isAlive = False

        if not self.isAlive:
            return

        desired_target = self.find_closest_food()
        if desired_target['food']:
            pygame.draw.aaline(screen, (255, 0, 0), (self.x, self.y), (desired_target['food'].x, desired_target['food'].y))
        if desired_target['distance'] < self.size:
            desired_target['food'].respawn()
            self.health += 20
            self.cntrFood += 1

        (gas, steer) = self.think(desired_target)
#        print("GAS: {} STEER: {}".format(gas, steer))
#        gas = self.gas()
#        steer = self.steer()
        if gas <= 3:
            return

        pseudo_target_x = self.x + int(math.cos(self.orientation) * gas)
        pseudo_target_y = self.y + int(math.sin(self.orientation) * gas)
#        print("{}, {} (gas: {}, steer: {}, ori: {}) ----> {}, {}".format(self.x, self.y, gas, steer, self.orientation, pseudo_target_x, pseudo_target_y))

        st_dir = self.orientation + math.pi / 2
        target_x = pseudo_target_x + int(math.cos(st_dir) * steer)
        target_y = pseudo_target_y + int(math.sin(st_dir) * steer)

        self.orientation = math.atan2(target_y - self.y, target_x - self.x)
        self.x = target_x
        self.y = target_y
        self.cntrLived += 1

    def steer(self):
        return random.randint(-3, 3) 

    def gas(self):
        return random.randint(0, 15)


    def display(self):
        if not self.isAlive:
            return
        # draw body
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size, 2)
        # draw antennas
        antena_len = 20
        antena_start = (self.x, self.y)
        antena_end = (
                antena_start[0] + math.cos(self.orientation) * antena_len,
                antena_start[1] + math.sin(self.orientation) * antena_len
                )
        antena = pygame.draw.aaline(screen, self.color, antena_start, antena_end)

    def find_closest_food(self):
        min_distance = None
        selected_food = None
        for i in foods:
            if not selected_food:
                selected_food = i
            distance = math.hypot(i.x - self.x, i.y - self.y)
            if not min_distance or min_distance > distance:
                min_distance = distance
                selected_food = i
        return {'food': selected_food, 'distance': min_distance}
    
    def mate_with(self, parent):
        kid = Insect()

        for i in range(1):
            for j in range(3):
                kid.brain.W1[i][j] = self.brain.W1[i][j] if random.randint(0, 1) == 0 else parent.brain.W1[i][j]

        for i in range(3):
            for j in range(1):
                kid.brain.W2[i][j] = self.brain.W2[i][j] if random.randint(0, 1) == 0 else parent.brain.W2[i][j]

        return kid
#        print("Brain self W1:", self.brain.W1)
#        print("Brain self W2:", self.brain.W2)
#        print("Brain other W1:", parent.brain.W1)
#        print("Brain other W2:", parent.brain.W2)
        #genome1 = self.brain.W1

    def mutate(self):
        if random.randint(0, 100) < mutating_chance:
            if random.randint(0, 1) == 1:
                # mutate W1
                i = random.randint(0, 1)
                j = random.randint(0, 3)
                self.brain.W1[i][j] = random.random()
            else:
                # mutate W2
                i = random.randint(0, 3)
                j = random.randint(0, 1)
                self.brain.W2[i][j] = random.random()

class Food:
    def __init__(self):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.color = (10, 255, 10)
        self.size = 3

    def display(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size, 0)

    def respawn(self):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)


insects = []
num_insects = 30
foods = []
num_food = 10
mating_pool = []
mutating_chance = 1 # %
generation_cntr = 1

for _ in range(num_insects):
    insect = Insect()
    insects.append(insect)

for _ in range(num_food):
    food = Food()
    foods.append(food)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))

    for i in foods:
        i.display()

    # population develop phase
    numAlive = 0
    for i in insects:
        i.update()
        i.display()
        if i.isAlive:
            numAlive += 1

    # evaluate fitness phase
    if numAlive == 0:
        (total_fitness, max_fitness, avg_fitness) = (0, 0, 0)
        for i in insects:
            total_fitness += i.cntrLived
            if i.cntrLived >= max_fitness:
                max_fitness = i.cntrLived
        avg_fitness = int(total_fitness / len(insects))
        print("Generation: {} fitness: total={} avg={} max={}".format(generation_cntr, total_fitness, avg_fitness, max_fitness))

        for i in insects:
            i.fitness = i.cntrLived / max_fitness
            i.partial_fitness = round(100 * i.cntrLived / total_fitness, 2)
            i.mating_slots = round(num_insects * i.partial_fitness / 100)
            # above average score is rewarded with extra mating slots
            if i.cntrLived > avg_fitness:
                #i.extra_mating_slots = int((i.fitness - average_fitness) * 5)
                i.extra_mating_slots = i.cntrFood * 2
                i.mating_slots += i.extra_mating_slots
            
            print("Individual {} fed: {} lived: {} fitness: {}, partial: {}, mating slots: {}".format(i.id, i.cntrFood, i.cntrLived, i.fitness, i.partial_fitness, i.mating_slots))
        # mating phase
        print("Mating phase")
        mating_pool = []
        for i in insects:
            for c in range(i.mating_slots):
                mating_pool.append(i)
        next_generation = []
        for _ in range(num_insects):
            parent1 = random.choice(mating_pool)
            parent2 = random.choice(mating_pool)
            kid = parent1.mate_with(parent2)
            kid.mutate()
            next_generation.append(kid)
        print("Running next generation")
        insects = next_generation
        generation_cntr += 1
        

#    pygame.time.delay(10)

    pygame.display.flip()
