import pygame
import random 
from sounds import *

# Constants
GRID_SIZE = 21
CELL_SIZE = 35
SCREEN_WIDTH, SCREEN_HEIGHT = CELL_SIZE * GRID_SIZE + 300, CELL_SIZE * GRID_SIZE + 100


##addign the types of potions 


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
        self.highlighted = False  
                
        # Assign move cost based on terrain type
        self.move_cost = {"grass": 1, "water": 2, "rock": float("inf")}[terrain]
        
        

    def draw_tile(self, screen):
        """Draw the tile with its texture and overlay."""
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        # Draw the base terrain
        self.texture = self.textures_file[self.terrain]
        screen.blit(pygame.transform.scale(self.texture, (CELL_SIZE, CELL_SIZE)), rect)

        # Draw overlay on top, if present
        if self.overlay :
            overlay_texture = self.textures_file[self.overlay]
            screen.blit(pygame.transform.scale(overlay_texture, (CELL_SIZE, CELL_SIZE)), rect)

        # Optional: Draw tile border
        #pygame.draw.rect(screen, (0, 0, 0), rect, 1)  # Black border


class Pickup:
    def __init__(self, x=None, y=None, overlay=None, spawn_turn=None):
        if x is None and y is None and overlay is None and spawn_turn is None:
            # This is the manager instance
            self.all_pickups = []
            self.textures_file = None
            self.turn_count = 0
            self.allowed_tile_types = ["grass", "water"]

            self.pickup_types = {
                "red_potion":   {"rarity": 0.8},
                "blue_potion":  {"rarity": 0.8},
                "green_potion": {"rarity": 0.3},
                "golden_potion":{"rarity": 0.2},
                "black_potion": {"rarity": 0.2},
            }
    
            self.next_spawn_turns = {}
            self.sound = Sounds() 
            self.event_log = [] # Initialize event log

        else:
            # This is a pickup item instance
            self.x = x
            self.y = y
            self.overlay = overlay
            self.spawn_turn = spawn_turn
            self.picked = False
            self.event_log = [] # Initialize event log


    def initialize(self, textures_file):
        """Initialize the pickup system and set initial next spawn attempts."""
        self.textures_file = textures_file
        for p_type in self.pickup_types:
            self.next_spawn_turns[p_type] = random.randint(5, 8)

    def update(self, turn_count, grid):
        """Update all pickups and attempt spawns each turn (manager only)."""
        self.turn_count = turn_count

        # Remove pickups that have stayed 15 turns without being picked
        for p in self.all_pickups[:]:
            if not p.picked and (self.turn_count - p.spawn_turn >= 15):
                self.remove_pickup(p)

        # Attempt to spawn each pickup type if it's time
        for p_type, config in self.pickup_types.items():
            if self.turn_count >= self.next_spawn_turns[p_type]:
                if len(self.all_pickups) < 10:
                    # Check rarity
                    if random.random() < config["rarity"]:
                        x, y = self.get_random_spawn_location(grid)
                        self.spawn_single_pickup(x, y, p_type, self.turn_count)
                    else:
                        # Not spawned this turn, try again soon
                        self.next_spawn_turns[p_type] = self.turn_count + random.randint(1, 3)

    def spawn_single_pickup(self, x, y, overlay, spawn_turn):
        """Create and store a single pickup item instance."""
        new_pickup = Pickup(x, y, overlay, spawn_turn)
        self.all_pickups.append(new_pickup)

    def draw_pickups(self, screen, visible_tiles):
        """Draw all item pickups (manager only)."""
        if not self.textures_file:
            return
        for p in self.all_pickups:
            if not p.picked and (p.x, p.y) in visible_tiles:
                texture = self.textures_file[p.overlay]
                rect = pygame.Rect(p.x * CELL_SIZE+CELL_SIZE/4, p.y * CELL_SIZE+CELL_SIZE/4, CELL_SIZE/2, CELL_SIZE/2)
                screen.blit(pygame.transform.scale(texture, (CELL_SIZE/2, CELL_SIZE/2)), rect)

    def picked_used(self, unit, pickup):
        """Apply the effect of this pickup to the unit and remove it (manager only)."""
        if not pickup.picked:
            if pickup.overlay == "red_potion":    # heals 30% missing health
                heal_amount = int((unit.max_health - unit.health) * 0.3)
                unit.attack(unit, -heal_amount)
                Highlight.log_event(self,f"{unit.name} used a Red Potion and healed {heal_amount} health!")
            elif pickup.overlay == "blue_potion": # full mana regeneration
                unit.mana = unit.max_mana
                Highlight.log_event(self,f"{unit.name} used a Blue Potion and fully restored their mana!")
            elif pickup.overlay == "green_potion": # +100 max health and heal 33% missing health
                increase = 100
                unit.max_health += increase
                heal_amount = (unit.max_health - unit.health) // 3
                unit.attack(unit, -heal_amount)
                Highlight.log_event(self,f"{unit.name} used a Green Potion, gaining {increase} max health and healing {heal_amount}!")
            elif pickup.overlay == "golden_potion": # reduces remaining cooldowns by 50%
                for ability in unit.abilities:
                    ability.remaining_cooldown //= 2
                Highlight.log_event(self,f"{unit.name} used a Golden Potion, reducing all cooldowns by 50%!")
            elif pickup.overlay == "black_potion": # increases critical chance
                for ability in unit.abilities:
                    unit.crit_chance += 5
                Highlight.log_event(self,f"{unit.name} used a Black Potion, increasing critical hit chance by 5%!")

        # Play the potion sound
        self.sound.play("potion")

        # Mark as picked and remove
        pickup.picked = True
        self.remove_pickup(pickup)


    def remove_pickup(self, pickup):
        """Remove a pickup and schedule next spawn attempt (manager only)."""
        if pickup in self.all_pickups:
            self.all_pickups.remove(pickup)
        delay = random.randint(15, 20)
        self.next_spawn_turns[pickup.overlay] = self.turn_count + delay

    def get_random_spawn_location(self, grid):
        """Get a random allowed cell for spawning."""
        while True:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            tile_type = grid.tiles[x][y].terrain
            if tile_type in self.allowed_tile_types :
                return x, y
            # If not allowed, loop again until we find a suitable tile



