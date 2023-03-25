import pygame
import this
from config import *
from classes import *

pygame.init()
print("\n")
pygame.display.set_caption("Ball Game")
pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Functions
def init():
    global player, crosshair
    pygame.mouse.set_pos(MIDDLE_OF_SCREEN)

    player = Player(MIDDLE_OF_SCREEN, 15, GREEN)
    crosshair = Crosshair(MIDDLE_OF_SCREEN)
    


def game_cursor():
    mouse_coords = pygame.mouse.get_pos()
    crosshair.movement((mouse_coords))


def spawn_bullet(player_coords: tuple, crosshair_coords:tuple):
    pass


# Other
enemyList = []
bulletList = []
player = None
crosshair = None    

# ========== Start ========== #
init()


# Main game loop
appRunning = True
while appRunning:
    screen.fill(BACKGROUND)
    game_cursor()

    # Update entities
    player.draw_self()
    crosshair.draw_self()

    for entity in enemyList:
        entity.draw_self()

    for bullet in bulletList:
        bullet.draw_self()


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

    # Update screen
    pygame.display.flip()
    pygame.time.Clock().tick(120)