import pygame

screen = pygame.display.set_mode((100, 100))

pygame.init()
pygame.mixer.init() 
sound_ = pygame.mixer.Sound('sounds/enemyHit.wav')

# Main game loop
appRunning = True
while appRunning:
    print("a")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            appRunning = False

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_DELETE, pygame.K_ESCAPE]:
                appRunning = False

            if event.key == pygame.K_0:
               sound_.play()