import pygame

# Title
pygame.display.set_caption("Ball Game")

# Create screen
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
MIDDLE_OF_SCREEN = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Colors
WHITE = 250, 250, 250
BLACK = 0, 0, 0
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
BACKGROUND = 5, 5, 10

# Other
enemyList = []
player = None


# Classes
class Dot(object):
    def __init__(self, coordinates: tuple = (0, 0), radius: int = 0, color: int = BLACK):
        self.x, self.y = coordinates
        self.r = radius
        self.color = color
        self.render_body = None

    def blit_self(self):
        self.render_body = pygame.draw.circle(screen, self.color, (self.x, self.y), self.r)


class Player(Dot):
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
        


# Functions
def init():
    global player

    player = Player(MIDDLE_OF_SCREEN, 15, GREEN)





# ========== Start ========== #
init()





# Main game loop
appRunning = True
while appRunning:
    screen.fill(BACKGROUND)

    # Update entities.
    player.blit_self()

    for entity in enemyList:
        entity.blit_self()


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