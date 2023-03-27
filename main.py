import pygame
import this
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


def game_cursor():
    mouse_coords = pygame.mouse.get_pos()
    crosshair.movement(mouse_coords)


def spawn_bullet(player_coords: tuple, crosshair_coords:tuple):
    bulletList.append(Bullet(player_coords, crosshair_coords))
  



# ========== Start ========== #
init()


# Main game loop
appRunning = True
while appRunning:
    screen.fill(BACKGROUND_COLOR)
    game_cursor()

    # Update entities
    for enemy in enemyList:
        player_coordinates = (player.x, player.y)
        enemy.movement(player_coordinates)
        enemy.draw_self()

    for bullet in bulletList:
        bullet.update()
        bullet.draw_self()

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
                enemyList.append(Enemy_walker((0, 0)))
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_presses = pygame.mouse.get_pressed()
            if mouse_presses[0]:
                player_coordinates = (player.x, player.y)
                crosshair_coordinates = (crosshair.x, crosshair.y)
                spawn_bullet(player_coordinates, crosshair_coordinates)

    

    # Update screen
    pygame.display.flip()
    pygame.time.Clock().tick(120)