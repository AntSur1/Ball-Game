import pygame
from threading import Timer
from config import *
from classes import *

pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(30)
pygame.key.set_repeat(500)

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
gameOverSound = pygame.mixer.Sound('sounds/gameOver.wav')

# Fonts
gameStateFont = pygame.font.SysFont("Consolas", 30)
menuTitleFont = pygame.font.SysFont("freesansbold", 64)

# todo PUT THIS SOMEWHERE ELSE ?
# Menu text 
menuTitleText = menuTitleFont.render("Ball-Game", True, BLACK)
menuGameOverText = menuTitleFont.render("Game Over", True, BLACK)


buttonList = [ ]
enemyList = [ ]
bulletList = [ ]
popFlashes = [ ]

player = None
crosshair = None
mapData = [ ]  # [[(spawnCoordinates), [[spawnDirection]], [directionPoint], [directionPoint]... ]]
mapDirectionPoints = [[0, -1], [0, 1], [-1, 0], [1, 0]]  # up, down, left, right

gameTick = 0
score = 0
playerHp = 1
bulletsShot = 0
bulletPenetration = 1  # TODO upgrades?
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
    global buttonList, player, crosshair, mapData

    # Reads map data
    screen.blit(gameMapConfig, (0,0))
    mapData = read_map_data()
    #print(mapData)

    # Creates a start button and centers it.
    startButton = Button("Start", (0, SCREEN_HEIGHT // 2), "isMenuActive")
    startButton.blit_self()
    startButton.x = SCREEN_WIDTH / 2 - startButton.width / 2
    buttonList.append(startButton)
    
    pygame.mouse.set_pos(MIDDLE_OF_SCREEN)

    player = Player(MIDDLE_OF_SCREEN, 15, GREEN)
    crosshair = Crosshair(MIDDLE_OF_SCREEN)

    introTuneSound.play()


def prepare_new_game() -> None:
    '''
    Resets crucial game variables.
    '''
    global score, playerHp, bulletsShot, bulletPenetration, player

    score = 0
    playerHp = 1
    bulletsShot = 0
    bulletPenetration = 0

    player = Player(MIDDLE_OF_SCREEN, 15, GREEN)


def draw_menu() -> None:
    '''
    Creates and draws a menu and a GUI.
    '''
    menuTitleTextCoordinates = (center("x", menuTitleText), 60)
    menuGameOverTextCoordinates = (center("x", menuGameOverText), 120)

    screen.fill(WHITE)
    screen.blit(menuTitleText, menuTitleTextCoordinates)

    if playerHp == 0:
        screen.blit(menuGameOverText, menuGameOverTextCoordinates)

    
    for button in buttonList:
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
    global bulletsShot

    bulletsShot += 1
    bulletList.append(Bullet(playerCoords, crosshairCoords, bulletPenetration, bulletsShot))
    playerShotSound.play()


def spawn_enemy_wave(enemyType: object, ammountOfEnemies: int, delay: int) -> None:
    '''
    Spawns an enemy wave.
    '''
    def spawn_enemy(loop: int):
        x = mapData[0][0]
        y = mapData[0][1]

        enemyList.append(enemyType(x, y))

        # Schedule the next enemy spawn
        if loop > 0:
            t = Timer(delay / 1000, lambda: spawn_enemy(loop - 2))
            t.start()

    # Start the first enemy spawn
    spawn_enemy(ammountOfEnemies)


def detect_bullets() -> None:
    '''
    Checks if a bullet has an enemy.
    '''
    global score

    for enemy in enemyList:
        for bullet in bulletList:
            distance = get_distance(enemy.x, enemy.y, bullet.x, bullet.y)

            # Hit and hit cooldown detection
            if distance <= enemy.r:
                if bullet.id not in enemy.bulletCooldown:
                    enemy.hp -= 1
                    bullet.pp -= 1

                    popFlashes.append(Pop_Flash((bullet.x, bullet.y), gameTick))
                    enemyHitSound.play()

                    enemy.bulletCooldown.append(bullet.id)

                if enemy.hp <= 0:
                    score += enemy.scoreReward
                    enemyList.remove(enemy)
                
                if bullet.pp <= 0:
                    bulletIndex = enemy.bulletCooldown.index(bullet.id)
                    enemy.bulletCooldown.pop(bulletIndex)
                    bulletList.remove(bullet)
            
            else:
                if bullet.id in enemy.bulletCooldown:
                    bulletIndex = enemy.bulletCooldown.index(bullet.id)
                    enemy.bulletCooldown.pop(bulletIndex)


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
            for point in directionPoints:
                distance = get_distance(enemy.x, enemy.y, point[0], point[1])
                if distance < 10:  # 10 because it's the default enemy radius
                    enemy.moveDirection = mapDirectionPoints[i]
                    break

        if out_of_bounds_check(enemy.x, enemy.y):
            enemyList.remove(enemy)
            playerHp -= enemy.maxHp
            print("playerHp -", enemy.maxHp)

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


def update_game_state_texts() -> None:
    '''
    Updates game state texts.
    '''    
    scoreText = gameStateFont.render(f"Score: {score}", True, WHITE)
    playerHpText = gameStateFont.render(f"Health: {playerHp}", True, WHITE)

    screenPaddingX = 10

    screen.blit(scoreText, (screenPaddingX, 5))
    screen.blit(playerHpText, (screenPaddingX, 35))


def run_game() -> None:
    '''
    Updates and draws screen.
    '''
    global playerHp

    screen.blit(gameMap, (0,0))

    detect_bullets()
    
    update_enemies()
    update_bullets()
    update_player()
    update_cursor()
        
    # Draw pop flash
    for popFlash in popFlashes:
        popFlash.self_draw()
        
        if popFlash.destructionTime <= gameTick:
            popFlashes.remove(popFlash)

    update_game_state_texts()
    
    if playerHp <= 0:
        end_game()


def end_game() -> None:
    global enemyList, bulletList, popFlashes, player, isMenuActive
    
    gameOverSound.play()

    enemyList = [ ]
    bulletList = [ ]
    popFlashes = [ ]

    player = None
    isMenuActive = True


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

            # DEBUG
            if event.key == pygame.K_l:
                spawn_enemy_wave(Enemy1, 3, 500)
            # DEBUG

        if isMenuActive:
            # Menu functionality
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttonList[0].background.collidepoint(event.pos):
                    buttonClickSound.play()
                    isMenuActive = False
                    pygame.mouse.set_visible(False)
                    gameStartSound.play()
                    prepare_new_game()

        else:
            # Player shoot
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousePresses = pygame.mouse.get_pressed()
                if mousePresses[0]:
                    playerCoordinates = (player.x, player.y)
                    crosshairCoordinates = (crosshair.x, crosshair.y)
                    spawn_bullet(playerCoordinates, crosshairCoordinates)
    
            # Spawns enemies
            if event.type == pygame.KEYDOWN:
                if keyHeldDown[pygame.K_HOME]:
                    x = mapData[0][0]
                    y = mapData[0][1]


                    # TODO Every base enemy should spawn 5 times every (enemy nr) seconds
                    # Base enemies
                    if event.key == pygame.K_1:
                        enemyList.append(Enemy1(x, y))

                    elif event.key == pygame.K_2:
                        enemyList.append(Enemy2(x, y))

                    elif event.key == pygame.K_3:
                        enemyList.append(Enemy3(x, y))

                    elif event.key == pygame.K_4:
                        enemyList.append(Enemy4(x, y))

                    elif event.key == pygame.K_5:
                        enemyList.append(Enemy5(x, y))

                    elif event.key == pygame.K_6:
                        enemyList.append(Enemy6(x, y))

                    elif event.key == pygame.K_7:
                        enemyList.append(Enemy7(x, y))

                    if False:
                    # TODO 1 boss should spawn every 30 seconds. The boss spawns should look like: this
                    # 1 nr1 
                    # 2 nr1 
                    # 3 nr1 
                    # 1 nr2
                    # 2 nr2
                    # 2 nr2, 1 nr1
                    # 2 nr2, 2 nr1
                    # 1 nr3
                    # 2 nr3
                    # 2 nr3, 2 nr1
                    # 2 nr3, 2 nr2, 2 nr1
                    # 1 nr 3
                        pass

                    # Bosses
                    elif event.key == pygame.K_8:
                        enemyList.append(Boss1(x, y))

                    elif event.key == pygame.K_9:
                        enemyList.append(Boss2(x, y))

                    elif event.key == pygame.K_0:
                        enemyList.append(Boss3(x, y))

                    elif event.key == pygame.K_p:
                        enemyList.append(Boss4(x, y))


    # Update screen
    pygame.display.flip()
    pygame.time.Clock().tick(120)