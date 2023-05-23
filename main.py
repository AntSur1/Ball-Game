import pygame
from threading import Timer
from config import *
from classes import *

# Init pygame
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(30)
pygame.key.set_repeat(500)
pygame.display.set_caption("Ball Game")

# Init screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Init map
gameMapConfig = pygame.image.load(f"maps/{GAME_MAP_NR}/game-map-config.png")
gameMap = pygame.image.load(f"maps/{GAME_MAP_NR}/game-map.png")

# Init sounds
introTuneSound = pygame.mixer.Sound('sounds/introTune.wav')
gameStartSound = pygame.mixer.Sound('sounds/gameStart.wav')
buttonClickSound = pygame.mixer.Sound('sounds/buttonClick.wav')
enemyHitSound = pygame.mixer.Sound('sounds/enemyHit.wav')
playerShotSound = pygame.mixer.Sound('sounds/playerShot.wav')
gameOverSound = pygame.mixer.Sound('sounds/gameOver.wav')

# Init fonts
gameStateFont = pygame.font.SysFont("Consolas", 30)
menuTitleFont = pygame.font.SysFont("freesansbold", 64)

# Init menu texts
menuTitleText = menuTitleFont.render("Ball-Game", True, BLACK)
menuGameOverText = menuTitleFont.render("Game Over", True, BLACK)

# Init globar variables
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
bulletPP = 1  # penetration points
reloadSpeed = 100
reloadDoneBy = 1
isMenuActive = True


# Functions
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
    global score, playerHp, bulletsShot, bulletPP, reloadSpeed, player

    score = 0
    playerHp = 1
    bulletsShot = 0
    bulletPP = 0
    reloadSpeed = 200

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


def menu_button_functionality() -> None:
    '''
    Adds functionality to the menu button
    '''
    global isMenuActive

    buttonClickSound.play()
    isMenuActive = False
    pygame.mouse.set_visible(False)
    gameStartSound.play()
    prepare_new_game()


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
            pixelColor = screen.get_at((x, y))

            if pixelColor == GO_UP_COLOR:
                changeDirectionData[0].append((x, y))

            if pixelColor == GO_DOWN_COLOR:
                changeDirectionData[1].append((x, y))

            if pixelColor == GO_LEFT_COLOR:
                changeDirectionData[2].append((x, y))

            if pixelColor == GO_RIGHT_COLOR:
                changeDirectionData[3].append((x, y))

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
    bulletList.append(Bullet(playerCoords, crosshairCoords, bulletPP, bulletsShot))
    playerShotSound.play()


def request_bullet_shoot() -> None:
    '''
    Checks if a bullet is ready to be fired. 
    If it is it prepares the coordinates and shoots a bullet.
    '''
    global reloadDoneBy

    if reloadDoneBy <= gameTick:
        playerCoordinates = (player.x, player.y)
        crosshairCoordinates = (crosshair.x, crosshair.y)
        spawn_bullet(playerCoordinates, crosshairCoordinates)

        reloadDoneBy = gameTick + reloadSpeed


def spawn_enemy_wave(enemyType: object, ammountOfEnemies: int, delay: int) -> None:
    '''
    Spawns an enemy wave. One enemyType ammountOfEnemies nr of times with a delay time delay.
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
    Updates the player.
    '''
    player.movement(keyHeldDown)
    player.draw_self()
    player.draw_reload_bar(gameTick, reloadDoneBy)

    if score >= UPGRADE_COST:
        if bulletPP <= MAX_BULLET_PP:
            player.draw_penetration_upgrade_feedback()

        if reloadSpeed >= MIN_RELOAD_SPEED:
            player.draw_reload_upgrade_feedback()


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
    for bullet in bulletList:
        bullet.update()
        bullet.draw_self()

        if out_of_bounds_check(bullet.x, bullet.y):
            bulletList.remove(bullet)


def run_game() -> None:
    '''
    Updates and draws screen all sprites on screen.
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
    '''
    Ends the current game session and opens the menu.
    '''
    global enemyList, bulletList, popFlashes, player, isMenuActive
    
    gameOverSound.play()

    enemyList = [ ]
    bulletList = [ ]
    popFlashes = [ ]

    player = None
    isMenuActive = True
    pygame.mouse.set_visible(True)


def update_game_state_texts() -> None:
    '''
    Updates game state texts.
    '''    
    scoreText = gameStateFont.render(f"Score: {score}", True, WHITE)
    playerHpText = gameStateFont.render(f"Health: {playerHp}", True, WHITE)

    screenPaddingX = 10

    screen.blit(scoreText, (screenPaddingX, 5))
    screen.blit(playerHpText, (screenPaddingX, 35))


def request_reload_upgrade() -> None:
    '''
    Checks if upgrading the reload speed is possible.
    '''
    global reloadSpeed, score

    if score >= UPGRADE_COST:
        if reloadSpeed >= MIN_RELOAD_SPEED:
            score -= UPGRADE_COST
            reloadSpeed -= RELOAD_REDUCTION


def request_bullet_pp_upgrade() -> None:
    '''
    Checks if upgrading the bullet pp is possible.
    '''
    global bulletPP, score

    if score >= UPGRADE_COST:
        if bulletPP >= MAX_BULLET_PP:
            score -= UPGRADE_COST
            bulletPP += 1


def cheat_controls(inputKey: int):
    '''
    Checks what secret chet key combination was clicked and runs the secret command.
    '''
    # Give score
    global score

    if inputKey == pygame.K_l:
        score += 1

    # Spawn base enemies
    x = mapData[0][0]
    y = mapData[0][1]

    if inputKey == pygame.K_1:
        enemyList.append(Enemy1(x, y))

    elif inputKey == pygame.K_2:
        enemyList.append(Enemy2(x, y))

    elif inputKey == pygame.K_3:
        enemyList.append(Enemy3(x, y))

    elif inputKey == pygame.K_4:
        enemyList.append(Enemy4(x, y))

    elif inputKey == pygame.K_5:
        enemyList.append(Enemy5(x, y))

    elif inputKey == pygame.K_6:
        enemyList.append(Enemy6(x, y))

    elif inputKey == pygame.K_7:
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

    # Spawn bosses
    elif inputKey == pygame.K_8:
        enemyList.append(Boss1(x, y))

    elif inputKey == pygame.K_9:
        enemyList.append(Boss2(x, y))

    elif inputKey == pygame.K_0:
        enemyList.append(Boss3(x, y))

    elif inputKey == pygame.K_p:
        enemyList.append(Boss4(x, y))


# ========== Start ========== #
init()

# Main game loop
appRunning = True
while appRunning:
    gameTick += 1
    keyHeldDown = pygame.key.get_pressed()
    
    # Check if a menu is active or not
    if isMenuActive:
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
            # Gives the menu button functionality
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttonList[0].background.collidepoint(event.pos):
                    menu_button_functionality()

        else:
            # Checks for bullet shoot key
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousePresses = pygame.mouse.get_pressed()
                if mousePresses[0]:
                    request_bullet_shoot()
    
            if event.type == pygame.KEYDOWN:
                # Checks for upgrade keys
                if event.key == pygame.K_o:
                    request_reload_upgrade()

                if event.key == pygame.K_p:
                    request_bullet_pp_upgrade()

                # Checks for cheat keys
                if keyHeldDown[pygame.K_HOME]:
                    cheat_controls(event.key)


    # Update screen
    pygame.display.flip()
    pygame.time.Clock().tick(120)