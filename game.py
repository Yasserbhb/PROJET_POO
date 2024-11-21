import pygame
import random
from unit import Unit

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
def load_unit_images():
    return {
        "ashe": "assets/ashe.png",
        "garen": "assets/garen.png",
        "darius": "assets/darius.png",
        "soraka": "assets/soraka.png",
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
        pygame.display.set_caption("Tactical Grid Game")
        self.clock = pygame.time.Clock()
        self.textures = load_textures()
        self.unit_images = load_unit_images()
        self.grid = self.create_grid()
        self.units = self.create_units()
        self.current_unit_index = 0
        self.last_turn_time = 0  # Initialize turn delay tracking
        self.last_move_time = 0  # Timestamp of the last movement

        

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

    def create_units(self):
        """Create units and place them on the grid."""
        return [
            Unit(14, 16, "Ashe", self.unit_images["ashe"], (0, 0, 255)),  # Blue team
            Unit(14, 15, "Garen", self.unit_images["garen"], (0, 0, 255)),  # Blue team
            Unit(18, 18, "Darius", self.unit_images["darius"], (255, 0, 0)),  # Red team
            Unit(17, 18, "Soraka", self.unit_images["soraka"], (255, 0, 0)),  # Red team
        ]

    def draw_units(self):
        """Draw all units on the screen with their images and team-colored health bars."""
        for unit in self.units:
            if unit.alive:
                # Draw the unit's image
                rect = pygame.Rect(unit.x * CELL_SIZE, unit.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                unit_image = pygame.transform.scale(unit.image, (CELL_SIZE, CELL_SIZE))
                self.screen.blit(unit_image, rect)

                # Determine health bar color based on team
                if unit.color == (0, 0, 255):  # Blue team (Ashe, Garen)
                    health_color = (0, 200, 100)  # Green
                    missing_health_color = (0, 50, 0)  # Dark green
                elif unit.color == (255, 0, 0):  # Red team (Darius, Soraka)
                    health_color = (150, 0, 128)  # Purple
                    missing_health_color = (50, 0, 50)  # Dark purple
                else:
                    health_color = (255, 255, 255)  # Default to white (fallback)
                    missing_health_color = (100, 100, 100)

                # Health bar background (missing health)
                health_bar_bg = pygame.Rect(
                    rect.x + 2, rect.y - 6, CELL_SIZE - 4, 5
                )
                pygame.draw.rect(self.screen, missing_health_color, health_bar_bg)

                # Health bar foreground (current health)
                health_percentage = unit.health / 100  # Assuming max health = 100
                health_bar_fg = pygame.Rect(
                    rect.x + 2, rect.y - 6, int((CELL_SIZE - 4) * health_percentage), 5
                )
                pygame.draw.rect(self.screen, health_color, health_bar_fg)


    def highlight_range(self, unit):
        """Highlight movement or attack range based on the unit's state."""
        if unit.state == "move":
            # Highlight movement range
            for dx in range(-unit.move_range, unit.move_range + 1):
                for dy in range(-unit.move_range, unit.move_range + 1):
                    x, y = unit.initial_x + dx, unit.initial_y + dy
                    if (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and
                            abs(dx) + abs(dy) <= unit.move_range):
                        color = (255, 255, 0)  # Yellow for movement range
                        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(self.screen, color, rect, 3)

        elif unit.state == "attack":
            # Highlight attack range
            for dx in range(-unit.attack_range, unit.attack_range + 1):
                for dy in range(-unit.attack_range, unit.attack_range + 1):
                    x, y = unit.x + dx, unit.y + dy
                    if (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and
                            abs(dx) + abs(dy) <= unit.attack_range):
                        color = (150, 0, 200)  # Purple for attack range
                        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(self.screen, color, rect, 2)

    def handle_turn(self):
        """Handle movement and attacks for the current unit."""
        current_time = pygame.time.get_ticks()
        current_unit = self.units[self.current_unit_index]

        keys = pygame.key.get_pressed()

        # Movement Phase
        # Movement Phase with delays and consistent elif structure
        if current_unit.state == "move":
            if current_time - self.last_move_time > 100:  # Delay of 300ms between movements
                if keys[pygame.K_UP]:
                    current_unit.move(0, -1, self.grid)
                    self.last_move_time = current_time  # Update the last movement time
                elif keys[pygame.K_DOWN]:
                    current_unit.move(0, 1, self.grid)
                    self.last_move_time = current_time  # Update the last movement time
                elif keys[pygame.K_LEFT]:
                    current_unit.move(-1, 0, self.grid)
                    self.last_move_time = current_time  # Update the last movement time
                elif keys[pygame.K_RIGHT]:
                    current_unit.move(1, 0, self.grid)
                    self.last_move_time = current_time  # Update the last movement time
                elif keys[pygame.K_RETURN]:
                    current_unit.state = "attack"  # Transition to attack phase

        # Attack Phase
        elif current_unit.state == "attack":
            # Check if there are valid targets
            targets_in_range = [
                unit for unit in self.units
                if unit != current_unit and unit.alive and current_unit.in_range(unit)
                and unit.color != current_unit.color  # Ensure not targeting teammates
            ]

            if targets_in_range:
                if keys[pygame.K_SPACE]:
                    # Attack the first valid target
                    current_unit.attack(targets_in_range[0])
                    current_unit.state = "done"  # Mark unit as done
            else:
                # No targets in range
                if keys[pygame.K_SPACE]:
                    print(f"{current_unit.name}: No targets in range. Skipping attack.")
                    current_unit.state = "done"  # Skip attack phase

        # End Turn
        if  current_unit.state == "done" and current_time - self.last_turn_time > 1000:
            self.last_turn_time = current_time  # Update the last turn time
            current_unit.state = "move"  # Reset state for the next turn
            current_unit.initial_x, current_unit.initial_y = current_unit.x, current_unit.y  # Reset initial position
            self.current_unit_index = (self.current_unit_index + 1) % len(self.units)


    def run(self):
        """Main game loop."""
        running = True
        while running:
            self.screen.fill((0, 0, 0))  # Clear the screen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Draw grid and units
            self.draw_grid()
            self.draw_units()

            # Highlight range for the active unit
            current_unit = self.units[self.current_unit_index]
            self.highlight_range(current_unit)

            # Handle current unit's turn
            self.handle_turn()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
# Run the game
if __name__ == "__main__":
    Game().run()
