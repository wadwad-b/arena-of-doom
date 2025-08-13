import pygame, random
pygame.init()

# Set up display & music
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Arena of Doom")
screen.fill((255, 255, 255))
pygame.mixer.music.load("assets/audio/olympus.mp3")
pygame.mixer.music.play(-1)
counter = 0

game_state = "title"


# Utility functions
damaged_enemies = {
    "damaged": [],
    "attacked": [],
}
wave_cooldown = 0
def draw_health_bar(surface, x, y, width, height, current, maximum):
    if maximum <= 0:
        return
    ratio = max(0, min(current / maximum, 1))  # clamp ratio between 0 and 1
    pygame.draw.rect(surface, (255, 0, 0), (x, y, width, height))
    pygame.draw.rect(surface, (0, 255, 0), (x, y, int(width * ratio), height))  # int cast here
    pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height), 2)

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
        else:
            self.angle = 0
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
        elif type == "shark":
            self.original_image = pygame.transform.scale(
                pygame.image.load("assets/sprites/enemy-shark.png").convert_alpha(),
                (60, 60)
            )
        elif type == "fennec fox":
            self.original_image = pygame.transform.scale(
                pygame.image.load("assets/sprites/enemy-fennec-fox.png").convert_alpha(),
                (60, 60)
            )
        else:
            raise ValueError(f"Unknown enemy type: {type}")
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.location = pygame.math.Vector2(x, y)
        self.speed = 1.5
        self.health = health
        self.max_health = health
        self.damage = damage
        self.cooldown = 0

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


class EnemySpawner:
    def __init__(self, enemy_group, type, difficulty, waves):
        self.enemy_group = enemy_group
        self.current_wave = 1
        self.wave_cooldown = 0
        self.total_waves = waves
        self.spawn_delay = 5 * 60 
        self.difficulty = difficulty
        self.type = type
    
    def spawn_enemies(self):
        num_enemies = self.current_wave + 1
        health_min = int(20 * (self.current_wave * 0.5) * (self.difficulty * 0.5))
        health_max = int(40 * (self.current_wave * 0.5) * (self.difficulty * 0.5))
        damage_min = int(5 * (self.current_wave * 0.5) * (self.difficulty * 0.5))
        damage_max = int(10 * (self.current_wave * 0.5) * (self.difficulty * 0.5))

        screen_width, screen_height = 800, 600
        spawn_margin = 50
        
        for _ in range(num_enemies):
            side = random.randint(0, 3)
            if side == 0:
                x = random.uniform(-spawn_margin, screen_width + spawn_margin)
                y = -spawn_margin
            elif side == 1:
                x = screen_width + spawn_margin
                y = random.uniform(-spawn_margin, screen_height + spawn_margin)
            elif side == 2:
                x = random.uniform(-spawn_margin, screen_width + spawn_margin)
                y = screen_height + spawn_margin
            else:
                x = -spawn_margin
                y = random.uniform(-spawn_margin, screen_height + spawn_margin)
            
            health = random.randint(health_min, health_max)
            damage = random.randint(damage_min, damage_max)
            enemy = Enemy(x, y, self.type, health, damage)
            self.enemy_group.add(enemy)
        
        print(f"Wave {self.current_wave} spawned with {num_enemies} enemies!")
        self.current_wave += 1
        self.wave_cooldown = self.spawn_delay
    
    def update(self):
        if self.wave_cooldown == 0 and self.current_wave <= self.total_waves:
            self.spawn_enemies()
        elif self.wave_cooldown > 0:
            self.wave_cooldown -= 1

            



# Set assets
player = Player(400, 300)
player.set_speed(2)

enemies = pygame.sprite.Group()

title_background = pygame.transform.scale(pygame.image.load("assets/backgrounds/arena.jpg").convert(), (800, 600))
t1_background = pygame.transform.scale(pygame.image.load("assets/backgrounds/grass.png").convert(), (800, 600))
t2_background = pygame.transform.scale(pygame.image.load("assets/backgrounds/desert.jpg").convert(), (800, 600))
t3_background = pygame.transform.scale(pygame.image.load("assets/backgrounds/ocean.jpg").convert(), (800, 600))

title_text = pygame.transform.scale(pygame.image.load("assets/text/title.png").convert_alpha(), (576, 84))

play_button = pygame.transform.scale(pygame.image.load("assets/buttons/play.png").convert_alpha(), (200, 200))
play_button_mask = pygame.mask.from_surface(play_button)
play_button_rect = play_button.get_rect(center=(250, 350))

quit_button = pygame.transform.scale(pygame.image.load("assets/buttons/quit.png").convert_alpha(), (200, 200))
quit_button_mask = pygame.mask.from_surface(quit_button)
quit_button_rect = quit_button.get_rect(center=(550, 350))

continue_button = pygame.transform.scale(pygame.image.load("assets/buttons/continue.png").convert_alpha(), (200, 200))
continue_button_mask = pygame.mask.from_surface(continue_button)
continue_button_rect = continue_button.get_rect(center=(400, 500))

