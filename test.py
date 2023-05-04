import pygame
import math
from config import *

pygame.init()
pygame.display.set_caption("Ball Game")

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


class Circle(object):
    def __init__(self, x, y, color = RED, name = "", radius = 30) -> None:
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.radius = radius

    def draw_self(self) -> object:
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


class Box(object):
    def __init__(self, x, y, color = GREEN, name = "") -> None:
        self.x = x
        self.y = y
        self.color = color
        self.side = 10
        self.centerX = self.x + self.side / 2
        self.centerY = self.y + self.side / 2
        self.name = name

    def draw_self(self) -> object:
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.side, self.side))
        
        self.centerX = self.x + self.side / 2
        self.centerY = self.y + self.side / 2


class Player(Box):
    def __init__(self, x, y, color=GREEN, name="") -> None:
        super().__init__(x, y, color, name)

        self.hitboxRadius = math.sqrt(2 * self.side ** 2)

    def show_hitbox(self):
        pygame.draw.circle(screen, self.color, (self.centerX, self.centerY), self.side)



enemies = []

player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT// 2)
enemies.append(Circle(SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT // 2, RED, len(enemies)))
#enemies.append(Circle(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2, BLACK, len(enemies)))


def get_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    ''' Gets the distance between two points.'''
    distance = math.sqrt((x2-x1) ** 2 + (y2-y1) ** 2)
    return distance


def detect_colision():
    global player, enemies

    for enemy in enemies:
        distance = get_distance(player.centerX, player.centerY, enemy.x, enemy.y)
        print()
        print("player", player.centerX, player.centerY)
        print("emeny:",enemy.x, enemy.y)
        
        minDistance = player.hitboxRadius + enemy.radius

        print()
        print("total distances:", distance)
        print("minDistance:", minDistance)
        print("difference:", distance - minDistance)


        if distance <= minDistance:
            print("hit", enemy.name)




# Main game loop
appRunning = True
debugMode = False
while appRunning:
    screen.fill((70, 20, 200))

    for enemy in enemies:
        enemy.draw_self()
        



    player.draw_self()
    if debugMode:
        player.show_hitbox()

    
    for enemy in enemies:
        pygame.draw.line(screen, BLACK, (player.centerX, player.centerY), (enemy.x, enemy.y), 2)

    # Detect pygame events.
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            appRunning = False

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_DELETE, pygame.K_ESCAPE]:
                appRunning = False

            if event.key == pygame.K_p:
                debugMode = not debugMode
                print(debugMode)

            if event.key == pygame.K_w:
                player.y -= 5
            if event.key == pygame.K_a:
                player.x -= 5
            if event.key == pygame.K_s:
                player.y += 5
            if event.key == pygame.K_d:
                player.x += 5


            detect_colision()


    # Update screen
    pygame.display.flip()
    pygame.time.Clock().tick(120)