import pygame
import time
import os

CELL_SIZE = 40
class Unit:
    """A single unit in the game."""
    def __init__(self, x, y, name, health, damage,image_path, color, move_range=3, attack_range=2):
        self.x = x
        self.y = y
        self.initial_x = x  # Initial position for movement range
        self.initial_y = y
        self.name = name
        if not isinstance(image_path, str):
            raise TypeError(f"Expected a string for image_path, got {type(image_path)}")
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image not found at path: {image_path}")
        self.image = pygame.image.load(image_path)
        self.color = color
        self.health = health
        self.max_health = health
        self.move_range = move_range
        self.attack_range = attack_range
        self.damage=damage
        self.alive = True
        self.state = "move"  # "move" or "attack"
        
        
        
        # Attack targeting cursor
        self.target_x = x
        self.target_y = y

        # Initialize for damage display
        self.last_damage_time = None ####################################################""""
        self.damage_taken = 0 #####################################################""""

        


    def in_range(self, target):
        """Check if the target is within attack range."""
        return abs(self.x - target.x) + abs(self.y - target.y) <= self.attack_range



    def move(self, dx, dy, grid):
        """Move the unit if within movement range and traversable."""
        if self.state != "move":
            print(f"{self.name} cannot move: Already moved this turn.")
            return
        new_x = self.x + dx
        new_y = self.y + dy
        distance = abs(self.initial_x - new_x) + abs(self.initial_y - new_y)

        if (0 <= new_x < len(grid.tiles) and 0 <= new_y < len(grid.tiles[0])  # Ensure within bounds
                and distance <= self.move_range  # Within movement range
                and grid.tiles[new_x][new_y].traversable) :  # Traversable tile
            self.x, self.y = new_x, new_y  # Update position
                      
            #print(f"{self.name} moved to ({self.x}, {self.y}).")
       # else:
            #print("Invalid move: Out of range or not traversable.")



    def attack(self, target):
        """Attack a target unit within range."""
        if self.state != "attack":
            print(f"{self.name} cannot attack: You must move first.")
            return

        if target and self.in_range(target):
            print(f"{self.name} attacks {target.name}!")
            
            target.health -= self.damage  # Example damage
            target.damage_taken = self.damage  #############################################""""""
            target.last_damage_time = pygame.time.get_ticks() 
            if target.health <= 0:
                target.health = 0
                target.alive = False
                print(f"{target.name} has been defeated!")
        else:
            print(f"{self.name} can't attack: Target is out of range or invalid.")



    def in_range(self, target):
        """Check if the target is within attack range."""
        return abs(self.x - target.x) + abs(self.y - target.y) <= self.attack_range
    
    
    
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
        pygame.draw.rect(
            screen,
            (0, 0, 0),  # Black color for the border
            (border_x, border_y, border_width, border_height),
            border_radius=border_radius,
        )

        # Glow effect for the current player's turn
        if is_current_turn:
            glow_rect = pygame.Rect(
                health_bar_x - 2,  # Slightly larger than the health bar
                health_bar_y - 2,
                health_bar_full_width + 4,
                health_bar_height + 4
            )
            pygame.draw.rect(
                screen,
                (255, 255, 0),  # Yellow glow color
                glow_rect,
                border_radius=5  # Rounded corners
            )

        # Health bar background (gray for missing health)
        pygame.draw.rect(
            screen,
            (0, 0, 0),  # Dark gray background
            (health_bar_x, health_bar_y, CELL_SIZE - 4, health_bar_height),
            border_radius=border_radius,
        )

        # Health bar foreground (green or purple for remaining health)
        if self.color == (0, 0, 255):  # Blue team
            health_color = (90, 120, 200)  # Blue
        elif self.color == (255, 0, 0):  # Red team
            health_color = (255, 90, 90)  # Red
        else:
            health_color = (200, 0 , 200)  # Default white
        pygame.draw.rect(
            screen,
            health_color,
            (health_bar_x, health_bar_y, health_bar_width, health_bar_height),
            border_radius=border_radius,
        )



        # Draw 40 HP markers
        segment_size = 100  # Size of each HP segment
        num_segments = self.health // segment_size  # Calculate the number of markers

        for i in range(1, num_segments):
            marker_x = health_bar_x + (health_bar_width * i / num_segments)  # Proportional spacing
            pygame.draw.line(
                screen,
                (0, 0, 0),  # Black lines for markers
                (marker_x, health_bar_y),
                (marker_x, health_bar_y + health_bar_height),
                1,  # Line thickness
            )

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
                offset_y = -time_passed // 30 + 25 # Move upward over time

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


                

