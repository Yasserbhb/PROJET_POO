import pygame
from interface import Highlight

class Abilities:
    def __init__(self, name, mana_cost, cooldown, ability_type, attack=0, defense=0, description="",attack_radius=3,is_aoe=0):
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
        self.event_log = [] # Initialize event log



    def use(self, user, targets):
        """
        Execute the ability. Supports AoE if `is_aoe` is True.
        :param user: Unit using the ability.
        :param targets: List of targets.
        :param grid: Grid object to calculate AoE range.
        """
        if user.mana < self.mana_cost:
            Highlight.log_event(self,f"Not enough mana to use {self.name}.")
            return False
        if self.remaining_cooldown > 0:
            Highlight.log_event(self,f"{self.name} is on cooldown.")
            return False

        

        Highlight.log_event(self,f"{user.name} uses {self.name} on multiple targets!")
        if self.is_aoe>0:
            for target in targets:
                self.apply_effect(user, target)
                print(target.name)
        else :
            self.apply_effect(user, targets)
            Highlight.log_event(self,targets.name)

        

        # Deduct mana and apply cooldown
        user.mana -= self.mana_cost
        self.remaining_cooldown = self.cooldown
        return True
    def get_targets_in_aoe(self, user, units):
        """Get all units within AoE radius."""
        aoe_targets = []
        for unit in units:
            if unit.alive and unit!=user:
                distance = abs(unit.x - user.target_x) + abs(unit.y - user.target_y)
                if distance <= self.is_aoe:
                    aoe_targets.append(unit)
        return aoe_targets

    def apply_effect(self, user, target):
        """Apply the ability's effect to the target."""
        if target is None:
            Highlight.log_event(self,"No valid target to apply effect.")
            return
        
        if self.ability_type == "damage" and user.color != target.color:
            Highlight.log_event(self,f"{target.name} takes {self.attack} damage!")
            user.attack(target, self.attack)
        elif self.ability_type == "heal" and user.color == target.color:
            heal_amount = min(target.max_health - target.health, self.attack)
            Highlight.log_event(self,f"{target.name} is healed by {heal_amount} health!")
            user.attack(target, -heal_amount)

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
            Highlight.log_event(self,f"{self.name} is on cooldown!")
            return False

        target = target or user  
        if target.color != user.color:  # Si la cible est un ennemi
            Highlight.log_event(self,f"{self.name}: You cannot use this ability on an enemy!")
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
            Highlight.log_event(self,f"{target.name} is already buffed")
            return False
   

        Highlight.log_event(self,f"{self.name}: {target.name} is buffed for 5 turns!")
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
            Highlight.log_event(self,f"{self.name}: You cannot use this on an ally!")
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
            Highlight.log_event(self,f"{target.name} is already debuffed")
            return False


        Highlight.log_event(self,f"{self.name}: {target.name} is debuffed for 5 turns!")
        user.mana -= self.mana_cost
        self.remaining_cooldown = self.cooldown
        return True

#using inheretence : vision ability teleport ability
#for buffs : crit and attack range(lasts long)
#make some of the abilities AOE