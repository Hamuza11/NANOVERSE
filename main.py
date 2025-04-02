import pygame
import random
import sys
import math
from enum import Enum

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
PLAYER_SPEED = 5
INVENTORY_SIZE = 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
BROWN = (139, 69, 19)

# Materials enum
class Material(Enum):
    EMPTY = 0
    DIRT = 1
    STONE = 2
    WATER = 3
    WOOD = 4
    PLANT = 5

# Material properties
MATERIAL_COLORS = {
    Material.EMPTY: BLACK,
    Material.DIRT: BROWN,
    Material.STONE: GRAY,
    Material.WATER: BLUE,
    Material.WOOD: (139, 115, 85),
    Material.PLANT: GREEN
}

MATERIAL_NAMES = {
    Material.EMPTY: "Empty",
    Material.DIRT: "Dirt",
    Material.STONE: "Stone",
    Material.WATER: "Water",
    Material.WOOD: "Wood",
    Material.PLANT: "Plant"
}

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.inventory = [None] * INVENTORY_SIZE
        self.selected_slot = 0
        self.color = RED
        self.health = 100
        self.max_health = 100
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw player's "face" direction
        pygame.draw.circle(screen, BLACK, (self.x + self.width // 2, self.y + self.height // 3), 5)

    def move(self, dx, dy, world):
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Simple collision detection
        if (0 <= new_x <= SCREEN_WIDTH - self.width and 
            0 <= new_y <= SCREEN_HEIGHT - self.height):
            
            # Check if we're colliding with solid tiles
            tile_x = new_x // TILE_SIZE
            tile_y = new_y // TILE_SIZE
            
            if (world.get_tile(tile_x, tile_y) != Material.STONE):
                self.x = new_x
                self.y = new_y
    
    def add_to_inventory(self, material):
        for i in range(INVENTORY_SIZE):
            if self.inventory[i] is None:
                self.inventory[i] = material
                return True
        return False
    
    def get_selected_material(self):
        return self.inventory[self.selected_slot]
    
    def remove_selected_material(self):
        material = self.inventory[self.selected_slot]
        self.inventory[self.selected_slot] = None
        return material

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Material.EMPTY for _ in range(height)] for _ in range(width)]
        
        # Generate terrain
        self.generate_terrain()
    
    def generate_terrain(self):
        # Simple terrain generation
        for x in range(self.width):
            for y in range(self.height):
                if y >= self.height - 3:
                    self.grid[x][y] = Material.DIRT
                elif random.random() < 0.02:
                    self.grid[x][y] = Material.STONE
                elif random.random() < 0.01:
                    self.grid[x][y] = Material.WATER
                elif random.random() < 0.03:
                    self.grid[x][y] = Material.PLANT
                elif random.random() < 0.01:
                    self.grid[x][y] = Material.WOOD
    
    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        return Material.EMPTY
    
    def set_tile(self, x, y, material):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[x][y] = material
    
    def draw(self, screen):
        for x in range(self.width):
            for y in range(self.height):
                material = self.grid[x][y]
                if material != Material.EMPTY:
                    pygame.draw.rect(screen, MATERIAL_COLORS[material], 
                                    (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("NANOVERSE")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 16)
        
        # Initialize world
        self.world_width = SCREEN_WIDTH // TILE_SIZE
        self.world_height = SCREEN_HEIGHT // TILE_SIZE
        self.world = World(self.world_width, self.world_height)
        
        # Initialize player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Fill player inventory with some materials
        self.player.inventory[0] = Material.DIRT
        self.player.inventory[1] = Material.STONE
        self.player.inventory[2] = Material.WATER
        self.player.inventory[3] = Material.WOOD
        self.player.inventory[4] = Material.PLANT
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                # Inventory selection
                if pygame.K_1 <= event.key <= pygame.K_5:
                    self.player.selected_slot = event.key - pygame.K_1
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                tile_x = mouse_x // TILE_SIZE
                tile_y = mouse_y // TILE_SIZE
                
                if event.button == 1:  # Left click - place
                    selected_material = self.player.get_selected_material()
                    if selected_material:
                        self.world.set_tile(tile_x, tile_y, selected_material)
                
                elif event.button == 3:  # Right click - break/collect
                    material = self.world.get_tile(tile_x, tile_y)
                    if material != Material.EMPTY:
                        self.player.add_to_inventory(material)
                        self.world.set_tile(tile_x, tile_y, Material.EMPTY)
        
        # Continuous movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player.move(0, -PLAYER_SPEED, self.world)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player.move(0, PLAYER_SPEED, self.world)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player.move(-PLAYER_SPEED, 0, self.world)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player.move(PLAYER_SPEED, 0, self.world)
        
        return True
    
    def draw_ui(self):
        # Draw inventory
        for i in range(INVENTORY_SIZE):
            slot_x = 20 + i * 60
            slot_y = SCREEN_HEIGHT - 60
            
            # Draw slot background
            pygame.draw.rect(self.screen, GRAY, (slot_x, slot_y, 50, 50))
            
            # Draw selection indicator
            if i == self.player.selected_slot:
                pygame.draw.rect(self.screen, YELLOW, (slot_x, slot_y, 50, 50), 3)
            else:
                pygame.draw.rect(self.screen, WHITE, (slot_x, slot_y, 50, 50), 1)
                
            # Draw item in slot
            material = self.player.inventory[i]
            if material:
                pygame.draw.rect(self.screen, MATERIAL_COLORS[material], 
                                (slot_x + 10, slot_y + 10, 30, 30))
                
                # Draw material name
                name_text = self.font.render(MATERIAL_NAMES[material], True, WHITE)
                self.screen.blit(name_text, (slot_x, slot_y + 50))
        
        # Draw health bar
        health_pct = self.player.health / self.player.max_health
        pygame.draw.rect(self.screen, RED, (SCREEN_WIDTH - 220, 20, 200, 20))
        pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 220, 20, 200 * health_pct, 20))
        health_text = self.font.render(f"Health: {self.player.health}/{self.player.max_health}", True, WHITE)
        self.screen.blit(health_text, (SCREEN_WIDTH - 220, 45))
        
        # Draw instructions
        instructions = [
            "Controls:",
            "WASD/Arrows: Move",
            "1-5: Select inventory slot",
            "Left-click: Place material",
            "Right-click: Collect material",
            "ESC: Quit"
        ]
        
        for i, line in enumerate(instructions):
            text = self.font.render(line, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH - 200, 80 + i * 25))
    
    def update(self):
        pass  # Additional game logic will go here
    
    def draw(self):
        self.screen.fill(BLACK)
        self.world.draw(self.screen)
        self.player.draw(self.screen)
        self.draw_ui()
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # FPS

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
