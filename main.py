import pygame
pygame.init()

# Set up display & music
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Arena of Doom")
screen.fill((255, 255, 255))
pygame.mixer.music.load("assets/audio/olympus.mp3")
pygame.mixer.music.play(-1)

game_state = "title"


# Utility functions
def keep_in_bounds(location, width, height):
    return [max(width, min(location[0], 800-width)), max(height, min(location[1], 600-height))]
def update_pos(object, x, y, keep_object_in_bounds = True):
    object.location[0] += x
    object.location[1] += y
    if keep_object_in_bounds:
        object.location = keep_in_bounds(object.location, object.original_image.get_width()//2, object.original_image.get_height()//2)

    else:
        pass
    object.rect.center = tuple(object.location)

# Player class (for variable storage purposes)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.location = [x, y]

        # Store original, unrotated sword image
        self.original_image = pygame.transform.scale(
            pygame.image.load("assets/sprites/sword-player.png").convert_alpha(),
            (int(275/10), int(775/10))
        )
        self.image = self.original_image
        self.rect = self.image.get_rect(center=tuple(self.location))

        self.speed = 1
        self.angle = 0
        self.main_attacking = False
        self.main_cooldown = 0

        # Vector from center to pivot (negative y = down towards base of hilt)
        self.pivot_offset = pygame.Vector2(0, self.image.get_height() / 2)

    def set_speed(self, speed):
        self.speed = speed

    def up(self, amt=1):
        update_pos(self, 0, -amt*(self.speed))
    def down(self, amt=1):
        update_pos(self, 0, amt*(self.speed))
    def left(self, amt=1):
        update_pos(self, -amt*(self.speed), 0)
    def right(self, amt=1):
        update_pos(self, amt*(self.speed), 0)

    def main_attack(self):
        if not self.main_attacking and self.main_cooldown == 0:
            self.main_attacking = True
            self.angle = 0
    
    def update(self):
        if self.main_attacking:
            if self.angle >= 360:
                self.angle = 0
                self.main_attacking = False
                self.main_cooldown = 2*60

                self.image = self.original_image
                self.rect = self.image.get_rect(center=self.location)
            else:
                self.angle += 15
                self.image = pygame.transform.rotate(self.original_image, self.angle)

                offset_rotated = self.pivot_offset.rotate(-self.angle)
                self.rect = self.image.get_rect(center=(self.location[0] - offset_rotated.x, self.location[1] - offset_rotated.y))


        if self.main_cooldown > 0:
            self.main_cooldown -= 1

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.image.load("assets/sprites/enemy.png").convert_alpha(),
            (50, 50)
        )
        self.rect = self.image.get_rect(center=(x, y))
        self.location = pygame.math.Vector2(x, y)
        self.speed = 1.5  # enemy movement speed

    def update(self, player_location):
        # Calculate direction vector from enemy to player
        direction = pygame.math.Vector2(player_location) - self.location
        if direction.length() != 0:
            direction = direction.normalize()  # get unit vector
        
        # Move enemy toward player
        self.location += direction * self.speed
        
        # Update rect position
        self.rect.center = (round(self.location.x), round(self.location.y))

# Set assets
player = Player(400, 300)
player.set_speed(2)
title_background = pygame.transform.scale(pygame.image.load("assets/backgrounds/arena.jpg").convert(), (800, 600))
l1_background = pygame.transform.scale(pygame.image.load("assets/backgrounds/grass.png").convert(), (800, 600))

title_text = pygame.transform.scale(pygame.image.load("assets/text/title.png").convert_alpha(), (576, 84))

play_button = pygame.transform.scale(pygame.image.load("assets/buttons/play.png").convert_alpha(), (200, 200))
play_button_mask = pygame.mask.from_surface(play_button)
play_button_rect = play_button.get_rect(center=(250, 350))

quit_button = pygame.transform.scale(pygame.image.load("assets/buttons/quit.png").convert_alpha(), (200, 200))
quit_button_mask = pygame.mask.from_surface(quit_button)
quit_button_rect = quit_button.get_rect(center=(550, 350))


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
                if play_button_mask.get_at((local_x, local_y)):
                    game_state = "play"
                    player.main_cooldown = 2*60
            if quit_button_rect.collidepoint(event.pos):
                local_x = event.pos[0] - quit_button_rect.left
                local_y = event.pos[1] - quit_button_rect.top
                if quit_button_mask.get_at((local_x, local_y)):
                    running = False
        if game_state == "play" and event.type == pygame.MOUSEBUTTONDOWN:
            player.main_attack()
    
    if game_state == "title":
        screen.blit(title_background, (0, 0))
        screen.blit(title_text, title_text.get_rect(center=(400, 200)))
        screen.blit(play_button, play_button_rect)
        screen.blit(quit_button, quit_button_rect)
        pygame.display.flip()

    elif game_state == "play":   

        # Set up inputs
        keys = pygame.key.get_pressed()
        inputs = {
            "up": keys[pygame.K_w] or keys[pygame.K_UP],
            "down": keys[pygame.K_s] or keys[pygame.K_DOWN],
            "left": keys[pygame.K_a] or keys[pygame.K_LEFT],
            "right": keys[pygame.K_d] or keys[pygame.K_RIGHT],
            "e": keys[pygame.K_e], 
        }

        if inputs["up"]:
            player.up()
        if inputs["down"]: 
            player.down()
        if inputs["left"]:
            player.left()
        if inputs["right"]:
            player.right()
        if inputs["e"]:
            player.main_attack()
        
        player.update()

        screen.blit(l1_background, (0, 0))
        screen.blit(player.image, player.rect)
        
        pygame.display.flip()
        clock.tick(60)



pygame.quit()