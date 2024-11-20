import pygame
import random

# === Constantes ===
CELL_SIZE = 40
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BEIGE = (245, 245, 220)
DARK_GRAY = (50, 50, 50)
BLUE = (0, 0, 200)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
WIDTH, HEIGHT = 1000, 600
GRID_WIDTH = 800
CONSOLE_BG = (30, 30, 30)
CONSOLE_TEXT_COLOR = (200, 200, 200)

# === Classe Skill ===
class Skill:
    def __init__(self, name, power, min_range, max_range, effect):
        self.name = name
        self.power = power
        self.min_range = min_range
        self.max_range = max_range
        self.effect = effect

# === Classe Unit ===
class Unit:
    def __init__(self, x, y, health, team, skills):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health
        self.team = team
        self.skills = skills
        self.is_selected = False

    def move(self, dx, dy, game):
        """Déplace l'unité si la case est traversable."""
        new_x = self.x + dx
        new_y = self.y + dy
        if game.is_traversable(new_x, new_y):
            self.x = new_x
            self.y = new_y

    def use_skill(self, skill, target, game):
        """Utilise une compétence sur une cible."""
        dist = abs(self.x - target.x) + abs(self.y - target.y)
        if skill.min_range <= dist <= skill.max_range:
            if skill.effect == "damage":
                target.health -= skill.power
                game.add_action_message(f"{self.team} utilise {skill.name} sur {target.team}, dégâts : {skill.power}")
                if target.health <= 0:
                    game.add_action_message(f"{target.team} est éliminé !")
                    game.enemy_units.remove(target)
            elif skill.effect == "heal":
                self.health = min(self.health + skill.power, self.max_health)
                game.add_action_message(f"{self.team} utilise {skill.name}, soins : {skill.power}")

    def draw(self, screen):
        """Dessine l'unité avec une barre de vie."""
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        color = RED if self.team == 'enemy' else BLUE
        pygame.draw.circle(screen, color, rect.center, CELL_SIZE // 3)

        if self.is_selected:
            pygame.draw.rect(screen, LIGHT_BLUE, rect, 3)

        # Barre de vie
        health_bar_width = int((self.health / self.max_health) * CELL_SIZE)
        health_bar = pygame.Rect(rect.x, rect.y - 5, health_bar_width, 5)
        pygame.draw.rect(screen, GREEN, health_bar)

# === Classe Game ===
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.grid_width = GRID_WIDTH // CELL_SIZE
        self.grid_height = HEIGHT // CELL_SIZE

        # Compétences
        pistol = Skill("Pistol", power=10, min_range=1, max_range=3, effect="damage")
        heal = Skill("Heal", power=5, min_range=1, max_range=2, effect="heal")
        grenade = Skill("Grenade", power=15, min_range=2, max_range=4, effect="damage")
        fireball = Skill("Fireball", power=20, min_range=2, max_range=5, effect="damage")
        sniper = Skill("Sniper", power=30, min_range=3, max_range=6, effect="damage")

        # Unités
        self.player_units = [
    Unit(0, 0, 20, 'player', [pistol, heal, fireball]),
    Unit(1, 0, 15, 'player', [pistol, grenade, sniper])
]

        
        self.enemy_units = [
            Unit(6, 6, 10, 'enemy', [pistol]),
            Unit(7, 6, 10, 'enemy', [pistol])
        ]

        # Génération de la grille
        self.generate_grid()

        self.selected_unit_index = 0
        self.selected_skill = None
        self.player_units[self.selected_unit_index].is_selected = True
        self.action_messages = []

    def generate_grid(self):
        """Génère la grille avec des murs, tout en dégageant les zones autour des unités."""
        self.grid = [[0 if random.random() > 0.2 else 1 for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        # Dégage une zone autour des unités (joueurs et ennemis)
        units = self.player_units + self.enemy_units
        for unit in units:
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    x, y = unit.x + dx, unit.y + dy
                    if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                        self.grid[y][x] = 0

    def add_action_message(self, message):
        """Ajoute un message à la console."""
        self.action_messages.append(message)
        if len(self.action_messages) > 10:
            self.action_messages.pop(0)

    def is_traversable(self, x, y):
        """Vérifie si une case est traversable."""
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            return self.grid[y][x] == 0
        return False

    def draw_grid(self):
        """Dessine la grille."""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                color = DARK_GRAY if self.grid[y][x] == 1 else BEIGE
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, WHITE, rect, 1)
    def draw_skills_bar(self):
        """Dessine la barre de sélection des compétences."""
        selected_unit = self.player_units[self.selected_unit_index]
        font = pygame.font.SysFont("monospace", 16)
        
        for i, skill in enumerate(selected_unit.skills):
            skill_rect = pygame.Rect(10 + i * 120, 10, 100, 30)
            pygame.draw.rect(self.screen, DARK_GRAY, skill_rect)
            pygame.draw.rect(self.screen, WHITE, skill_rect, 2)
            
            text_surface = font.render(skill.name, True, WHITE)
            self.screen.blit(text_surface, (skill_rect.x + 10, skill_rect.y + 5))
            
            if self.selected_skill == skill:
                pygame.draw.rect(self.screen, LIGHT_BLUE, skill_rect, 3)

    def draw_console(self):
        """Affiche la console des actions."""
        console_rect = pygame.Rect(GRID_WIDTH, 0, WIDTH - GRID_WIDTH, HEIGHT)
        pygame.draw.rect(self.screen, CONSOLE_BG, console_rect)

        font = pygame.font.SysFont("monospace", 16)
        y_offset = 10
        for message in self.action_messages:
            text_surface = font.render(message, True, CONSOLE_TEXT_COLOR)
            self.screen.blit(text_surface, (GRID_WIDTH + 10, y_offset))
            y_offset += 20
    def highlight_skill_range(self, unit, skill):
        if skill:
            for dx in range(-skill.max_range, skill.max_range + 1):
                for dy in range(-skill.max_range, skill.max_range + 1):
                    x = unit.x + dx
                    y = unit.y + dy
                    dist = abs(dx) + abs(dy)
                    if (0 <= x < self.grid_width and
                        0 <= y < self.grid_height and
                        skill.min_range <= dist <= skill.max_range):
                        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(self.screen, LIGHT_BLUE, rect, 2)

    def flip_display(self):
        """Affiche le jeu."""
        self.screen.fill(BLACK)
        self.draw_grid()
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen)

        # Afficher la portée de la compétence sélectionnée
        selected_unit = self.player_units[self.selected_unit_index]
        if self.selected_skill:
            self.highlight_skill_range(selected_unit, self.selected_skill)

        self.draw_skills_bar()  # Ajouter la barre des compétences
        self.draw_console()
        pygame.display.flip()



    def handle_player_turn(self):
        selected_unit = self.player_units[self.selected_unit_index]
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    dx, dy = 0, 0
                    if event.key == pygame.K_LEFT:
                        dx = -1
                    elif event.key == pygame.K_RIGHT:
                        dx = 1
                    elif event.key == pygame.K_UP:
                        dy = -1
                    elif event.key == pygame.K_DOWN:
                        dy = 1
                    selected_unit.move(dx, dy, self)
                    self.flip_display()

                    if event.key == pygame.K_SPACE:
                        selected_unit.is_selected = False
                        self.selected_unit_index = (self.selected_unit_index + 1) % len(self.player_units)
                        self.player_units[self.selected_unit_index].is_selected = True
                        self.selected_skill = None
                        self.flip_display()

                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        skill_index = event.key - pygame.K_1
                        if skill_index < len(selSected_unit.skills):
                            self.selected_skill = selected_unit.skills[skill_index]
                            self.flip_display()


                    elif event.key in [pygame.K_RETURN, pygame.K_z] and self.selected_skill:
                        for enemy in self.enemy_units:
                            dist = abs(selected_unit.x - enemy.x) + abs(selected_unit.y - enemy.y)
                            if self.selected_skill.min_range <= dist <= self.selected_skill.max_range:
                                selected_unit.use_skill(self.selected_skill, enemy, self)
                                self.selected_skill = None
                                self.flip_display()
                                return


    def update(self):
        self.flip_display()

# === Fonction Principale ===
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jeu de stratégie")
    game = Game(screen)

    while True:
        game.handle_player_turn()

if __name__ == "__main__":
    main()
