import pygame
import random
from unit import Unit 
from interface import Grid,Highlight,Pickup
from sounds import Sounds


# Constants
GRID_SIZE = 21
CELL_SIZE = 40
SCREEN_WIDTH, SCREEN_HEIGHT = CELL_SIZE * GRID_SIZE + 300, CELL_SIZE * GRID_SIZE + 100
FPS = 60

# Load assets

def load_textures():
    """Load textures for different terrain and overlays."""
    return {
        #grid 
        "grass": pygame.image.load("assets/grass_new.png"),
        "water": pygame.image.load("assets/water.jpg"),
        "rock": pygame.image.load("assets/new_rock.png"),
        #overlays
        "bush": pygame.image.load("assets/bush.png"),
        "barrier": pygame.image.load("assets/inhibetor.png"),
    }

def load_unit_images():
    return {
        "ashe": "assets/ashe.png",
        "garen": "assets/garen.png",
        "darius": "assets/darius.png",
        "soraka": "assets/soraka.png",
        "rengar": "assets/rengar.png",
        "bluebuff": "assets/BlueBuff.png",
        "redbuff": "assets/Redbuff.png",
        "bigbuff": "assets/BigBuff.png",
        "baseblue": "assets/Nexus_Blue.png",
        "basered": "assets/Nexus_Red.png"
    }

def load_indicators():
    return {
        "indicator": pygame.image.load("assets/indicator.png"),
        "indicator1": pygame.image.load("assets/indicator1.jpg"),
        "redsquare": pygame.image.load("assets/redsquare.png"),
    }

def load_pickups():
    """Load the different potion types"""
    return{
        #pick ups
        "red_potion": pygame.image.load("assets/red_potion.png"),
        "blue_potion": pygame.image.load("assets/blue_potion.png"),
        "green_potion": pygame.image.load("assets/green_potion.png"),
        "golden_potion": pygame.image.load("assets/golden_potion.png"),
        "black_potion": pygame.image.load("assets/black_potion.png"),

    }



# Game class
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("League on Budget")
        self.clock = pygame.time.Clock()
        self.unit_images = load_unit_images()
        self.indicators = load_indicators()
        self.textures_file=load_textures()
        self.pickup=Pickup()
        self.sound=Sounds()
        self.pickup_textures=load_pickups()
        self.grid = Grid(GRID_SIZE, self.textures_file)
        self.units = [] 
        self.pickups=[]

        self.pickup.initialize(self.pickup_textures)  
        self.current_unit_index = 0
        self.last_move_time = 0  # Timestamp of the last movement
        self.visible_tiles = set()
        self.event_log = [] # Initialize event log


        
        #initilizing main menu
        self.font_title = pygame.font.Font("assets/League.otf", 65)
        self.font_small = pygame.font.Font("assets/RussoOne.ttf", 36)
        self.background_image = pygame.image.load("assets/lol_background.jpg")  # Load main menu background
        self.champ_select_image = pygame.image.load("assets/champ_select.jpg")  # Load champion selection background

        #intializing key menu
        self.red_key_img = pygame.image.load("assets/red_key.png")
        self.blue_key_img = pygame.image.load("assets/blue_key.png")
        self.font = pygame.font.Font(None, 24)  # Use a small font size for clarity
        
        
        self.key_last_state = {} # prevent repeated actions
        self.current_turn=1

        


    def log_event(self, message):
        """Add an event to the event log."""
        self.event_log.append(message)
        if len(self.event_log) > 10:  # Limit the log to the last 10 events
            self.event_log.pop(0)

    def draw_info_panel(self):
        """Draw the information panel with word wrapping for long text."""
        panel_x = CELL_SIZE * GRID_SIZE
        panel_width = 300  # Width of the info panel
        panel_height = SCREEN_HEIGHT
        padding = 10  # Padding inside the panel

        # Draw panel background
        pygame.draw.rect(self.screen, (30, 30, 30), (panel_x, 0, panel_width, panel_height))

        # Render event log with word wrapping
        font = pygame.font.Font(None, 24)
        y_offset = padding
        line_spacing = 5  # Spacing between lines
        max_line_width = panel_width - 2 * padding

        for event in reversed(self.event_log):  # Display from newest to oldest
            # Split the text into multiple lines if necessary
            words = event.split(" ")
            current_line = ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                text_surface = font.render(test_line, True, (255, 255, 255))
                if text_surface.get_width() > max_line_width:
                    # Render the current line and move to the next
                    rendered_surface = font.render(current_line, True, (255, 255, 255))
                    self.screen.blit(rendered_surface, (panel_x + padding, y_offset))
                    y_offset += rendered_surface.get_height() + line_spacing
                    current_line = word
                else:
                    current_line = test_line
            # Render the last line of the current event
            if current_line:
                rendered_surface = font.render(current_line, True, (255, 255, 255))
                self.screen.blit(rendered_surface, (panel_x + padding, y_offset))
                y_offset += rendered_surface.get_height() + line_spacing

            # Stop rendering if we've filled the panel
            if y_offset > panel_height - padding:
                break



