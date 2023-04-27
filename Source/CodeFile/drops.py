import pygame

class Pile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = pygame.transform.scale(pygame.image.load('Source/img/player/hp_bar/spr_12_heal.png').convert_alpha(), (25, (377/126)*25))
        self.colision_rect = pygame.rect.Rect(self.x, self.y, 25, (377/126)*25)

    def move(self):
        self.y += 0.6
        self.colision_rect.y = self.y

class FragementOverdrive:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.sprite = None
        self.colision_rect = pygame.rect.Rect(self.x, self.y, 32, 32)
    
    def move(self):
        self.y += 0.6
        self.colision_rect.y = self.y
