import pygame
import this
print("\n")
import random
from config import *
from classes import *

pygame.init()
pygame.display.set_caption("Ball Game")
pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
gameMapConfig = pygame.image.load(GAME_MAP_CONFIG)
gameMap = pygame.image.load(GAME_MAP_FILE)

enemyList = []
bulletList = []
player = None
crosshair = None
spawnDirection = [0, 0]  # What axis the enemies will go towards: [x, y]


def init() -> None:
    ''' Initializes player and mouse coorinates, and finds enemy spawnpoint.'''
    global player, crosshair
    pygame.mouse.set_pos(MIDDLE_OF_SCREEN)

    player = Player(MIDDLE_OF_SCREEN, 15, GREEN)
    crosshair = Crosshair(MIDDLE_OF_SCREEN)

    screen.blit(gameMapConfig,(0,0))
    startCoordinates = find_spawn_point()
    print(startCoordinates)


def cursor_movement() -> None:
    ''' Moves the player crosshair to the mouse coordinates.'''
    mouse_coords = pygame.mouse.get_pos()
    crosshair.movement(mouse_coords)


def spawn_bullet(player_coords: tuple, crosshair_coords:tuple) -> None:
    ''' Creates a bullet at the player.'''
    bulletList.append(Bullet(player_coords, crosshair_coords))


def get_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    ''' Gets the distance between two points.'''
    distance = math.sqrt((x1-x2) ** 2 + (y1-y2) ** 2)
    return distance


def random_enemy_spawn_coordinates() -> tuple:
    ''' Spawns an enemy at a random set of coordinates outside of the screen.'''
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


def check_bullet_hit() -> None:
    ''' Checks if a bullet has an enemy.'''
    for enemy in enemyList:
        for bullet in bulletList:
            distance = get_distance(enemy.x, enemy.y, bullet.x, bullet.y)
            
            if distance < enemy.r:
                enemyList.remove(enemy)
                #? Should this here?  
                # bulletList.remove(bullet)
                # print("+1")


def out_of_bounds_check(x: int, y: int) -> bool:
    ''' Checks if coordinates are outside of game screen.'''
    if x < -MAX_OUT_OF_BOUNDS_PX or x > SCREEN_WIDTH + MAX_OUT_OF_BOUNDS_PX:
        return True
    if y < -MAX_OUT_OF_BOUNDS_PX or y > SCREEN_HEIGHT + MAX_OUT_OF_BOUNDS_PX:
        return True
    
    return False


def find_spawn_point() -> tuple:
    ''' Finds the coordinates for the enemy spawn point.'''
    global spawnDirection
    x = 0
    y = 0

    startCoordinate = 0
    
    for width in range(SCREEN_WIDTH-1):
        pixelColor = screen.get_at((x, y))

        if pixelColor == SPAWN_COLOR:
            startCoordinate = (x, y - 15)
            spawnDirection = [0, 1]
            break

        else:
            x += 1

    for height in range(SCREEN_HEIGHT-1):
        pixelColor = screen.get_at((x, y))

        if pixelColor == SPAWN_COLOR:
            startCoordinate = (x + 15, y)
            spawnDirection = [-1, 0]
            break

        else:
            y += 1
        
    for width in range(SCREEN_WIDTH-1):
        pixelColor = screen.get_at((x, y))

        if pixelColor == SPAWN_COLOR:
            startCoordinate = (x, y + 15)
            spawnDirection = [0, -1]
            break

        else:
            x -= 1

    for height in range(SCREEN_HEIGHT-1):
        pixelColor = screen.get_at((x, y))

        if pixelColor == SPAWN_COLOR:
            startCoordinate = (x - 15, y)
            spawnDirection = [1, 0]
            break

        else:
            y -= 1

    return startCoordinate


# ========== Start ========== #
init()

# Main game loop
appRunning = True
while appRunning:
    screen.blit(gameMap,(0,0))
    cursor_movement()
    check_bullet_hit()

    # Update and draw screen.
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


    # Player movement.
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
                enemyList.append(Enemy_class1(coordinates))

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_presses = pygame.mouse.get_pressed()
            if mouse_presses[0]:
                player_coordinates = (player.x, player.y)
                crosshair_coordinates = (crosshair.x, crosshair.y)
                spawn_bullet(player_coordinates, crosshair_coordinates)

    

    # Update screen
    pygame.display.flip()
    pygame.time.Clock().tick(120)