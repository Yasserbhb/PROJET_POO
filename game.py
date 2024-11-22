import pygame
import random
from unit import Unit

# Constants
GRID_SIZE = 21
CELL_SIZE = 40
SCREEN_WIDTH, SCREEN_HEIGHT = CELL_SIZE * GRID_SIZE, CELL_SIZE * GRID_SIZE
FPS = 60

# Load assets
def load_textures():
    """Load textures for grass, water, and rocks."""
    return {
        "grass": [
            
            pygame.image.load("assets/grass4.jpg"),
            pygame.image.load("assets/grass4.jpg"),
        ],
        "water": pygame.image.load("assets/water.jpg"),
        "rock": pygame.image.load("assets/rock.jpg"),
        "bush": pygame.image.load("assets/bush.png"),
        "nexus": pygame.image.load("assets/nexus.png"),
        "barrier": pygame.image.load("assets/barrier.png"),
    }
def load_unit_images():
    return {
        "ashe": "assets/ashe.png",
        "garen": "assets/garen.png",
        "darius": "assets/darius.png",
        "soraka": "assets/soraka.png",
    }
def load_indicators():
    return {
        "indicator": pygame.image.load("assets/indicator.png"),
        "indicator": pygame.image.load("assets/indicator.png")
    }
    
    
    
