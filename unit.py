class Unit:
    """A single unit in the game."""
    def __init__(self, x, y, name, color):
        self.x = x
        self.y = y
        self.name = name
        self.color = color
        self.health = 100  # Default health

    def move(self, dx, dy, grid):
        """Move the unit if the target cell is traversable."""
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < len(grid) and 0 <= new_y < len(grid[0]):  # Ensure within bounds
            if grid[new_x][new_y].traversable:
                self.x, self.y = new_x, new_y  # Update position
                print(f"{self.name} moved to ({self.x}, {self.y}).")
            else:
                print("Cannot move: Tile is not traversable.")
        else:
            print("Cannot move: Out of bounds.")
