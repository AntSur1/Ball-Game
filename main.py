import pygame
from random import randint, randrange
from config import *
from classes import *

pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(30)

pygame.display.set_caption("Ball Game")

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

gameMapConfig = pygame.image.load(f"maps/{GAME_MAP_NR}/game-map-config.png")
gameMap = pygame.image.load(f"maps/{GAME_MAP_NR}/game-map.png")

# todo PUT THIS SOMEWHERE ELSE ?
# Sounds
introTuneSound = pygame.mixer.Sound('sounds/introTune.wav')
gameStartSound = pygame.mixer.Sound('sounds/gameStart.wav')
buttonClickSound = pygame.mixer.Sound('sounds/buttonClick.wav')
enemyHitSound = pygame.mixer.Sound('sounds/enemyHit.wav')
playerShotSound = pygame.mixer.Sound('sounds/playerShot.wav')

# Fonts
gameStateFont = pygame.font.SysFont("Consolas", 30)
menuTitleFont = pygame.font.SysFont("freesansbold", 64)

# todo PUT THIS SOMEWHERE ELSE ?
# Menu text 
menuTitleText = menuTitleFont.render("Ball-Game", True, BLACK)
menuGameOverText = menuTitleFont.render("Game Over", True, BLACK)


# todo

todoList = []

todoList.append(TodoListItem("New enemies", ["Enemies"], "create a few more enemies and a boss or two."))
todoList.append(TodoListItem("Attack patterns", ["Enemies"], "How should the enemy waves look like?"))
todoList.append(TodoListItem("Player upgrades", ["Player"], "Upgrade bullet penetration and reload speed."))
todoList.append(TodoListItem("Death screen", ["Menu"], "Show a game over screen."))
todoList.append(TodoListItem("Higscore", ["Higscore"], "Save highscores."))

# todo


buttons = []

enemyList = [ ]
bulletList = [ ]
popFlashes = [ ]
soundChannels = [ ]

player = None
crosshair = None
mapData = [ ]  # [[(spawnCoordinates), [[spawnDirection]], [directionPoint], [directionPoint]... ]]
mapDirectionPoints = [[0, -1], [0, 1], [-1, 0], [1, 0]]  # up, down, left, right

gameTick = 0
score = 0
playerHp = 50
isDebugModeActive = False
isMenuActive = True


def center(axis: str, item) -> float:
    '''
    Takes in an axis and an item, and returns the coordinate the item will be centered on the coordinate axis.
    OBS: Should only be used with rendered text and images!
    '''
    if axis == "x":
        return SCREEN_WIDTH / 2 - item.get_width() / 2
    elif axis == "y":
        return SCREEN_HEIGHT / 2 - item.get_height() / 2
    else:
        return ValueError


def get_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    ''' Gets the distance between two points.'''
    distance = math.sqrt((x1-x2) ** 2 + (y1-y2) ** 2)
    return distance


def out_of_bounds_check(x: int, y: int) -> bool:
    ''' Checks if coordinates are outside of game screen.'''
    if x < -MAX_OUT_OF_BOUNDS_PX or x > SCREEN_WIDTH + MAX_OUT_OF_BOUNDS_PX:
        return True
    if y < -MAX_OUT_OF_BOUNDS_PX or y > SCREEN_HEIGHT + MAX_OUT_OF_BOUNDS_PX:
        return True
    
    return False


