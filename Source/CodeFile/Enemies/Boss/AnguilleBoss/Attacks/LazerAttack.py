import pygame
import random

from Source.CodeFile.GameConstant import ANGUILLE_LAZER_SPEED
from Source.CodeFile.Enemies.Attack import Attack
from Source.CodeFile.Utility import Timer
from Source.CodeFile.particle import Particle

class LazerAttack(Attack):
    def __init__(self, boss_object):
        Attack.__init__(self)
        self.v_sprite = pygame.image.load("Source/img/Boss/spr_46_lazer_anguille.png").convert()
        self.h_sprite = pygame.transform.rotate(self.v_sprite, 90.0).convert()
        self.warning_sign = pygame.transform.scale(
            pygame.image.load("Source/img/Ovni/spr_19_ovni_bomb_warning_sign.png"), (70, 54)
        ).convert_alpha()
        self.is_started = False
        self.side = 0
        self.__particle = []
        self.__warning_x = 0
        self.__warning_y = -55
        self.v_hitbox = pygame.rect.Rect(310, 180, 85, 0)
        self.h_hitbox = pygame.rect.Rect(0, 0, 0, 85)
        self.__timer = Timer(300)

    def new(self):
        self.is_started = True

    def update(self, game_instance):
        ended = self.__timer.tick()
        if not ended:
            if self.__timer.getTimeLeft() > 250:
                particule = Particle(15, 'circle', '#fec047', ((random.randint(-11, 11) + 1)/2, (random.randint(-11, 11) + 1)/2), [12, 12], [353 + random.randint(-10, 10), 235 + random.randint(-10, 10)], random.choice(('shrink', 'fade_out')))
                self.__particle.append(particule)
            elif self.__timer.getTimeLeft() == 250:
                self.side = random.randint(0, 1)
                self.h_hitbox.x = self.side * 680
                self.__warning_x = self.side * 580
            else:
                game_instance.screen_shake_duration = 1
                game_instance.screen_shake_intencity = 15
                if self.v_hitbox.height < 615:
                    self.v_hitbox.height += ANGUILLE_LAZER_SPEED
                    self.__warning_y = game_instance.player.colision_rect.y
                elif 180 < self.__timer.getTimeLeft() < 219:
                    self.__warning_y = game_instance.player.colision_rect.y
                elif self.h_hitbox.y == 0:
                    self.h_hitbox.y = game_instance.player.colision_rect.y
                    self.v_hitbox.height += ANGUILLE_LAZER_SPEED
                elif self.h_hitbox.width < 680:
                    if self.side == 1:
                        self.h_hitbox.x -= ANGUILLE_LAZER_SPEED
                    self.h_hitbox.width += ANGUILLE_LAZER_SPEED
                    
        else:
            self.is_started = False
            self.__timer.restart()
            self.v_hitbox.height = 0
            self.h_hitbox.width = 0
            self.__warning_y = -55
            self.h_hitbox.y = 0
        backup = []
        for i in range(len(self.__particle)):
            self.__particle[i].update()
            if self.__particle[i].get_dead():
                backup.append(i)
        
        backup.sort(reverse=True)
        
        for elt in backup:
            self.__particle.pop(elt)
            backup.pop(0)
        
        return ended

    def clear(self) -> None:
        self.v_hitbox.height = 0
        self.h_hitbox.width = 0
        self.is_started = False

    def draw(self, screen_buffer):
        if self.is_started:
            if self.h_hitbox.width < 1:
                screen_buffer.blit(self.warning_sign, (self.__warning_x, self.__warning_y))
            for i in range(self.v_hitbox.height):
                screen_buffer.blit(self.v_sprite, (self.v_hitbox.x, self.v_hitbox.y + i))
            for i in range(self.h_hitbox.width):
                screen_buffer.blit(self.h_sprite, (self.h_hitbox.x + i, self.h_hitbox.y))
            for particle in self.__particle:
                particle.draw(screen_buffer)
