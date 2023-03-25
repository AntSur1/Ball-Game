import pygame
from config import *

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Classes
class Crosshair(object):
    """
    Movable croshair.
    """
    def __init__(self, coordinates: tuple = (0, 0)):
        self.x, self.y = coordinates
        self.width = 2
        self.height = 8
        self.middle_space_x = 3
        self.middle_space_y = 7
        self.color = LIGHT_GRAY
     

    def draw_self(self):
        # Draw top, bottom, left and right lines 
        pygame.draw.rect(screen, self.color, (self.x, self.y - self.middle_space_y, self.width, self.height))

        pygame.draw.rect(screen, self.color, (self.x, self.y + self.middle_space_y, self.width, self.height))

        pygame.draw.rect(screen, self.color, (self.x - self.middle_space_y - self.middle_space_x, self.y + self.middle_space_x, self.height, self.width))

        pygame.draw.rect(screen, self.color, (self.x + self.middle_space_y - self.middle_space_x, self.y + self.middle_space_x, self.height, self.width))
    

    def movement(self, coordinates: tuple):
        self.x, self.y = coordinates


class Dot(object):
    """
    Base entity texture.
    """
    def __init__(self, coordinates: tuple = (0, 0), radius: int = 0, color: int = BLACK):
        self.x, self.y = coordinates
        self.r = radius
        self.color = color


    def draw_self(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.r)


class Player(Dot):
    """
    Child of Dot. Is the playable character.
    """
    def __init__(self, coordinates: tuple = (0, 0), radius: int = 0, color: int = BLACK):
        super().__init__(coordinates, radius, color)
        # ! Who said stolen code ;)
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

        # Apply friction
        self.vx *= (1 - self.friction)
        self.vy *= (1 - self.friction)

        # Update position based on velocity
        new_x = self.x + self.vx
        new_y = self.y + self.vy

        # Check if new position is outside the screen
        if new_x < self.r:
            new_x = self.r
            self.vx = 0

        elif new_x > SCREEN_WIDTH - self.r:
            new_x = SCREEN_WIDTH - self.r
            self.vx = 0

        if new_y < self.r:
            new_y = self.r
            self.vy = 0

        elif new_y > SCREEN_HEIGHT - self.r:
            new_y = SCREEN_HEIGHT - self.r
            self.vy = 0

        # Set new coordinates
        self.x = new_x
        self.y = new_y
        
        
class Bullet(object):
    """
    Shootable bullet.
    """
    def __init__(self, coordinates: tuple, rotation: float):
        self.x, self.y = coordinates
        self.width = 5
        self.color = YELLOW
        self.rotation = rotation
    

    def draw_self(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.width))


    def movement(self):
        pass