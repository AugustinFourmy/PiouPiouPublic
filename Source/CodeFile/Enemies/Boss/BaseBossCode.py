import logging

import pygame
from Source.CodeFile.Enemies.Boss.BossHealthBar import HealthBar


class BaseBoss:
    def __init__(self, name, max_hp, x, y):


        # Début du combat

        self.fight_started = False

        # Point de vie

        self.hp_bar = HealthBar(max_hp, name)

        # Position

        self.x = x
        self.y = y

        # Invincivilité

        self.invincibility_time = 0

        # Sprites

        self.sprite_dict = {}
        self.damaged_sprite_id = None

        # Fonction draw

        self.draw_func_list = []
        
    def update(self, *args):
        self.timer_decrease()

    def intro_sequence_update(self) -> bool:
        logging.debug("Pas d'intro de boss")
        return True
    
    def reset(self, hard: bool = False) -> None:
        self.hp_bar.reset()
        if hard:
            self.fight_started = False


    def take_damage(self, damage_value: int, invincibility_value: int) -> None:
        self.invincibility_time = invincibility_value
        self.hp_bar.update_damage(damage_value)
    
    def timer_decrease(self):
        if self.invincibility_time > 0:
            self.invincibility_time -= 1
        self.hp_bar.cooldown_update()


    # Sprites

    def add_sprite(self, sprite_id: str, sprite: pygame.Surface):
        self.sprite_dict[sprite_id] = sprite

    def add_sprite_from_list(self, sprite_list: list[tuple[str, pygame.Surface]]):
        for sprite in sprite_list:
            self.add_sprite(sprite[0], sprite[1])

    def set_damaged_sprite_id(self, sprite_id):
        self.damaged_sprite_id = sprite_id

    #Draw

    def add_draw_element(self, draw_function):
        self.draw_func_list.append(draw_function)

    def add_draw_element_from_list(self, draw_functions):
        for function in draw_functions:
            self.add_draw_element(function)

    def remove_draw_element(self, draw_function):
        backup = []
        for i in range(len(self.draw_func_list)):
            if self.draw_func_list[i] == draw_function:
                backup.append(i)

        backup.sort(reverse=True)

        for elt in backup:
            self.draw_func_list.pop(elt)
            backup.pop(0)

    def remove_draw_element_from_list(self, draw_functions):
        for function in draw_functions:
            self.remove_draw_element(function)

    def draw(self, screen_buffer):
        for draw_function in self.draw_func_list:
            draw_function(screen_buffer)

    def draw_bg(self, screen_buffer):
        pass

    def draw_fg(self, screen_buffer):
        pass