# permanently increases the critical chance by 10%        


# Grid Class
class Grid:
    """Manages the entire grid."""
    def __init__(self, size, textures_file):
        self.size = size
        self.textures_file = textures_file
        self.tiles = self.create_grid()
        self.highlight=Highlight(self.textures_file)
        

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
    
            [(2, 4), (2, 5), (2, 6),(2,12), (3, 3),(3, 4), (3, 5),(3,6),(3,10),(3,11),(3,12),
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
    def __init__(self,textures_file):
        
        self.visible_tiles = set()
        self.textures_file=textures_file
        self.event_log = [] # Initialize event log

        
        

    def highlight_range(self, unit):
        """Highlight movement or attack range based on the unit's state."""
        overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)  # Transparent overlay

        for row in self.grid.tiles:
            for tile in row:
                tile.highlighted = False 

        if unit.state == "move":
            visited = set()
            queue = [(unit.initial_x, unit.initial_y, 0)]  # (x, y, current_distance)
            
            while queue:
                x, y, cost = queue.pop(0)
                if (x, y) in visited or cost > unit.move_range:  # Skip already visited or out-of-range tiles
                    continue
                visited.add((x, y))

                if self.grid.tiles[x][y].traversable:
                    self.grid.tiles[x][y].highlighted = True
                    overlay.fill((50, 150, 255, 100))  # Blue with transparency
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    self.screen.blit(overlay, rect)  # Highlight this tile

                    # Check cardinal directions for next tiles
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:  # Ensure within bounds
                            next_cost = cost + self.grid.tiles[nx][ny].move_cost
                            if next_cost <= unit.move_range and (nx, ny) not in visited:
                                queue.append((nx, ny, next_cost))

                        
        elif unit.state == "attack":
            # Determine the current attack range based on the selected ability
            if unit.selected_ability is not None:
                attack_range = unit.selected_ability.attack_radius
                aoe_range = unit.selected_ability.is_aoe
            else:
                attack_range = unit.attack_range
                aoe_range = 0

            # Highlight the attack range
            for dx in range(-attack_range, attack_range + 1):
                for dy in range(-attack_range, attack_range + 1):
                    x, y = unit.x + dx, unit.y + dy
                    if (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and
                            abs(dx) + abs(dy) <= attack_range):  # Manhattan distance restriction
                        overlay.fill((250, 0, 250, 50) if unit.selected_ability else (250, 0, 0, 50))  
                        # Green for ability, red for normal attack
                        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        self.screen.blit(overlay, rect)


            for dx in range(-aoe_range,aoe_range+1):
                for dy in range(-aoe_range,aoe_range+1):
                    x, y = unit.target_x + dx, unit.target_y + dy

                    if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE and abs(dx) + abs(dy) <= aoe_range:
                    # Highlight the target cursor
                        target_rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        beat_scale = 100  # Indicator scale percentage
                        beat_alpha = 180 + 70 * (pygame.time.get_ticks() % 1000 / 500 - 1)  # Smoother alpha transition
                        indicator_size = int(CELL_SIZE * beat_scale / 100)*1.2  # Scale the indicator image
                        indicator_image = pygame.transform.scale(self.indicators["redsquare"], (indicator_size, indicator_size))
                        indicator_image.set_alpha(beat_alpha)

                        # Center the scaled indicator within the target tile
                        indicator_x = target_rect.x + (CELL_SIZE - indicator_size) // 2
                        indicator_y = target_rect.y + (CELL_SIZE - indicator_size) // 2

                        self.screen.blit(indicator_image, (indicator_x, indicator_y))



    def update_fog_visibility(self, team_color):
        """
        Update the set of visible tiles based on all members of the team.
        :param team_color: Color of the current team.
        """
        self.visible_tiles = set()  # Reset visible tiles
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Light propagation directions

        # Process visibility for each unit on the team
        for unit in self.units:
            if unit.color == team_color and unit.alive:

                # BFS for this unit's visibility
                queue = [(unit.x, unit.y, 0)]  # BFS queue: (x, y, distance)
                max_visibility = unit.move_range + 2  # Visibility range slightly larger than movement

                # Local set to track tiles visible by this unit
                unit_visible_tiles = set()

                while queue:
                    x, y, distance = queue.pop(0)

                    # Stop propagation if the distance exceeds the visibility range
                    if distance > max_visibility:
                        continue

                    # Mark tile as visible for this unit
                    unit_visible_tiles.add((x, y))

                    # Propagate light in all directions
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < GRID_SIZE
                            and 0 <= ny < GRID_SIZE
                            and (nx, ny) not in unit_visible_tiles
                            and distance + 1 <= max_visibility
                        ):
                            # If the tile is non-traversable, stop propagation in this direction
                            if not self.grid.tiles[nx][ny].traversable:
                                unit_visible_tiles.add((nx, ny))  # Add for visual accuracy
                                continue

                            # Add to queue to continue propagation
                            queue.append((nx, ny, distance + 1))

                # Add this unit's visibility to the team's visibility
                self.visible_tiles.update(unit_visible_tiles)
                
                

        # Final combined visible tiles




    def draw_fog(self,screen):
 
        """Draw the fog of war and dim lighting based on the visible tiles."""
        
        fog_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        fog_overlay.fill((0, 0, 0, 170))  # Dark fog (alpha = 200)

        dim_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        dim_overlay.fill((50, 50, 50, 85))  # Dim lighting (alpha = 100)

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Light propagation directions

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if (x, y) not in self.visible_tiles:
                    # Fully fogged areas
                    screen.blit(fog_overlay, rect)   
                elif (x, y) in self.visible_tiles and any(
                    (x + dx, y + dy) not in self.visible_tiles for dx, dy in directions
                ):
                    # Dim lighting at the edges of visibility
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


    def log_event(self, message):
        """Add an event to the event log."""
        #print(f"Logging event: {message}")  # Debug
        self.event_log.append(message)
        if len(self.event_log) > 10:  # Limit the log to the last 10 events
            self.event_log.pop(0)


    def draw_info_panel(self,screen):
        """Draw the information panel with word wrapping for long text."""
        panel_x = CELL_SIZE * GRID_SIZE
        panel_width = 300
        panel_height = SCREEN_HEIGHT
        padding = 10

        pygame.draw.rect(screen, (30, 30, 30), (panel_x, 0, panel_width, panel_height))

        # Render event log with word wrapping
        font = pygame.font.Font(None, 24)
        y_offset = padding
        line_spacing = 5  # Spacing between lines
        max_line_width = panel_width - 2 * padding
        
        for i, message in enumerate(reversed(self.event_log)):  # `for i, message` structure
            words = message.split(" ")
            current_line = ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                text_surface = font.render(test_line, True, (255, 255, 255))
                if text_surface.get_width() > max_line_width:
                    # Render the current line and move to the next
                    rendered_surface = font.render(current_line, True, (255, 255, 255))
                    self.screen.blit(rendered_surface, (panel_x + padding, y_offset))
                    y_offset += rendered_surface.get_height() + line_spacing
                    current_line = word
                else:
                    current_line = test_line
            # Render the last line of the current event
            if current_line:
                rendered_surface = font.render(current_line, True, (255, 255, 255))
                self.screen.blit(rendered_surface, (panel_x + padding, y_offset))
                y_offset += rendered_surface.get_height() + line_spacing

            # Stop rendering if we've filled the panel
            if y_offset > panel_height - padding:
                break
   