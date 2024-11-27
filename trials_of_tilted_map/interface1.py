import pygame
import random

# Constants
GRID_SIZE = 21
CELL_SIZE = 45
SCREEN_WIDTH, SCREEN_HEIGHT = CELL_SIZE * GRID_SIZE + 300, CELL_SIZE * GRID_SIZE 
FPS = 60

def to_iso(x, y):
    tile_width = CELL_SIZE
    tile_height = CELL_SIZE // 2
    iso_x = (x - y) * (tile_width // 2) + SCREEN_WIDTH // 4
    iso_y = (x + y) * (tile_height // 2)
    return iso_x, iso_y

# Tile Class
class Tile:
    """Represents a single tile in the grid."""
    def __init__(self, x, y, terrain, textures_file, overlay=None):
        self.x = x
        self.y = y
        self.terrain = terrain  # "grass", "water", or "rock"
        self.overlay = overlay  # Optional overlay: "bush", "barrier"
        self.textures_file = textures_file
        self.traversable = terrain in ["grass", "water"]  # Grass and water are traversable

    def draw_tile(self, screen):
        tile_width = CELL_SIZE
        tile_height = CELL_SIZE // 2
        iso_x, iso_y = to_iso(self.x, self.y)

        # Draw the base terrain
        rect = pygame.Rect(iso_x, iso_y, tile_width, tile_height)
        self.texture = self.textures_file[self.terrain]
        screen.blit(pygame.transform.scale(self.texture, (tile_width, tile_height)), rect)

        # Draw overlay on top, if present
        if self.overlay:
            overlay_texture = self.textures_file[self.overlay]
            screen.blit(pygame.transform.scale(overlay_texture, (tile_width, tile_height)), rect)

class Pickup(Tile):
    def __init__(self, x, y, textures_file, visible_tiles, overlay=None):
        super().__init__(x, y, "grass", textures_file, overlay)
        self.visible_tiles = visible_tiles
        self.picked = False

    def draw_tile(self, screen):
        if (self.x, self.y) in self.visible_tiles and not self.picked:
            tile_width = CELL_SIZE
            tile_height = CELL_SIZE // 2
            iso_x, iso_y = to_iso(self.x, self.y)
            rect = pygame.Rect(iso_x, iso_y, tile_width, tile_height)
            overlay_texture = self.textures_file[self.overlay]
            screen.blit(pygame.transform.scale(overlay_texture, (tile_width, tile_height)), rect)

    def picked_used(self, player):
        if player.state == "move" and player.x == self.x and player.y == self.y and not self.picked:
            if player.health < player.max_health:
                heal_amount = 10  # Define how much the potion heals
                player.health = min(player.max_health, player.health + heal_amount)
                print(f"{player.name} healed for {heal_amount} HP!")
                self.picked = True

# Grid Class
class Grid:
    """Manages the entire grid."""
    def __init__(self, size, textures_file):
        self.size = size
        self.textures_file = textures_file
        self.tiles = self.create_grid()
        self.highlight = Highlight(self.textures_file, self)

    def create_grid(self):
        """Create the grid with predefined terrain and overlays."""
        grid = [[Tile(x, y, "grass", self.textures_file) for y in range(self.size)] for x in range(self.size)]

        # Add water (lakes)
        lakes = [
            [(5, 5), (5, 6), (6, 5), (6, 6), (7, 6)],  
            [(10, 7), (11, 6), (11, 7), (12, 6),(12,7)],  
            [(8, 13),(9, 13), (8, 14), (9, 14), (10, 13)], 
            [(13, 14), (14, 14), (14, 15), (15, 14), (15, 15)],  
        ]
        for lake in lakes:
            for x, y in lake:
                grid[x][y] = Tile(x, y, "water", self.textures_file)

        # Add rocks (hills)
        hills = [
            [
                (2, 4), (2, 5), (2, 6),(2,12), (3, 3),(3, 4), (3, 5),(3,6),(3,10),(3,11),(3,12),
                (3,13),(3,14),(4, 3), (5, 3),(5,8),(5,10),(5,12),(6,3),(6, 8), (6, 9),
                (6,10),(6,12),(6,13),(6,17),(7,8),(7,12),(7,16),(7,17),(8,11),(8,15),(8,16),(8,17),
                (9, 3), (9, 8), (9, 12), (9, 16), (9, 17),(10,2),(10,3),(10,8),(10,12),(10,17),(10,18),
                (11,3),(11,4),(11,8),(11,12),(11,17),(12,3),(12,4),(12,5),(12,9),(13,3),(13,4),(13,8),(13,12),
                (14,3),(14,7),(14,8),(14,10),(14,11),(14,12),(14,17),(15,8),(15,10),(15,12),(15,17),(16,17),
                (17,6),(17,7),(17,8),(17,9),(17,10),(17,14),(17,15),(17,16),(17,17),
                (18,8),(18,14),(18,15),(18,16),
            ]
        ]
        for hill in hills:
            for x, y in hill:
                grid[x][y] = Tile(x, y, "rock", self.textures_file)

        # Add overlays (bushes, barriers)
        overlays = {
            "bush": [(0, 0), (1, 0), (0, 1), (20, 20), (19, 20), (20, 19), (3, 7), (3, 8), (8, 3), (17, 12), (17, 13), (12, 17)],
            "barrier": [(0, 17), (1, 17), (2, 17), (3, 17), (3, 18), (3, 19), (3, 20), (17, 0), (17, 1), (17, 2), (17, 3), (18, 3), (19, 3), (20, 3)],
        }
        for overlay_type, positions in overlays.items():
            for x, y in positions:
                grid[x][y].overlay = overlay_type

        return grid

    def draw(self, screen):
        """Draw all tiles in the grid."""
        for row in self.tiles:
            for tile in row:
                tile.draw_tile(screen)

# Highlight Class
class Highlight:
    """Manages highlighting for movement and attack ranges."""
    def __init__(self, textures_file, grid):
        self.visible_tiles = set()
        self.textures_file = textures_file
        self.grid = grid  # Reference to the Grid object
        self.units = []   # Placeholder for unit list, needs to be populated

    def highlight_range(self, unit, screen):
        """Highlight movement or attack range based on the unit's state."""
        tile_width = CELL_SIZE
        tile_height = CELL_SIZE // 2
        overlay = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)

        if unit.state == "move":
            visited = set()
            queue = [(unit.x, unit.y, 0)]  # Assuming unit.x and unit.y are current positions

            while queue:
                x, y, dist = queue.pop(0)
                if (x, y) in visited or dist > unit.move_range:
                    continue
                visited.add((x, y))

                if self.grid.tiles[x][y].traversable:
                    overlay.fill((50, 150, 255, 100))
                    iso_x, iso_y = to_iso(x, y)
                    rect = pygame.Rect(iso_x, iso_y, tile_width, tile_height)
                    screen.blit(overlay, rect)

                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                            if self.grid.tiles[nx][ny].traversable and (nx, ny) not in visited:
                                queue.append((nx, ny, dist + 1))

        elif unit.state == "attack":
            # Highlight attack range
            for dx in range(-unit.attack_range, unit.attack_range + 1):
                for dy in range(-unit.attack_range, unit.attack_range + 1):
                    x, y = unit.x + dx, unit.y + dy
                    if (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and abs(dx) + abs(dy) <= unit.attack_range):
                        overlay.fill((250, 0, 0, 50))
                        iso_x, iso_y = to_iso(x, y)
                        rect = pygame.Rect(iso_x, iso_y, tile_width, tile_height)
                        screen.blit(overlay, rect)

    def update_fog_visibility(self, team_color):
        """Update the set of visible tiles based on all members of the team."""
        self.visible_tiles = set()
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Process visibility for each unit on the team
        for unit in self.units:
            if unit.color == team_color and unit.alive:
                queue = [(unit.x, unit.y, 0)]
                max_visibility = unit.move_range + 2
                unit_visible_tiles = set()

                while queue:
                    x, y, distance = queue.pop(0)
                    if distance > max_visibility:
                        continue
                    unit_visible_tiles.add((x, y))

                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < GRID_SIZE
                            and 0 <= ny < GRID_SIZE
                            and (nx, ny) not in unit_visible_tiles
                            and distance + 1 <= max_visibility
                        ):
                            if not self.grid.tiles[nx][ny].traversable:
                                unit_visible_tiles.add((nx, ny))
                                continue
                            queue.append((nx, ny, distance + 1))

                self.visible_tiles.update(unit_visible_tiles)



    def draw_fog(self, screen):
        """Draw the fog of war and dim lighting based on the visible tiles."""
        tile_width = CELL_SIZE
        tile_height = CELL_SIZE // 2
        fog_overlay = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
        fog_overlay.fill((0, 0, 0, 170))

        dim_overlay = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
        dim_overlay.fill((50, 50, 50, 85))

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                iso_x, iso_y = to_iso(x, y)
                rect = pygame.Rect(iso_x, iso_y, tile_width, tile_height)
                if (x, y) not in self.visible_tiles:
                    screen.blit(fog_overlay, rect)
                elif any((x + dx, y + dy) not in self.visible_tiles for dx, dy in directions):
                    screen.blit(dim_overlay, rect)
    def show_buff_animation(self, screen, buff_image, key_message="You won a key"):
        """Displays a buff animation after a monster is defeated."""
        clock = pygame.time.Clock()
        duration = 2500  # Total animation duration in ms
        start_time = pygame.time.get_ticks()

        # Capture and blur the background
        background = pygame.Surface((CELL_SIZE*GRID_SIZE, CELL_SIZE*GRID_SIZE))
        background.blit( self.screen, (0, 0))  # Copy the current screen into the background surface

        blur_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        blur_surface.fill((0, 0, 0, 150))  # Semi-transparent black for the blur effect

        # Initial PNG size and position
        original_width, original_height = buff_image.get_width(), buff_image.get_height()
        center_x, center_y = (screen.get_width()-300) // 2, screen.get_height() // 2
        shake_amplitude = 2  # Pixels for shaking

        while True:
            current_time = pygame.time.get_ticks()
            time_elapsed = current_time - start_time
            if time_elapsed > duration:
                break  # End the animation after the duration

            screen.blit(background, (0, 0))  # Restore the background
            screen.blit(blur_surface, (0, 0))  # Apply the blur overlay

            # Calculate current PNG size (grows over time)
            scale_factor = min(2, 1 + time_elapsed / (duration // 2))  # Scale up to 200%
            scaled_width = int(original_width * scale_factor)
            scaled_height = int(original_height * scale_factor)

            # Apply shaking effect
            offset_x = center_x - scaled_width // 2 + (shake_amplitude if (time_elapsed // 100) % 2 == 0 else -shake_amplitude)
            offset_y = center_y - scaled_height // 2 + (shake_amplitude if (time_elapsed // 100) % 2 == 0 else -shake_amplitude)

            # Draw the PNG image
            scaled_image = pygame.transform.scale(buff_image, (scaled_width, scaled_height))
            screen.blit(scaled_image, (offset_x, offset_y))

            
            if time_elapsed > duration - 1500:
                font = pygame.font.Font("assets/RussoOne.ttf", 50)
                text_surface = font.render(key_message, True, (0,0,0))
                text_rect = text_surface.get_rect(center=(center_x, center_y + 100))
                screen.blit(text_surface, text_rect)
                text_surface1 = font.render(key_message, True, (0, 255,0))
                text_rect1 = text_surface1.get_rect(center=(center_x + 2, center_y + 102))
                screen.blit(text_surface1, text_rect1)

            pygame.display.flip()
            clock.tick(60)