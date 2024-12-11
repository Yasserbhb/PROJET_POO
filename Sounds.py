import pygame

class Sounds:
    def __init__(self):
        """
        Initialise le gestionnaire de sons et prépare le dictionnaire de sons.
        """
        pygame.mixer.init()
        self.sounds = {
            "menu_music":pygame.mixer.Sound("sounds/menu_music.mp3"),
            #ashe
            "Arrow Shot": pygame.mixer.Sound("sounds/ashe_arrow.mp3"),
            "Frost Arrow": pygame.mixer.Sound("sounds/ashe_arrowattack.mp3"),
            "Ashe Basic Attack":pygame.mixer.Sound("sounds/ashe_attack.ogg"),
            "Healing Wind":pygame.mixer.Sound("sounds/blood.mp3"),
            #garen
            "Charge":pygame.mixer.Sound("sounds/charge.mp3"),
            "Slash":pygame.mixer.Sound("sounds/sword.wav"),
            "Fortify":pygame.mixer.Sound("sounds/justice_garen.mp3"),
            "Garen Basic Attack":pygame.mixer.Sound("sounds/garen_ha.mp3"),

            #darius
            "Darius Basic Attack":pygame.mixer.Sound("sounds/darius_attack.ogg"),
            "Decimate ":pygame.mixer.Sound("sounds/darius_attack2.ogg"),
            "Crippling Strike":pygame.mixer.Sound("sounds/darius_laugh.ogg"),
            "darius_death":pygame.mixer.Sound("sounds/darius_death.ogg"),
            "Noxian Guillotine":pygame.mixer.Sound("sounds/Darius_Original_R_1.ogg"),
            
            "potion":pygame.mixer.Sound("sounds/potion_sound.mp3"),
            #rengar
            "rengar_attack":pygame.mixer.Sound("sounds/rengar_attack.ogg"),
            "rengar_attack2":pygame.mixer.Sound("sounds/rengar_attack2.ogg"),
            "Rengar Come ON":pygame.mixer.Sound("sounds/rengar_comeon.ogg"),
            "Thrill of the Hunt":pygame.mixer.Sound("sounds/rengar_hunt.ogg"),
            "Rengar Basic Attack":pygame.mixer.Sound("sounds/rengar_roar.ogg"),
            "Battle Roar":pygame.mixer.Sound("sounds/rengar_roarbattle.ogg"),
            "Savagery":pygame.mixer.Sound("sounds/rengar_savagery.ogg"),

            "bomb":pygame.mixer.Sound("sounds/smite-101soundboards.mp3"),
            #soraka
            "Soraka Basic Attack":pygame.mixer.Sound("sounds/soraka_attack.ogg"),
            "soraka_death":pygame.mixer.Sound("sounds/soraka_death.ogg"),
            "Starcall":pygame.mixer.Sound("sounds/soraka_starcall.ogg"),
            "Wish":pygame.mixer.Sound("sounds/soraka_wish.ogg"),
            "Astral Infusion":pygame.mixer.Sound("sounds/soraka_astral.ogg"),
            
            "selection":pygame.mixer.Sound("sounds/selection.mp3"),
            "game_music": pygame.mixer.Sound("sounds/game_music.mp3"),


        }


    def play(self, name, loop=0):
        if name in self.sounds:
            self.sounds[name].play(loops=loop)  # Utilise l'option `loops` de pygame


    def set_volume(self, sound_name, volume):
        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(volume)
    
    def stop(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()
    