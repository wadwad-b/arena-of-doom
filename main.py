import pygame, random
pygame.init()

# Set up display & music
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Arena of Doom")
screen.fill((255, 255, 255))
pygame.mixer.music.load("assets/audio/olympus.mp3")
pygame.mixer.music.play(-1)

game_state = "title"


# Utility functions
def draw_health_bar(surface, x, y, width, height, current, maximum):
    if maximum <= 0:
        return
    ratio = current / maximum
    pygame.draw.rect(surface, (255, 0, 0), (x, y, width, height))
    pygame.draw.rect(surface, (0, 255, 0), (x, y, width * ratio, height))
    pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height), 2)

def spawn_enemies(difficulty, enemy_group):

    num_enemies = int(difficulty * 2)
    health_min = 20 * difficulty
    health_max = 40 * difficulty
    damage_min = 1 * difficulty
    damage_max = 5 * difficulty

    screen_width, screen_height = 800, 600
    spawn_margin = 50  # how far offscreen enemies spawn

    for _ in range(num_enemies):
        # Random side: 0=top, 1=right, 2=bottom, 3=left
        side = random.randint(0, 3)

        if side == 0:  # top
            x = random.uniform(-spawn_margin, screen_width + spawn_margin)
            y = -spawn_margin
        elif side == 1:  # right
            x = screen_width + spawn_margin
            y = random.uniform(-spawn_margin, screen_height + spawn_margin)
        elif side == 2:  # bottom
            x = random.uniform(-spawn_margin, screen_width + spawn_margin)
            y = screen_height + spawn_margin
        else:  # left
            x = -spawn_margin
            y = random.uniform(-spawn_margin, screen_height + spawn_margin)

        health = random.randint(health_min, health_max)
        damage = random.randint(damage_min, damage_max)

        enemy = Enemy(x, y, "spider", health, damage)
        enemy_group.add(enemy)
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
        self.mask = pygame.mask.from_surface(self.image)

        self.speed = 1
        self.angle = 0
        self.main_attacking = False
        self.main_cooldown = 0
        self.health = 100
        self.max_health = 100

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
                self.mask = pygame.mask.from_surface(self.image)


        if self.main_cooldown > 0:
            self.main_cooldown -= 1

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type, health, damage):
        super().__init__()
        if type == "spider":
            self.original_image = pygame.transform.scale(
                pygame.image.load("assets/sprites/enemy-spider.png").convert_alpha(),
                (50, 50)
        )
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.location = pygame.math.Vector2(x, y)
        self.speed = 1.5
        self.health = health
        self.max_health = health
        self.damage = damage

    def update(self, player_location):
        # Calculate vector to player
        direction = pygame.math.Vector2(player_location) - self.location
        if direction.length() != 0:
            direction = direction.normalize()

            # Move enemy toward player
            self.location += direction * self.speed

            # Calculate angle in degrees to face player
            # pygame's y-axis is down, so adjust accordingly:
            angle = direction.angle_to(pygame.math.Vector2(0, -1))

            # Rotate image so it faces the player
            self.image = pygame.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect(center=(round(self.location.x), round(self.location.y)))
            self.mask = pygame.mask.from_surface(self.image)

# Set assets
player = Player(400, 300)
player.set_speed(2)

enemies = pygame.sprite.Group()

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
play_start_time = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state = "title"
                enemies.empty()
                player.main_attacking = False

        
        if game_state == "title" and event.type == pygame.MOUSEBUTTONDOWN:
            if play_button_rect.collidepoint(event.pos):
                local_x = event.pos[0] - play_button_rect.left
                local_y = event.pos[1] - play_button_rect.top
                if play_button_mask.get_at((local_x, local_y)):
                    game_state = "play"
                    player.main_cooldown = 2*60
                    play_start_time = pygame.time.get_ticks()

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
        current_play_time = pygame.time.get_ticks()
        if play_start_time is not None and current_play_time - play_start_time > 2000:
            spawn_enemies(1, enemies)
            play_start_time = None

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

        enemies.update(player.location)
        player.update()

        if player.main_attacking:
            for enemy in enemies:
                if pygame.sprite.collide_mask(player, enemy):
                    enemy.health -= 10
                    if enemy.health <= 0:
                        enemies.remove(enemy)
        else:
            for enemy in enemies:
                if pygame.sprite.collide_mask(player, enemy):
                    player.health -= enemy.damage
                    enemy.kill()
                    if player.health <= 0:
                        enemies.remove(enemy)

        

        screen.blit(l1_background, (0, 0))
        screen.blit(player.image, player.rect)
        draw_health_bar(screen, player.rect.centerx - 30, player.rect.bottom + 5, 60, 8, player.health, player.max_health)
        enemies.draw(screen)
        for enemy in enemies:
            print(f"Enemy Health: {enemy.health}/{enemy.max_health}, Enemy Damage: {enemy.damage}")
            draw_health_bar(screen, enemy.rect.centerx - 15, enemy.rect.bottom + 5, 30, 4, enemy.health, enemy.max_health)


        pygame.display.flip()
        clock.tick(60)



pygame.quit()