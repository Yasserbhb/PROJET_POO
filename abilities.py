import pygame


class Abilities:
    def __init__(self, name, mana_cost, cooldown, ability_type, attack=0, defense=0, description="", attack_radius=0):
        self.name = name
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.remaining_cooldown = 0
        self.ability_type = ability_type
        self.attack = attack
        self.defense = defense
        self.description = description
        self.attack_radius = attack_radius

    def use(self, user, target=None):
        if self.ability_type in ["damage", "heal"] and not target:
            print(f"No valid target for {self.name}.")
            return False
        if user.mana < self.mana_cost:
            print(f"Not enough mana to use {self.name}.")
            return False
        if self.remaining_cooldown > 0:
            print(f"{self.name} is on cooldown.")
            return False

        # Prevent friendly fire for damage abilities
        if self.ability_type == "damage" and target and user.color == target.color:
            print(f"{self.name} cannot be used on a teammate!")
            return False
        
        # Apply effects based on ability type
        if self.ability_type == "damage" and target:
            print(f"{user.name} uses {self.name} on {target.name}, dealing {self.attack} damage!")
            target.health -= self.attack
            if target.health <= 0:
                target.health = 0
                target.alive = False  # Mark the target as dead
        elif self.ability_type == "heal" and target:
            print(f"{user.name} uses {self.name}, healing {self.attack} health!")
            target.health = min(target.max_health, target.health + self.attack)
        elif self.ability_type == "buff":
            print(f"{user.name} uses {self.name}, gaining {self.defense} defense!")
            user.damage += self.defense

        # Deduct mana and apply cooldown
        user.mana -= self.mana_cost
        self.remaining_cooldown = self.cooldown
        return True


    def reduce_cooldown(self):
        """
        Réduit le cooldown de l'ability à chaque tour.
        """
        if self.remaining_cooldown > 0:
            self.remaining_cooldown -= 1  # Réduit de 1 à chaque tour
            if self.remaining_cooldown < 0:
                self.remaining_cooldown = 0  # Assure que le cooldown ne soit pas négatif
                
class BuffAbility(Abilities):
    def __init__(self, name, mana_cost, cooldown, attack=0, defense=0, description="", duration=3, attack_radius=1):
        # Call the parent constructor with "buff" as the ability type
        super().__init__(name, mana_cost, cooldown, "buff", attack=attack, defense=defense, description=description, attack_radius=attack_radius)
        self.duration = duration  # Number of turns the buff lasts
        self.remaining_duration = 0
        self.attack_radius = attack_radius  # Add the attack radius here

    def use(self, user, target=None):
        if self.remaining_cooldown > 0:
            print(f"{self.name} is on cooldown!")
            return False

        target = target or user  
        if target.color != user.color:  # Si la cible est un ennemi
            print(f"{self.name}: You cannot use this ability on an enemy!")
            return False
        
        if self.attack:
            target.attack += self.attack
        if self.defense:
            target.defense += self.defense

        target.is_buffed = True 
        if target.buff_duration == 0: 
            target.buff_duration = 3 

        print(f"{self.name}: {target.name} is buffed for 3 turns!")
        user.mana -= self.mana_cost
        self.remaining_cooldown = self.cooldown
        return True
    
class DebuffAbility(Abilities):
    def __init__(self, name, mana_cost, cooldown, attack=0, defense=0, description="", duration=3, attack_radius=1):
        # Call the parent constructor with "debuff" as the ability type
        super().__init__(name, mana_cost, cooldown, "debuff", attack=attack, defense=defense, description=description, attack_radius=attack_radius)
        self.duration = duration  # Number of turns the debuff lasts
        self.remaining_duration = 0
        self.attack_radius = attack_radius  # Add the attack radius here

    def use(self, user, target=None):
        if self.remaining_cooldown > 0:
            print(f"{self.name} is on cooldown!")
            return False

        if target is None:
            print(f"{self.name}: No valid target to debuff!")
            return False
        
        if target.color == user.color:
            print(f"{self.name}: You cannot use this on an ally!")
            return False

        if self.attack:
            target.attack -= self.attack
        if self.defense:
            target.defense -= self.defense

        target.is_debuffed = True
        if target.debuff_duration == 0:  
            target.debuff_duration = 3  

        print(f"{self.name}: {target.name} is debuffed for 3 turns!")
        user.mana -= self.mana_cost
        self.remaining_cooldown = self.cooldown
        return True
