import pygame

class Sounds:
    def __init__(self):
        """
        Initialise le gestionnaire de sons et prépare le dictionnaire de sons.
        """
        pygame.mixer.init()
        self.sounds = {
            "menu_music":pygame.mixer.Sound("sounds/menu_music.mp3"),
            "ashe_arrow": pygame.mixer.Sound("sounds/ashe_arrow.mp3"),
            "ashe_arrow2": pygame.mixer.Sound("sounds/ashe_arrowattack.mp3"),
            "ashe_killing":pygame.mixer.Sound("sounds/ashe_attack.ogg"),
            "blood":pygame.mixer.Sound("sounds/blood.mp3"),
            "charge":pygame.mixer.Sound("sounds/charge.mp3"),
            "darius_attack":pygame.mixer.Sound("sounds/darius_attack.ogg"),
            "darius_attack2":pygame.mixer.Sound("sounds/darius_attack2.ogg"),
            "darius_laugh":pygame.mixer.Sound("sounds/darius_laugh.ogg"),
            "darius_death":pygame.mixer.Sound("sounds/darius_death.ogg"),
            "potion":pygame.mixer.Sound("sounds/potion_sound.mp3"),
            "rengar_attack":pygame.mixer.Sound("sounds/rengar_attack.ogg"),
            "rengar_attack2":pygame.mixer.Sound("sounds/rengar_attack2.ogg"),
            "rengar_comeon":pygame.mixer.Sound("sounds/rengar_comeon.ogg"),
            "rengar_hunt":pygame.mixer.Sound("sounds/rengar_hunt.ogg"),
            "rengar_roar":pygame.mixer.Sound("sounds/rengar_roar.ogg"),
            "rengar_roarbattle":pygame.mixer.Sound("sounds/rengar_roarbattle.ogg"),
            "rengar_savagery":pygame.mixer.Sound("sounds/rengar_savagery.ogg"),
            "bomb":pygame.mixer.Sound("sounds/smite-101soundboards.mp3"),
            "soraka_attack":pygame.mixer.Sound("sounds/soraka_attack.ogg"),
            "soraka_death":pygame.mixer.Sound("sounds/soraka_death.ogg"),
            "soraka_starcall":pygame.mixer.Sound("sounds/soraka_starcall.ogg"),
            "soraka_wish":pygame.mixer.Sound("sounds/soraka_wish.ogg"),
            "sword":pygame.mixer.Sound("sounds/sword.wav"),
            "selection":pygame.mixer.Sound("sounds/selection.mp3"),
            "moving":pygame.mixer.Sound("sounds/moving.mp3"),
            "game_music": pygame.mixer.Sound("sounds/game_music.mp3"),


        }


    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def set_volume(self, sound_name, volume):
        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(volume)
    
    def stop(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()
    
