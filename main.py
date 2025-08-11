import pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Arena of Doom")
screen.fill((255, 255, 255))

game_state = "title"

# Fonts
font_big = pygame.font.SysFont(None, 72)

# Utility functions
def keep_in_bounds(location, width, height):
    return [max(width, min(location[0], 800-width)), max(height, min(location[1], 600-height))]
def update_pos(object, x, y, keep_object_in_bounds = True):
    object.location[0] += x
    object.location[1] += y
    if keep_object_in_bounds:
        object.location = keep_in_bounds(object.location, object.rect.width, object.rect.height)
    else:
        pass
    object.rect.center = tuple(object.location)

# Player class (for variable storage purposes)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.location = [x, y]
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 0, 255), (15, 15), 15)
        self.rect = self.image.get_rect(center=tuple(self.location))
        self.speed = 1

    def set_speed(self, speed):
        self.speed = speed

    def up(self, amt=1):
        update_pos(self, 0, -amt*(self.speed/10))
    def down(self, amt=1):
        update_pos(self, 0, amt*(self.speed/10))
    def left(self, amt=1):
        update_pos(self, -amt*(self.speed/10), 0)
    def right(self, amt=1):
        update_pos(self, amt*(self.speed/10), 0)

# Set assets
player = Player(400, 300)
player.set_speed(2)
background = pygame.transform.scale(pygame.image.load("assets/backgrounds/arena.jpg").convert(), (800, 600))
play_button = pygame.transform.scale(pygame.image.load("assets/buttons/play.png").convert_alpha(), (200, 200))
button_mask = pygame.mask.from_surface(play_button)
play_button_rect = play_button.get_rect(center=(400, 350))

# Run game
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == "title" and event.type == pygame.MOUSEBUTTONDOWN:
            if play_button_rect.collidepoint(event.pos):
                local_x = event.pos[0] - play_button_rect.left
                local_y = event.pos[1] - play_button_rect.top
                if button_mask.get_at((local_x, local_y)):
                    game_state = "play"
    
    if game_state == "title":
        screen.blit(background, (0, 0))
        title_text = font_big.render("Arena of Doom", True, (255, 0, 0))
        screen.blit(title_text, title_text.get_rect(center=(400, 200)))
        screen.blit(play_button, play_button_rect)
        pygame.display.flip()

    elif game_state == "play":   

        # Set up inputs
        keys = pygame.key.get_pressed()
        inputs = {
            "up": keys[pygame.K_w] or keys[pygame.K_UP],
            "down": keys[pygame.K_s] or keys[pygame.K_DOWN],
            "left": keys[pygame.K_a] or keys[pygame.K_LEFT],
            "right": keys[pygame.K_d] or keys[pygame.K_RIGHT],
        }

        if inputs["up"]:
            player.up()
        if inputs["down"]: 
            player.down()
        if inputs["left"]:
            player.left()
        if inputs["right"]:
            player.right()

        screen.fill((255, 255, 255))
        screen.blit(player.image, player.rect)
        pygame.display.flip()



pygame.quit()