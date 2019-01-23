import random
import pygame
import math
import numpy as np
import sys
import string
import time
#from nn import NeuralNetwork
from nn2 import NeuralNetwork

results_filename = "results_" + str(time.time()) + ".csv"
fp = open(results_filename, 'a')
fp.write("generation,total,avg,max\n")

(width, height) = (800, 800)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Insects simulation')

def renormalize(n, range1, range2):
    delta1 = range1[1] - range1[0]
    delta2 = range2[1] - range2[0]
    return (delta2 * (n - range1[0]) / delta1) + range2[0]

def randomid(n = 3):
    out = []
    for _ in range(n):
        out.append(random.choice(string.ascii_uppercase))
    return ''.join(out)

class Insect:
    def __init__(self):
        self.id = randomid()
        self.parentAid = ''
        self.parentBid = ''
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.orientation = 2 * math.pi * random.random()
        self.size = 10
        self.health = 200
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
        steer = renormalize(steer, [0, 1], [-15, 15]) 
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
            self.health += 40
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
        kid.parentAid = self.id
        kid.parentBid = parent.id

#        print("W1: ", self.brain.W1)
        selfLinearW1 = [item for sublist in self.brain.W1 for item in sublist] #np.concatenate(self.brain.W1)
        parentLinearW1 = [item for sublist in parent.brain.W1 for item in sublist] #np.concatenate(parent.brain.W1)
        median = random.randint(0, len(selfLinearW1))
        kidLinearW1 = np.concatenate([selfLinearW1[0:median], parentLinearW1[median:]])
#        print("linear W1: ", kidLinearW1)
        kid.brain.W1 = np.split(kidLinearW1, 2)
#        print("New W1: ", kid.brain.W1)

#        print("W2: ", self.brain.W2)
        selfLinearW2 = [item for sublist in self.brain.W2 for item in sublist] #np.concatenate(self.brain.W2)
        parentLinearW2 = [item for sublist in parent.brain.W2 for item in sublist] #np.concatenate(parent.brain.W2)
        median = random.randint(0, len(selfLinearW2))
        kidLinearW2 = np.concatenate([selfLinearW2[0:median], parentLinearW2[median:]])
#        print("linear W2: ", kidLinearW2)
        kid.brain.W2 = np.split(kidLinearW2, 4)
#        print("New W2: ", kid.brain.W2)

#        for i in range(1):
#            for j in range(3):
#                kid.brain.W1[i][j] = self.brain.W1[i][j] if random.randint(0, 1) == 0 else parent.brain.W1[i][j]
#
#        for i in range(3):
#            for j in range(1):
#                kid.brain.W2[i][j] = self.brain.W2[i][j] if random.randint(0, 1) == 0 else parent.brain.W2[i][j]

        return kid

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
num_insects = 50
foods = []
num_food = 60
mating_pool = []
max_mating_pool = 50
mutating_chance = 1 # %
generation_cntr = 1

for _ in range(num_insects):
    insect = Insect()
    insects.append(insect)

for _ in range(num_food):
    food = Food()
    foods.append(food)

running = True
isRunningFast = True 

while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            print
            if pygame.key.get_pressed()[pygame.K_s]:
                isRunningFast ^= 1

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
        (total_food, max_food, avg_food, total_mating_slots) = (0, 1, 0, 0)
        for i in insects:
            total_food += i.cntrFood
            if i.cntrFood >= max_food:
                max_food = i.cntrFood
        avg_food = int(total_food / len(insects))
        print("Generation: {} food total={} avg={} max={}".format(generation_cntr, total_food, avg_food, max_food))
        fp = open(results_filename, 'a')
        fp.write("{},{},{},{}\n".format(generation_cntr, total_food, avg_food, max_food))
        fp.close()

        for i in insects:
            i.desired_mating_slots = i.cntrFood 
            # above average score is rewarded with extra mating slots
            if i.cntrFood > avg_food:
                i.extra_mating_slots = (i.cntrFood - avg_food) ** 2
                i.desired_mating_slots += i.extra_mating_slots
                total_mating_slots += i.desired_mating_slots
            
        # mating phase
        mating_pool = []
        for i in insects:
            mating_slots = round(max_mating_pool * i.desired_mating_slots / total_mating_slots)
            print("Individual {} ({}/{}) fed: {} lived: {}, desired mating slots: {} actual: {}".format(
                i.id, i.parentAid, i.parentBid, i.cntrFood, i.cntrLived, i.desired_mating_slots, mating_slots
                ))
            for c in range(mating_slots):
                mating_pool.append(i)

        print("Mating pool size: {}".format(len(mating_pool)))
        next_generation = []
        for _ in range(num_insects):
            parent1 = random.choice(mating_pool)
            parent2 = random.choice(mating_pool)
            kid = parent1.mate_with(parent2)
            kid.mutate()
            next_generation.append(kid)

        insects = next_generation
        generation_cntr += 1
        

    if not isRunningFast:
        pygame.time.delay(20)

    pygame.display.flip()
