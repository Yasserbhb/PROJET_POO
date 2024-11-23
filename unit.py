import pygame
import time


CELL_SIZE = 40
class Unit:
    """A single unit in the game."""
    def __init__(self, x, y, name, image_path, color, move_range=3, attack_range=2):
        self.x = x
        self.y = y
        self.initial_x = x  # Initial position for movement range
        self.initial_y = y
        self.name = name
        self.image = pygame.image.load(image_path)
        self.color = color
        self.health = 100
        self.move_range = move_range
        self.attack_range = attack_range
        self.alive = True
        self.state = "move"  # "move" or "attack"
        self.damage_popup = None
        
        
        # Attack targeting cursor
        self.target_x = x
        self.target_y = y
        


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
                and grid.tiles[new_x][new_y].traversable):  # Traversable tile
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
            target.health -= 30  # Example damage
            if target.health <= 0:
                target.health = 0
                target.alive = False
                print(f"{target.name} has been defeated!")
        else:
            print(f"{self.name} can't attack: Target is out of range or invalid.")



    def in_range(self, target):
        """Check if the target is within attack range."""
        return abs(self.x - target.x) + abs(self.y - target.y) <= self.attack_range
    
    
    
    def draw(self, screen):
        # Draw the unit's image inside the square
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        screen.blit(pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE)), rect)

        # Health bar settings
        health_ratio = self.health / 100  # Health percentage
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

        # Health bar background (gray for missing health)
        pygame.draw.rect(
            screen,
            (125, 75, 75),  # Dark gray background
            (health_bar_x, health_bar_y, CELL_SIZE - 4, health_bar_height),
            border_radius=border_radius,
        )

        # Health bar foreground (green or purple for remaining health)
        if self.color == (0, 0, 255):  # Blue team
            health_color = (0, 200, 0)  # Green
        elif self.color == (255, 0, 0):  # Red team
            health_color = (150, 0, 150)  # Purple
        else:
            health_color = (200, 200, 200)  # Default white
        pygame.draw.rect(
            screen,
            health_color,
            (health_bar_x, health_bar_y, health_bar_width, health_bar_height),
            border_radius=border_radius,
        )
        # Draw 20 HP markers
        segment_size = 20  # Size of each HP segment
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


