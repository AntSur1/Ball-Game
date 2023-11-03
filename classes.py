import pygame
import math
from config import *
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
buttonFont = pygame.font.SysFont("freesansbold", 42)


# Functions
def calculate_angle(coordinates1: tuple, coordinates2: tuple) -> float:
    '''
    Calculates the angle between two points in degrees.
    '''
    x1, y1 = coordinates1
    x2, y2 = coordinates2
    try:
        angle = math.atan((y2 - y1) / (x2 - x1))
    except:
        angle = 0

    rotation = 360 - math.degrees(angle)
    return rotation


# Classes
class Button(object):
    '''
    Creates a clickable button.
    '''
    def __init__(self, text: str, coordinates: tuple, variable: str) -> None:
        self.text = text
        self.x, self.y = coordinates
        self.renderedText = buttonFont.render("Start", True, BLACK)

        self.width = self.renderedText.get_width()
        self.height = self.renderedText.get_height()

        self.variable = variable
        
        self.paddingX = 28
        self.paddingY = self.paddingX / 2
        self.background = pygame.draw.rect(screen, WHITE, (self.x - self.paddingX,
                                                                  self.y - self.paddingY,
                                                                  self.width + 2 * self.paddingX,
                                                                  self.height + 2 * self.paddingY), 0, 2)

    def draw_self(self):
        # Check if mouse is over button
        if self.background.collidepoint(pygame.mouse.get_pos()):
            # Change button color
            color = LIGHT_GRAY
        else:
            color = WHITE

        self.border = pygame.draw.rect(screen, BLACK, (self.x - self.paddingX - 1,
                                                                     self.y - self.paddingY - 1,
                                                                     self.width + 2 * self.paddingX + 2,
                                                                     self.height + 2 * self.paddingY + 2), 0, 2)
        self.background = pygame.draw.rect(screen, color, (self.x - self.paddingX,
                                                                  self.y - self.paddingY,
                                                                  self.width + 2 * self.paddingX,
                                                                  self.height + 2 * self.paddingY), 0, 2)

        screen.blit(self.renderedText, (self.x, self.y))


class Crosshair(object):
    '''
    Creates a movable croshair.
    '''
    def __init__(self, coordinates: tuple) -> None:
        self.x, self.y = coordinates
        self.width = 2
        self.height = 8
        self.middleSpaceX = 3
        self.middleSpaceY = 7
        self.color = LIGHT_GRAY

    def draw_self(self) -> None:
        pygame.draw.rect(screen, self.color, (self.x, self.y - self.middleSpaceY, self.width, self.height))

        pygame.draw.rect(screen, self.color, (self.x, self.y + self.middleSpaceY, self.width, self.height))

        pygame.draw.rect(screen, self.color, (self.x - self.middleSpaceY - self.middleSpaceX, self.y + self.middleSpaceX, self.height, self.width))

        pygame.draw.rect(screen, self.color, (self.x + self.middleSpaceY - self.middleSpaceX, self.y + self.middleSpaceX, self.height, self.width))

    def movement(self, coordinates: tuple) -> None:
        self.x, self.y = coordinates


class Dot(object):
    '''
    Creates a base entity.
    '''
    def __init__(self, coordinates: tuple, radius: int = 0, color: int = BLACK) -> None:
        self.x, self.y = coordinates
        self.r = radius
        self.color = color

    def draw_self(self) -> None:
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.r)


class Player(Dot):
    '''
    Creates a playable character.
    '''
    def __init__(self, coordinates: tuple, radius: int = 0, color: int = BLACK) -> None:
        super().__init__(coordinates, radius, color)
        # Base speed factors
        self.speed = 1
        self.vx = 0
        self.vy = 0
        self.friction = 0.18
    
    def movement(self, key) -> None:
        if key[pygame.K_w]:
            self.vy -= self.speed
        if key[pygame.K_s]:
            self.vy += self.speed
        if key[pygame.K_a]:
            self.vx -= self.speed
        if key[pygame.K_d]:
            self.vx += self.speed

        # Apply friction.
        self.vx *= (1 - self.friction)
        self.vy *= (1 - self.friction)

        # Update position based on velocity.
        newX = self.x + self.vx
        newY = self.y + self.vy

        # Check if new position is outside the screen.
        if newX < self.r:
            newX = self.r
            self.vx = 0

        elif newX > SCREEN_WIDTH - self.r:
            newX = SCREEN_WIDTH - self.r
            self.vx = 0

        if newY < self.r:
            newY = self.r
            self.vy = 0

        elif newY > SCREEN_HEIGHT - self.r:
            newY = SCREEN_HEIGHT - self.r
            self.vy = 0

        # Set new coordinates.
        self.x = newX
        self.y = newY

    def draw_self(self) -> None:
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.r)
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.r - 1)

    def draw_reload_bar(self, gameTicks, doneBy, currentReloadSpeed) -> None:
        if doneBy > gameTicks:
            ticksLeft = doneBy - gameTicks
        else:
            ticksLeft = 0

        ticksLeftPrecentage = ticksLeft / currentReloadSpeed

        x = self.x - 20 
        y = self.y + self.r + 10
        width = 40
        height = 5

        pygame.draw.rect(screen, BLACK, (
            (x - 1 , y - 1),
            (width + 2, height + 2)
        ))

        pygame.draw.rect(screen, GRAY, (
            (x, y),
            (width, height)
        ))

        pygame.draw.rect(screen, LIGHT_GRAY, (
            (x, y),
            (width * ( 1 - ticksLeftPrecentage ), height)
        ))

    def draw_penetration_upgrade_feedback(self) -> None:
        x = self.x - 20
        y = self.y + self.r + 10
        width = 2
        height = 5

        pygame.draw.rect(screen, GREEN, (
            (x, y), (width, height)))

    def draw_reload_upgrade_feedback(self) -> None:
        x = self.x - 20
        y = self.y + self.r + 10
        width = 2
        height = 5

        pygame.draw.rect(screen, BLUE, (
            (x + width, y), (width, height)))


