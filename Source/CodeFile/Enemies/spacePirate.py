
import pygame
from Source.CodeFile import Utility
from Source.CodeFile.Enemies.Attack import Attack
from Source.CodeFile.Enemies.enemies import Enemy
from Source.CodeFile.GameConstant import LASER_HIGH_SPEED_BOOST, LASER_BASE_SPEED


class SpacePirate(Enemy):
    def __init__(self, hp: int, colonne: int, shoot_speed):
        Enemy.__init__(self, hp, colonne, '#AAAAAA', (colonne * 106, 6), (102, 53), shoot_speed)
        self.attack = CornerLaserAttack(self)
    
    def move(self):
        Enemy.move(self)
        self.attack.follow_sp(self.y)
        

    def __str__(self):
        return f"Pirate de l'espace avec {self.hp} pv"


class CornerLaserAttack(Attack):
    def __init__(self, sp_pirate: SpacePirate):
        Attack.__init__(self)
        self.sp_pirate = sp_pirate
    
    def new(self, player, fast: bool):
        target_x = player.sprite_x + 30  # 60/54
        target_y = player.sprite_y + 27
        vertical_hitbox = pygame.rect.Rect(self.sp_pirate.x + 51, self.sp_pirate.y + 55, 4, 0)
        horizontal_hitbox = pygame.rect.Rect(self.sp_pirate.x + 51, target_y - 2, 0, 4)
        end_duration_timer = Utility.Timer(10)
        direction = (target_x - horizontal_hitbox.x)/abs(target_x - horizontal_hitbox.x)
        assert direction in (1, -1), f"{direction}"
        self.bullet_list.append((vertical_hitbox, horizontal_hitbox, target_y, direction, int(fast), end_duration_timer))
    
    def follow_sp(self, sp_y):
        for bullet in self.bullet_list:
            bullet[0].h -= sp_y - bullet[0].y + 55
            bullet[0].y = sp_y + 55
        
    
    def update(self, screen_width: int, player):
        backup = []
        for i in range(len(self.bullet_list)):
            if self.bullet_list[i][0].y + self.bullet_list[i][0].h + LASER_BASE_SPEED + self.bullet_list[i][4]*LASER_HIGH_SPEED_BOOST < self.bullet_list[i][2]:
                self.bullet_list[i][0].h += LASER_BASE_SPEED + self.bullet_list[i][4]*LASER_HIGH_SPEED_BOOST
            elif self.bullet_list[i][2] - self.bullet_list[i][0].y - 2 > self.bullet_list[i][0].h > self.bullet_list[i][2] - self.bullet_list[i][0].y + 2:
                self.bullet_list[i][0].h = self.bullet_list[i][2] - self.bullet_list[i][0].y
            elif self.bullet_list[i][2] - self.bullet_list[i][0].y != self.bullet_list[i][0].h:
                self.bullet_list[i][0].h = self.bullet_list[i][2] - self.bullet_list[i][0].y
            elif abs(self.bullet_list[i][1].w + LASER_BASE_SPEED + self.bullet_list[i][4]*LASER_HIGH_SPEED_BOOST) < screen_width:
                if self.bullet_list[i][3] < 0:
                    self.bullet_list[i][1].x -= LASER_BASE_SPEED + self.bullet_list[i][4]*LASER_HIGH_SPEED_BOOST
                self.bullet_list[i][1].w += LASER_BASE_SPEED + self.bullet_list[i][4] * LASER_HIGH_SPEED_BOOST

            else:
                timeout = self.bullet_list[i][5].tick()
                if timeout:
                    backup.append(i)
            if player.colision_rect.colliderect(self.bullet_list[i][0]) or player.colision_rect.colliderect(self.bullet_list[i][1]):
                player.take_damage(
                    2 - self.bullet_list[i][4],
                    60,
                    f"LaserCouder{'Rapide' if self.bullet_list[i][4] else 'Lent'}"
                                   )
                if i not in backup:
                    backup.append(i)

        backup.sort(reverse=True)

        for elt in backup:
            self.bullet_list.pop(elt)

    def draw(self, screen_buffer):
        for bullet in self.bullet_list:
            if bullet[4]:
                pygame.draw.rect(screen_buffer, '#ff0000', bullet[0])
                pygame.draw.rect(screen_buffer, '#ff0000', bullet[1])
            else:
                pygame.draw.rect(screen_buffer, '#ff7300', bullet[0])
                pygame.draw.rect(screen_buffer, '#ff7300', bullet[1])









