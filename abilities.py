import pygame


class Abilities:
    def __init__(self, name, mana_cost, cooldown, ability_type, attack=0, defense=0, description="",attack_radius=3,is_aoe=False):
        self.name = name
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.remaining_cooldown = 0
        self.ability_type = ability_type
        self.attack = attack
        self.defense = defense
        self.description = description
        self.attack_radius=attack_radius
        self.is_aoe = is_aoe

    def get_targets_in_aoe(self, user, units):
        """
        Retourne toutes les cibles valides dans la zone AoE (ennemis et monstres uniquement).
        """
        aoe_targets = []
        for unit in units:  # Parcourt toutes les unités sur la grille
            if unit.alive:
                distance = abs(unit.x - user.x) + abs(unit.y - user.y)
                if distance <= self.attack_radius and unit.color != user.color:  # Exclut les alliés
                    aoe_targets.append(unit)
        return aoe_targets
    
    def use(self, user, target, grid):
        """
        Execute the ability. Supports AoE if `is_aoe` is True.
        :param user: Unit using the ability.
        :param targets: List of targets.
        :param grid: Grid object to calculate AoE range.
        """
        if user.mana < self.mana_cost:
            print(f"Not enough mana to use {self.name}.")
            return False
        if self.remaining_cooldown > 0:
            print(f"{self.name} is on cooldown.")
            return False

        if self.is_aoe:
            # Get all targets in the AoE range
            aoe_targets = self.get_targets_in_aoe(user, grid)
            if not aoe_targets:
                print(f"No targets in range for {self.name}.")
                return False

            print(f"{user.name} uses {self.name} on multiple targets!")
            for target in aoe_targets:
                self.apply_effect(user, target)

        else:
            print(f"No valid target for {self.name}.")
            return False

        # Deduct mana and apply cooldown
        user.mana -= self.mana_cost
        self.remaining_cooldown = self.cooldown
        return True



    def apply_effect(self, user, target):
        """Apply the ability's effect to the target."""
        if target is None:
            print("No valid target to apply effect.")
            return
        
        if self.ability_type == "damage" and user.color != target.color:
            print(f"{target.name} takes {self.attack} damage!")
            target.health -= self.attack
            if target.health <= 0:
                target.alive = False
                print(f"{target.name} est éliminé !")
        elif self.ability_type == "heal" and user.color == target.color:
            heal_amount = min(target.max_health - target.health, self.attack)
            print(f"{target.name} is healed by {heal_amount} health!")
            target.health += heal_amount

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