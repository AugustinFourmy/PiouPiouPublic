import random

import pygame
from Source.CodeFile.Enemies.Attack import Attack
from Source.CodeFile.Enemies.enemies import Alien
from Source.CodeFile.GameConstant import ENEMY_HEIGHT, ENEMY_VERTICAL_LIMIT, ENEMY_WIDTH
from Source.CodeFile.Utility import Timer
from Source.CodeFile.player import Player


class BlackAlienAttack(Attack):
    bullet_velocite_list = [
            [(0, 6), (3, 6), (6, 6), (-3, 6), (-6, 6)],
            [(6, 6), (0, 6), (-6, 6)],
            [(0, 6)]
        ]
    bullet_num_list = [5, 3, 1]

    def __init__(self, bullet_list, list_velocity):
        Attack.__init__(self,
                        pygame.transform.scale(
                            pygame.image.load("Source/img/enemies/spr_28_alien_bullet.png"),
                            (10, 44)))
        self.bullet_list = bullet_list
        self.bullet_velocite = list_velocity
        self.bullet_spawn_delais = Timer(30, looping=True)
        self.reversed = False
        self.started = False
        self.current_index = 0

    def spawn_bullet_wave(self, alien):
        for i in range(self.bullet_num_list[self.current_index]):
            self.bullet_list.append(
                pygame.rect.Rect(alien.x + ENEMY_WIDTH // 2, alien.y + ENEMY_HEIGHT // 2, 10, 44)
            )
            self.bullet_velocite.append(self.bullet_velocite_list[self.current_index][i])
        if self.current_index != 0:
            self.current_index += int(1 * (self.current_index/abs(self.current_index)))
        else:
            self.current_index += 1

    def new(self, reverse: bool, alien) -> None:
        self.current_index = -1 if reverse else 0
        self.spawn_bullet_wave(alien)
        self.bullet_spawn_delais.restart()
        self.reversed = reverse
        self.started = True

    def delete_bullet(self, identifiant: int):
        self.bullet_list.pop(identifiant)
        self.bullet_velocite.pop(identifiant)
    
    def draw(self, screen_buffer):
        for bullet in self.bullet_list:
            screen_buffer.blit(self.sprite, (bullet.x, bullet.y))
            
    
    def clear(self) -> None:
        self.started = False
        self.current_index = 0
        self.reversed = False

    def update(self, player: Player, alien) -> None:
        if self.started:
            timeout = self.bullet_spawn_delais.tick()
            if timeout:
                if self.current_index < len(self.bullet_num_list) and not self.reversed:
                    self.spawn_bullet_wave(alien)
                elif self.current_index > -1 * len(self.bullet_num_list) - 1 and self.reversed:
                    self.spawn_bullet_wave(alien)
                else:
                    self.clear()

class BlackAlien(Alien):
    def __init__(self, colonne: int, y: int, bullet_list: list, velocities: list) -> None:
        Alien.__init__(self, 45, colonne, -10, hard_y=y)
        self.y = y

        self.collision_rect.x, self.collision_rect.y = self.x, self.y
        self.damaged_sprite = pygame.transform.scale(
            pygame.image.load("Source/img/enemies/spr_26_alien_damage.png"),
            (ENEMY_WIDTH, ENEMY_HEIGHT)
        ).convert_alpha()

        self.sprite = pygame.transform.scale(
            pygame.image.load("Source/img/enemies/spr_27_alien_shadow.png"),
            (ENEMY_WIDTH, ENEMY_HEIGHT)
        ).convert_alpha()
        self.attaque = BlackAlienAttack(bullet_list, velocities)
        self.attaque_timer = Timer(360, looping=True)
    
    def update(self, player) -> None:
        if self.is_invincible:
            self.invincibility_decrease()
        if self.y <= ENEMY_VERTICAL_LIMIT:
            self.move()
        collided_bullet = self.collision_rect.collidelist(player.bullets)
        if collided_bullet != -1 and not self.is_invincible:
            self.invincibility_timer = 2
            self.is_invincible = True
            self.hp -= 1
            player.delete_bullet(collided_bullet)
        self.attaque.update(player, self)
        if self.attaque_timer.tick():
            self.attaque.new(bool(random.randint(0, 1)), self)

    def draw(self, screen_buffer):
        self.attaque.draw(screen_buffer)
        if self.is_invincible:
            screen_buffer.blit(self.damaged_sprite, (self.x, self.y))
        else:
            screen_buffer.blit(self.sprite, (self.x, self.y))


class SpawnAttack(Attack):
    def __init__(self, poing):
        Attack.__init__(self)
        self.poing = poing
        self.velocite = pygame.Vector2(0, 0)
        self.comming_back = False
        self.boss = None
        self.target_colonne = 0
        self.started = False

    def clear(self) -> None:
        self.poing.collision_rect.x = self.poing.start_point[0]
        self.poing.collision_rect.y = self.poing.start_point[1]
        self.velocite = pygame.Vector2()
        self.comming_back = False
        self.started = False
        self.target_colonne = 0
        self.poing.retourner = False
        self.poing.liste_de_point = []
        self.poing.drawing_sprite = self.poing.sprite.convert_alpha()

    def new(self, player, boss) -> bool:
        self.boss = boss
        spawning_colone = player.get_colonne()
        if spawning_colone in self.boss.colonne_taken or len(self.boss.aliens) == 2:
            return False

        speed = 3
        self.target_colonne = spawning_colone

        self.velocite.y = 350 - self.poing.collision_rect.y
        self.velocite.x = int(((spawning_colone * 106 - self.poing.collision_rect.x) / self.velocite.y) * speed)
        self.velocite.y = (self.velocite.y / abs(self.velocite.y)) * speed
        self.started = True
        self.poing.retourner = True
        return True

    def update(self, *a) -> bool:
        self.poing.collision_rect.x += self.velocite.x
        self.poing.collision_rect.y += self.velocite.y
        
        self.poing.point_placement()
        
        if int(self.poing.collision_rect.x) in range(int(self.target_colonne * 106 - 25), int(self.target_colonne * 106 + 25)) \
                and not self.comming_back:
            self.velocite = -1/2 * self.velocite
            self.boss.aliens.append(BlackAlien(self.target_colonne, int(350), self.poing.bullets, self.poing.velocities))
            self.boss.colonne_taken.append(self.target_colonne)
            self.comming_back = True
        if self.poing.collision_rect.y in range(self.poing.start_point[1] - 30, self.poing.start_point[1] + 30)\
                and self.comming_back:
            self.clear()
            return False
        return True
