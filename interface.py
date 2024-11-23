import pygame
import random

# Constants
GRID_SIZE = 21
CELL_SIZE = 40



# Tile Class
class Tile:
    """Represents a single tile in the grid."""
    def __init__(self, x, y, terrain, textures, overlay=None):
        self.x = x
        self.y = y
        self.terrain = terrain  # "grass", "water", or "rock"
        self.overlay = overlay  # Optional overlay: "bush", "barrier", "nexus"
        self.textures = textures
        self.traversable = terrain in ["grass", "water"]  # Grass and water are traversable

        # Assign the texture based on terrain
        if self.terrain == "grass":
            self.texture = random.choice(self.textures["grass"])
        else:
            self.texture = self.textures[self.terrain]

    def is_overlay_blocking(self):
        """Check if the overlay blocks visibility or movement."""
        return self.overlay in ["barrier", "nexus"]

    def draw(self, screen):
        """Draw the tile with its texture and overlay."""
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        # Draw the base terrain
        screen.blit(pygame.transform.scale(self.texture, (CELL_SIZE, CELL_SIZE)), rect)

        # Draw overlay on top, if present
        if self.overlay:
            overlay_texture = self.textures[self.overlay]
            screen.blit(pygame.transform.scale(overlay_texture, (CELL_SIZE, CELL_SIZE)), rect)

        # Optional: Draw tile border
        pygame.draw.rect(screen, (0, 0, 0), rect, 1)  # Black border

# Grid Class
class Grid:
    """Manages the entire grid."""
    def __init__(self, size, textures):
        self.size = size
        self.textures = textures
        self.tiles = self.create_grid()

    def create_grid(self):
        """Create the grid with predefined terrain and overlays."""
        grid = [[Tile(x, y, "grass", self.textures) for y in range(self.size)] for x in range(self.size)]

        # Add water (lakes)
        lakes = [
            [(5, 5), (5, 6), (5, 7), (6, 5), (6, 6), (6, 7)],
            [(12, 12), (12, 13), (13, 12), (13, 13)],
            [(14, 5), (14, 6), (15, 5), (15, 6)],
        ]
        for lake in lakes:
            for x, y in lake:
                grid[x][y] = Tile(x, y, "water", self.textures)

        # Add rocks (hills)
        hills = [
            [(2, 2), (2, 3), (3, 2), (3, 3), (4, 3)],
            [(10, 8), (10, 9), (10, 10), (11, 8), (11, 9), (12, 9), (12, 10), (12, 11), (13, 10), (13, 9), (13, 8), (14, 11), (14, 10)],
            [(5, 16), (10, 17), (11, 16), (11, 17), (7, 16), (8, 17), (9, 17)],
            [(11, 3), (11, 4), (12, 3), (12, 4), (13, 3), (13, 4)],
            [(4, 4), (4, 5), (4, 6), (5, 4), (5, 5)],  # 9 blocks
            [(15, 14),(15, 13),(15, 15), (15, 16), (15, 17), (16, 15), (16, 16), (16, 17)], 
        ]
        for hill in hills:
            for x, y in hill:
                grid[x][y] = Tile(x, y, "rock", self.textures)

        # Add overlays (bushes, barriers, nexus)
        overlays = {
            "bush": [(0, 0), (1, 0), (0, 1), (20, 20), (19, 20), (20, 19), (3, 7), (3, 8), (8, 3), (17, 12), (17, 13), (12, 17)],
            "barrier": [(0, 17), (1, 17), (2, 17), (3, 17), (3, 18), (3, 19), (3, 20), (17, 0), (17, 1), (17, 2), (17, 3), (18, 3), (19, 3), (20, 3)],
            "nexus": [(1, 19), (19, 1)],  # Nexus positions
        }
        for overlay_type, positions in overlays.items():
            for x, y in positions:
                grid[x][y].overlay = overlay_type

        return grid

    def draw(self, screen):
        """Draw all tiles in the grid."""
        for row in self.tiles:
            for tile in row:
                tile.draw(screen)

