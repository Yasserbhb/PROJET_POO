import pygame
import random
from unit import Unit , MonsterUnit
from interface import Grid,Highlight 
from abilities import Abilities

# Constants
GRID_SIZE = 21
CELL_SIZE = 30
SCREEN_WIDTH, SCREEN_HEIGHT = CELL_SIZE * GRID_SIZE + 300, CELL_SIZE * GRID_SIZE 
FPS = 60

# Load assets

def load_textures():
    """Load textures for different terrain and overlays."""
    return {
        "grass": pygame.image.load("assets/grass4.jpg"),
        "water": pygame.image.load("assets/water.jpg"),
        "rock": pygame.image.load("assets/rock.jpg"),
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

# Abilities
abilities = [
    Abilities("Fireball", 50, 10, "damage", attack=10000, description="Deals fire damage to a single target."),
    Abilities("Heal", 40, 15, "heal", attack=50, description="Restores health to an ally."),
    Abilities("Shield", 30, 20, "buff", defense=30, description="Increases defense temporarily."),
    Abilities("Frostbite", 60, 12, "debuff", attack=20, description="Reduces enemy attack power."),
]

# Game class
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("League on Budget")
        self.clock = pygame.time.Clock()
        self.unit_images = load_unit_images()
        self.indicators = load_indicators()
        self.textures=load_textures()
        self.grid = Grid(GRID_SIZE, self.textures)
        self.units = [] 
        self.current_unit_index = 0
        self.last_move_time = 0  # Timestamp of the last movement
        self.visible_tiles = set()
        self.event_log = [] # Initialize event log
        self.mana = 1000
        self.max_mana = 1000
        # Pre-calculate fog for the starting team (blue)
        
        #initilizing main menu
        self.font_title = pygame.font.Font("assets/League.otf", 65)
        self.font_small = pygame.font.Font("assets/RussoOne.ttf", 36)
        self.background_image = pygame.image.load("assets/lol_background.jpg")  # Load main menu background
        self.champ_select_image = pygame.image.load("assets/champ_select.jpg")  # Load main menu background

        self.key_last_state = {} # prevent repeated actions

        
 

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
        pygame.draw.rect(self.screen, (20, 20, 20), (panel_x, 0, panel_width, panel_height))

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

        # Current unit's abilities
        #current_unit = self.units[self.current_unit_index]
        #if hasattr(current_unit, "abilities"):
            # for i, ability in enumerate(current_unit.abilities):
                #ability_text = f"Key {i + 1}: {ability.name} (Mana: {ability.mana_cost}, CD: {ability.remaining_cooldown}s)"
                #text_surface = font.render(ability_text, True, (255, 255, 255))
                #self.screen.blit(text_surface, (panel_x + padding, y_offset))
                #y_offset += text_surface.get_height() + 5


    def draw_abilities_bar(self):
        """Draw the abilities of the current unit at the top of the screen with dynamic sizing."""
        # Définir la barre d'abilities
        panel_x = 0  # La barre commence en haut à gauche
        panel_width = SCREEN_WIDTH - 300  # La largeur de la barre 
        panel_height = 40  # Hauteur de la barre
        padding = 10  # Espacement interne pour les textes

        pygame.draw.rect(self.screen, (30, 30, 30), (panel_x, 0, panel_width, panel_height))
        font = pygame.font.Font(None, 16)
        current_unit = self.units[self.current_unit_index]  # Récupérer l'unité actuelle
        if hasattr(current_unit, "abilities"): # Vérifier que l'unité a des abilities
            num_abilities = len(current_unit.abilities)
            max_width_per_ability = (panel_width - 2 * padding) // max(1, num_abilities)  # Assurer au moins 1 espace
            # Dessiner chaque ability
            for i, ability in enumerate(current_unit.abilities):
                ability_text = f"{i + 1}: {ability.name} (Mana: {ability.mana_cost}, CD: {ability.remaining_cooldown}s)"
                # Calculer la position pour cette ability
                ability_x = panel_x + padding + i * max_width_per_ability  # Décalage horizontal
                text_surface = font.render(ability_text, True, (255, 255, 255))
                # Centrer le texte dans son espace alloué
                centered_x = ability_x + (max_width_per_ability - text_surface.get_width()) // 2
                self.screen.blit(text_surface, (centered_x, panel_height // 4))


    def create_units(self):
        """Create units and assign abilities."""
        return [
            Unit(3, 15, "Garen", 400, 99, self.unit_images["garen"], None, 3, 2, "player", mana=120, abilities=[
                Abilities("Slash", 30, 5, "damage", attack=200, description="A quick slash attack."),
                BuffAbility("Fortify", 20, 10, defense=50, description="Increases defense temporarily for 3 turns."),
                Abilities("Charge", 40, 8, "damage", attack=300, description="A powerful charging attack that stuns the target."),
            ]),
            Unit(4, 16, "Ashe", 500, 70, self.unit_images["ashe"], None, 3, 2, "player", mana=100, abilities=[
                Abilities("Arrow Shot", 20, 5, "damage", attack=150, description="Shoots an arrow at the target."),
                DebuffAbility("Frost Arrow", 30, 10, attack=20, defense=10, description="Slows and weakens the target."),
                BuffAbility("Healing Wind", 50, 15, defense=20, description="Restores health to an ally and grants temporary defense."),
            ]),
            Unit(15, 3, "Darius", 700, 90, self.unit_images["darius"], None, 3, 2, "player", mana=120, abilities=[
                Abilities("Decimate", 50, 7, "damage", attack=250, description="Spins his axe, dealing damage to nearby enemies."),
                DebuffAbility("Crippling Strike", 40, 8, attack=30, defense=10, description="A heavy strike that slows and weakens the target."),
                Abilities("Noxian Guillotine", 80, 15, "damage", attack=400, description="Executes an enemy with low health."),
            ]),
            Unit(16, 4, "Soraka", 490, 50, self.unit_images["soraka"], None, 3, 2, "player", mana=150, abilities=[
                Abilities("Starcall", 30, 5, "damage", attack=50, description="Calls a star down, dealing magic damage."),
                Abilities("Astral Infusion", 40, 8, "heal", attack=100, description="Sacrifices own health to heal an ally."),
                BuffAbility("Wish", 100, 20, defense=30, description="Restores health to all allies and grants defense for 3 turns."),
            ]),
            Unit(0, 0, "Rengar", 700, 180, self.unit_images["rengar"], None, 3, 2, "player", mana=120, abilities=[
                Abilities("Savagery", 30, 5, "damage", attack=300, description="Empowered strike dealing extra damage."),
                BuffAbility("Battle Roar", 40, 8, defense=40, description="Boosts defense and regenerates health."),
                DebuffAbility("Thrill of the Hunt", 80, 20, attack=20, description="Tracks the enemy, reducing their attack temporarily."),
            ]),


            MonsterUnit(10, 10, "BigBuff", 1000, 50, self.unit_images["bigbuff"], "neutral", 3, 2, "monster"),
            MonsterUnit(5, 7, "BlueBuff", 390, 250, self.unit_images["bluebuff"], "neutral", 3, 2, "monster"),
            MonsterUnit(15, 13, "RedBuff", 390, 250, self.unit_images["redbuff"], "neutral", 3, 2, "monster"),

            Unit(1, 19, "NexusBlue", 390, 50, self.unit_images["baseblue"], "blue", 0, 0, "base"),
            Unit(19, 1, "NexusRed", 390, 50, self.unit_images["basered"], "red", 0, 0, "base"),
        ]

    def draw_units(self):
        """Draw all units on the grid with visibility logic."""
        current_team_color = self.units[self.current_unit_index].color
        for index, unit in enumerate(self.units):
            if unit.alive:
                is_current_turn = (index == self.current_unit_index)  # Check if it's the current unit's turn
                # Draw units only if they belong to the current team or are in visible tiles
                if unit.color == current_team_color or (unit.x, unit.y) in self.visible_tiles and self.grid.tiles[unit.x][unit.y].overlay != "bush":
                    unit.draw(self.screen, is_current_turn=is_current_turn)

    def resolve_attack(self, unit):
        """Resolve the attack or ability use at the current target location."""
        target_hit = False

    # Find a valid target at the attack cursor location
        for other_unit in self.units:
            if (
                other_unit.alive
                and other_unit.x == unit.target_x
                and other_unit.y == unit.target_y
                and other_unit.color != unit.color
            ):

                damage=unit.attack(other_unit)  # Use the Unit's attack method
                if other_unit.unit_type =="monster" and other_unit.alive==False :
                    Highlight.show_buff_animation(self,self.screen,other_unit.image)
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


    
    def handle_turn(self):
        """Handle movement and attacks for the current unit."""
        current_time = pygame.time.get_ticks()
        current_unit = self.units[self.current_unit_index]
        keys = pygame.key.get_pressed()

        # Debounce mechanism to track key states
        if not hasattr(self, "key_last_state"):
            self.key_last_state = {}  # Initialize key state tracker

        def is_key_just_pressed(key):
            """Check if a key was just pressed."""
            pressed = keys[key] and not self.key_last_state.get(key, False)
            self.key_last_state[key] = keys[key]
            return pressed

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
                elif is_key_just_pressed(pygame.K_SPACE):  # Finalize movement
                    self.log_event(f"{current_unit.name} finalized move at ({current_unit.x}, {current_unit.y}).")
                    current_unit.state = "attack"
                    current_unit.target_x, current_unit.target_y = current_unit.x, current_unit.y

        # Attack Phase
        elif current_unit.state == "attack":
            if current_time - self.last_move_time > 100:  # Delay of 100ms between cursor movements
                new_target_x, new_target_y = current_unit.target_x, current_unit.target_y

                # Move the attack cursor
                if keys[pygame.K_UP]:
                    new_target_y = max(0, current_unit.target_y - 1)
                elif keys[pygame.K_DOWN]:
                    new_target_y = min(GRID_SIZE - 1, current_unit.target_y + 1)
                elif keys[pygame.K_LEFT]:
                    new_target_x = max(0, current_unit.target_x - 1)
                elif keys[pygame.K_RIGHT]:
                    new_target_x = min(GRID_SIZE - 1, current_unit.target_x + 1)

                # Enforce attack range restriction
                if (
                    abs(current_unit.x - new_target_x) + abs(current_unit.y - new_target_y)
                    <= current_unit.attack_range
                ):
                    current_unit.target_x, current_unit.target_y = new_target_x, new_target_y
                    self.last_move_time = current_time

            # Using Abilities
            target = next(
                (unit for unit in self.units if unit.alive and unit.x == current_unit.target_x and unit.y == current_unit.target_y),
                None,
            )
            if hasattr(current_unit, "abilities"):
                if is_key_just_pressed(pygame.K_1) and len(current_unit.abilities) > 0:
                    if current_unit.abilities[0].use(current_unit, target):
                        current_unit.state = "done"  # Mark turn as done after using an ability
                elif is_key_just_pressed(pygame.K_2) and len(current_unit.abilities) > 1:
                    if current_unit.abilities[1].use(current_unit, target):
                        current_unit.state = "done"
                elif is_key_just_pressed(pygame.K_3) and len(current_unit.abilities) > 2:
                    if current_unit.abilities[2].use(current_unit, target):
                        current_unit.state = "done"

            # Standard attack logic if no ability is used
            if is_key_just_pressed(pygame.K_SPACE):
                self.resolve_attack(current_unit)
                current_unit.state = "done"

        # End Turn
        if is_key_just_pressed(pygame.K_r) and current_unit.state == "done":
            current_unit.state = "move"  # Reset state for the next turn
            current_unit.initial_x, current_unit.initial_y = current_unit.x, current_unit.y  # Reset initial position
            self.advance_to_next_unit()

            next_team_color = self.units[self.current_unit_index].color
            Highlight.update_fog_visibility(self,next_team_color)

    def main_menu(self):
        """Display the main menu with options to start or quit."""
        menu_running = True

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
        all_units = self.create_units()

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
                                menu_running = False

        # Build self.units in the required order: blue team → red team → monsters
        monsters = [unit for unit in all_units if unit.unit_type == "monster"]
        bases = [unit for unit in all_units if unit.unit_type == "base"]
        self.units = blue_team + red_team + monsters + bases

        return self.units
    

    def select_abilities(self):
        menu_running = True
        selected_ability = None
        while menu_running:
            self.screen.fill((30, 30, 30))
            y_offset = 100
            for i, ability in enumerate(abilities):
                text = self.font_small.render(f"{i + 1}: {ability.name} - {ability.description}", True, (255, 255, 255))
                self.screen.blit(text, (50, y_offset))
                y_offset += 40
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        index = event.key - pygame.K_1
                        if 0 <= index < len(abilities):
                            selected_ability = abilities[index]
                            menu_running = False
        return selected_ability

    def run(self):
        """Main game loop."""
        self.main_menu()  # Display main menu
        self.units = self.show_menu()
        
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
            
            # Render fog of war
            Highlight.draw_fog(self,self.screen)

            # Highlight range for the active unit
            current_unit = self.units[self.current_unit_index]
            Highlight.highlight_range(self,current_unit)
            
            #Display units
            self.draw_units()
            self.draw_abilities_bar()
            # Handle current unit's turn
            self.handle_turn()

            #Show Info panel
            self.draw_info_panel()
            

            #draw HUD
            

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
# Run the game
if __name__ == "__main__":
    Game().run()


#make grid have 3 different maps , everything related to grid stays in grid and make ice make you slower next round (less range) , and add a hiding place that we can use as a dmg boost if you hit from it
#make an ability class that has a name, description, and a function that gets called when the ability is used and a lot of attributes
#take the turn handler to a diffrent class ?
# create a HUD as a class
# add pick ups class
# take in rnage verification to game instead of unit , so resolve attack checks all the enviromeent and confirms if we attack , and attack method only works after we confim that so it just modifies the hp and effects...
# i want the highlight for range to also be like the attack so the move phase only the cursor for target position moves than when we confirm , the unit snaps to that posotion
# verify all conditions after creating TP and healings and effects 

# add objective class it has a nexus also red and blue monster  (red and blue monster spawn once each 6 rounds)
# each team has 2 keys 1 on each player and the third is hidden in a monster ( 2 keys 2 buffs , 1 for each team and there are 3 monsters total ) and one that spawns randomly
# once u have 3 keys of the enemy (1 from monster 1 random and 1 from killing them) the barriere disappears and their nexus is visible and u can hit it )
# game ends with nexus exploding 
# USE INHERETENCE FOR TILES UNITS AND ABILITIES to let the main class focus on basic tasks and add more complexity



#work to do tomorrow
#take the info panel to interface if possible
#1st thing to do tmrrw morning : and add some pick ups && reacting to attacks (maybe make monsters and base to inheretance) and also fix all the attacking methods to remove what's redandent
#2nd thing is creating an ability class and surely use inheretence 
#create split screen
#5th check if i want to make a cursor for moving phase , if yes i need to fix the move method so it is generalised bcs the unit will snap right in (so both fct tell me im not in a good spot , but if i need to call move without handler i'll be fine)
#6th make subclasses 
#add reviving system and lvl system but the pickups will tend to be closer to the losing team 
# after killing  buff add an animation that covers eveyrhting and shows what the buff gave you

#if u jump into a bush and there is a unit there u die bcs u get assassinated