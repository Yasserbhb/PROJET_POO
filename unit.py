import pygame
from interface import Highlight
from abilities import Abilities

CELL_SIZE = 30
class Unit:
    def __init__(self, x, y, name, health, damage, image_path, color, move_range, attack_range, unit_type, mana=100, abilities=None):
        self.x = x
        self.y = y
        self.initial_x = x
        self.initial_y = y
        self.name = name
        self.image = pygame.image.load(image_path)
        self.color = color
        self.health = health
        self.max_health = health
        self.mana = mana
        self.max_mana = mana
        self.move_range = move_range
        self.attack_range = attack_range
        self.damage = damage
        self.unit_type = unit_type
        self.alive = True
        self.state = "move"
        self.target_x = x
        self.target_y = y
        self.abilities = abilities if abilities else []  # Default to an empty list if no abilities are provided
        
        # new attributes
        self.attack = damage 
        self.defense = 0  
        self.is_buffed = False
        self.is_debuffed = False
        self.buff_duration = 0
        self.debuff_duration = 0
        
        # Initialize for damage display
        self.last_damage_time = None 
        self.damage_taken = 0 
        

    def in_range(self, target):
        """Check if the target is within attack range."""
        return abs(self.x - target.x) + abs(self.y - target.y) <= self.attack_range



    def move(self, dx, dy, grid):
    
        """Move the unit if within movement range, traversable, and highlighted."""
        new_x = self.x + dx
        new_y = self.y + dy

        # Check if the current position is within grid bounds
        if 0 <= new_x < len(grid.tiles) and 0 <= new_y < len(grid.tiles[0]):

            # Get the target tile at the new position
            target_tile = grid.tiles[new_x][new_y]

            # Check if the target tile is highlighted
            if not target_tile.highlighted:
                print(f"Cannot move to ({new_x}, {new_y}) because it's not highlighted.")
                return  # Can't move if the tile is not highlighted
            else : self.x, self.y = new_x, new_y
            """# Get the move cost for the target tile
            move_cost = target_tile.move_cost

            # Calculate the total movement cost from the initial position
            distance_cost = (abs(self.initial_x - new_x) + abs(self.initial_y - new_y)) * move_cost

            # Check if the move is valid and if the target tile is traversable
            if distance_cost <= self.move_range and target_tile.traversable:
                self.x, self.y = new_x, new_y  # Update position
                print(f"Moved to ({new_x}, {new_y}).")
            else:
                print(f"Invalid move due to cost or non-traversable tile at ({new_x}, {new_y}).")
                return  # Invalid move due to cost or non-traversable tile
        else:
            print(f"Invalid move: position ({new_x}, {new_y}) is out of bounds.")
            return  # Invalid move out of bounds """

    #neutral monsters reacting to attacks
    def react_to_attack(self, attacker):
        return

    def attack(self, target):

        effective_damage = max(0, self.damage - target.defense)  # Prevent negative damage
        print(f"{self.name} attacks {target.name}, dealing {effective_damage} damage!")
        target.health -= effective_damage  
        target.damage_taken = effective_damage
        target.last_damage_time = pygame.time.get_ticks() 
        if target.health <= 0:
            target.health = 0
            target.alive = False
        target.react_to_attack(self)  # Trigger monster reaction
        return effective_damage



    def draw(self, screen, is_current_turn):
        # Draw the unit's image inside the square
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        screen.blit(pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE)), rect)

        # Health bar settings
        health_ratio = max(0, self.health / self.max_health)  # Ensure health_ratio is not negative
        health_bar_full_width = int(CELL_SIZE * 0.95)  # Full width of the health bar
        health_bar_width = max(1, int(health_bar_full_width * health_ratio))  # Width of the current health bar
        health_bar_height = 7  # Height of the health bar
        health_bar_x = self.x * CELL_SIZE + 2  # Margin from the left
        health_bar_y = self.y * CELL_SIZE + 2  # Margin from the top
        border_radius = 3  # Rounded corners

        # Border settings
        border_thickness = 1  # Thickness of the border
        border_x = health_bar_x - border_thickness
        border_y = health_bar_y - border_thickness
        border_width = health_bar_full_width + (2 * border_thickness)
        border_height = health_bar_height + (2 * border_thickness)

        # Draw the black border
        pygame.draw.rect(screen, (0, 0, 0), (border_x, border_y, border_width, border_height), border_radius=border_radius)

        # Glow effect for the current player's turn
        if is_current_turn:
            glow_rect = pygame.Rect(health_bar_x - 2, health_bar_y - 2, health_bar_full_width + 4, health_bar_height + 4)
            pygame.draw.rect(screen, (255, 255, 0), glow_rect, border_radius=5)

        # Health bar background (gray for missing health)
        pygame.draw.rect(screen, (0, 0, 0), (health_bar_x, health_bar_y, health_bar_full_width, health_bar_height), border_radius=border_radius)

        # Health bar foreground
        if self.color == "blue":  # Blue team
            health_color = (90, 120, 200)  # Blue
        elif self.color == "red":  # Red team
            health_color = (255, 90, 90)  # Red
        else:
            health_color = (200, 0, 200)  # Default purple
        pygame.draw.rect(screen, health_color, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), border_radius=border_radius)

        # Glossy overlay on the health bar
        gloss_surface_width = max(1, int(health_bar_width * 0.85))  # Ensure at least 1 pixel width for the gloss surface
        gloss_surface = pygame.Surface((gloss_surface_width, int(health_bar_height / 3)), pygame.SRCALPHA)
        gloss_surface.fill((255, 255, 255, 150))  # Semi-transparent white with alpha
        screen.blit(gloss_surface, (health_bar_x + 1, health_bar_y + 1))

        # Draw damage text with a black boundary
        if hasattr(self, "last_damage_time") and hasattr(self, "damage_taken") and self.damage_taken > 0:
            time_passed = pygame.time.get_ticks() - self.last_damage_time

            if time_passed < 1000:  # Show for 1 second
                # Calculate alpha (opacity) and vertical position
                alpha = max(255 - (time_passed // 4), 0)  # Fade out over time
                offset_y = -time_passed // 40 + 15  # Move upward over time

                # Red flash effect on damage
                if time_passed < 200:
                    flash_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    flash_overlay.fill((255, 0, 0, 100))  # Semi-transparent red overlay
                    screen.blit(flash_overlay, rect)

                # Create the text surface with fading effect
                font = pygame.font.Font("assets/RussoOne.ttf", 18)
                text_surface = font.render(f"-{self.damage_taken}", True, (255, 0, 0))
                text_surface.set_alpha(alpha)

                # Add a black outline
                outline_surface = font.render(f"-{self.damage_taken}", True, (0, 0, 0))
                outline_surface.set_alpha(alpha)

                # Draw the outline slightly offset in each direction
                x = self.x * CELL_SIZE + CELL_SIZE // 2 - text_surface.get_width() // 2
                y = self.y * CELL_SIZE + offset_y
                for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    screen.blit(outline_surface, (x + dx, y + dy))

                # Draw the text
                screen.blit(text_surface, (x, y))
            else:
                # Clear the damage_taken attribute after animation ends
                self.damage_taken = 0
        # Draw upward arrow if buffed and duration > 0
        if self.is_buffed and self.buff_duration > 0:
            arrow_color = (0, 255, 0)  # Green arrow for buffs
            arrow_center = (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE - 10)
            pygame.draw.polygon(screen, arrow_color, [
                (arrow_center[0], arrow_center[1] - 10),  # Top point
                (arrow_center[0] - 5, arrow_center[1]),  # Bottom left
                (arrow_center[0] + 5, arrow_center[1])   # Bottom right
            ])

        # Draw downward arrow if debuffed and duration > 0
        if self.is_debuffed and self.debuff_duration > 0:
            arrow_color = (255, 0, 0)  # Red arrow for debuffs
            arrow_center = (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE + 10)
            pygame.draw.polygon(screen, arrow_color, [
                (arrow_center[0], arrow_center[1] + 10),  # Bottom point
                (arrow_center[0] - 5, arrow_center[1]),  # Top left
                (arrow_center[0] + 5, arrow_center[1])   # Top right
            ])

                
class MonsterUnit(Unit):
    def __init__(self, x, y, name, health, damage,image_path, color, move_range, attack_range, unit_type):  
        Unit.__init__(self, x, y, name, health, damage,image_path, color, move_range, attack_range, unit_type)

    def react_to_attack(self, attacker):
        if self.alive:
            # Attack the attacker (if in range)    
            if self.in_range(attacker):
                self.attack(attacker)
                