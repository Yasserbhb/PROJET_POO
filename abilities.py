import pygame


class Abilities:
    def __init__(self, name, mana_cost, cooldown, ability_type, attack=0, defense=0, description="",attack_radius=3):
        self.name = name
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.remaining_cooldown = 0
        self.ability_type = ability_type
        self.attack = attack
        self.defense = defense
        self.description = description
        self.attack_radius=attack_radius


    def use(self, user, target=None):
        if self.ability_type in ["damage", "heal"] and not target:
            print(f"No valid target for {self.name}.")
            user.mana -= self.mana_cost
            self.remaining_cooldown = self.cooldown
            return True
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
            user.attack(target,self.attack+user.damage)

        elif self.ability_type == "heal" and target:
            print(f"{user.name} uses {self.name}, healing {self.attack} health!")
            user.attack(target,-min(target.max_health-target.health, self.attack+user.damage))


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
    def __init__(self, name, mana_cost, cooldown, attack=0, defense=0, description="", duration=8,attack_radius=1):
        # Call the parent constructor with "buff" as the ability type
        super().__init__(name, mana_cost, cooldown, "buff", attack=attack, defense=defense, description=description,attack_radius=attack_radius)
        self.duration = duration  # Number of turns the buff lasts
        self.remaining_cooldown = 0

    def use(self, user, target=None):
        if self.remaining_cooldown > 0:
            print(f"{self.name} is on cooldown!")
            return False

        target = target or user  
        if target.color != user.color:  # Si la cible est un ennemi
            print(f"{self.name}: You cannot use this ability on an enemy!")
            return False
        if not target.is_buffed :
            if self.attack:
                target.damage += self.attack
                target.buffed_attack_increase = self.attack  # Track the increase
            if self.defense:
                target.defense += self.defense
                target.buffed_defense_increase = self.defense  # Track the increase
            target.is_buffed=True
            target.buff_duration = self.duration 
        else :
            print(f"{target.name} is already buffed")
            return False
        



        print(f"{self.name}: {target.name} is buffed for 5 turns!")
        user.mana -= self.mana_cost
        self.remaining_cooldown = self.cooldown
        return True
    


    
class DebuffAbility(Abilities):
    def __init__(self, name, mana_cost, cooldown, attack=0, defense=0, description="", duration=8,attack_radius=1):
        # Call the parent constructor with "debuff" as the ability type
        super().__init__(name, mana_cost, cooldown, "debuff", attack=attack, defense=defense, description=description,attack_radius=attack_radius)
        self.duration = duration  # Number of turns the debuff lasts


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
        
        if not target.is_debuffed:
            if self.attack:
                target.damage -= self.attack
                target.debuffed_attack_reduction = self.attack  # Track the reduction
            if self.defense:
                target.defense -= self.defense
                target.debuffed_defense_reduction = self.defense  # Track the reduction
            target.is_debuffed=True
            target.debuff_duration = self.duration
        else:
            print(f"{target.name} is already debuffed")
            return False


        print(f"{self.name}: {target.name} is debuffed for 5 turns!")
        user.mana -= self.mana_cost
        self.remaining_cooldown = self.cooldown
        return True
    
#using inheretence : vision ability teleport ability
#for buffs : crit and attack range(lasts long)
#make some of the abilities AOE