# Tile class
class Tile:
    def __init__(self, x, y, terrain, textures,  overlay=None):
        self.x = x
        self.y = y
        self.terrain = terrain  # "grass", "water", or "rock"
        self.textures = textures
        self.overlay = overlay  # Overlay type: "bush", "barrier", "nexus"
        self.traversable = terrain in ["grass", "water"]  # Only grass is traversable
        

        # Assign texture for grass
        if self.terrain == "grass":
            self.texture = random.choice(self.textures["grass"])
        else:
            self.texture = self.textures[terrain]

    def draw(self, screen):
        """Draw the tile with its texture."""
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        screen.blit(pygame.transform.scale(self.texture, (CELL_SIZE, CELL_SIZE)), rect)

        # Draw the overlay (if any) on top
        if self.overlay:
            overlay_texture = self.textures[self.overlay]
            screen.blit(pygame.transform.scale(overlay_texture, (CELL_SIZE, CELL_SIZE)), rect)

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
        self.indicators = load_indicators()
        self.grid = self.create_grid()
        self.units = self.create_units()
        self.current_unit_index = 0
        self.last_turn_time = 0  # Initialize turn delay tracking
        self.last_move_time = 0  # Timestamp of the last movement
        self.last_action_time = 0  # Timestamp of the last attack movement to target

        self.damage_popups = []  # List to store active damage popups
        self.visible_tiles = set()
        
        starting_team_color = self.units[self.current_unit_index].color
        self.update_fog_visibility(starting_team_color)  # Pre-calculate fog for the starting team
        


    def create_grid(self):
        """Create a grid with predefined lakes and hills."""
        grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        # Fill grid with grass by default
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                grid[x][y] = Tile(x, y, "grass", self.textures)

        # Add lakes (water tiles)
        lakes = [
            [(5, 5), (5, 6), (5, 7), (6,5),(6, 6),(6,7)],
            [(12, 12), (12, 13), (13, 12), (13, 13)],
            [(14, 5), (14, 6), (15, 5), (15, 6)],
        ]
        for lake in lakes:
            for x, y in lake:
                grid[x][y] = Tile(x, y, "water", self.textures)

        # Add hills (rock tiles)
        hills = [
            [(2, 2), (2, 3), (3, 2), (3, 3), (4, 3)],
            [(10, 8), (10, 9), (10, 10), (11, 8), (11, 9), (12, 9), (12, 10), (12, 11), (13, 10), (13, 9), (13, 8), (14, 11), (14, 10)],
            [(5, 16), (10, 17), (11, 16), (11, 17), (7, 16), (8, 17), (9, 17)],
            [(11, 3), (11, 4), (12, 3), (12, 4), (13, 3), (13, 4)],
            [(4, 4), (4, 5), (4, 6), (5, 4), (5, 5)],  # 9 blocks
            [(15, 14),(15, 13),(15, 15), (15, 16), (15, 17), (16, 15), (16, 16), (16, 17)],             # 6 blocks   
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
                if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                    grid[x][y].overlay = overlay_type

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
        """Draw all units on the grid with visibility logic."""
        current_team_color = self.units[self.current_unit_index].color

        for unit in self.units:
            if unit.alive:
                if unit.color == current_team_color or (unit.x, unit.y) in self.visible_tiles:
                    unit.draw(self.screen)



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
            
                    
                if (self.grid[x][y].traversable ):
                    overlay.fill((50, 150, 255, 100))  # Blue with transparency (alpha = 100)
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    self.screen.blit(overlay, rect)
                    
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Check cardinal directions
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:  # Ensure within bounds
                            if self.grid[nx][ny].traversable and (nx, ny) not in visited:
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
            
            

    def resolve_attack(self, unit):
        """Resolve the attack at the current target location."""
        target_hit = False

        # Find a valid target at the attack cursor location
        for other_unit in self.units:
            if (
                other_unit.alive
                and other_unit.x == unit.target_x
                and other_unit.y == unit.target_y
                and other_unit.color != unit.color
            ):
                unit.attack(other_unit)  # Use the Unit's attack method
                target_hit = True
                break

        if not target_hit:
            print(f"{unit.name} attacked but missed!")

        unit.state = "done"  # Mark the unit as done after the attack
        
        
        
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
                max_visibility = unit.move_range + 1  # Visibility range slightly larger than movement

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
                            if not self.grid[nx][ny].traversable:
                                self.visible_tiles.add((nx, ny))  # Add for visual accuracy
                                continue

                            # Add to queue to continue propagation
                            queue.append((nx, ny, distance + 1))

        
        
    def draw_fog(self):
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



    def advance_to_next_unit(self):
        """Advance to the next unit, skipping dead ones."""
        # Start from the current unit
        start_index = self.current_unit_index

        while True:
            # Move to the next unit
            self.current_unit_index = (self.current_unit_index + 1) % len(self.units)

            # Check if the unit is alive
            if self.units[self.current_unit_index].alive:
                break

            # If we've cycled through all units and come back to the start, stop (prevents infinite loops)
            if self.current_unit_index == start_index:
                print("No alive units remaining!")
                return

    def handle_turn(self):
        """Handle movement and attacks for the current unit."""
        current_time = pygame.time.get_ticks()
        current_unit = self.units[self.current_unit_index]

        if not current_unit.alive:
            # Move to the next unit's turn
            self.current_unit_index = (self.current_unit_index + 1) % len(self.units)
            return
        
        keys = pygame.key.get_pressed()

        # Movement Phase
        if current_unit.state == "move":
            if current_time - self.last_move_time > 100:  # Delay of 100ms between movements
                if keys[pygame.K_UP]:
                    current_unit.move(0, -1, self.grid)
                    self.last_move_time = current_time
                elif keys[pygame.K_DOWN]:
                    current_unit.move(0, 1, self.grid)
                    self.last_move_time = current_time
                elif keys[pygame.K_LEFT]:
                    current_unit.move(-1, 0, self.grid)
                    self.last_move_time = current_time
                elif keys[pygame.K_RIGHT]:
                    current_unit.move(1, 0, self.grid)
                    self.last_move_time = current_time
                elif keys[pygame.K_RETURN]:
                    print(f"{current_unit.name} moved to ({current_unit.x}, {current_unit.y}).")
                    # Start attack phase
                    current_unit.state = "attack"
                    current_unit.target_x, current_unit.target_y = current_unit.x, current_unit.y  # Initialize cursor
                    
                    next_team_color = self.units[self.current_unit_index].color
                    self.update_fog_visibility(next_team_color)
                    
        # Attack Phase
        elif current_unit.state == "attack":
            if current_time - self.last_move_time > 100:  # Delay of 100ms between movements
                new_target_x, new_target_y = current_unit.target_x, current_unit.target_y

                # Move the attack cursor
                if keys[pygame.K_UP]:
                    new_target_y = max(0, current_unit.target_y - 1)
                elif keys[pygame.K_DOWN]:
                    new_target_y = min(GRID_SIZE - 1, current_unit.target_y + 1)
                elif keys[pygame.K_LEFT]:
                    new_target_x = max(0, current_unit.target_x - 1)
                elif keys[pygame.K_RIGHT]:
                    new_target_x = min(GRID_SIZE - 1, current_unit.target_x + 1)

                # Enforce attack range restriction
                if (
                    abs(current_unit.x - new_target_x) + abs(current_unit.y - new_target_y)
                    <= current_unit.attack_range
                ):
                    current_unit.target_x, current_unit.target_y = new_target_x, new_target_y
                    self.last_move_time = current_time

            # Confirm attack
            if keys[pygame.K_SPACE] and current_time - self.last_action_time > 100:
                self.resolve_attack(current_unit)
                self.last_action_time = current_time
                current_unit.state = "done"  # Mark attack as finished

        # End Turn
        if  current_unit.state == "done" and current_time - self.last_turn_time > 1000:
            self.last_turn_time = current_time  # Update the last turn time
            current_unit.state = "move"  # Reset state for the next turn
            current_unit.initial_x, current_unit.initial_y = current_unit.x, current_unit.y  # Reset initial position
            #self.current_unit_index = (self.current_unit_index + 1) % len(self.units)  

            # Advance to the next unit, skipping dead ones
            self.advance_to_next_unit()

            next_team_color = self.units[self.current_unit_index].color
            print(next_team_color)
            self.update_fog_visibility(next_team_color)
            # Reset state for the next unit

            
            # Check for win condition
            result = self.check_win_condition()
            if result:
                print(result)
                
                

    def check_win_condition(self):
        """Check if one team has won."""
        blue_team_alive = any(unit.alive and unit.color == (0, 0, 255) for unit in self.units)
        red_team_alive = any(unit.alive and unit.color == (255, 0, 0) for unit in self.units)

        if not blue_team_alive:
            return "Red Team Wins!"
        elif not red_team_alive:
            return "Blue Team Wins!"
        return None
    
    
            
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
            
            # Render fog of war
            self.draw_fog()


            # Highlight range for the active unit
            current_unit = self.units[self.current_unit_index]
            self.highlight_range(current_unit)
            
            
            self.draw_units()
            # Handle current unit's turn
            self.handle_turn()
            
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
# Run the game
if __name__ == "__main__":
    Game().run()


#make grid and tile as a class and have 3 different maps, no need for config map in the game part , everything related to grid stays in grid and make ice make you slower next round (less range) , and add a hiding place that we can use as a dmg boost if you hit from it
#make an ability class that has a name, description, and a function that gets called when the ability is used and a lot of attributes
#take the turn handler to a diffrent class ?
# take in rnage verification to game instead of unit , so resolve attack checks all the enviromeent and confirms if we attack , and attack method only works after we confim that so it just modifies the hp and effects...
# after done attacking add button so that it doesnt directly go to the enemy team to give me time to look at the impacts i did or to use the vision i gained from the move ability
# i want the highlight for range to also be like the attack so the move phase only the cursor for target position moves than when we confirm , the unit snaps to that posotion
# create a HUD as a class
# add pick ups class
# verify all conditions after creating TP and healings and effects 
# add objective class it has a nexus also red and blue monster  (red and blue monster spawn once each 6 rounds)
# each team has 2 keys 1 on each player and the third is hidden in a monster ( 2 keys 2 buffs , 1 for each team and there are 3 monsters total ) and one that spawns randomly
# once u have 3 keys of the enemy (1 from monster 1 random and 1 from killing them) the barriere disappears and their nexus is visible and u can hit it )
# game ends with nexus exploding 