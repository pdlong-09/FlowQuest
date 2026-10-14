import pygame
import sys
pygame.init()

# setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer: FlowQuest")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
clock = pygame.time.Clock()
pixel_font = pygame.font.Font("assets/pixel_font.ttf", 36)
grid_square = pygame.image.load("assets/grid_square.png")
player_image = pygame.image.load("assets/player.png")
water_droplet_image = pygame.image.load("assets/water_droplet.png")
terrain_tile = pygame.image.load("assets/terrain.png")
player_water = 0
MAX_WATER = 100

# Draw Text on Screen
def draw_text_centered(text, font, color, y_offset=0):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(text_surface, text_rect)
def show_beginning_screens():
    screen.fill(BLACK)
    draw_text_centered("FlowQuest", pixel_font, WHITE)
    draw_text_centered("Press any key to start", pixel_font, WHITE, 50)
    pygame.display.flip()
    wait_for_key()
    intro_texts = [
        "In Africa every year,",
        "418 million people still lack basic drinking water",
        "and 779 million lack basic sanitation services",
        "You are a hero that collects water for your village",
        "Press any key to begin your adventure!"
    ]
    for text in intro_texts:
        screen.fill(BLACK)
        draw_text_centered(text, pixel_font, WHITE)
        pygame.display.flip()
        wait_for_key()

# Wait for Key Press
def wait_for_key():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return

#Grid class          
class Grid:
    def __init__(self, tile_image, tile_size, screen_width, screen_height):
        self.tile_image = tile_image
        self.tile_size = tile_size
        self.screen_width = screen_width
        self.screen_height = screen_height

    def draw(self, camera):
        offset_x = -camera.camera.x % self.tile_size
        offset_y = -camera.camera.y % self.tile_size
        for x in range(offset_x - self.tile_size, self.screen_width + self.tile_size, self.tile_size):
            for y in range(offset_y - self.tile_size, self.screen_height + self.tile_size, self.tile_size):
                screen.blit(self.tile_image, (x, y))


# Terrain Class
class Terrain(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = terrain_tile
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
terrain_group = pygame.sprite.Group()

# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (100, SCREEN_HEIGHT - 100)
        self.velocity = pygame.math.Vector2(0, 0)
        self.on_ground = False
    def update(self, keys, terrain_group):
        self.velocity.x = 0
        if keys[pygame.K_LEFT]:
            self.velocity.x = -5
        if keys[pygame.K_RIGHT]:
            self.velocity.x = 5
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity.y = -10
            self.on_ground = False
        self.velocity.y += 0.5
        self.rect.x += self.velocity.x
        self.check_horizontal_collisions(terrain_group)
        self.rect.y += self.velocity.y
        self.check_vertical_collisions(terrain_group)
    def check_horizontal_collisions(self, terrain_group):
        for terrain in terrain_group:
            if self.rect.colliderect(terrain.rect):
                if self.velocity.x > 0:
                    self.rect.right = terrain.rect.left
                elif self.velocity.x < 0:
                    self.rect.left = terrain.rect.right
    def check_vertical_collisions(self, terrain_group):
        self.on_ground = False
        for terrain in terrain_group:
            if self.rect.colliderect(terrain.rect):
                if self.velocity.y > 0:
                    self.rect.bottom = terrain.rect.top
                    self.velocity.y = 0
                    self.on_ground = True
                elif self.velocity.y < 0:
                    self.rect.top = terrain.rect.bottom
                    self.velocity.y = 0
    def has_died(self):
        return self.rect.top > SCREEN_HEIGHT
    def reset(self):
        self.rect.topleft = (50, SCREEN_HEIGHT - 100)
        self.velocity = pygame.math.Vector2(0, 0)

# Camera Class
class Camera:
    def __init__(self, level_width, level_height):
        self.camera = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.width = level_width
        self.height = level_height
    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)
    def update(self, target):
        x = -target.rect.centerx + SCREEN_WIDTH // 2
        y = -target.rect.centery + SCREEN_HEIGHT // 2
        x = max(-(self.width - SCREEN_WIDTH), min(0, x))
        y = max(-(self.height - SCREEN_HEIGHT), min(0, y))
        self.camera = pygame.Rect(x, y, SCREEN_WIDTH, SCREEN_HEIGHT)