menu_button = pygame.transform.scale(pygame.image.load("assets/buttons/menu.png").convert_alpha(), (200, 200))
menu_button_mask = pygame.mask.from_surface(menu_button)
menu_button_rect = menu_button.get_rect(center=(400, 500))
menu_button_rect.center = (800 - menu_button_rect.width // 2 - 25, 600 - menu_button_rect.height // 2 - 10)

infinity_button_width = 400
infinity_button_height = menu_button_rect.height
infinity_button_rect = pygame.Rect(
    10,  # left padding
    menu_button_rect.top,
    menu_button_rect.left - 10 - 10,  # from left padding to menu button left minus 10px spacing
    menu_button_rect.height
)

infinity_panel_rect = pygame.Rect(30, menu_button_rect.centery - 100, 520, 200)

# Difficulty buttons inside panel
difficulty_button_width = 80
difficulty_button_height = 50
difficulty_button_margin = 20

difficulty_buttons = []
start_x = infinity_panel_rect.x + 20
start_y = infinity_panel_rect.y + 120

for i in range(5):
    btn_rect = pygame.Rect(
        start_x + i * (difficulty_button_width + difficulty_button_margin),
        start_y,
        difficulty_button_width,
        difficulty_button_height
    )
    difficulty_buttons.append((btn_rect, str(i + 1)))

# Run game
running = True
clock = pygame.time.Clock()
play_start_time = None

level_font_title = pygame.font.Font("assets/fonts/MedievalSharp-Regular.ttf", 48)
level_font_button = pygame.font.Font("assets/fonts/MedievalSharp-Regular.ttf", 28)
infinity_title_font = pygame.font.Font("assets/fonts/MedievalSharp-Regular.ttf", 36)
infinity_subtitle_font = pygame.font.Font("assets/fonts/MedievalSharp-Regular.ttf", 24)


cols = 5
rows = 3
button_width = 130
button_height = 60
button_margin_x = 20
button_margin_y = 20
start_x = (800 - (button_width * cols + button_margin_x * (cols - 1))) // 2
start_y = 150

level_buttons = []
for i in range(15):
    row = i // cols
    col = i % cols
    x = start_x + col * (button_width + button_margin_x)
    y = start_y + row * (button_height + button_margin_y)
    rect = pygame.Rect(x, y, button_width, button_height)
    level_buttons.append((rect, f"Level {i+1}"))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state = "title"
                enemies.empty()
                player.main_attacking = False

        
        if game_state == "title" and event.type == pygame.MOUSEBUTTONUP:
            if play_button_rect.collidepoint(event.pos):
                local_x = event.pos[0] - play_button_rect.left
                local_y = event.pos[1] - play_button_rect.top
                if play_button_mask.get_at((local_x, local_y)):
                    pygame.event.clear(pygame.MOUSEBUTTONDOWN)
                    pygame.event.clear(pygame.MOUSEBUTTONUP)

                    game_state = "level"

            if quit_button_rect.collidepoint(event.pos):
                local_x = event.pos[0] - quit_button_rect.left
                local_y = event.pos[1] - quit_button_rect.top
                if quit_button_mask.get_at((local_x, local_y)):
                    running = False

        if game_state == "play" and event.type == pygame.MOUSEBUTTONDOWN:
            player.main_attack()

        if game_state == "over" and event.type == pygame.MOUSEBUTTONUP:
            if continue_button_rect.collidepoint(event.pos):
                game_state = "level"
                player.health = player.max_health
                enemies.empty()
                player.main_attacking = False

        if game_state == "level" and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if menu_button_rect.collidepoint(event.pos):
                    game_state = "title"
                for rect, label in level_buttons:
                    if rect.collidepoint(event.pos):
                        print(f"Selected {label}")
                        selected_level = int(label.split()[1])
                        player.main_cooldown = 2*60
                        play_start_time = pygame.time.get_ticks()

                        if selected_level <= 5:
                            map = t1_background
                            enemy_type = "spider"
                        if 6 <= selected_level <= 10:
                            map = t2_background
                            enemy_type = "fennec fox"  
                        if selected_level >= 11:
                            map = t3_background
                            enemy_type = "shark"

                        if selected_level % 5 == 1:
                            enemy_spawner = EnemySpawner(enemies, enemy_type, 1, 3)
                        if selected_level % 5 == 2:
                            enemy_spawner = EnemySpawner(enemies, enemy_type, 2, 3)
                        if selected_level % 5 == 3:
                            enemy_spawner = EnemySpawner(enemies, enemy_type, 2, 4)
                        if selected_level % 5 == 4:
                            enemy_spawner = EnemySpawner(enemies, enemy_type, 2, 5)
                            enemy_spawner.spawn_delay += 60
                        if selected_level % 5 == 0:
                            enemy_spawner = EnemySpawner(enemies, enemy_type, 3, 5)
                            enemy_spawner.spawn_delay += 120

                        


                        game_state = "play"
                        pygame.event.clear(pygame.MOUSEBUTTONDOWN)
                        pygame.event.clear(pygame.MOUSEBUTTONUP)
    
    if game_state == "title":
        screen.blit(title_background, (0, 0))
        screen.blit(title_text, title_text.get_rect(center=(400, 200)))
        screen.blit(play_button, play_button_rect)
        screen.blit(quit_button, quit_button_rect)
        pygame.display.flip()
        clock.tick(60)
    
    elif game_state == "over":
        screen.blit(freeze_end_level, (0, 0))
        player.main_attacking = False
        draw_health_bar(screen, player.rect.centerx - 30, player.rect.bottom + 5, 60, 8, player.health, player.max_health)
        font = pygame.font.Font(None, 74)
        if status == "win":
            text = font.render("You Win!", True, (255, 255, 255))
        elif status == "loss":
            text = font.render("You Lose!", True, (255, 255, 255))

        screen.blit(text, text.get_rect(center=(400, 300)))
        screen.blit(continue_button, continue_button_rect)
        pygame.display.flip()
        clock.tick(60)

    elif game_state == "level":
        counter += 1
        if 0 <= counter <= 90:
            screen.blit(t1_background, (0, 0))
        elif 91 <= counter <= 180:
            screen.blit(t2_background, (0, 0))
        elif 181 <= counter <= 270:
            screen.blit(t3_background, (0, 0))
        else:
            counter = 0
        
        # Title text
        title_surface = level_font_title.render("Level Select", True, (0, 0, 0))
        title_rect = title_surface.get_rect(center=(400, 70))
        screen.blit(title_surface, title_rect)

        mouse_pos = pygame.mouse.get_pos()

        for rect, label in level_buttons:
            # Change color if hovered
            color = (200, 100, 30) if rect.collidepoint(mouse_pos) else (150, 75, 0)
            pygame.draw.rect(screen, color, rect, border_radius=15)
            # Draw label centered
            text_surf = level_font_button.render(label, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)
            
        screen.blit(menu_button, menu_button_rect)

        pygame.draw.rect(screen, (230, 230, 230), infinity_panel_rect, border_radius=15)
        pygame.draw.rect(screen, (150, 75, 0), infinity_panel_rect, 3, border_radius=15)

        # Draw the "Infinity Mode" title
        title_surf = infinity_title_font.render("Infinity Mode", True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(infinity_panel_rect.centerx, infinity_panel_rect.y + 40))
        screen.blit(title_surf, title_rect)

        # Draw "Select Difficulty" subtitle
        subtitle_surf = infinity_subtitle_font.render("Select Difficulty", True, (50, 50, 50))
        subtitle_rect = subtitle_surf.get_rect(center=(infinity_panel_rect.centerx, infinity_panel_rect.y + 85))
        screen.blit(subtitle_surf, subtitle_rect)

        # Draw difficulty buttons
        mouse_pos = pygame.mouse.get_pos()
        for rect, label in difficulty_buttons:
            color = (200, 100, 30) if rect.collidepoint(mouse_pos) else (150, 75, 0)
            pygame.draw.rect(screen, color, rect, border_radius=12)
            text_surf = level_font_button.render(label, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

        # Draw the menu button bottom right
        screen.blit(menu_button, menu_button_rect)

        
        pygame.display.flip()
        clock.tick(60)

    elif game_state == "play":
        current_play_time = pygame.time.get_ticks()
        if play_start_time is not None and current_play_time - play_start_time > 2000:
            enemy_spawner.spawn_enemies()
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
        if play_start_time is None:
            enemy_spawner.update()

        if player.main_attacking:
            for enemy in enemies:
                if pygame.sprite.collide_mask(player, enemy):
                    if enemy not in damaged_enemies["damaged"]:
                        enemy.health -= 10
                        damaged_enemies["damaged"].append(enemy)
                    if enemy.health <= 0:
                        enemies.remove(enemy)
        else:
            damaged_enemies["damaged"] = []
            for enemy in enemies:
                if pygame.sprite.collide_mask(player, enemy):
                    if enemy not in damaged_enemies["attacked"]:
                        player.health -= enemy.damage
                        enemy.health -= 0.25 * enemy.health
                        damaged_enemies["attacked"].append(enemy)
                        enemy.cooldown = 2*60
                
                if enemy in damaged_enemies["attacked"]:
                    enemy.cooldown -= 1
                if enemy.cooldown <= 0 and enemy in damaged_enemies["attacked"]:
                    damaged_enemies["attacked"].remove(enemy)
                if enemy.health <= 0:
                    enemies.remove(enemy)
            

        screen.blit(map, (0, 0))
        screen.blit(player.image, player.rect)
        draw_health_bar(screen, player.rect.centerx - 30, player.rect.bottom + 5, 60, 8, player.health, player.max_health)
        enemies.draw(screen)
        for enemy in enemies:
            draw_health_bar(screen, enemy.rect.centerx - 20, enemy.rect.bottom + 5, 40, 6, enemy.health, enemy.max_health)
        
        if player.health <= 0:
            game_state = "over"
            status = "loss"

        elif enemy_spawner.current_wave >= enemy_spawner.total_waves and len(enemies) == 0:
            game_state = "over"
            status = "win"

        
        freeze_end_level = screen.copy()

        pygame.display.flip()
        clock.tick(60)



pygame.quit()