# Highlight Class
class Highlight:
    """Manages highlighting for movement and attack ranges."""
    def __init__(self, grid):
        self.grid = grid
        self.visible_tiles = set()

    def highlight_range(self, unit):
        """Highlight movement or attack range based on the unit's state."""
        overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)  # Transparent overlay

        if unit.state == "move":
            visited = set()
            queue = [(unit.initial_x, unit.initial_y, 0)]  # (x, y, current_distance)
            
            while queue:
                x, y, dist = queue.pop(0)
                if (x, y) in visited or dist > unit.move_range:  # Skip already visited or out-of-range tiles
                    continue
                visited.add((x, y))
            
                    
                if (self.grid.tiles[x][y].traversable ):
                    overlay.fill((50, 150, 255, 100))  # Blue with transparency (alpha = 100)
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    self.screen.blit(overlay, rect)
                    
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Check cardinal directions
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:  # Ensure within bounds
                            if self.grid.tiles[nx][ny].traversable and (nx, ny) not in visited:
                                queue.append((nx, ny, dist + 1))
                        
        elif unit.state == "attack":
            # Highlight attack range
            for dx in range(-unit.attack_range, unit.attack_range + 1):
                for dy in range(-unit.attack_range, unit.attack_range + 1):
                    x, y = unit.x + dx, unit.y + dy
                    if (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and
                            abs(dx) + abs(dy) <= unit.attack_range):
                        overlay.fill((250, 0, 0, 100))  # Red with transparency (alpha = 100)
                        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        self.screen.blit(overlay, rect)

            # Highlight the target cursor
            target_rect = pygame.Rect(unit.target_x * CELL_SIZE, unit.target_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            beat_scale = 90  # Indicator scale percentage
            beat_alpha = 180 + 70 * (pygame.time.get_ticks() % 1000 / 500 - 1)  # Smoother alpha transition
            indicator_size = int(CELL_SIZE * beat_scale / 100)  # Scale the indicator image
            indicator_image = pygame.transform.scale(self.indicators["indicator"], (indicator_size, indicator_size))
            indicator_image.set_alpha(beat_alpha)

            # Center the scaled indicator within the target tile
            indicator_x = target_rect.x + (CELL_SIZE - indicator_size) // 2
            indicator_y = target_rect.y + (CELL_SIZE - indicator_size) // 2

            self.screen.blit(indicator_image, (indicator_x, indicator_y))




    def update_fog_visibility(self, team_color):
        print(f"Updating fog visibility for team: {team_color}")


        """
        Update the set of visible tiles based on the current team's visibility.
        :param team_color: Color of the current team.
        """
        
        self.visible_tiles = set()  # Reset visible tiles
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Light propagation directions

        for unit in self.units:
            if unit.color == team_color and unit.alive:
                queue = [(unit.x, unit.y, 0)]  # BFS queue: (x, y, distance)
                max_visibility = unit.move_range + 2  # Visibility range slightly larger than movement

                while queue:
                    x, y, distance = queue.pop(0)

                    # Stop propagation if the distance exceeds the visibility range
                    if distance > max_visibility:
                        continue

                    # Mark tile as visible
                    self.visible_tiles.add((x, y))

                    # Propagate light in all directions
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy

                        if (
                            0 <= nx < GRID_SIZE
                            and 0 <= ny < GRID_SIZE
                            and (nx, ny) not in self.visible_tiles
                            and distance + 1 <= max_visibility
                        ):
                            # If the tile is non-traversable, stop propagation in this direction
                            if not self.grid.tiles[nx][ny].traversable:
                                self.visible_tiles.add((nx, ny))  # Add for visual accuracy
                                continue

                            # Add to queue to continue propagation
                            queue.append((nx, ny, distance + 1))

    def draw_fog(self, screen):
        """Draw the fog of war and dim lighting based on the visible tiles."""
        
        fog_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        fog_overlay.fill((0, 0, 0, 200))  # Dark fog (alpha = 200)

        dim_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        dim_overlay.fill((50, 50, 50, 100))  # Dim lighting (alpha = 100)

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Light propagation directions

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if (x, y) not in self.visible_tiles:
                    # Fully fogged areas
                    self.screen.blit(fog_overlay, rect)   
                elif (x, y) in self.visible_tiles and any(
                    (x + dx, y + dy) not in self.visible_tiles for dx, dy in directions
                ):
                    # Dim lighting at the edges of visibility
                    self.screen.blit(dim_overlay, rect)   
