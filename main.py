import random
import pygame
import math

(width, height) = (800, 800)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Insects simulation')

class Insect:
    def __init__(self):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.orientation = 2 * math.pi * random.random()
        self.size = 20
        self.health = 100
        self.isAlive = True

    def update(self):
        if not self.isAlive:
            return

        desired_target = self.find_closest_food()
        if desired_target['food']:
            pygame.draw.aaline(screen, (255, 0, 0), (self.x, self.y), (desired_target['food'].x, desired_target['food'].y))
        if desired_target['distance'] < self.size:
            desired_target['food'].respawn()
            self.health += 20

        gas = self.gas()
        steer = self.steer()
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

        self.health -= 1
        if self.health <= 0:
            self.isAlive = False

    def steer(self):
        return random.randint(-3, 3) 

    def gas(self):
        return random.randint(0, 15)


    def display(self):
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
num_insects = 10
foods = []
num_food = 50

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

    for i in insects:
        i.update()
        i.display()

    for i in foods:
        i.display()

    pygame.time.delay(100)

    pygame.display.flip()
