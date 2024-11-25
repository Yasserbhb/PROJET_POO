import pygame

class Abilities:
    def __init__(self, name, mana_cost, cooldown, ability_type, range_of_damage=0, attack=0, defense=0, description=""):
        """
        :param name: Nom de l'ability.
        :param mana_cost: Coût en mana pour utiliser l'ability.
        :param cooldown: Temps de recharge en secondes.
        :param ability_type: Type de l'ability ('heal', 'damage', 'buff', 'debuff').
        :param range_of_damage: Dommages infligés dans une zone (pour les abilities AoE).
        :param attack: Dommages infligés à une cible unique.
        :param defense: Bouclier ou défense ajoutée.
        :param description: Description de l'ability.
        "buff" Il améliore temporairement ses statistiques ou lui accorde des capacités supplémentaires.
        "debuff" Il affaiblit temporairement les statistiques ou handicape les actions de la cible(ennemmis)
        """
        self.name = name
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.ability_type = ability_type
        self.range_of_damage = range_of_damage
        self.attack = attack
        self.defense = defense
        self.description = description
        self.remaining_cooldown = 0  # Cooldown restant en secondes.temps resetant avant de pouvoir utiliser l'abilities

    def use(self, user, target=None):
        """
        Utilise l'ability si les conditions sont remplies.

        :param user: L'utilisateur de l'ability.
        :param target: La cible de l'ability (None pour certaines abilities).
        """
        if self.remaining_cooldown > 0:
            print(f"{self.name} est en recharge ({self.remaining_cooldown}s restantes).")
            return False
        
        if user.mana < self.mana_cost:
            print(f"{user.name} n'a pas assez de mana pour utiliser {self.name}. Mana actuel : {user.mana}.")
            return False

        # Déduire le mana et activer l'effet
        user.mana -= self.mana_cost
        self.remaining_cooldown = self.cooldown
        print(f"{user.name} utilise {self.name}!")

        # Appliquer l'effet de l'ability en fonction de son type
        if self.ability_type == "damage":
            if target:
                target.health -= self.attack
                print(f"{target.name} subit {self.attack} dégâts.")
        elif self.ability_type == "heal":
            if target:
                target.health = min(target.max_health, target.health + self.attack)
                print(f"{target.name} est soigné de {self.attack} points de vie.")
        elif self.ability_type == "buff":
            user.defense += self.defense
            print(f"{user.name} gagne {self.defense} points de défense.")
        elif self.ability_type == "debuff":
            if target:
                target.attack -= self.attack
                print(f"{target.name} perd {self.attack} points d'attaque.")
        elif self.ability_type == "aoe":
            if target:  # Target peut être une liste dans ce cas
                for enemy in target:
                    enemy.health -= self.range_of_damage
                    print(f"{enemy.name} subit {self.range_of_damage} dégâts AoE.")
        return True

    def reduce_cooldown(self, time_passed):
        """
        Réduit le cooldown de l'ability en fonction du temps écoulé.

        :param time_passed: Temps écoulé en secondes.
        """
        if self.remaining_cooldown > 0:
            self.remaining_cooldown = max(0, self.remaining_cooldown - time_passed)
