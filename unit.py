import pygame

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

    def move(self, dx, dy, grid):
        """Move the unit if within movement range and traversable."""
        if self.state != "move":
            print(f"{self.name} cannot move: Already moved this turn.")
            return

        new_x = self.x + dx
        new_y = self.y + dy
        distance = abs(self.initial_x - new_x) + abs(self.initial_y - new_y)

        if (0 <= new_x < len(grid) and 0 <= new_y < len(grid[0])  # Ensure within bounds
                and distance <= self.move_range  # Within movement range
                and grid[new_x][new_y].traversable):  # Traversable tile
            self.x, self.y = new_x, new_y  # Update position
            print(f"{self.name} moved to ({self.x}, {self.y}).")
        else:
            print("Invalid move: Out of range or not traversable.")

    def attack(self, target):
        """Attack a target unit within range."""
        if self.state != "attack":
            print(f"{self.name} cannot attack: You must move first.")
            return

        if target and self.in_range(target):
            print(f"{self.name} attacks {target.name}!")
            target.health -= 20  # Example damage
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
        """Draw the unit on the screen."""
        rect = pygame.Rect(self.x * 40, self.y * 40, 40, 40)  # Adjust size
        screen.blit(pygame.transform.scale(self.image, (40, 40)), rect)


        # Draw health bar
        health_ratio = self.health / 100
        health_bar_width = int(40 * health_ratio)
        pygame.draw.rect(screen, (255, 0, 0), (self.x * 40, self.y * 40 - 10, 40, 5))  # Red bar
        pygame.draw.rect(screen, (0, 255, 0), (self.x * 40, self.y * 40 - 10, health_bar_width, 5))  # Green bar
