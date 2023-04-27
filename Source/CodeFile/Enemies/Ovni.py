import pygame
import random

class OvniEnemy:
    def __init__(self, colonne, line, speed):
        if colonne < 3:
            self.side = 'left'
            self.x = -106 # Coté gauche de l'écran
        elif colonne >= 3:
            self.side = 'right'
            self.x = 640 + 106
        self.y = line * 53
        self.final_x = colonne * 106
        self.colision_rect = pygame.rect.Rect(self.x, self.y, 106, 53)
        self.end_move = False
        self.draw = True
        self.hp = 30
        self.came_back = False
        self.movement_speed = speed

    def move_to_place(self, retour: bool):
        if not retour:
            if self.side == 'left':
                if self.x + self.movement_speed <= self.final_x:
                    self.x += self.movement_speed
                else:
                    self.x = self.final_x
                    self.end_move = True
            else:
                if self.x - self.movement_speed >= self.final_x:
                    self.x -= self.movement_speed
                else:
                    self.x = self.final_x
                    self.end_move = True
        else:
            if self.side == 'left':
                if self.x - self.movement_speed >= -106:
                    self.x -= self.movement_speed
                else:
                    self.x = -106
                    self.came_back = True
            else:
                if self.x + self.movement_speed <= 640 + 106:
                    self.x += self.movement_speed
                else:
                    self.x = 640 + 106
                    self.came_back = True
        self.colision_rect.x = self.x
        self.colision_rect.y = self.y


class OvniBomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.has_explode = False
        self.base_affichage_timer = 5
        self.affichage_timer = self.base_affichage_timer
        self.explosion_timer = 180 + random.randint(0, 120)
        self.explosion_duration = 60 + random.randint(1, 120)
        self.damage_rect_vertical = None
        self.damage_rect_horizontal = None

    def explode(self):
        self.has_explode = True
        self.damage_rect_horizontal = pygame.rect.Rect(0, self.y, 640, 60)
        self.damage_rect_vertical = pygame.rect.Rect(self.x, 0, 60, 780)

    def get_column(self):
        for i in range(6):
            if 0 + (i * 106) <= self.x <= 106 + (i * 106):
                return i