class Bullet(object):
    '''
    Creates a shootable bullet.
    '''
    def __init__(self, coordinates: tuple, targetCoordinates: tuple = (0, 0), penetrationPoionts: int = 1, bulletID: int = 0) -> None:
        self.x, self.y = coordinates
        self.tx, self.ty = targetCoordinates
        self.pp = penetrationPoionts
        self.width = 5
        self.height = self.width
        self.color = YELLOW
        self.spawnAngle = calculate_angle((self.x, self.y), targetCoordinates)  # Different from bulletAngle for some reason
        self.speed = 5
        self.bulletAngle = math.atan2(self.ty - self.y, self.tx - self.x)
        self.id = bulletID

        # Spawn a new bullet
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.set_colorkey((0, 0, 0))
        self.surface.fill(self.color)
        self.rect = self.surface.get_rect()

        # Rotate the bullet
        oldCenter = self.rect.center
        self.newSurface = pygame.transform.rotate(self.surface, self.spawnAngle)
        self.rect = self.newSurface.get_rect()
        self.rect.center = oldCenter

    def update(self) -> None:
        # Move bullet based on its rotation
        self.x += math.cos(self.bulletAngle) * self.speed
        self.y += math.sin(self.bulletAngle) * self.speed

    def draw_self(self) -> None:
        # Redraw bullet
        self.surface.fill(self.color)
        self.rect = self.surface.get_rect()
        self.rect.center = (self.x, self.y)

        screen.blit(self.newSurface, self.rect)


class Pop_Flash(object):
    '''
    Creates a shortlived enemy hit effect.
    '''
    def __init__(self, coordinates: tuple, currentTime: int = 0) -> None:
        self.x, self.y = coordinates
        self.visibleTime = 5
        self.destructionTime = currentTime + self.visibleTime
        self.size = 5
        self.indent = 3
        self.points = (
            (self.x - self.size, self.y),
            (self.x - self.size / self.indent, self.y + self.size / self.indent),

            (self.x, self.y + self.size),
            (self.x + self.size / self.indent, self.y + self.size / self.indent),

            (self.x + self.size, self.y),
            (self.x + self.size / self.indent, self.y - self.size / self.indent),
            
            (self.x, self.y - self.size),
            (self.x - self.size / self.indent, self.y - self.size / self.indent)
        )
    
    def self_draw(self) -> None:
        pygame.draw.polygon(screen, WHITE, self.points)


class Enemy(Dot):
    '''
    Creates a default enemy.
    '''
    def __init__(self, coordinates: tuple, spawnDirection: list) -> None:
        super().__init__(coordinates)
        self.moveDirection = spawnDirection
        self.bulletCooldown = [ ]
        self.speed = 1
        self.maxHp = 1
        self.hp = self.maxHp

    def movement(self) -> None:
        vx = self.moveDirection[0]
        vy = self.moveDirection[1]

        self.x += self.speed * vx
        self.y += self.speed * vy

    def draw_health_bar(self) -> None:
        hpLost = self.maxHp - self.hp
        hpLostPrecentage = hpLost / self.maxHp

        x = self.x - 20 
        y = self.y - self.r  - 15
        width = 40
        height = 5

        pygame.draw.rect(screen, BLACK, (
            (x - 1 , y - 1),
            (width + 2, height + 2)
        ))

        pygame.draw.rect(screen, RED, (
            (x, y),
            (width, height)
        ))

        pygame.draw.rect(screen, GREEN, (
            (x, y),
            (width * ( 1 - hpLostPrecentage ), height)
        ))


