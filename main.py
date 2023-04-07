import pygame
import this
import random
from config import *
from classes import *

pygame.init()
print("\n")
pygame.display.set_caption("Ball Game")
pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

enemyList = []
bulletList = []
player = None
crosshair = None


def init():
    global player, crosshair
    pygame.mouse.set_pos(MIDDLE_OF_SCREEN)

    player = Player(MIDDLE_OF_SCREEN, 15, GREEN)
    crosshair = Crosshair(MIDDLE_OF_SCREEN)


def cursor_movement():
    mouse_coords = pygame.mouse.get_pos()
    crosshair.movement(mouse_coords)


def spawn_bullet(player_coords: tuple, crosshair_coords:tuple):
    bulletList.append(Bullet(player_coords, crosshair_coords))


def get_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    #print(x1, y1, ":", x2, y2)
    distance = math.sqrt((x1-x2) ** 2 + (y1-y2) ** 2)
    return distance


def random_enemy_spawn_coordinates() -> tuple:
    side = random.randint(0,3)

    if side == 0:
        x = -20
        y = random.randint(0, SCREEN_HEIGHT)
        
    if side == 1:
        x = SCREEN_WIDTH + 20
        y = random.randint(0, SCREEN_HEIGHT)

    if side == 2:
        x = random.randint(0, SCREEN_WIDTH)
        y = -20
        
    if side == 3:
        x = random.randint(0, SCREEN_WIDTH)
        y = SCREEN_HEIGHT + 20

    return (x, y)


def check_bullet_hit():
    for enemy in enemyList:
        for bullet in bulletList:
            distance = get_distance(enemy.x, enemy.y, bullet.x, bullet.y)
            
            if distance < enemy.r:
                enemyList.remove(enemy)
                #bulletList.remove(bullet)
                print("+1")


def out_of_bounds_check(x: int, y: int) -> bool:
    if x < -20 or x > SCREEN_WIDTH + 20:
        return True
    if y < -20 or y > SCREEN_HEIGHT + 20:
        return True
    
    return False


# ========== Start ========== #
init()


# Main game loop
appRunning = True
while appRunning:
    screen.fill(BACKGROUND_COLOR)
    cursor_movement()
    check_bullet_hit()

    # Update entities
    for enemy in enemyList:
        player_coordinates = (player.x, player.y)
        enemy.movement(player_coordinates)
        enemy.draw_self()

    for bullet in bulletList:
        bullet.update()
        bullet.draw_self()
        
        if out_of_bounds_check(bullet.x, bullet.y):
            bulletList.remove(bullet)
        

    player.draw_self()
    crosshair.draw_self()


    # Player movement
    keyHeldDown = pygame.key.get_pressed()
    player.movement(keyHeldDown)


    # Detect pygame events.
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            appRunning = False

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_DELETE, pygame.K_ESCAPE]:
                appRunning = False
            
            # DEBUG
            if event.key == pygame.K_b:
                coordinates = random_enemy_spawn_coordinates()
                enemyList.append(Enemy_walker(coordinates))
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_presses = pygame.mouse.get_pressed()
            if mouse_presses[0]:
                player_coordinates = (player.x, player.y)
                crosshair_coordinates = (crosshair.x, crosshair.y)
                spawn_bullet(player_coordinates, crosshair_coordinates)

    

    # Update screen
    pygame.display.flip()
    pygame.time.Clock().tick(120)