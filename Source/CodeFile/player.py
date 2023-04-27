import pygame
from Source.CodeFile.Utility import Timer

class Player:
    def __init__(self, start_co: tuple):
        self.max_hp = 10
        self.hp = 10
        self.last_damage_source = ""
        self.sprite_x = start_co[0] - 15
        self.sprite_y = start_co[1] - 15
        self.colision_rect = pygame.rect.Rect(start_co[0], start_co[1], 30, 34)
        self.sprite = pygame.image.load('Source/img/player/vaisseau/spr_04_player_spaceship.png').convert_alpha()
        self.overheat_sprite = pygame.image.load('Source/img/player/vaisseau/spr_43_player_broken_spaceship.png').convert_alpha()
        self.base_point_overheat = 45
        self.point_overheat = self.base_point_overheat
        self.is_overheat = False
        self.is_overdrive = False
        self.overdrive_timer = Timer(25*60) 
        self.bullet_sprite = pygame.image.load('Source/img/player/vaisseau/spr_05_player_bullet.png').convert_alpha()
        self.hp_bar = (pygame.image.load('Source/img/player/hp_bar/spr_13_player_health_bar_full.png').convert_alpha(), pygame.image.load('Source/img/player/hp_bar/spr_14_player_health_bar_half.png').convert_alpha(), pygame.image.load('Source/img/player/hp_bar/spr_15_player_health_bar_empty.png').convert_alpha())
        self.hp_bar = (pygame.transform.rotate(self.hp_bar[0], 90), pygame.transform.rotate(self.hp_bar[1], 90), pygame.transform.rotate(self.hp_bar[2], 90),)
        self.hp_bar = (pygame.transform.scale(self.hp_bar[0], ((207/455)*60, 60)), pygame.transform.scale(self.hp_bar[1], ((207/455)*60, 60)), pygame.transform.scale(self.hp_bar[2], ((207/455)*60, 60)))
        self.upgrade_dict = {
            'simple': {
                'untoggle': pygame.image.load('Source/img/player/Upgrade/spr_06_upgrade_x1.png').convert_alpha(),
                'toggle': pygame.image.load('Source/img/player/Upgrade/spr_07_upgrade_x1_toggled.png').convert_alpha()
            },
            'double': {
                'untoggle': pygame.image.load('Source/img/player/Upgrade/spr_08_upgrade_x2.png').convert_alpha(),
                'toggle': pygame.image.load('Source/img/player/Upgrade/spr_09_upgrade_x2_toggled.png').convert_alpha()
            },
            'diagonal': {
                'untoggle': pygame.image.load('Source/img/player/Upgrade/spr_10_upgrade_x8.png').convert_alpha(),
                'toggle': pygame.image.load('Source/img/player/Upgrade/spr_11_upgrade_x8_toggled.png').convert_alpha()
            },
        }
        self.invincibility_timer = 0
        self.x_velocity = 0
        self.y_velocity = 0
        self.timer_bullets = 0
        self.bullets = []
        self.bullets_velocity = []
        self.shot_mode = 0
        self.recul_x = 0
        self.recul_y = 0
        self.dead = False
        self.overdive_song = pygame.mixer.Sound('Source/music/msc_06_overdrive.ogg')
    
    def overdrive(self):
        self.is_overdrive = True
        self.point_overheat = self.base_point_overheat
        self.overdrive_timer.restart()
        pygame.mixer.music.stop()
        pygame.mixer.Channel(14).play(self.overdive_song)
        
    def move(self, top_limit):
        """Deplace le personage"""
        self.colision_rect.x += self.x_velocity
        self.colision_rect.y += self.y_velocity
        if self.colision_rect.x > 590:
            self.colision_rect.x = 590
        elif self.colision_rect.x < 15:
            self.colision_rect.x = 15
        if self.colision_rect.y > 670:
            self.colision_rect.y = 670
        elif self.colision_rect.y < top_limit:
            self.colision_rect.y = top_limit
        self.sprite_x = self.colision_rect.x - 15
        self.sprite_y = self.colision_rect.y - 15
    
    def delete_bullet(self, indice):
        self.bullets.pop(indice)
        self.bullets_velocity.pop(indice)

    def unoverdrive(self):
        self.is_overdrive = False
        self.overdive_song.stop()
        pygame.mixer.music.play(loops=-1)

    def take_damage(self, damage_taken: int, invincibility: int, damage_source: str) -> None:
        assert damage_taken > 0, "Les dégats doivent être positif"
        if self.invincibility_timer == 0:
            self.hp -= damage_taken
            if self.hp < 0:
                self.hp = 0
            self.invincibility_timer = invincibility
            self.last_damage_source = damage_source

    def shot(self, bullet_type: str):
        if bullet_type == 'simple':
            self.bullets.append(pygame.rect.Rect(self.colision_rect.x+ 13, self.colision_rect.y - 15, 5, 5))
            self.bullets_velocity.append((0, -10))
        if bullet_type == 'double':
            self.final_achievement = False
            self.bullets.append(pygame.rect.Rect(self.colision_rect.x- 5, self.colision_rect.y - 10,  5, 5))
            self.bullets.append(pygame.rect.Rect(self.colision_rect.x+ 28, self.colision_rect.y - 10,  5, 5))
            self.bullets_velocity.append((0, -10))
            self.bullets_velocity.append((0, -10))
        if bullet_type == 'diagonal':
            self.final_achievement = False
            self.bullets.append(pygame.rect.Rect(self.colision_rect.x, self.colision_rect.y - 10,  5, 5))
            self.bullets.append(pygame.rect.Rect(self.colision_rect.x+ 28, self.colision_rect.y - 10,  5, 5))
            self.bullets.append(pygame.rect.Rect(self.colision_rect.x- 12, self.colision_rect.y + 34,  5, 5))
            self.bullets.append(pygame.rect.Rect(self.colision_rect.x+ 38, self.colision_rect.y + 34,  5, 5))
            self.bullets.append(pygame.rect.Rect(self.colision_rect.x+ 13, self.colision_rect.y - 15,  5, 5))
            self.bullets.append(pygame.rect.Rect(self.colision_rect.x- 10, self.colision_rect.y,  5, 5))
            self.bullets.append(pygame.rect.Rect(self.colision_rect.x+ 65, self.colision_rect.y,  5, 5))
            self.bullets.append(pygame.rect.Rect(self.colision_rect.x+ 13, self.colision_rect.y + 34,  5, 5))
            self.bullets_velocity.append((-10, -10))
            self.bullets_velocity.append((10, -10))
            self.bullets_velocity.append((-10, 10))
            self.bullets_velocity.append((10, 10))
            self.bullets_velocity.append((0, -10))
            self.bullets_velocity.append((-10, 0))
            self.bullets_velocity.append((10, 0))
            self.bullets_velocity.append((0, 10))

    def bullet_move(self):
        off_screens = []
        for i in range(len(self.bullets)):
            self.bullets[i].x += self.bullets_velocity[i][0]
            self.bullets[i].y += self.bullets_velocity[i][1]
            if 800 < self.bullets[i].y or self.bullets[i].y < -20 or 660 < self.bullets[i].x or self.bullets[i].x < -20:
                off_screens.append(i)
        off_screens.sort(reverse=True)
        for bullet in off_screens:
            self.delete_bullet(bullet)
            off_screens.pop(0)

    def get_colonne(self):
        for i in range(6):
            if 0 + (i*106) <= self.colision_rect.x + 15 <= 106 + (i*106):
                return i

    def get_line(self):
        for i in range(15):
            if 0 + (i*53) <= self.colision_rect.y <= 53 + (i*53):
                return i

    def timer_decrease(self):
        if self.timer_bullets != 0:
            self.timer_bullets -= 1

        if self.is_overdrive:
            timeout = self.overdrive_timer.tick()
            if timeout:
                self.unoverdrive()
        
        if self.invincibility_timer != 0:
            self.invincibility_timer -= 1

    def recul(self):
        self.colision_rect.x+= self.recul_x
        self.colision_rect.y += self.recul_y
        if self.recul_x > 0:
            self.recul_x -= 1
        elif self.recul_x < 0:
            self.recul_x += 1
        if self.recul_y > 0:
            self.recul_y -= 1
        if self.recul_y < 0:
            self.recul_y += 1
        self.sprite_x = self.colision_rect.x - 15
        self.sprite_y = self.colision_rect.y - 15