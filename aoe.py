import pygame
import random 

from abilities import Abilities

class AOEAbility(Abilities):
    def __init__(self, name, mana_cost, cooldown, attack=0, defense=0, description="", attack_radius=2):
        super().__init__(name, mana_cost, cooldown, "aoe", attack=attack, defense=defense, description=description, attack_radius=attack_radius)

    def use(self, user, grid, units):
        if user.mana < self.mana_cost:
            print(f"Not enough mana to use {self.name}.")
            return False

        if self.remaining_cooldown > 0:
            print(f"{self.name} is on cooldown.")
            return False

        # Get all tiles in the AOE radius
        affected_tiles = self.get_aoe_tiles(user.x, user.y, self.attack_radius, grid)

        # Apply effect to all units in the affected tiles
        for tile in affected_tiles:
            for unit in units:
                if unit.x == tile[0] and unit.y == tile[1]:
                    if self.attack > 0:  # Damage ability
                        user.attack(unit, self.attack)
                    elif self.defense > 0:  # Buff/defense ability
                        unit.defense += self.defense
                        print(f"{unit.name} gains {self.defense} defense from {self.name}.")

        # Deduct mana and apply cooldown
        user.mana -= self.mana_cost
        self.remaining_cooldown = self.cooldown
        print(f"{user.name} uses {self.name}, affecting an area!")
        return True
    
    def get_aoe_tiles(self, x, y, radius, grid):
        tiles = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if 0 <= x + dx < len(grid.tiles) and 0 <= y + dy < len(grid.tiles[0]) and abs(dx) + abs(dy) <= radius:
                    tiles.append((x + dx, y + dy))
        return tiles