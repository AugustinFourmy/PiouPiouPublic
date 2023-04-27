import pygame
import pathlib


class HealthBar:
    def __init__(self, max_hp : int, text: str) -> None:

        self.surface = pygame.surface.Surface((400, int(111*0.607)))

        self.hud_font = pygame.font.Font(pathlib.Path('Source/Font/prstart.ttf'), 16)  # Police pour le HUD(Heads-Up display) du joueur
        self.text = self.hud_font.render(text, True, 'white').convert_alpha()
        self.sprite = pygame.transform.scale(pygame.image.load('Source/img/Boss/spr_30_boss_healthbar.png'), (400, 111 * 0.607)).convert_alpha()

        self.max_hp = max_hp
        self.boss_hp = self.max_hp
        self.hp_loosed = 0
        self.hp_loosed_cd = 5

    def draw(self, screen_buffer: pygame.surface.Surface):
        self.surface.fill((30, 19, 8))
        pygame.draw.rect(self.surface, (229, 127, 229), (15, 0, self.boss_hp * (375 / self.max_hp), 111 * 0.607))
        pygame.draw.rect(self.surface, (239, 180, 239), (15 + self.boss_hp * (375 / self.max_hp), 0, self.hp_loosed * (375 / self.max_hp), 111 * 0.607))
        self.surface.blit(self.sprite, (0, 0))
        self.surface.set_colorkey((30, 19, 8))
        screen_buffer.blit(self.text, ((125 + (400 - self.text.get_width()) / 2), 3))
        screen_buffer.blit(self.surface, (120, 20))
    
    def reset(self) -> None:
        self.boss_hp = self.max_hp

    def update_damage(self, damage_value: int):
        self.boss_hp -= damage_value
        self.hp_loosed += damage_value
        self.hp_loosed_cd = 5

    def cooldown_update(self):
        if self.hp_loosed_cd != 0:
            self.hp_loosed_cd -= 1
        elif self.hp_loosed - self.max_hp / 200 >= 0:
            self.hp_loosed -= self.max_hp / 200
        else:
            self.hp_loosed = 0