# Water Drop Class
class WaterDrop(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = water_droplet_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
water_drops = pygame.sprite.Group()
def draw_water_counter():
    water_text = pixel_font.render(f"Water: {player_water}/{MAX_WATER}", True, WHITE)
    screen.blit(water_text, (10, 10))
    meter_width = 200
    filled_width = (player_water / MAX_WATER) * meter_width
    pygame.draw.rect(screen, WHITE, (10, 40, meter_width, 20), 2)
    pygame.draw.rect(screen, (0, 191, 255), (10, 40, filled_width, 20))

#load level
def load_level(level_data):
    global LEVEL_WIDTH, LEVEL_HEIGHT
    terrain_group.empty()
    water_drops.empty()
    # Calculate dimensions
    LEVEL_HEIGHT = len(level_data) * 32 #tile size
    LEVEL_WIDTH = len(level_data[0]) * 32

    for row_index, row in enumerate(level_data):
        for col_index, tile in enumerate(row):
            x, y = col_index * 32, row_index * 32

            if tile == "#":
                terrain = Terrain(x, y)
                terrain_group.add(terrain)
            elif tile == "D":
                drop = WaterDrop(x + 8, y - 32)
                water_drops.add(drop)




# Levels
LEVEL_1 = [
    ".......................................................................................................................................................", 
    ".......................................................................................................................................................",
    ".......................................................................................................................................................",
    "..................D..................................................................D.................................................................",
    "................#####...............................................#######........######....#######.....................D.............................",
    "............................####................................................................................####...#####...........................",
    "......................#####...................................#####.........####....................######...................#####.....................",
    "................................###.....####.....###......................................##########................................................D..",
    ".....................................D................#######.........................................................................###..........###.",
    "....................................####.............................................#####...........................................#.................",
    "........................................#........................................D......................................................######.........",
    "................................................................................#####............................D..............#####..................",
    "............................#####.........#####..................................................................D......#####..........................",
    "......................D........................................................................................######..................................",
    "....................#####..........######..............................................................................................................",
    ".......................................................................................................................................................",
    "....D.........#####....................................................................................................................................",
    "##########.............................................................................................................................................",
]

def game_loop(level_data):
    global player_water
    player = Player()
    load_level(level_data)
    camera = Camera(LEVEL_WIDTH, LEVEL_HEIGHT)
    grid = Grid(grid_square, 32, SCREEN_WIDTH, SCREEN_HEIGHT)

    player.reset() 
    player_water = 0 
    level_running = True

    while level_running:
        screen.fill(BLACK)
        grid.draw(camera)
        camera.update(player)
        keys = pygame.key.get_pressed()
        player.update(keys, terrain_group)
        for terrain in terrain_group:
            screen.blit(terrain.image, camera.apply(terrain)) 
        for drop in water_drops:
            screen.blit(drop.image, camera.apply(drop)) 
        screen.blit(player.image, camera.apply(player)) 

        # water collection
        draw_water_counter()
        collected = pygame.sprite.spritecollide(player, water_drops, True)
        for _ in collected:
            player_water += 10 
            if player_water > MAX_WATER:
                player_water = MAX_WATER 
        # Check for death
        if player.has_died():
            death_text = pixel_font.render("You Died!", True, (255, 0, 0))
            screen.blit(death_text, (SCREEN_WIDTH // 2 - death_text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(1000)
            player.reset()
        # Check for completion
        if len(water_drops) == 0:
            if len(terrain_group) > 0:
                print("Warning: No more water droplets. Terrain remains.")
            level_running = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.flip()
        clock.tick(60)

    # Win screen
    screen.fill(BLACK)
    win_text = pixel_font.render("You Win! Your Village is saved from thirst!", True, WHITE)
    screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()


show_beginning_screens()
game_loop(LEVEL_1)