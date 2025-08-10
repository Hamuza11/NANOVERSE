import pygame
import random
import sys
import math
from enum import Enum
from typing import List, Optional, Tuple

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

SOLID_MATERIALS = {Material.STONE}

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


def is_solid(material: Material) -> bool:
    return material in SOLID_MATERIALS


class Player:
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y
        self.width: int = TILE_SIZE
        self.height: int = TILE_SIZE
        self.inventory: List[Optional[Material]] = [None] * INVENTORY_SIZE
        self.selected_slot: int = 0
        self.color: Tuple[int, int, int] = RED
        self.health: int = 100
        self.max_health: int = 100
        
    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw player's "face" direction
        pygame.draw.circle(screen, BLACK, (self.x + self.width // 2, self.y + self.height // 3), 5)

    def move(self, dx: int, dy: int, world: 'World') -> None:
        new_x = self.x + dx
        new_y = self.y + dy

        # Keep within screen bounds first
        new_x = max(0, min(SCREEN_WIDTH - self.width, new_x))
        new_y = max(0, min(SCREEN_HEIGHT - self.height, new_y))

        # Robust collision detection against solid tiles using rectangle overlap
        proposed_rect = pygame.Rect(new_x, new_y, self.width, self.height)
        tile_x_start = proposed_rect.left // TILE_SIZE
        tile_y_start = proposed_rect.top // TILE_SIZE
        tile_x_end = (proposed_rect.right - 1) // TILE_SIZE
        tile_y_end = (proposed_rect.bottom - 1) // TILE_SIZE

        collides = False
        for tx in range(tile_x_start, tile_x_end + 1):
            for ty in range(tile_y_start, tile_y_end + 1):
                if is_solid(world.get_tile(tx, ty)):
                    collides = True
                    break
            if collides:
                break

        if not collides:
            self.x = new_x
            self.y = new_y
    
    def add_to_inventory(self, material: Material) -> bool:
        for i in range(INVENTORY_SIZE):
            if self.inventory[i] is None:
                self.inventory[i] = material
                return True
        return False
    
    def get_selected_material(self) -> Optional[Material]:
        return self.inventory[self.selected_slot]
    
    def remove_selected_material(self) -> Optional[Material]:
        material = self.inventory[self.selected_slot]
        self.inventory[self.selected_slot] = None
        return material


class World:
    def __init__(self, width: int, height: int) -> None:
        self.width: int = width
        self.height: int = height
        self.grid: List[List[Material]] = [[Material.EMPTY for _ in range(height)] for _ in range(width)]
        
        # Generate terrain
        self.generate_terrain()
    
    def generate_terrain(self) -> None:
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
    
    def get_tile(self, x: int, y: int) -> Material:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[x][y]
        return Material.EMPTY
    
    def set_tile(self, x: int, y: int, material: Material) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[x][y] = material
    
    def draw(self, screen: pygame.Surface) -> None:
        for x in range(self.width):
            for y in range(self.height):
                material = self.grid[x][y]
                if material != Material.EMPTY:
                    pygame.draw.rect(screen, MATERIAL_COLORS[material], 
                                    (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))


class Game:
    def __init__(self) -> None:
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

        # Toggles
        self.show_grid: bool = False
    
    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                # Inventory selection
                if pygame.K_1 <= event.key <= pygame.K_5:
                    self.player.selected_slot = event.key - pygame.K_1

                # Toggle grid
                if event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                tile_x = mouse_x // TILE_SIZE
                tile_y = mouse_y // TILE_SIZE
                
                if event.button == 1:  # Left click - place (consumes item)
                    selected_material = self.player.get_selected_material()
                    if selected_material:
                        self.world.set_tile(tile_x, tile_y, selected_material)
                        self.player.remove_selected_material()
                
                elif event.button == 3:  # Right click - break/collect (only if space)
                    material = self.world.get_tile(tile_x, tile_y)
                    if material != Material.EMPTY:
                        if self.player.add_to_inventory(material):
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
    
    def draw_ui(self) -> None:
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

            # Draw slot number label
            index_text = self.font.render(str(i + 1), True, WHITE)
            self.screen.blit(index_text, (slot_x + 2, slot_y - 14))
        
        # Draw health bar
        health_pct = self.player.health / self.player.max_health
        pygame.draw.rect(self.screen, RED, (SCREEN_WIDTH - 220, 20, 200, 20))
        pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 220, 20, int(200 * health_pct), 20))
        health_text = self.font.render(f"Health: {self.player.health}/{self.player.max_health}", True, WHITE)
        self.screen.blit(health_text, (SCREEN_WIDTH - 220, 45))
        
        # Draw instructions
        instructions = [
            "Controls:",
            "WASD/Arrows: Move",
            "1-5: Select inventory slot",
            "Left-click: Place material (consumes)",
            "Right-click: Collect material",
            "G: Toggle grid",
            "ESC: Quit"
        ]
        
        for i, line in enumerate(instructions):
            text = self.font.render(line, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH - 200, 80 + i * 25))

        # FPS display
        fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, WHITE)
        self.screen.blit(fps_text, (20, 20))
    
    def update(self) -> None:
        pass  # Additional game logic will go here
    
    def draw_grid(self) -> None:
        grid_color = (50, 50, 50)
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, grid_color, (0, y), (SCREEN_WIDTH, y))
    
    def draw(self) -> None:
        self.screen.fill(BLACK)
        self.world.draw(self.screen)
        if self.show_grid:
            self.draw_grid()
        self.player.draw(self.screen)
        self.draw_ui()
        pygame.display.flip()
    
    def run(self) -> None:
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
