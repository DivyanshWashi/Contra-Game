import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Game settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Create screen with FULLSCREEN mode
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Contra-Inspired Shooter")

# Utility function to load and scale image assets
def load_image(filename, size):
    try:
        image = pygame.image.load(filename).convert_alpha()
        print(f"Loaded image: {filename}")
        return pygame.transform.scale(image, size)
    except Exception as e:
        print(f"Error loading image {filename}: {e}")
        return pygame.Surface(size)  # Return blank surface if loading fails

# Load and scale assets
player_img = load_image("player.png", (100, 100))
bullet_img = load_image("bullet.png", (20, 10))
enemy_img = load_image("enemy.png", (100, 100))
background_img = load_image("background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
boss_img = load_image("boss.png", (300, 300))
powerup_img = load_image("powerup.png", (40, 40))
enemy_bullet_img = load_image("enemy_bullet.png", (20, 10))
fireball_img = load_image("fireball.png", (30, 30))
ice_shard_img = load_image("ice_shard.png", (30, 30))

# Set up font for HUD elements
font = pygame.font.Font(None, 36)

# Player class definition
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT - 100)
        self.speed = 5
        self.jump_power = -15
        self.velocity_y = 0
        self.on_ground = True
        self.health = 100
        self.powered_up = False
        self.shoot_delay = 100  # delay in milliseconds
        self.last_shot = pygame.time.get_ticks()
        self.powerup_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()

        # Movement controls
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_LSHIFT]:  # Sprinting
            self.rect.x += self.speed * 2

        # Jumping
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False

        # Apply gravity
        self.velocity_y += 1
        self.rect.y += self.velocity_y

        # Ground collision
        if self.rect.bottom >= SCREEN_HEIGHT - 50:
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.on_ground = True

        # Power-up duration handling
        if self.powered_up and pygame.time.get_ticks() > self.powerup_timer:
            self.powered_up = False
            self.shoot_delay = 100

        # Shooting with Z key
        if keys[pygame.K_z]:
            self.shoot()

        # Quit game with ESC
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        # Check player death
        if self.health <= 0:
            print("Game Over")
            pygame.quit()
            sys.exit()

    def shoot(self):
        # Fire a bullet if enough time has passed since the last shot
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.right, self.rect.centery, 10)
            all_sprites.add(bullet)
            bullets.add(bullet)

    def draw_health_bar(self, surface):
        # Draw a simple health bar
        pygame.draw.rect(surface, RED, (20, 20, 200, 20))
        pygame.draw.rect(surface, GREEN, (20, 20, 2 * self.health, 20))

# Power-up class definition
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = powerup_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        # Move power-up downward and check collision with player
        self.rect.y += 2
        if self.rect.colliderect(player.rect):
            player.powered_up = True
            player.shoot_delay = 50
            player.powerup_timer = pygame.time.get_ticks() + 15000  # 15 sec
            self.kill()

# Bullet class for player bullets
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.midleft = (x, y)
        self.speed = speed

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.kill()

# Enemy bullet class
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_bullet_img
        self.rect = self.image.get_rect()
        self.rect.midright = (x, y)
        self.speed = -7

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0:
            self.kill()
        if self.rect.colliderect(player.rect):
            player.health -= 10
            self.kill()

# Enemy class definition
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.midleft = (x, y)

    def update(self):
        self.rect.x -= 3  # Move left
        # If hit by player bullet
        if pygame.sprite.spritecollide(self, bullets, True):
            self.kill()
        # Occasionally shoot bullets
        if random.random() < 0.01:
            bullet = EnemyBullet(self.rect.left, self.rect.centery)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

# Sprite groups
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()

# Function to spawn new enemies
def spawn_enemy():
    enemy = Enemy(SCREEN_WIDTH, SCREEN_HEIGHT - 100)
    all_sprites.add(enemy)
    enemies.add(enemy)

# Main game loop
running = True
clock = pygame.time.Clock()
enemy_spawn_timer = pygame.time.get_ticks()

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Spawn enemy every 1.5 seconds
    if pygame.time.get_ticks() - enemy_spawn_timer > 1500:
        spawn_enemy()
        enemy_spawn_timer = pygame.time.get_ticks()

    # Update all sprites
    all_sprites.update()

    # Draw everything
    screen.blit(background_img, (0, 0))
    all_sprites.draw(screen)
    player.draw_health_bar(screen)

    # Refresh screen
    pygame.display.flip()
    clock.tick(FPS)

# Quit when game loop ends
pygame.quit()
sys.exit()
