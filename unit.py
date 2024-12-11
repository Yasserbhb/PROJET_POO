import pygame
import random
from abilities import Abilities,BuffAbility,DebuffAbility
from sounds import *


CELL_SIZE = 35
class Unit:
    """A single unit in the game."""
    def __init__(self, x, y, name, health, damage,defense,crit_chance,image_path, color, move_range, attack_range, unit_type, mana=100, abilities=None):
        self.x = x
        self.y = y
        self.initial_x = x  # Initial position for movement range
        self.initial_y = y
        self.name = name
        self.image = pygame.image.load(image_path)
        self.color = color
        self.health = health
        self.max_health = health
        self.defense=defense
        self.damage=damage
        self.crit_chance=crit_chance
        self.mana = mana
        self.max_mana = mana
        self.move_range = move_range
        self.attack_range = attack_range
        self.unit_type=unit_type   #player or neutral or base_blue or base_red
        self.alive = True
        self.state = "move"  # "move" or "attack"
        self.selected_ability = None  # Currently selected ability

        # Attack targeting cursor
        self.target_x = x
        self.target_y = y
        self.abilities = abilities if abilities else []  # Default to an empty list if no abilities are provided


        # Buff and debuff trackers
        self.buffed_damage_increase = 0
        self.buffed_defense_increase = 0
        self.debuffed_attack_reduction = 0
        self.debuffed_defense_reduction = 0
        self.buff_duration = 0
        self.debuff_duration = 0
        self.is_buffed = False
        self.is_debuffed = False

        # Add key variables
        self.red_keys = 0  # Number of red keys this unit holds
        self.blue_keys = 0  # Number of blue keys this unit holds

        # Initialize for damage display
        self.last_damage_time = None 
        self.damage_taken = 0 
        #self.sound=Sounds()



    def create_units(self):
        """Create units and place them on the grid."""       
        return [            
            Unit(3,15, "Garen", 900, 99,0,50, self.unit_images["garen"], None,3,2,"player", mana=120, abilities=[
                Abilities("Slash", 30, 5, "damage", attack=900, description="A quick slash attack.",attack_radius=3),
                BuffAbility("Fortify", 20, 14, defense=50, description="Increases defense temporarily for 3 turns.",attack_radius=8),
                Abilities("Charge", 40, 8, "damage", attack=300, description="A powerful charging attack that stuns the target.",attack_radius=2),
            ]),  
            Unit(4,16, "Ashe", 500, 70,100,50 ,self.unit_images["ashe"], None,3,2,"player", mana=100, abilities=[
                Abilities("Arrow Shot", 20, 5, "damage", attack=150, description="Shoots an arrow at the target."),
                DebuffAbility("Frost Arrow", 30, 10, attack=20, defense=10, description="Slows and weakens the target."),
                BuffAbility("Healing Wind", 50, 15, defense=20, description="Restores health to an ally and grants temporary defense."),
            ]),  
            Unit(15,3, "Darius",700, 90,0,50,self.unit_images["darius"], None,3,2,"player", mana=120, abilities=[
                Abilities("Decimate", 50, 7, "damage", attack=250, description="Spins his axe, dealing damage to nearby enemies."),
                DebuffAbility("Crippling Strike", 40, 8, attack=30, defense=10, description="A heavy strike that slows and weakens the target."),
                Abilities("Noxian Guillotine", 80, 15, "damage", attack=400, description="Executes an enemy with low health."),
            ]), 
            Unit(16,4, "Soraka",490, 50 ,0,50,self.unit_images["soraka"], None,3,2,"player", mana=250, abilities=[
                Abilities("Starcall", 30, 5, "damage", attack=50, description="Calls a star down, dealing magic damage."),
                Abilities("Astral Infusion", 40, 8, "heal", attack=100, description="Sacrifices own health to heal an ally."),
                BuffAbility("Wish", 100, 20, defense=30, description="Restores health to all allies and grants defense for 3 turns."),
            ]),  
            Unit(0,0, "Rengar",700, 180 ,0,50,self.unit_images["rengar"], None,3,2,"player", mana=120, abilities=[
                Abilities("Savagery", 30, 5, "damage", attack=300, description="Empowered strike dealing extra damage."),
                BuffAbility("Battle Roar", 40, 8, defense=40, description="Boosts defense and regenerates health."),
                DebuffAbility("Thrill of the Hunt", 80, 20, attack=20, description="Tracks the enemy, reducing their attack temporarily."),
            ]),  


            MonsterUnit(10, 10, "BigBuff",1000, 50 ,0,0,self.unit_images["bigbuff"], "neutral",3,2,"monster"),  #neutral monster
            MonsterUnit(1, 13, "BlueBuff",390, 250 ,0,0,self.unit_images["bluebuff"], "neutral",3,2,"monster"),  #neutral monster
            MonsterUnit(15, 13, "RedBuff",390, 250 ,0,0,self.unit_images["redbuff"], "neutral",3,2,"monster"), #neutral monster

            Unit(1, 19, "NexusBlue",390, 50 ,0,0,self.unit_images["baseblue"], "blue",0,0,"base"),  #Blue team base
            Unit(19, 1, "NexusRed",390, 50 ,0,0,self.unit_images["basered"], "red",0,0,"base"), #Red team base
       ]



    def in_range(self, target):
        """Check if the target is within attack range."""
        return abs(self.x - target.x) + abs(self.y - target.y) <= self.attack_range



    def move(self, dx, dy, grid):
    
        """Move the unit if within movement range, traversable, and highlighted."""
        new_x = self.x + dx
        new_y = self.y + dy

        # Check if the current position is within grid bounds
        if 0 <= new_x < len(grid.tiles) and 0 <= new_y < len(grid.tiles[0]):

            # Get the target tile at the new position
            target_tile = grid.tiles[new_x][new_y]

            # Check if the target tile is highlighted
            if not target_tile.highlighted:
                print(f"Cannot move to ({new_x}, {new_y}) because it's not highlighted.")
                return  # Can't move if the tile is not highlighted
            else : 
                self.x, self.y = new_x, new_y
                



    #neutral monsters reacting to attacks
    def react_to_attack(self, attacker):
        return

    def attack(self, target,damage):
        multiplyer=1
        if random.randint(1, 100) <= self.crit_chance:
            multiplyer = 2  # Double the damage for critical hit
        print(f"{self.name} attacks {target.name}!")
        damage_after_def=int(damage*multiplyer*(1-target.defense/(target.defense+100)))
        target.health -= damage_after_def  
        target.damage_taken = damage_after_def 
        target.last_damage_time = pygame.time.get_ticks() 
        if target.health <= 0:
            target.health = 0
            target.alive = False
        target.react_to_attack(self)  # Trigger monster reaction
        return damage_after_def
    
    def update_buffs_and_debuffs(self):
            # Handle buffs
            if self.buff_duration > 0:
                self.buff_duration -= 1
                if self.buff_duration == 0:
                    print(f"{self.name}'s buff has expired.")
                    self.revert_buff()

            # Handle debuffs
            if self.debuff_duration > 0:
                self.debuff_duration -= 1
                if self.debuff_duration == 0:
                    print(f"{self.name}'s debuff has expired.")
                    self.revert_debuff()

    def revert_buff(self):
        # Revert buff effects
        self.damage -= self.buffed_damage_increase
        self.defense -= self.buffed_defense_increase
        self.buffed_damage_increase = 0
        self.buffed_defense_increase = 0
        self.is_buffed = False
        print(f"{self.name}'s stats after buff ended: Damage: {self.damage}, Defense: {self.defense}")

    def revert_debuff(self):
        # Revert debuff effects
        self.damage += self.debuffed_attack_reduction
        self.defense += self.debuffed_defense_reduction
        self.debuffed_attack_reduction = 0
        self.debuffed_defense_reduction = 0
        self.is_debuffed = False
        print(f"{self.name}'s stats after debuff ended: Damage: {self.damage}, Defense: {self.defense}")



    def draw(self, screen, is_current_turn):
        # Draw the unit's image inside the square
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        screen.blit(pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE)), rect)

        # Health bar settings
        health_ratio = self.health / self.max_health  # Health percentage
        health_bar_full_width = int (CELL_SIZE*0.95)  # width of the full bar not just the health part
        health_bar_width = int(CELL_SIZE * health_ratio * 0.95)  # Width of the health bar
        health_bar_height = 7  # Height of the health bar
        health_bar_x = self.x * CELL_SIZE + 2  # Margin from the left
        health_bar_y = self.y * CELL_SIZE + 2  # Margin from the top
        border_radius = 3  # Rounded corners
        
        # Border settings
        border_thickness = 1  # Thickness of the border
        border_x = health_bar_x - border_thickness
        border_y = health_bar_y - border_thickness
        border_width = health_bar_width/health_ratio + (2 * border_thickness)
        border_height = health_bar_height + (2 * border_thickness)

        # Draw the black border
        pygame.draw.rect(screen,(0, 0, 0), (border_x, border_y, border_width, border_height),border_radius=border_radius)

        # Glow effect for the current player's turn
        if is_current_turn:
            #contour on the unit
            #glow_rect = pygame.Rect(self.x * CELL_SIZE - 5, self.y * CELL_SIZE - 5, CELL_SIZE + 10, CELL_SIZE + 10)
            #pygame.draw.rect(screen, (255, 255, 0), glow_rect, width=3, border_radius=10)
            #contour on the health bar
            glow_rect = pygame.Rect(health_bar_x - 2, health_bar_y - 2, health_bar_full_width + 4, health_bar_height + 4)
            pygame.draw.rect(screen, (255, 255, 0), glow_rect, border_radius=5)


        # Health bar background (gray for missing health)
        pygame.draw.rect(screen, (0, 0, 0), (health_bar_x, health_bar_y, CELL_SIZE - 4, health_bar_height), border_radius=border_radius)

        # Health bar foreground 
        if self.color == "blue":  # Blue team
            health_color = (90, 120, 200)  # Blue
        elif self.color == "red":  # Red team
            health_color = (255, 90, 90)  # Red
        else:
            health_color = (200, 0 , 200)  # Default purple
        pygame.draw.rect(screen, health_color, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), border_radius=border_radius)

        # Draw 100 HP markers
        segment_size = 100  # Size of each HP segment
        num_segments = self.health // segment_size  # Calculate the number of markers

        for i in range(1, num_segments):
            marker_x = health_bar_x + (health_bar_width * i / num_segments)  # Proportional spacing
            pygame.draw.line( screen, (0, 0, 0), (marker_x, health_bar_y), (marker_x, health_bar_y + health_bar_height-3), 1 )

        # Glossy overlay on the health bar
        gloss_surface = pygame.Surface((health_bar_width*0.85, int(health_bar_height / 3)), pygame.SRCALPHA)
        gloss_surface.fill((255, 255, 255, 150))  # Semi-transparent white with alpha 50
        screen.blit(gloss_surface, (health_bar_x+1, health_bar_y+1))

        # Draw damage text with a black boundary
        if hasattr(self, "last_damage_time") and hasattr(self, "damage_taken") and self.damage_taken != 0:
            time_passed = pygame.time.get_ticks() - self.last_damage_time

            if time_passed < 1000:  # Show for 1 second
                # Calculate alpha (opacity) and vertical position
                alpha = max(255 - (time_passed // 4), 0)  # Fade out over time
                offset_y = -time_passed // 40 + 15 # Move upward over time
                # Red flash effect on damage

                #A is to determine if the flash is red or green
                if self.damage_taken>0:A=255
                else:A=0
                if time_passed < 200 :
                    flash_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    flash_overlay.fill((A, 255-A, 0, 100))  # Semi-transparent red overlay
                    screen.blit(flash_overlay, rect)

                # Create the text surface with fading effect
                font = pygame.font.Font("assets/RussoOne.ttf", 18)
                if self.damage_taken>0:
                    text_surface = font.render(f"-{abs(self.damage_taken)}", True, (A, 255-A, 0))
                    outline_surface = font.render(f"-{abs(self.damage_taken)}", True, (0, 0, 0))
                else:
                    text_surface = font.render(f"+{abs(self.damage_taken)}", True, (A, 255-A, 0))
                    outline_surface = font.render(f"+{abs(self.damage_taken)}", True, (0, 0, 0))
                text_surface.set_alpha(alpha)

                # Add a black outline
                #outline_surface = font.render(f"-{abs(self.damage_taken)}", True, (0, 0, 0))
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

# Draw upward arrow if buffed and duration > 0
        if self.buff_duration > 0:
            arrow_color = (0, 255, 0)  # Green arrow for buffs
            arrow_center = (self.x * CELL_SIZE + CELL_SIZE // 5, self.y * CELL_SIZE + CELL_SIZE -2)
            pygame.draw.polygon(screen, arrow_color, [
                (arrow_center[0], arrow_center[1] - 10),  # Top point
                (arrow_center[0] - 5, arrow_center[1]),  # Bottom left
                (arrow_center[0] + 5, arrow_center[1])   # Bottom right
            ])

        # Draw downward arrow if debuffed and duration > 0
        if self.debuff_duration > 0:
            arrow_color = (255, 0, 0)  # Red arrow for debuffs
            arrow_center = (self.x * CELL_SIZE + CELL_SIZE -7, self.y * CELL_SIZE + CELL_SIZE - 12)
            pygame.draw.polygon(screen, arrow_color, [
                (arrow_center[0], arrow_center[1] + 10),  # Bottom point
                (arrow_center[0] - 5, arrow_center[1]),  # Top left
                (arrow_center[0] + 5, arrow_center[1])   # Top right
            ])


                
class MonsterUnit(Unit):
    def __init__(self, x, y, name, health, damage,defense,crit_chance,image_path, color, move_range, attack_range, unit_type):  
        Unit.__init__(self, x, y, name, health, damage,defense,crit_chance,image_path, color, move_range, attack_range, unit_type)

    def react_to_attack(self, attacker):
        if self.alive:
            # Attack the attacker (if in range)    
            if self.in_range(attacker):
                self.attack(attacker,self.damage)
                