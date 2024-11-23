import pygame
import random
from unit import Unit
from interface import Tile,Grid,Highlight 


# Constants
GRID_SIZE = 21
CELL_SIZE = 40
SCREEN_WIDTH, SCREEN_HEIGHT = CELL_SIZE * GRID_SIZE + 300, CELL_SIZE * GRID_SIZE
FPS = 60

# Load assets

def load_textures():
    """Load textures for different terrain and overlays."""
    return {
        "grass": [pygame.image.load("assets/grass4.jpg")],
        "water": pygame.image.load("assets/water.jpg"),
        "rock": pygame.image.load("assets/rock.jpg"),
        "bush": pygame.image.load("assets/bush.png"),
        "barrier": pygame.image.load("assets/barrier.png"),
        "nexus": pygame.image.load("assets/nexus.png"),
    }
def load_unit_images():
    return {
        "ashe": "assets/ashe.png",
        "garen": "assets/garen.png",
        "darius": "assets/darius.png",
        "soraka": "assets/soraka.png",
        "barrier": "assets/barrier.jpg"
    }
def load_indicators():
    return {
        "indicator": pygame.image.load("assets/indicator.png"),
    }


# Game class
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tactical Grid Game")
        self.clock = pygame.time.Clock()
        self.unit_images = load_unit_images()
        self.indicators = load_indicators()
        self.textures=load_textures()
        self.grid = Grid(GRID_SIZE, self.textures)
        self.units = self.create_units()
        self.current_unit_index = 0
        self.last_turn_time = 0  # Initialize turn delay tracking
        self.last_move_time = 0  # Timestamp of the last movement
        self.last_action_time = 0  # Timestamp of the last attack movement to target


        self.visible_tiles = set()
        
        starting_team_color = self.units[self.current_unit_index].color
        Highlight.update_fog_visibility(self,starting_team_color)  # Pre-calculate fog for the starting team

        # Initialize event log
        self.event_log = []

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


    def create_units(self):
        """Create units and place them on the grid."""
        
        return [
            Unit(16, 4, "Ashe", 700, 170, self.unit_images["ashe"], (0, 0, 255),3,2),  # Blue team
            Unit(4, 17, "Garen", 1300, 60, self.unit_images["garen"], (0, 0, 255),3,2),  # Blue team
            Unit(16, 3, "Darius",1090, 80,self.unit_images["darius"], (255, 0, 0),3,2),  # Red team
            Unit(17, 4, "Soraka",490, 50 ,self.unit_images["soraka"], (255, 0, 0),3,2),  # Red team
            Unit(10, 10, "Monstera",390, 50 ,self.unit_images["barrier"], (255, 10, 0),0,0),  
            Unit(5, 7, "Monsterb",390, 50 ,self.unit_images["barrier"], (255, 10, 0),0,0),  
            Unit(15, 13, "Monsterc",390, 50 ,self.unit_images["barrier"], (255, 10, 0),0,0), 

        ]
    


    def draw_units(self):
        """Draw all units on the grid with visibility logic."""
        current_team_color = self.units[self.current_unit_index].color

        for index, unit in enumerate(self.units):
            if unit.alive:
                is_current_turn = (index == self.current_unit_index)  # Check if it's the current unit's turn
                # Draw units only if they belong to the current team or are in visible tiles
                if unit.color == current_team_color or (unit.x, unit.y) in self.visible_tiles:
                    unit.draw(self.screen, is_current_turn=is_current_turn)




    def resolve_attack(self, unit):
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
                damage=unit.attack(other_unit)  # Use the Unit's attack method
                if damage > 0:
                    self.log_event(
                        f"{unit.name} attacked {other_unit.name} for {damage} damage!"
                    )
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
                and (self.units[self.current_unit_index].color==(255,0,0) or self.units[self.current_unit_index].color==(0,0,255))):
                break

            # If we've cycled through all units and come back to the start, stop (prevents infinite loops)
            if self.current_unit_index == start_index:
                print("No alive units remaining!")
                return


    
    def handle_turn(self):
        """Handle movement and attacks for the current unit."""
        current_time = pygame.time.get_ticks()
        current_unit = self.units[self.current_unit_index]

        
        keys = pygame.key.get_pressed()
        
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
                elif keys[pygame.K_RETURN]:
                    if not any(
                        unit.x == current_unit.x and unit.y == current_unit.y and unit != current_unit
                        and unit.alive for unit in self.units 
                    ):  
                        print(f"{current_unit.name} finalized move at ({current_unit.x}, {current_unit.y}).")
                        current_unit.state = "attack"
                        current_unit.target_x, current_unit.target_y = current_unit.x, current_unit.y  # Initialize cursor
                        next_team_color = self.units[self.current_unit_index].color
                        Highlight.update_fog_visibility(self,next_team_color)
                    else:
                        print("Cannot finalize move: Another unit is already occupying this position.")
                    
        # Attack Phase
        elif current_unit.state == "attack":
            if current_time - self.last_move_time > 100:  # Delay of 100ms between movements
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

            # Confirm attack
            if keys[pygame.K_SPACE] and current_time - self.last_action_time > 100:
                self.resolve_attack(current_unit)
                self.last_action_time = current_time
                current_unit.state = "done"  # Mark attack as finished

        # End Turn
        if  current_unit.state == "done" and current_time - self.last_turn_time > 1000:
            self.last_turn_time = current_time  # Update the last turn time
            current_unit.state = "move"  # Reset state for the next turn
            current_unit.initial_x, current_unit.initial_y = current_unit.x, current_unit.y  # Reset initial position
            #self.current_unit_index = (self.current_unit_index + 1) % len(self.units)  

            # Advance to the next unit, skipping dead ones

            self.advance_to_next_unit()

            next_team_color = self.units[self.current_unit_index].color
            print(next_team_color)
            Highlight.update_fog_visibility(self,next_team_color)
            # Reset state for the next unit

    
            
    def run(self):
        """Main game loop."""
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
            
            
            self.draw_units()
            # Handle current unit's turn
            
            self.handle_turn()
            self.draw_info_panel()
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
# after done attacking add button so that it doesnt directly go to the enemy team to give me time to look at the impacts i did or to use the vision i gained from the move ability
# i want the highlight for range to also be like the attack so the move phase only the cursor for target position moves than when we confirm , the unit snaps to that posotion

# verify all conditions after creating TP and healings and effects 
# add objective class it has a nexus also red and blue monster  (red and blue monster spawn once each 6 rounds)
# each team has 2 keys 1 on each player and the third is hidden in a monster ( 2 keys 2 buffs , 1 for each team and there are 3 monsters total ) and one that spawns randomly
# once u have 3 keys of the enemy (1 from monster 1 random and 1 from killing them) the barriere disappears and their nexus is visible and u can hit it )
# game ends with nexus exploding 
# USE INHERETENCE FOR TILES UNITS AND ABILITIES to let the main class focus on basic tasks and add more complexity



#work to do tomorrow
#1st thing to do tmrrw morning : try movement cost and bush hiding units (maybe use inheretance) and add some pick ups
#2nd thing is creating an ability class and surely use inheretence 
#3rd create more units 
#4th
#create split screen
#5th check if i want to make a cursor for moving phase , if yes i need to fix the move method so it is generalised bcs the unit will snap right in (so both fct tell me im not in a good spot , but if i need to call move without handler i'll be fine)