#space for the abilities abr

    def draw_abilities_bar(self):
        """Draw the abilities bar and HUD for the current unit at the bottom of the screen."""
        # Bar dimensions
        bar_height = 100
        bar_y = SCREEN_HEIGHT - bar_height
        padding = 10  # Padding for internal elements
        icon_size = 80  # Size for the champion's icon

        # Background panel for the HUD
        pygame.draw.rect(self.screen, (30, 30, 30), (0, bar_y, SCREEN_WIDTH, bar_height))

        # Get the current unit
        current_unit = self.units[self.current_unit_index]

        # Define fonts
        font_large = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 16)

        # Champion icon
        if current_unit.image:
            icon = pygame.transform.scale(current_unit.image, (icon_size, icon_size))
            self.screen.blit(
                icon, (padding, bar_y + (bar_height - icon_size) // 2)
            )

        # Unit Stats Display (Name, HP, Mana)
        stats_x = padding + icon_size + padding
        stats_y = bar_y + padding

        # Unit name
        name_surface = font_large.render(current_unit.name, True, (255, 255, 255))
        self.screen.blit(name_surface, (stats_x, stats_y))

        # HP Bar
        hp_bar_width = 200
        hp_bar_height = 15
        hp_x = stats_x
        hp_y = stats_y + name_surface.get_height() + padding
        pygame.draw.rect(
            self.screen, (255, 0, 0), (hp_x, hp_y, hp_bar_width, hp_bar_height)
        )
        hp_fill_width = int(hp_bar_width * (current_unit.health / current_unit.max_health))
        pygame.draw.rect(
            self.screen, (0, 255, 0), (hp_x, hp_y, hp_fill_width, hp_bar_height)
        )
        hp_text = f"{current_unit.health}/{current_unit.max_health}"
        hp_text_surface = font_small.render(hp_text, True, (0, 0, 0))
        self.screen.blit(
            hp_text_surface,
            (hp_x + (hp_bar_width - hp_text_surface.get_width()) // 2, hp_y),
        )

        # Mana Bar
        mana_bar_width = 200
        mana_bar_height = 10
        mana_x = stats_x
        mana_y = hp_y + hp_bar_height + padding
        pygame.draw.rect(
            self.screen, (0, 0, 255), (mana_x, mana_y, mana_bar_width, mana_bar_height)
        )
        mana_fill_width = int(mana_bar_width * (current_unit.mana / current_unit.max_mana))
        pygame.draw.rect(
            self.screen, (0, 191, 255), (mana_x, mana_y, mana_fill_width, mana_bar_height)
        )

        # Draw abilities
        if hasattr(current_unit, "abilities"):
            num_abilities = len(current_unit.abilities)
            if num_abilities > 0:
                ability_x_start = stats_x + hp_bar_width + 2 * padding
                ability_width = (SCREEN_WIDTH-300 - ability_x_start - padding) // num_abilities

                for i, ability in enumerate(current_unit.abilities):
                    # Highlight the selected ability
                    if current_unit.selected_ability == ability:
                        ability_bg_color = (0, 128, 255)  # Blue background for selected ability
                    else:
                        ability_bg_color = (50, 50, 50)  # Default gray background

                    ability_x = ability_x_start + i * ability_width
                    ability_rect = pygame.Rect(
                        ability_x, bar_y + padding, ability_width - padding, bar_height - 2 * padding
                    )
                    pygame.draw.rect(self.screen, ability_bg_color, ability_rect)
                    pygame.draw.rect(self.screen, (255, 255, 255), ability_rect, 2)

                    # Ability name and mana cost
                    ability_text = f"{i + 1}: {ability.name} (Mana: {ability.mana_cost})"
                    text_surface = font_small.render(ability_text, True, (255, 255, 255))
                    text_x = ability_x + (ability_width - text_surface.get_width()) // 2
                    self.screen.blit(text_surface, (text_x, bar_y + padding + 10))

                    # Cooldown display
                    cooldown_text = f"CD: {ability.remaining_cooldown}s"
                    cooldown_surface = font_small.render(cooldown_text, True, (255, 0, 0))
                    cooldown_x = ability_x + (ability_width - cooldown_surface.get_width()) // 2
                    self.screen.blit(
                        cooldown_surface, (cooldown_x, bar_y + padding + 30)
                    )

                    # Cooldown bar
                    cooldown_bar_width = ability_width - 2 * padding
                    cooldown_bar_x = ability_x + padding
                    cooldown_bar_y = bar_y + bar_height - 15
                    pygame.draw.rect(
                        self.screen, (50, 50, 50), (cooldown_bar_x, cooldown_bar_y, cooldown_bar_width, 5)
                    )
                    if ability.cooldown > 0:
                        cooldown_fill_width = int(
                            cooldown_bar_width
                            * (1 - ability.remaining_cooldown / ability.cooldown)
                        )
                        pygame.draw.rect(
                            self.screen,
                            (0, 255, 0),
                            (cooldown_bar_x, cooldown_bar_y, cooldown_fill_width, 5),
                        )
            else:
                # No abilities available
                no_abilities_text = "No abilities available"
                no_abilities_surface = font_small.render(
                    no_abilities_text, True, (255, 255, 255)
                )
                no_abilities_x = stats_x + hp_bar_width + padding
                self.screen.blit(
                    no_abilities_surface, (no_abilities_x, bar_y + padding)
                )




    def draw_units(self):
        """Draw all units on the grid with visibility logic."""
        current_team_color = self.units[self.current_unit_index].color
        for index, unit in enumerate(self.units):
            if unit.alive:
                is_current_turn = (index == self.current_unit_index)  # Check if it's the current unit's turn
                # Draw units only if they belong to the current team or are in visible tiles
                if unit.color == current_team_color or (unit.x, unit.y) in self.visible_tiles and self.grid.tiles[unit.x][unit.y].overlay != "bush":
                    unit.draw(self.screen, is_current_turn=is_current_turn)
                    



    def basic_attack(self, unit):
        """Resolve the attack at the current target location."""
        target_hit = False

        # Find a valid target at the attack cursor location
        for other_unit in self.units:
            if (
                other_unit.alive
                and other_unit.x == unit.target_x
                and other_unit.y == unit.target_y
                and other_unit.color != unit.color
            ):
                damage=unit.attack(other_unit,unit.damage)  # Use the Unit's attack method
                if damage > 0:
                    self.log_event(f"{unit.name} attacked {other_unit.name} for {damage} damage!")
                    # Vérifier si l'unité est morte
                    if not other_unit.alive:
                        self.log_event(f"{other_unit.name} has been defeated!")
                else:
                    self.log_event(f"{unit.name} attacked {other_unit.name} but missed!")
                target_hit = True
                break
        if not target_hit:
            self.log_event(f"{unit.name} attacked but missed!")

        unit.state = "done"  # Mark the unit as done after the attack
        


    def advance_to_next_unit(self):
        """Advance to the next unit, skipping dead ones."""
        # Start from the current unit
        start_index = self.current_unit_index

        #we keep incrementing the index untill we fullfil the conditions
        while True:
            # Move to the next unit
            self.current_unit_index = (self.current_unit_index + 1) % len(self.units)

            # Check if the unit is alive and that is part of either team red or team blue
            if (self.units[self.current_unit_index].alive 
                and self.units[self.current_unit_index].unit_type=="player"):
                break

            # If we've cycled through all units and come back to the start, stop (prevents infinite loops)
            if self.current_unit_index == start_index:
                self.log_event("No alive units remaining!")
                return


#add a mana and health regen for each round (2% mana ,1%hp)   

    def handle_turn(self):
        """Handle movement and attacks for the current unit."""
        current_time = pygame.time.get_ticks()
        current_unit = self.units[self.current_unit_index]
        keys = pygame.key.get_pressed()

        action_key = pygame.K_SPACE

        # debounce mechanism to avoid repeated triggers.
        if not hasattr(self, "key_last_state"):
            self.key_last_state = {}

        key_just_pressed = keys[action_key] and not self.key_last_state.get(action_key, False)
        self.key_last_state[action_key] = keys[action_key]

        # Movement Phase
        if current_unit.state == "move":
            if current_time - self.last_move_time > 100:  # Delay of 100ms between movements
                if keys[pygame.K_UP]:
                    current_unit.move(0, -1, self.grid)
                    self.last_move_time = current_time
                elif keys[pygame.K_DOWN]:
                    current_unit.move(0, 1, self.grid)
                    self.last_move_time = current_time
                elif keys[pygame.K_LEFT]:
                    current_unit.move(-1, 0, self.grid)
                    self.last_move_time = current_time
                elif keys[pygame.K_RIGHT]:
                    current_unit.move(1, 0, self.grid)
                    self.last_move_time = current_time
                elif key_just_pressed:
                    if not any(
                        unit.x == current_unit.x and unit.y == current_unit.y and unit != current_unit
                        and unit.alive for unit in self.units 
                    ):  
                        self.log_event(f"{current_unit.name} finalized move at ({current_unit.x}, {current_unit.y}).")

                        for p in self.pickup.all_pickups:
                            if p.x == current_unit.x and p.y == current_unit.y:
                                self.pickup.picked_used(current_unit,p)


                        current_unit.state = "attack"
                        
                        current_unit.target_x, current_unit.target_y = current_unit.x, current_unit.y  # Initialize cursor

                        next_team_color = self.units[self.current_unit_index].color
                        Highlight.update_fog_visibility(self,next_team_color)



                            #check if there is enemy in bush
                    elif self.grid.tiles[current_unit.x][current_unit.y].overlay == "bush" and any(
                            unit.x == current_unit.x and unit.y == current_unit.y 
                            and unit.alive and unit.color != current_unit.color for unit in self.units
                        ) :   #in the presence of an enemy on this position but it's a bush u just get assassinated
                        enemy_unit = next(
                            (unit for unit in self.units if unit.x == current_unit.x and unit.y == current_unit.y 
                            and unit.alive and unit.color != current_unit.color), 
                            None
                        )
                        if enemy_unit:
                            self.log_event(f"{current_unit.name} got assassinated")
                            
                            enemy_unit.attack(current_unit,9999)
                            current_unit.state="done"
                            self.manage_keys(dead_player=current_unit, killer=enemy_unit)



                    else :      #if it's another unit u just can't finalise movement
                        self.log_event("can't finalise movement , another unit is filling this position")
                    
        # Attack Phase
        elif current_unit.state == "attack":
            if current_time - self.last_move_time > 100:  # Delay of 100ms between movements
                new_target_x, new_target_y = current_unit.target_x, current_unit.target_y

                # Determine current range restriction
                if hasattr(current_unit, "selected_ability") and current_unit.selected_ability is not None:
                    current_range = current_unit.selected_ability.attack_radius
                else:
                    current_range = current_unit.attack_range

                # Move the attack cursor
                if keys[pygame.K_UP]:
                    new_target_y = max(0, current_unit.target_y - 1)
                elif keys[pygame.K_DOWN]:
                    new_target_y = min(GRID_SIZE - 1, current_unit.target_y + 1)
                elif keys[pygame.K_LEFT]:
                    new_target_x = max(0, current_unit.target_x - 1)
                elif keys[pygame.K_RIGHT]:
                    new_target_x = min(GRID_SIZE - 1, current_unit.target_x + 1)

                # Enforce range restriction
                if abs(current_unit.x - new_target_x) + abs(current_unit.y - new_target_y) <= current_range:
                    current_unit.target_x, current_unit.target_y = new_target_x, new_target_y
                    self.last_move_time = current_time

            # Ability Selection
            if hasattr(current_unit, "abilities"):
                if keys[pygame.K_1] and len(current_unit.abilities) > 0:
                    current_unit.selected_ability = current_unit.abilities[0]
                    current_unit.target_x, current_unit.target_y = current_unit.x, current_unit.y
                   
                elif keys[pygame.K_2] and len(current_unit.abilities) > 1:
                    current_unit.selected_ability = current_unit.abilities[1]
                    current_unit.target_x, current_unit.target_y = current_unit.x, current_unit.y

                elif keys[pygame.K_3] and len(current_unit.abilities) > 2:
                    current_unit.selected_ability = current_unit.abilities[2]
                    current_unit.target_x, current_unit.target_y = current_unit.x, current_unit.y
                   
                elif keys[pygame.K_c]:  # Cancel ability selection
                    current_unit.selected_ability = None
                    current_unit.target_x, current_unit.target_y = current_unit.x, current_unit.y


            # Execute Selected Ability or Basic Attack
            target = next(
                (unit for unit in self.units if unit.alive and unit.x == current_unit.target_x and unit.y == current_unit.target_y),
                None,
            )
            if current_unit.selected_ability is not None :
                if key_just_pressed:  # Confirm ability usage
                    if current_unit.selected_ability.is_aoe>0:   #logic when using aoe abilities
                        aoe_targets = current_unit.selected_ability.get_targets_in_aoe(current_unit, self.units)
                        if aoe_targets is not None:  # Ensure targets exist
                            if current_unit.selected_ability.use(current_unit, aoe_targets):
                                self.sound.play(current_unit.selected_ability.name)
                                current_unit.state = "done"
                                current_unit.selected_ability = None  # Reset ability selection
                        
                        else:
                            print("No valid target selected.")

                        #manage after using aoe abilitities
                        for targets in aoe_targets:
                            #manage the mssg to show when buff is killed 
                            if targets !=None and targets.unit_type =="monster" and targets.alive==False :
                                #if the buff dies the team gets a permanent buff
                                for unit in self.units:
                                        if unit.color == current_unit.color:
                                            if unit.name=="BigBuff":
                                                unit.max_health = int(unit.max_health * 1.10)
                                                unit.damage = int(unit.damage * 1.15)
                                            else :
                                                unit.max_health = int(unit.max_health * 1.05)
                                                unit.damage = int(unit.damage * 1.05)
                                
                                if targets.red_keys==1:
                                    Highlight.show_buff_animation(self,self.screen,targets.image,"You won a red key + buff")
                                elif targets.blue_keys==1:
                                    Highlight.show_buff_animation(self,self.screen,targets.image,"You won a blue key + buff")
                                else:
                                    Highlight.show_buff_animation(self,self.screen,targets.image,"You got the Buff ")

                                # managing the keys
                            if targets !=None and targets.alive==False:
                                self.manage_keys(dead_player=targets, killer=current_unit)

                    else : #logic when using none aoe abilities
                        if target is not None:  # Ensure targets exist
                            if current_unit.selected_ability.use(current_unit, target):
                                self.sound.play(current_unit.selected_ability.name)
                                current_unit.state = "done"
                                current_unit.selected_ability = None  # Reset ability selection
                        
                        else:
                            print("No valid target selected.")



            elif  key_just_pressed:
                self.basic_attack(current_unit)  # Basic attack
                current_unit.state = "done"

                # Jouer le son d'attaque de base
                basic_attack_sound = f"{current_unit.name} Basic Attack"
                if basic_attack_sound in self.sound.sounds:
                    self.sound.play(basic_attack_sound)
            
                
            #manage after using basic attack and none aoe abilities
            #manage the mssg to show when buff is killed 
            if target !=None and target.unit_type =="monster" and target.alive==False :
                #if the buff dies the team gets a permanent buff
                for unit in self.units:
                    if unit.color == current_unit.color:
                        if unit.name=="BigBuff":
                            unit.max_health = int(unit.max_health * 1.10)
                            unit.damage = int(unit.damage * 1.15)
                        else :
                            unit.max_health = int(unit.max_health * 1.05)
                            unit.damage = int(unit.damage * 1.05)
                
                if target.red_keys==1:
                    Highlight.show_buff_animation(self,self.screen,target.image,"You won a red key + buff")
                elif target.blue_keys==1:
                    Highlight.show_buff_animation(self,self.screen,target.image,"You won a blue key + buff")
                else:
                    Highlight.show_buff_animation(self,self.screen,target.image,"You got the Buff ")

                # managing the keys
            if target !=None and target.alive==False:
                self.manage_keys(dead_player=target, killer=current_unit)

            

        # End Turn
        if  keys[pygame.K_r] and current_unit.state == "done" :
            self.current_turn+=1

            #each turn we reduce the cooldowns and reduce the duration remaaning on the buffs
            for unit in self.units:
                for ability in unit.abilities:
                        ability.reduce_cooldown()
            for unit in self.units:
                unit.update_buffs_and_debuffs()


            current_unit.state = "move"  # Reset state for the next turn
            current_unit.initial_x, current_unit.initial_y = current_unit.x, current_unit.y  # Reset initial position
            self.advance_to_next_unit()

            next_team_color = self.units[self.current_unit_index].color
            Highlight.update_fog_visibility(self,next_team_color)
            self.pickup.update(self.current_turn,self.grid)
            self.manage_keys(current_turn=self.current_turn)

            #health and mana regeneration each turn
            for unit in self.units:
                if unit.unit_type=="player":
                    unit.health+=min(unit.max_health-unit.health,int(0.005*unit.max_health))
                    unit.mana +=min(unit.max_mana-unit.mana,int(0.01*unit.max_mana))

            #respawn logic
            # Calculate respawn cap  
            respawn = min(self.current_turn // 8, 10)

            # Update death timers and respawn dead units
            for unit in self.units:
                if not unit.alive and unit.unit_type=="player":
                    unit.death_timer += 1  # Increment death timer for dead units
                    print(f"{unit.death_timer}seconds of death for {unit.name}")
                    # Respawn logic
                    if unit.death_timer >= respawn :
                        self.log_event(f"{unit.name} has respawned at base!")
                        unit.alive = True
                        unit.health = unit.max_health  # Restore health
                        unit.state = "move"
                        unit.initial_x, unit.initial_y = self.get_respawn_location(unit)  # Define respawn location logic
                        unit.x,unit.y = unit.initial_x, unit.initial_y
                        unit.death_timer = 0  # Reset death timer

            

            
    
    def get_respawn_location(self, unit):
    # Example: respawn at a fixed position or base location
        unit_index = self.units.index(unit)
        # Determine the respawn location based on the index
        if unit_index == 0:
            return (3, 15)  # Respawn point for the first unit
        elif unit_index == 1:
            return (4, 16)  # Respawn point for the second unit
        elif unit_index == 2:
            return (15, 2)  # Respawn point for the third unit
        elif unit_index == 3:
            return (17, 4)
        # Add more conditions as needed for additional indices



    
    def manage_keys(self, dead_player=None, killer=None, current_turn=None):
        """
        Handles all key-related logic:
        - Initializes keys at the start of the game.
        - Transfers keys when a player dies.
        - Spawns additional keys based on turn events.
        - Tracks team progress on key collection.

        :param dead_player: The unit that died (optional).
        :param killer: The unit that killed the dead player (optional).
        :param current_turn: The current turn number (optional).
        """
        # Initialize keys at the start of the game
        if not hasattr(self, "keys_initialized") or not self.keys_initialized:
            self.units[0].blue_keys = 1  # Blue Player 1 starts with one Blue key
            self.units[1].blue_keys = 1  # Blue Player 2 starts with one Blue key
            self.units[2].red_keys = 1  # Red Player 1 starts with one Red key
            self.units[3].red_keys = 1  # Red Player 2 starts with one Red key
            self.keys_initialized = True
            print(f"Initial keys have been assigned to players.")

        # Handle key transfer on player death
        if dead_player and killer:
            if killer.unit_type == "player":
                # Transfer keys to the killer
                killer.red_keys += dead_player.red_keys
                killer.blue_keys += dead_player.blue_keys
                print(f"{killer.name} collected {dead_player.red_keys} Red key(s) and {dead_player.blue_keys} Blue key(s) from {dead_player.name}.")
                dead_player.red_keys = 0
                dead_player.blue_keys = 0
            else:
                # Keys are lost if the killer is not a player
                print(f"{dead_player.name}'s {dead_player.red_keys} Red key(s) and {dead_player.blue_keys} Blue key(s) are not lost.")

            # Reset keys on the dead player
            

        # Spawn additional keys based on turn events
        if current_turn:
            if current_turn == random.randint(25,30):
                # Assign keys to a monster
                for unit in self.units :
                    if unit.unit_type == "monster" :
                        if unit.alive==False:
                            unit.health=unit.max_health
                            unit.alive=True
                        if unit.name=="BlueBuff":
                            unit.blue_keys += 1
                            print("BlueBuff now holds 1 Blue key")
                        if unit.name=="RedBuff":
                            unit.red_keys += 1
                            print("RedBuff now holds 1 Red key.")
                    
                    
                    




    def draw_key_counts(self):
        """
        Draws the number of red and blue keys each player and team has,
        including the player's image next to their key counts.
        """
        # Constants for layout
        key_icon_size = 20  # Size of the key images
        unit_icon_size = int(CELL_SIZE / 2)  # Size of the unit image (1/3 of cell height and width)
        x_offset = SCREEN_WIDTH-220  # Horizontal margin
        y_offset = SCREEN_HEIGHT /2  # Vertical margin
        spacing = 30  # Space between rows

        # Draw individual player key counts
        for i, unit in enumerate(self.units):
            if unit.unit_type == "player":
                # Calculate vertical position
                player_y = y_offset + i * spacing

                # Draw unit image
                self.screen.blit(
                    pygame.transform.scale(unit.image, (unit_icon_size, unit_icon_size)),
                    (x_offset, player_y)
                )

                # Draw key images and counts
                self.screen.blit(
                    pygame.transform.scale(self.red_key_img, (key_icon_size, key_icon_size)),
                    (x_offset + unit_icon_size + 10, player_y)
                )
                self.screen.blit(
                    pygame.transform.scale(self.blue_key_img, (key_icon_size, key_icon_size)),
                    (x_offset + unit_icon_size + 70, player_y)
                )  # Space between keys

                # Draw key count texts
                red_key_count_text = self.font.render(str(unit.red_keys), True, (255, 0, 0))
                blue_key_count_text = self.font.render(str(unit.blue_keys), True, (0, 0, 255))
                self.screen.blit(
                    red_key_count_text,
                    (x_offset + unit_icon_size + 10 + key_icon_size + 5, player_y)
                )
                self.screen.blit(
                    blue_key_count_text,
                    (x_offset + unit_icon_size + 70 + key_icon_size + 5, player_y)
                )

        





    def main_menu(self):
        """Display the main menu with options to start or quit."""
        menu_running = True

        # Start menu sound
        self.sound.play("game_music")

        while menu_running:
            rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
            self.screen.blit(pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)), rect)

            # Render game title
            title_text = self.font_title.render("League on Budget", True, (200, 156, 56))
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2  , SCREEN_HEIGHT // 4  ))
            title_text1 = self.font_title.render("League on Budget", True, (0,0,0))
            title_rect1 = title_text1.get_rect(center=(SCREEN_WIDTH // 2 +2, SCREEN_HEIGHT // 4+ 2))

            self.screen.blit(title_text1, title_rect1)
            self.screen.blit(title_text, title_rect)
            
            
            # Render instructions
            start_text = self.font_small.render("Press ENTER to Play", True, (200, 200, 200))
            quit_text = self.font_small.render("Press ESC to Quit", True, (200, 200, 200))

            start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

            self.screen.blit(start_text, start_rect)
            self.screen.blit(quit_text, quit_rect)

            pygame.display.flip()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Start the game
                        menu_running = False
                    elif event.key == pygame.K_ESCAPE:  # Quit the game
                        pygame.quit()
                        exit()





    def show_menu(self):
        """Enhanced team selection menu."""
        menu_running = True
        
        # Initialize assets
        font = self.font_title
        small_font = self.font_small

        # Get all units from create_units
        all_units = Unit.create_units(self)

        # Filter player units for selection (those with team=None)
        available_units = [unit for unit in all_units if unit.color is None]

        # Track selected units and predefined positions
        blue_team = []
        red_team = []
        blue_positions = [(3, 15), (4, 16)]
        red_positions = [(15, 2), (17, 4)]
        current_team = "blue"  # Start with Blue's turn
        selected_units = []
        selected_unit_info = None  # Track which unit's details are displayed

        while menu_running:
            rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
            self.screen.blit(pygame.transform.scale(self.champ_select_image, (SCREEN_WIDTH, SCREEN_HEIGHT)), rect)

            # Render the middle section with available units
            y_offset = SCREEN_HEIGHT // 3
            for i, unit in enumerate(available_units):
                color = (200, 100, 100) if unit in selected_units else (255, 255, 255)
                unit_text = small_font.render(f"{i + 1}: {unit.name}", True, color)
                self.screen.blit(unit_text, (SCREEN_WIDTH // 2 - 50, y_offset))
                y_offset += 40

            # Display currently selected unit's attributes
            if selected_unit_info:
                attributes_text = [
                    f"Name: {selected_unit_info.name}",
                    f"HP: {selected_unit_info.health}",
                    f"ATK: {selected_unit_info.damage}",
                ]
                y_offset = SCREEN_HEIGHT // 3
                for line in attributes_text:
                    attr_text = small_font.render(line, True, (255, 255, 255))
                    self.screen.blit(attr_text, (SCREEN_WIDTH // 2 + 200, y_offset))
                    y_offset += 40
                     # Show the selected champion's image larger
                selected_image = pygame.transform.scale(selected_unit_info.image, (150, 150))
                self.screen.blit(selected_image, (SCREEN_WIDTH - 420, y_offset+30))

            # Render team rosters
            blue_text = font.render("Blue Team", True, (0, 0, 255))
            red_text = font.render("Red Team", True, (255, 0, 0))
            self.screen.blit(blue_text, (50, 50))
            self.screen.blit(red_text, (SCREEN_WIDTH-400, 50))

            y_offset_blue = 200
            for unit in blue_team:
                unit_text = small_font.render(unit.name, True, (0, 0, 255))
                self.screen.blit(unit_text, (100, y_offset_blue))
                selected_image = pygame.transform.scale(unit.image, (50, 50))
                self.screen.blit(selected_image, (250, y_offset_blue-10))
                y_offset_blue += 60

            y_offset_red = 200
            for unit in red_team:
                unit_text = small_font.render(unit.name, True, (255, 0, 0))
                self.screen.blit(unit_text, (SCREEN_WIDTH-400+50, y_offset_red))
                selected_image = pygame.transform.scale(unit.image, (50, 50))
                self.screen.blit(selected_image, (SCREEN_WIDTH-200, y_offset_red-10))
                y_offset_red += 60

            pygame.display.flip()

            # Handle menu events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        index = event.key - pygame.K_1
                        if 0 <= index < len(available_units):
                            selected_unit_info = available_units[index]  # Show attributes for this unit
                    elif event.key == pygame.K_RETURN and selected_unit_info:
                        self.sound.play("selection") 
                        self.sound.set_volume("selection", 0.5)
                        if selected_unit_info not in selected_units:
                            # Assign the current team and position to the selected unit
                            if current_team == "blue":
                                selected_unit_info.color = "blue"
                                selected_unit_info.initial_x = blue_positions[len(blue_team)][0]
                                selected_unit_info.initial_y = blue_positions[len(blue_team)][1]
                                selected_unit_info.x = blue_positions[len(blue_team)][0]
                                selected_unit_info.y = blue_positions[len(blue_team)][1]
                                blue_team.append(selected_unit_info)
                                current_team = "red"
                            else:
                                selected_unit_info.color = "red"
                                selected_unit_info.initial_x = red_positions[len(red_team)][0]
                                selected_unit_info.initial_y = red_positions[len(red_team)][1]
                                selected_unit_info.x = red_positions[len(red_team)][0]
                                selected_unit_info.y = red_positions[len(red_team)][1]
                                red_team.append(selected_unit_info)
                                current_team = "blue"
                            selected_units.append(selected_unit_info)
                            selected_unit_info = None
                            # End selection if both teams have 2 units each
                            if len(blue_team) == 2 and len(red_team) == 2 :
                                for i in range(3, 0, -1):  # Countdown from 3 to 1
                                    rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
                                    self.screen.blit(pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)), rect)
                                    countdown_text = small_font.render(f"Starting in {i}...", True, (55, 255, 55))
                                    countdown_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                                    self.screen.blit(countdown_text, countdown_rect)
                                    pygame.display.flip()
                                    pygame.time.delay(1000)  # Delay for 1 second
                                    # Play game music
                                for volume in reversed([x / 100 for x in range(1, 101)]):  # De 1.0 à 0.01
                                    self.sound.set_volume("game_music", volume)  
                                    pygame.time.delay(10) 
                                self.sound.set_volume("game_music", 0.03)  
                                self.sound.sounds["game_music"].play(loops=-1)
                                menu_running = False

        # Build self.units in the required order: blue team → red team → monsters
        monsters = [unit for unit in all_units if unit.unit_type == "monster"]
        bases = [unit for unit in all_units if unit.unit_type == "base"]
        self.units = blue_team + red_team + monsters + bases

        return self.units
    



    def run(self):
        """Main game loop."""
        self.main_menu()  # Display main menu
        self.units = self.show_menu()
        self.manage_keys()  # Initializes keys
         
        starting_team_color = self.units[self.current_unit_index].color
        Highlight.update_fog_visibility(self, starting_team_color)
        

        

        running = True
        while running:
            self.screen.fill((0, 0, 0))  # Clear the screen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            
            # Draw grid and units
            self.grid.draw(self.screen)

            # Highlight range for the active unit
            current_unit = self.units[self.current_unit_index]
            Highlight.highlight_range(self,current_unit)
 
            # Render fog of war
            Highlight.draw_fog(self,self.screen)
            
            #Display pcikups
            self.pickup.draw_pickups(self.screen, self.visible_tiles)

            
            #Display units
            self.draw_units()

            # Handle current unit's turn
            self.handle_turn()
            
            #Show Info panel
            self.draw_info_panel()

            #draw HUD
            self.draw_abilities_bar()

            #draw keys
            self.draw_key_counts()
            

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
# Run the game
if __name__ == "__main__":
    Game().run()





#fix the keys vfx ; make the showing of mssgs better

#add the win conditions and make base inhereted class
