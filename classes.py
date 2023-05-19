import pygame
import math
from config import *

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


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
class Crosshair(object):
    '''
    Creates a movable croshair.
    '''
    def __init__(self, coordinates: tuple = (0, 0)):
        self.x, self.y = coordinates
        self.width = 2
        self.height = 8
        self.middleSpaceX = 3
        self.middleSpaceY = 7
        self.color = LIGHT_GRAY

    def draw_self(self):
        # Draw top, bottom, left and right lines 
        pygame.draw.rect(screen, self.color, (self.x, self.y - self.middleSpaceY, self.width, self.height))

        pygame.draw.rect(screen, self.color, (self.x, self.y + self.middleSpaceY, self.width, self.height))

        pygame.draw.rect(screen, self.color, (self.x - self.middleSpaceY - self.middleSpaceX, self.y + self.middleSpaceX, self.height, self.width))

        pygame.draw.rect(screen, self.color, (self.x + self.middleSpaceY - self.middleSpaceX, self.y + self.middleSpaceX, self.height, self.width))

    def movement(self, coordinates: tuple):
        self.x, self.y = coordinates


class Dot(object):
    '''
    Base entity texture.
    '''
    def __init__(self, coordinates: tuple = (0, 0), radius: int = 0, color: int = BLACK):
        self.x, self.y = coordinates
        self.r = radius
        self.color = color

    def draw_self(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.r)


class Player(Dot):
    '''
    Playable character.
    '''
    def __init__(self, coordinates: tuple = (0, 0), radius: int = 0, color: int = BLACK):
        super().__init__(coordinates, radius, color)
        #! Who said something about stolen code ;)
        # Base speed factors
        self.speed = 1.3
        self.vx = 0
        self.vy = 0
        self.friction = 0.13
    
    def movement(self, key):
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


class Bullet(object):
    '''
    Creates a shootable bullet.
    '''
    def __init__(self, coordinates: tuple = (0, 0), targetCoordinates: tuple = (0, 0), hp: int = 1):
        self.x, self.y = coordinates
        self.tx, self.ty = targetCoordinates
        self.hp = hp
        self.width = 5
        self.height = self.width
        self.color = YELLOW
        self.spawnAngle = calculate_angle(coordinates, targetCoordinates)  # Different from bulletAngle for some reason.
        self.speed = 5
        self.bulletAngle = math.atan2(self.ty - self.y, self.tx - self.x)

        # Spawn a new bullet.
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.set_colorkey((0, 0, 0))
        self.surface.fill(self.color)
        self.rect = self.surface.get_rect()

        # Rotate the bullet.
        oldCenter = self.rect.center
        self.new = pygame.transform.rotate(self.surface, self.spawnAngle)
        self.rect = self.new.get_rect()
        self.rect.center = oldCenter

    def update(self):
        # Move bullet based on its rotation.
        self.x += math.cos(self.bulletAngle) * self.speed
        self.y += math.sin(self.bulletAngle) * self.speed

    def draw_self(self):
        # Redraw bullet.
        self.surface.fill(self.color)
        self.rect = self.surface.get_rect()
        self.rect.center = (self.x, self.y)

        screen.blit(self.new, self.rect)


class Pop_Flash(object):
    '''
    Creates a shortlived enemy hit effect.
    '''
    def __init__(self, coordinates: tuple = (0, 0), currentTime: int = 0) -> None:
        self.coordinates = coordinates
        self.visibleTime = 5
        self.destructionTime = currentTime + self.visibleTime
        self.size = 5
        self.indent = 3
        self.points = (
            (coordinates[0] - self.size, coordinates[1]),
            (coordinates[0] - self.size / self.indent, coordinates[1] + self.size / self.indent),

            (coordinates[0], coordinates[1] + self.size),
            (coordinates[0] + self.size / self.indent, coordinates[1] + self.size / self.indent),

            (coordinates[0] + self.size, coordinates[1]),
            (coordinates[0] + self.size / self.indent, coordinates[1] - self.size / self.indent),
            
            (coordinates[0], coordinates[1] - self.size),
            (coordinates[0] - self.size / self.indent, coordinates[1] - self.size / self.indent)
        )
    
    def self_draw(self):
        pygame.draw.polygon(screen, WHITE, self.points)


class Enemy_walker(Dot):
    '''
    Creates a walker enemy.
    '''
    def __init__(self, coordinates: tuple = (0, 0)):
        super().__init__(coordinates)
        self.r = 10
        self.color = RED
        self.speed = 1.3

    def movement(self, player_coordinates):
        x, y = player_coordinates
        dx = x - self.x
        dy = y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        self.x += dx / distance * self.speed * 2.3
        self.y += dy / distance * self.speed * 2.3


class Enemy(Dot):
    '''
    Creates a default enemy.
    '''
    def __init__(self, coordinates: tuple, spawnDirection: list):
        super().__init__(coordinates)
        self.moveDirection = spawnDirection
        self.hitCooldown = False
        self.speed = 1
        self.hp = 1

    def movement(self):
        vx = self.moveDirection[0]
        vy = self.moveDirection[1]

        self.x += self.speed * vx
        self.y += self.speed * vy

    def draw_health_bar(self):
        pygame.draw.rect(screen, BLACK, (
            (self.x - 21, self.y - 2 * self.r - 1),
            (42, 7)
        ))
        pygame.draw.rect(screen, GREEN, (
            (self.x - 20, self.y - 2 * self.r),
            (40, 5)
        ))
        
        
class Enemy1(Enemy):
    def __init__(self, coordinates: tuple, spawnDirection: list):
        super().__init__(coordinates, spawnDirection)
        self.r = 10
        self.color = PURPLE
        self.moveDirection = spawnDirection
        self.speed = 1
        self.hp = 1


class Enemy2(Enemy):
    def __init__(self, coordinates: tuple, spawnDirection: list):
        super().__init__(coordinates,  spawnDirection)
        self.r = 15
        self.color = BLUE
        self.moveDirection = spawnDirection
        self.speed = 0.6
        self.hp = 3
