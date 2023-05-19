import pygame

pygame.init()

# Set up the screen
screen = pygame.display.set_mode((400, 400))

# Set up colors
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)

# Set up font
buttonFont = pygame.font.Font(None, 34)

# Set up global variables
thisVariable1 = True

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
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.background.collidepoint(event.pos):
                global_var = globals()[self.variable]
                globals()[self.variable] = not global_var

    def blit_self(self):
        # Check if mouse is over button
        if self.background.collidepoint(pygame.mouse.get_pos()):
            # Change button color
            color = GRAY
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



# Create button objects
button1 = Button("Boobs", (50, 50), "thisVariable1")

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        button1.handle_event(event)
    
    # Fill screen with background color
    screen.fill((255, 255, 255))
    
    # Draw buttons
    button1.blit_self()
    
    print(thisVariable1)

    pygame.display.update()

pygame.quit()