def init() -> None:
    '''
    Reads map config, creates the start menu, and calulates mouse and player start coordinates. 
    '''
    global buttons, player, crosshair, mapData

    # Reads map data
    screen.blit(gameMapConfig, (0,0))
    mapData = read_map_data()
    #print(mapData)

    # Creates a start button and centers it.
    startButton = Button("Start", (0, SCREEN_HEIGHT // 2), "isMenuActive")
    startButton.blit_self()
    startButton.x = SCREEN_WIDTH / 2 - startButton.width / 2
    buttons.append(startButton)
    
    pygame.mouse.set_pos(MIDDLE_OF_SCREEN)

    player = Player(MIDDLE_OF_SCREEN, 15, GREEN)
    crosshair = Crosshair(MIDDLE_OF_SCREEN)

    introTuneSound.play()


def start_new_game() -> None:
    '''
    Resets crucial game variables.
    '''
    global score, playerHp

    score = 0
    playerHp = 50


def draw_menu() -> None:
    '''
    Creates and draws a menu and a GUI.
    '''
    menuTitleTextCoordinates = (center("x", menuTitleText), 60)

    screen.fill(WHITE)
    screen.blit(menuTitleText, menuTitleTextCoordinates)
    
    for button in buttons:
        button.blit_self()


def find_enemy_spawn() -> list:
    '''
    Returns the coordinates for the enemy spawn point and the direction for enemy attack. \n Returns: [(spawnCoordinates), (spawnDirection)]
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


def find_enemy_direction_points() -> list:
    '''
    Returns all coordinates with direction change data.
    '''
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
    '''
    Reads map data and returns mapData content.
    '''
    mapData = []

    spawnData = find_enemy_spawn()
    directionData = find_enemy_direction_points()

    mapData.append(spawnData)
    mapData.append(directionData)

    return mapData


def spawn_bullet(playerCoords: tuple, crosshairCoords:tuple) -> None:
    ''' Creates a bullet at the player.'''
    bulletList.append(Bullet(playerCoords, crosshairCoords, 5))  # TODO change 5 to upgrade value
    playerShotSound.play()


def check_bullet_hit() -> None:
    '''
    Checks if a bullet has an enemy.
    '''
    global score

    for enemy in enemyList:
        for bullet in bulletList:
            distance = get_distance(enemy.x, enemy.y, bullet.x, bullet.y)

            # Hit and hit cooldown detection
            if distance < enemy.r:
                if not enemy.hitCooldown:
                    enemy.hp -= 1
                    bullet.pp -= 1
                    enemy.hitCooldown = True

                    popFlashes.append(Pop_Flash((bullet.x, bullet.y), gameTick))
                    enemyHitSound.play()

                if enemy.hp <= 0:
                    score += enemy.scoreReward
                    enemyList.remove(enemy)
                
                if bullet.pp <= 0:
                    bulletList.remove(bullet)

            else:
                enemy.hitCooldown = False


def update_cursor() -> None:
    ''' Moves the player crosshair to the mouse coordinates.'''
    mouseCoords = pygame.mouse.get_pos()
    crosshair.movement(mouseCoords)
    crosshair.draw_self()


def update_player() -> None:
    '''
    Updates player.
    '''
    player.movement(keyHeldDown)
    player.draw_self()


def update_enemies() -> None:
    '''
    Updates and draws enemies.
    '''
    global playerHp
    for enemy in enemyList:
        for i, directionPoints in enumerate(mapData[1]):
            
            # if isDebugModeActive:
            #     print()
            #     print("mapData:", mapData)
            #     print("mapData[1]:", mapData[1])
            #     print("mapData[1][0]:", mapData[1][0])

            for point in directionPoints:
                # if isDebugModeActive:
                #     print("directionPoints", directionPoints)
                #     print("point", point)
                distance = get_distance(enemy.x, enemy.y, point[0], point[1])
                if distance < 10:  # 10 because it's the default enemy radius
                    enemy.moveDirection = mapDirectionPoints[i]
                    break

        if out_of_bounds_check(enemy.x, enemy.y):
            enemyList.remove(enemy)
            playerHp -= 1
            print("playerHp -1")

        enemy.movement()
        enemy.draw_self()
        enemy.draw_health_bar()


def update_bullets() -> None:
    '''
    Updates and draws bullets.
    '''
    # Draw bullets
    for bullet in bulletList:
        bullet.update()
        bullet.draw_self()
        
        if out_of_bounds_check(bullet.x, bullet.y):
            bulletList.remove(bullet)


def update_game_state_text() -> None:
    '''
    Updates game state text.
    '''
    
    scoreText = gameStateFont.render(f"Score: {score}", True, WHITE)
    playerHpText = gameStateFont.render(f"Health: {playerHp}", True, WHITE)
    screen.blit(scoreText, (10, 5))
    screen.blit(playerHpText, (10, 35))


def run_game() -> None:
    '''
    Updates and draws screen.
    '''
    global playerHp
    if isDebugModeActive:
        screen.fill(BLACK)
        screen.blit(gameMapConfig, (0,0))

    else:
        screen.blit(gameMap, (0,0))

    check_bullet_hit()
    
    update_player()
    update_cursor()
    update_enemies()
    update_bullets()
        
    # Draw pop flash
    for popFlash in popFlashes:
        popFlash.self_draw()
        
        if popFlash.destructionTime <= gameTick:
            popFlashes.remove(popFlash)

    update_game_state_text()


# ========== Start ========== #
init()

# Main game loop
appRunning = True
while appRunning:
    gameTick += 1
    keyHeldDown = pygame.key.get_pressed()
    
    # Check if a menu is active or not.
    if isMenuActive:
        pygame.mouse.set_visible(True)
        draw_menu()
    
    else:
        run_game()


    # Detect events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            appRunning = False

        # Exit game
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_DELETE, pygame.K_ESCAPE]:
                appRunning = False


        if isMenuActive:
            # Menu functionality
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttons[0].background.collidepoint(event.pos):
                    buttonClickSound.play()
                    isMenuActive = False
                    pygame.mouse.set_visible(False)
                    gameStartSound.play()            

        else:
            # Player shoot
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousePresses = pygame.mouse.get_pressed()
                if mousePresses[0]:
                    playerCoordinates = (player.x, player.y)
                    crosshairCoordinates = (crosshair.x, crosshair.y)
                    spawn_bullet(playerCoordinates, crosshairCoordinates)
    
            # DEBUG START
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    isDebugModeActive = not isDebugModeActive

                if event.key == pygame.K_t:
                    print(todoList)            
            
            if keyHeldDown[pygame.K_1]:
                x = mapData[0][0]
                y = mapData[0][1]

                enemyList.append(Enemy1(x, y))

            elif keyHeldDown[pygame.K_2]:
                x = mapData[0][0]
                y = mapData[0][1]

                enemyList.append(Enemy2(x, y))
            #DEBUG END

    # Update screen
    pygame.display.flip()
    pygame.time.Clock().tick(120)