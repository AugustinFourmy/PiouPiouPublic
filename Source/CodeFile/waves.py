import logging
import random
import pygame
from Source.CodeFile.Enemies.Boss.BaseBossCode import BaseBoss as Boss
from Source.CodeFile.dialogue_system import DialogueHandler

class Wave:
    def __init__(self,
                 boss_wave: bool,
                 big_font: pygame.font.Font,
                 small_font: pygame.font.Font,
                 vague_num: int = 0,
                 green: int = 0,
                 yellow: int = 0,
                 red: int = 0,
                 sp: int = 0,
                 shoot_speed: int = 180,
                 ovni_frequency: int = -1,
                 ovni_sp: int = 0,
                 spawn_delais: int = 0,
                 boss: Boss = None,
                 has_starting_dialogue: bool = False,
                 dialogue_id: str = None,
                 ):

        assert (has_starting_dialogue and dialogue_id is not None)\
             or not has_starting_dialogue,\
             "Il y a besoin d'un id de dialogue"
        
        self.dialogue_id = dialogue_id
        self.has_starting_dialogue = has_starting_dialogue
        self.is_playing_dialogue = has_starting_dialogue

        self.is_started = False
        self.boss_wave = boss_wave
        self.num = vague_num
        if self.boss_wave:
            self.small_wave_txt = small_font.render("Boss", True, "#ffffff").convert_alpha()
            self.boss = boss
        else:
            self.small_wave_txt = small_font.render(f"Vague {vague_num}", True, '#ffffff').convert_alpha()
        self.enemies_type = [0 for _ in range(green)] + [1 for _ in range(yellow)] + [2 for _ in range(red)] + [3 for _ in range(sp)]
        self.__enemies_type_tuple = tuple(self.enemies_type)
        random.shuffle(self.enemies_type)
        self.enemies_shoot_speed = shoot_speed
        self.enemies_spawn_delais = spawn_delais
        self.ovni_frequency = ovni_frequency
        self.ovni_speed = ovni_sp
        self.big_txt_y = - 72
        self.timer_intro_txt = 60
        self.opacite = 255
        self.big_wave_txt = big_font.render(f"Vague {vague_num}", True, '#dddddd').convert_alpha()

    def intro_seq(self):
        if self.boss_wave:
            self.is_started = self.boss.intro_sequence_update()
        else:
            if self.big_txt_y < 340:
                self.big_txt_y += 4
            elif self.timer_intro_txt > 0:
                self.timer_intro_txt -= 1
            elif self.timer_intro_txt <= 0 and self.opacite != 0:
                self.opacite -= 5
                self.big_wave_txt.set_alpha(self.opacite)
                self.big_wave_txt.convert_alpha()
            elif self.opacite == 0:
                self.is_started = True

    def load_dialogue(self, dialogue_handler: DialogueHandler):
        if self.is_playing_dialogue:
            dialogue_handler.play_dialog(self.dialogue_id)
        logging.info(f"Dialogue de la Vague {self.num} charger")
    
    def reset(self, hard: bool = False):
        self.enemies_type = list(self.__enemies_type_tuple)
        if not self.boss_wave:
            self.big_txt_y = -72
            self.timer_intro_txt = 60
            self.opacite = 255
            self.big_wave_txt.set_alpha(255)
            
        self.is_started = False

        if hard:
            self.is_playing_dialogue = self.has_starting_dialogue

