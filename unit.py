import pygame


CELL_SIZE = 40
class Unit:
    """A single unit in the game."""
    def __init__(self, x, y, name, health, damage,image_path, color, move_range, attack_range, unit_type):
        self.x = x
        self.y = y
        self.initial_x = x  # Initial position for movement range
        self.initial_y = y
        self.name = name
        self.image = pygame.image.load(image_path)
        self.color = color
        self.health = health
        self.max_health = health
        self.move_range = move_range
        self.attack_range = attack_range
        self.damage=damage
        self.unit_type=unit_type   #player or neutral or base_blue or base_red
        self.alive = True
        self.state = "move"  # "move" or "attack"

        # Attack targeting cursor
        self.target_x = x
        self.target_y = y

        # Initialize for damage display
        self.last_damage_time = None 
        self.damage_taken = 0 

        

    def in_range(self, target):
        """Check if the target is within attack range."""
        return abs(self.x - target.x) + abs(self.y - target.y) <= self.attack_range



    def move(self, dx, dy, grid):
        """Move the unit if within movement range and traversable."""
        new_x = self.x + dx
        new_y = self.y + dy
        distance = abs(self.initial_x - new_x) + abs(self.initial_y - new_y)

        if (0 <= new_x < len(grid.tiles) and 0 <= new_y < len(grid.tiles[0])  # Ensure within bounds
                and distance <= self.move_range  # Within movement range
                and grid.tiles[new_x][new_y].traversable) :  # Traversable tile
            self.x, self.y = new_x, new_y  # Update position



    #neutral monsters reacting to attacks
    def react_to_attack(self, attacker):
        """Define the behavior when this unit is attacked.""" 
        if self.unit_type == "monster" and self.alive:
            print(f"{self.name} reacts to {attacker.name}'s attack!")

            # Attack the attacker (if in range)    
            if self.in_range(attacker):
                print(f"{self.name} counterattacks {attacker.name}!")
                attacker.health -= int(attacker.max_health * 0.2)
                attacker.damage_taken =int(attacker.max_health * 0.2) 
                attacker.last_damage_time = pygame.time.get_ticks()

                if attacker.health <= 0:
                    attacker.alive = False
                    print(f"{attacker.name} has been defeated by {self.name}!")



    def attack(self, target):

        print(f"{self.name} attacks {target.name}!")
        target.health -= self.damage  
        target.damage_taken = self.damage 
        target.last_damage_time = pygame.time.get_ticks() 

        if target.unit_type == "monster":
            #pygame.time.wait(100)  # Add a delay
            target.react_to_attack(self)  # Trigger monster reaction

        if target.health <= 0:
            target.health = 0
            target.alive = False
            print(f"{target.name} has been defeated!")
        return self.damage

    
    
    def draw(self, screen, is_current_turn):
        # Draw the unit's image inside the square
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        screen.blit(pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE)), rect)

        # Health bar settings
        health_ratio = self.health / self.max_health  # Health percentage
        health_bar_full_width = int (CELL_SIZE*0.95)  # width of the full bar not just the health part
        health_bar_width = int(CELL_SIZE * health_ratio * 0.95)  # Width of the health bar
        health_bar_height = 7  # Height of the health bar
        health_bar_x = rect.x + 2  # Margin from the left
        health_bar_y = rect.y + 2  # Margin from the top
        border_radius = 3  # Rounded corners
        
        # Border settings
        border_thickness = 1  # Thickness of the border
        border_x = health_bar_x - border_thickness
        border_y = health_bar_y - border_thickness
        border_width = health_bar_width/health_ratio + (2 * border_thickness)
        border_height = health_bar_height + (2 * border_thickness)

        # Draw the black border
        pygame.draw.rect(screen,(0, 0, 0), (border_x, border_y, border_width, border_height),border_radius)

        # Glow effect for the current player's turn
        if is_current_turn:
            glow_rect = pygame.Rect(health_bar_x - 2, health_bar_y - 2, health_bar_full_width + 4, health_bar_height + 4)
            pygame.draw.rect(screen, (255, 255, 0), glow_rect, border_radius=5)

        # Health bar background (gray for missing health)
        pygame.draw.rect(screen, (0, 0, 0), (health_bar_x, health_bar_y, CELL_SIZE - 4, health_bar_height), border_radius)

        # Health bar foreground (green or purple for remaining health)
        if self.color == "blue":  # Blue team
            health_color = (90, 120, 200)  # Blue
        elif self.color == "red":  # Red team
            health_color = (255, 90, 90)  # Red
        else:
            health_color = (200, 0 , 200)  # Default purple
        pygame.draw.rect(screen, health_color, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), border_radius)

        # Draw 40 HP markers
        segment_size = 100  # Size of each HP segment
        num_segments = self.health // segment_size  # Calculate the number of markers

        for i in range(1, num_segments):
            marker_x = health_bar_x + (health_bar_width * i / num_segments)  # Proportional spacing
            pygame.draw.line( screen, (0, 0, 0), (marker_x, health_bar_y), (marker_x, health_bar_y + health_bar_height), 1 )

        # Glossy overlay on the health bar
        gloss_surface = pygame.Surface((health_bar_width*0.85, int(health_bar_height / 3)), pygame.SRCALPHA)
        gloss_surface.fill((255, 255, 255, 150))  # Semi-transparent white with alpha 50
        screen.blit(gloss_surface, (health_bar_x+1, health_bar_y+1))

        # Draw damage text with a black boundary
        if hasattr(self, "last_damage_time") and hasattr(self, "damage_taken") and self.damage_taken > 0:
            time_passed = pygame.time.get_ticks() - self.last_damage_time

            if time_passed < 1000:  # Show for 1 second
                # Calculate alpha (opacity) and vertical position
                alpha = max(255 - (time_passed // 4), 0)  # Fade out over time
                offset_y = -time_passed // 40 + 15 # Move upward over time
                # Red flash effect on damage
                if time_passed < 200 :
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


                