class Enemy1(Enemy):
    '''
    Creates a type 1 enemy.
    '''
    def __init__(self, coordinates: tuple, spawnDirection: list) -> None:
        super().__init__(coordinates, spawnDirection)
        self.r = 10
        self.color = PURPLE
        self.moveDirection = spawnDirection
        self.speed = 1.2
        self.maxHp = 2
        self.hp = self.maxHp
        self.scoreReward = 2


class Enemy2(Enemy):
    '''
    Creates a type 2 enemy.
    '''
    def __init__(self, coordinates: tuple, spawnDirection: list) -> None:
        super().__init__(coordinates,  spawnDirection)
        self.r = 15
        self.color = BLUE
        self.moveDirection = spawnDirection
        self.speed = 0.6
        self.maxHp = 4
        self.hp = self.maxHp
        self.scoreReward = 4


class Enemy3(Enemy):
    '''
    Creates a type 3 enemy.
    '''
    def __init__(self, coordinates: tuple, spawnDirection: list) -> None:
        super().__init__(coordinates, spawnDirection)
        self.r = 13
        self.color = DARK_GREEN
        self.moveDirection = spawnDirection
        self.speed = 1
        self.maxHp = 3
        self.hp = self.maxHp
        self.scoreReward = 3


class Enemy4(Enemy):
    '''
    Creates a type 4 enemy.
    '''
    def __init__(self, coordinates: tuple, spawnDirection: list) -> None:
        super().__init__(coordinates, spawnDirection)
        self.r = 8
        self.color = WHITE
        self.moveDirection = spawnDirection
        self.speed = 2
        self.maxHp = 1
        self.hp = self.maxHp
        self.scoreReward = 3


class Enemy5(Enemy):
    '''
    Creates a type 5 enemy.
    '''
    def __init__(self, coordinates: tuple, spawnDirection: list) -> None:
        super().__init__(coordinates, spawnDirection)
        self.r = 12
        self.color = YELLOW
        self.moveDirection = spawnDirection
        self.speed = 1.8
        self.maxHp = 3
        self.hp = self.maxHp
        self.scoreReward = 4


class Enemy6(Enemy):
    '''
    Creates a type 6 enemy.
    '''
    def __init__(self, coordinates: tuple, spawnDirection: list) -> None:
        super().__init__(coordinates, spawnDirection)
        self.r = 18
        self.color = ORANGE
        self.moveDirection = spawnDirection
        self.speed = 1
        self.maxHp = 15
        self.hp = self.maxHp
        self.scoreReward = 10


class Enemy7(Enemy):
    '''
    Creates a type 7 enemy.
    '''
    def __init__(self, coordinates: tuple, spawnDirection: list) -> None:
        super().__init__(coordinates, spawnDirection)
        self.r = 10
        self.color = AQUA
        self.moveDirection = spawnDirection
        self.speed = 1.5
        self.maxHp = 4
        self.hp = self.maxHp
        self.scoreReward = 6


class Boss1(Enemy):
    '''
    Creates a type 1 boss.
    '''
    def __init__(self, coordinates: tuple, spawnDirection: list) -> None:
        super().__init__(coordinates, spawnDirection)
        self.r = 30
        self.color = PINK
        self.moveDirection = spawnDirection
        self.speed = 1
        self.maxHp = 30
        self.hp = self.maxHp
        self.scoreReward = 30


class Boss2(Enemy):
    '''
    Creates a type 2 boss.
    '''
    def __init__(self, coordinates: tuple, spawnDirection: list) -> None:
        super().__init__(coordinates, spawnDirection)
        self.r = 40
        self.color = RED
        self.moveDirection = spawnDirection
        self.speed = 0.5
        self.maxHp = 40
        self.hp = self.maxHp
        self.scoreReward = 30


class Boss3(Enemy):
    '''
    Creates a type 3 boss.
    '''
    def __init__(self, coordinates: tuple, spawnDirection: list) -> None:
        super().__init__(coordinates, spawnDirection)
        self.r = 50
        self.color = BROWN
        self.moveDirection = spawnDirection
        self.speed = 0.3
        self.maxHp = 60
        self.hp = self.maxHp
        self.scoreReward = 60


class Boss4(Enemy):
    '''
    Creates a type 4 boss.
    '''
    def __init__(self, coordinates: tuple, spawnDirection: list) -> None:
        super().__init__(coordinates, spawnDirection)
        self.r = 100
        self.color = BLACK
        self.moveDirection = spawnDirection
        self.speed = 0.2
        self.maxHp = 200
        self.hp = self.maxHp
        self.scoreReward = 200
