import pygame
import this
print("\n")
from random import randint 
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
mapData = []  # [[(spawnCoordinates), [spawnDirection]], [directionPoint], [directionPoint]...]
mapDirectionPoints = [[0, -1], [0, 1], [-1, 0], [1, 0]]  # U, D, L, R

isDebugModeActive = False

def init() -> None:
    ''' Initializes player and mouse coorinates, and reads map config.'''
    global player, crosshair, mapData
    pygame.mouse.set_pos(MIDDLE_OF_SCREEN)

    player = Player(MIDDLE_OF_SCREEN, 15, GREEN)
    crosshair = Crosshair(MIDDLE_OF_SCREEN)

    mapData = read_map_data()
    print(mapData)


def find_enemy_spawn() -> list:
    ''' 
    Returns the coordinates for the enemy spawn point and the direction for enemy attack.
    '''
    data = []

    x = 0
    y = 0
    
    for width in range(SCREEN_WIDTH-1):
        pixelColor = screen.get_at((x, y))

        if pixelColor == SPAWN_COLOR:
            spawnCoordinates = (x, y - 15)
            spawnDirection = mapDirectionPoints[1]
            break

        else:
            x += 1

    for height in range(SCREEN_HEIGHT-1):
        pixelColor = screen.get_at((x, y))

        if pixelColor == SPAWN_COLOR:
            spawnCoordinates = (x + 15, y)
            spawnDirection = mapDirectionPoints[2]
            break

        else:
            y += 1
        
    for width in range(SCREEN_WIDTH-1):
        pixelColor = screen.get_at((x, y))

        if pixelColor == SPAWN_COLOR:
            spawnCoordinates = (x, y + 15)
            spawnDirection = mapDirectionPoints[0]
            break

        else:
            x -= 1

    for height in range(SCREEN_HEIGHT-1):
        pixelColor = screen.get_at((x, y))

        if pixelColor == SPAWN_COLOR:
            spawnCoordinates = (x - 15, y)
            spawnDirection = mapDirectionPoints[3]
            break

        else:
            y -= 1

    data.append(spawnCoordinates)
    data.append(spawnDirection)

    return data


def find_enemy_direction_change() -> list:
    ''' Returns all coordinates with direction change data.'''
    changeDirectionData = [[], [], [], []]  # [[up], [down], [left], [right]]

    for y in range(SCREEN_HEIGHT):
        for x in range(SCREEN_WIDTH):
            coordinates = (x, y)

            pixelColor = screen.get_at(coordinates)

            if pixelColor == GO_UP_COLOR:
                changeDirectionData[0].append(coordinates)

            if pixelColor == GO_DOWN_COLOR:
                changeDirectionData[1].append(coordinates)

            if pixelColor == GO_LEFT_COLOR:
                changeDirectionData[2].append(coordinates)

            if pixelColor == GO_RIGHT_COLOR:
                changeDirectionData[3].append(coordinates)
                
    return changeDirectionData


def read_map_data() -> list:
    ''' Reads map data and returns mapData content.'''

    mapData = []

    screen.blit(gameMapConfig, (0, 0))

    spawnData = find_enemy_spawn()
    directionData = find_enemy_direction_change()

    mapData.append(spawnData)
    mapData.append(directionData)

    return mapData


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
    side = randint(0, 3)

    if side == 0:
        x = -20
        y = randint(0, SCREEN_HEIGHT)
        
    if side == 1:
        x = SCREEN_WIDTH + 20
        y = randint(0, SCREEN_HEIGHT)

    if side == 2:
        x = randint(0, SCREEN_WIDTH)
        y = -20
        
    if side == 3:
        x = randint(0, SCREEN_WIDTH)
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


# ========== Start ========== #
init()

# Main game loop
appRunning = True
while appRunning:
    if isDebugModeActive:
        screen.fill((0, 0, 0))
        screen.blit(gameMapConfig,(0,0))

    else:
        screen.blit(gameMap,(0,0))

    cursor_movement()
    check_bullet_hit()

    # Update and draw screen.
    for enemy in enemyList:
        for directionPoints in mapData[1]:
            
            if isDebugModeActive:
                print()
                print("mapData:", mapData)
                print("mapData[1]:", mapData[1])
                print("mapData[1][0]:", mapData[1][0])

            for point in directionPoints:
                if isDebugModeActive:
                    print("directionPoints", directionPoints)
                    print("point", point)


                distance = get_distance(enemy.x, enemy.y, point[0], point[1])
                if distance < enemy.r/2:
                    enemy.moveDirection = mapDirectionPoints[0]
                    break


        enemy.movement()
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
            if event.key == pygame.K_1:
                enemyList.append(Enemy_class1(mapData[0][0], mapData[0][1]))
                
            if event.key == pygame.K_p:
                isDebugModeActive = not isDebugModeActive

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_presses = pygame.mouse.get_pressed()
            if mouse_presses[0]:
                player_coordinates = (player.x, player.y)
                crosshair_coordinates = (crosshair.x, crosshair.y)
                spawn_bullet(player_coordinates, crosshair_coordinates)

    

    # Update screen
    pygame.display.flip()
    pygame.time.Clock().tick(120)