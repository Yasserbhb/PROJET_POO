import pygame
import random

# Constants
GRID_SIZE = 20
CELL_SIZE = 40
SCREEN_WIDTH, SCREEN_HEIGHT = CELL_SIZE * GRID_SIZE, CELL_SIZE * GRID_SIZE
FPS = 60

# Load assets
def load_textures():
    """Load textures for grass, water, and rocks."""
    return {
        "grass": [
            pygame.image.load("assets/grass4.jpg"),
            pygame.image.load("assets/grass5.jpg"),
        ],
        "water": pygame.image.load("assets/water.jpg"),
        "rock": pygame.image.load("assets/rock.jpg"),
    }

# Tile class
class Tile:
    def __init__(self, x, y, terrain, textures):
        self.x = x
        self.y = y
        self.terrain = terrain  # "grass", "water", or "rock"
        self.textures = textures
        self.traversable = terrain == "grass"  # Only grass is traversable

        # Assign texture for grass
        if self.terrain == "grass":
            self.texture = random.choice(self.textures["grass"])
        else:
            self.texture = self.textures[terrain]

    def draw(self, screen):
        """Draw the tile with its texture."""
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        screen.blit(pygame.transform.scale(self.texture, (CELL_SIZE, CELL_SIZE)), rect)
        # Optional: Add a subtle border for tiles
        pygame.draw.rect(screen, (0, 0, 0), rect, 1)  # Black border

# Game class
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dynamic Tactical Grid Game")
        self.clock = pygame.time.Clock()
        self.textures = load_textures()
        self.grid = self.create_grid()

    def create_grid(self):
        """Create a grid with predefined lakes and hills."""
        grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        # Fill grid with grass by default
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                grid[x][y] = Tile(x, y, "grass", self.textures)

        # Add lakes (water tiles)
        lakes = [
            [(5, 5), (5, 6), (5, 7), (6,5),(6, 6),(6,7),(7, 6)],
            [(12, 12), (12, 13), (13, 12), (13, 13)],
        ]
        for lake in lakes:
            for x, y in lake:
                grid[x][y] = Tile(x, y, "water", self.textures)

        # Add hills (rock tiles)
        # Add hills (rock tiles)
        hills = [
            [(2, 2), (2, 3), (3, 2), (3, 3), (4, 3)],
            [(10, 8), (10, 9),(10,10), (11, 8), (11, 9), (12, 9),(12,10),(12,11),(13,10),(13,9),(13,8),(14,11),(14,10)],
            [(5, 16), (10, 17), (11, 16), (11, 17), (7, 16),(8,17),(9,17)]
        ]

        for hill in hills:
            for x, y in hill:
                grid[x][y] = Tile(x, y, "rock", self.textures)

        return grid

    def draw_grid(self):
        """Draw all tiles in the grid."""
        for row in self.grid:
            for tile in row:
                tile.draw(self.screen)

    def run(self):
        """Main game loop."""
        running = True
        while running:
            self.screen.fill((0, 0, 0))  # Clear the screen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Draw the grid
            self.draw_grid()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

# Run the game
if __name__ == "__main__":
    Game().run()
