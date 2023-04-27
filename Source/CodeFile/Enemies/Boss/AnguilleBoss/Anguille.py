import json
import math
import random

import pygame
from Source.CodeFile.GameConstant import ANGUILLE_FIGHT_MUSIC, ANGUILLE_INTRO_MUSIC

from Source.CodeFile.drops import Pile
from Source.CodeFile.Cutscene.cutscene import Cutscene
from Source.CodeFile.Enemies.Boss.BaseBossCode import BaseBoss
from Source.CodeFile.particle import Particle
from Source.CodeFile.player import Player
from Source.CodeFile.Enemies.Boss.AnguilleBoss.Attacks.SideWayAttack import SidewayAttack
from Source.CodeFile.Enemies.Boss.AnguilleBoss.Attacks.HomingAttack import HommingAttack
from Source.CodeFile.Enemies.Boss.AnguilleBoss.Attacks.LazerAttack import LazerAttack


class Anguille(BaseBoss):
    def __init__(self, font: pygame.font.Font):
        BaseBoss.__init__(self, "Anguille", 300, 0, -380) # 300

        # Boss sprites

        _sprite_list = [
            (
                'BossNormal',  pygame.transform.scale(pygame.image.load('Source/img/Boss/Anguille/spr_32_anguille.png'), (251, 295)).convert_alpha()
            ),
            (
                'Damaged', pygame.transform.scale(pygame.image.load('Source/img/Boss/Anguille/spr_34_anguille_hurt.png'), (251, 295)).convert_alpha()
            ),
            (
                'Sleep', pygame.transform.scale(pygame.image.load('Source/img/Boss/Anguille/spr_33_anguille_eye_colosed.png'), (251, 295)).convert_alpha()
            ),
            (
                'Open_Mouse',  pygame.transform.scale(pygame.image.load('Source/img/Boss/Anguille/spr_35_anguille_open_mouse.png'), (251, 295)).convert_alpha()
            ),
            (
                'Open_Mouse_Damaged', pygame.transform.scale(pygame.image.load('Source/img/Boss/Anguille/spr_43_anguille_open_mouse_hurt.png'), (251, 295)).convert_alpha()
            ),
            (
                'Forcefield', pygame.transform.scale(pygame.image.load('Source/img/Boss/Forcefield/spr_37_forcefield.png'), (655, 300)).convert_alpha()
            ),
            (
                'Turret', pygame.transform.scale(pygame.image.load('Source/img/Boss/Turret/spr_39_turret.png'), (99, 113)).convert_alpha()
            ),
            (
                "LeftTurret", pygame.transform.scale(pygame.image.load('Source/img/Boss/Turret/spr_39_turret.png'), (99, 113)).convert_alpha()
            ),
            (
                "RightTurret", pygame.transform.scale(pygame.image.load('Source/img/Boss/Turret/spr_39_turret.png'), (99, 113)).convert_alpha()
            ),
            (
                'BrokenTurret', pygame.transform.scale(pygame.image.load('Source/img/Boss/Turret/spr_40_turret_broken.png'), (99, 113)).convert_alpha()
            ),
            (
                'BulletSmall', pygame.transform.scale(pygame.image.load('Source/img/Boss/spr_29_boss_bullet.png'), (10, 10)).convert_alpha()
            ),
            (
                'BulletMedium', pygame.transform.scale(pygame.image.load('Source/img/Boss/spr_29_boss_bullet.png'), (30, 30)).convert_alpha()
            ),
            (
                'ShadowForcefield', pygame.transform.scale(pygame.image.load('Source/img/Boss/Forcefield/spr_38_forcefield_shadow.png'), (655, 300)).convert_alpha()
            ),
            (
                'ShadowTurret', pygame.transform.scale(pygame.image.load('Source/img/Boss/Turret/spr_41_turret_shadow.png'), (452 * 0.22, 514 * 0.22)).convert_alpha()
            ),
            (
                "FakeBoss", pygame.transform.scale(pygame.image.load('Source/img/enemies/spr_23_alien_green.png'), (106, (119 / 229) * 106)).convert_alpha()
            ),
            (
                "ShadowFakeBoss", pygame.transform.scale(pygame.image.load('Source/img/enemies/spr_27_alien_shadow.png'), (600, 600 * (119 / 229))).convert_alpha()
            )
            ]

        self.add_sprite_from_list(_sprite_list)

        self.y = -400

        # Rectangle de colision

        self.boss_colision_rect = pygame.rect.Rect(170, 0, 290, 295)
        self.turret_colision_rect_left = pygame.rect.Rect(20, 270, 99, 113)
        self.turret_colision_rect_right = pygame.rect.Rect(530, 270, 99, 113)
        self.forcefield_colision_rect = pygame.rect.Rect(119, 250, 411, 50)
        

        # Bullet cinématique

        self.intro_cutscene = Cutscene()
        with open("Source/Cutscenes/Introduction_Boss.json") as f:
            self.intro_cutscene.load_from_json_dict(json.load(f))

        self.add_draw_element(self.draw_boss)
        self.add_draw_element(self.intro_cutscene.draw)

        # Attack

        self.sideway_attack = SidewayAttack(self.sprite_dict['BulletSmall'])
        self.homing_attack = HommingAttack(self.sprite_dict['BulletMedium'], self)
        self.lazer_attack = LazerAttack(self)
        
        self.mega_lazer_delais = 90

        self.homing_attack_cd = 30

        # Boss

        self.turret_data = {
            'left': {
                'pv': 20,
                'invincibility_time': 0,
                'is_broken': False,
                'rotation_angle': 0
            },
            'right':{
                'pv': 20,
                'invincibility_time': 0,
                'is_broken': False,
                'rotation_angle': 0
            }
        }
        self.forcefield_broken = False
        self.turret_actual_sprite_id = {
            'left': 'LeftTurret',
            'right': 'RightTurret'
        }
        self.boss_actual_sprite_id = 'Sleep'
        self.forcefield_regeneration_time = 0
        self.boss_attack_delay = 60
        self.lazer_cd = 0

    def intro_sequence_update(self):
        self.intro_cutscene.play()
        if not self.intro_cutscene.playing:
            self.remove_draw_element(self.intro_cutscene.draw)
            self.y = 0
            return True
        return False

    def calculer_angle_direction_tourelle(self, player: Player, turret: pygame.Rect):
        """
        Fonction qui renvoie l'angle en radiant vers lequel la tourelle doit tirer pour cibler la joueur

        ------------------------------Explication des calcul--------------------------------------------

        Prenons des vecteurs u(x; y) et v (x'; y').

        On a:
                u.v = ||u|| * ||v|| * cos(alpha)
            et
                u.v = x*x' + y*y'
        Ainsi:

            ||u|| * ||v|| * cos(alpha) = x*x' + y*y'
            sqrt(x**2 + y**2) * sqrt(x'**2 + y'**2) * cos(alpha) = x*x' + y*y'
            cos(alpha) = (x*x' + y*y')/(sqrt(x**2 + y**2) * sqrt(x'**2 + y'**2))

        On pose les points :

            A: Centre du joueur
            B: Centre de la tourelle
            C: Point de même abscisse  que le centre du joueur et de même ordonnée que le centre de la trourelle

        Par conséquent : xC = xA et yC = yB

        On remplace:
            - u(x; y)   par (->)BA(xB - xA; yB - yA)
            - v(x'; y') par (->)BC(xC - xB; yC - yB)
 
        Donc:
            cos(alpha) = (   x(->)BA * x(->)BC   +   y(->)BA * y(->)BC)  ) / ( sqrt(   x(->)BA**2 + y(->)BA**2)   * sqrt(  x(->)BC**2  + y(->)BC**2  ))
            cos(alpha) = ( (xA - xB) * (xC - xB) + (yA - yB) * (yC - yB) ) / ( sqrt( (xA - xB)**2 + (yA - yB)**2) * sqrt( (xC - xB)**2 + (yC - yB)**2))
        """

        x_ba = (player.sprite_x + 30) - (turret.x + 50)
        x_bc = 0  # x_bc = (turret.x + 50) - (turret.x + 50) = 0
        y_ba = (player.sprite_y + 27) - (turret.y + 57)
        y_bc = (player.sprite_y + 27) - (turret.y + 57)

        ba = math.sqrt(x_ba ** 2 + y_ba ** 2)
        bc = math.sqrt(x_ba ** 2 + y_bc ** 2)

        numerateur = x_ba * x_bc + y_ba * y_bc
        denominateur = ba * bc

        if denominateur == 0:
            return 0

        return math.degrees(math.acos(numerateur / denominateur))

    def update(self, game_instance):
        BaseBoss.update(self)
        if self.fight_started:
            backup = []

            for i in range(len(game_instance.player.bullets)):  # Parcours toutes les balles du joueur

                a_supprimer = False

                # Collision avec le champs de force

                if not self.forcefield_broken and self.forcefield_colision_rect.colliderect(game_instance.player.bullets[i]):  # Si le rectangle de colision d'une balle entre en colistion avec le rectangle de colistion de l'ennemi
                    backup.append(i)  # On ajoute l'indice de la balle du joueur a la liste de disparition
                    a_supprimer = True

                # Collision avec l'Anguille

                if not a_supprimer and self.boss_colision_rect.colliderect(game_instance.player.bullets[i]) and self.invincibility_time == 0:  # Si le rectangle de colision d'une balle entre en colistion avec le rectangle de colistion de l'ennemi
                    backup.append(i)  # On ajoute l'indice de la balle du joueur a la liste de disparition
                    a_supprimer = True
                    if game_instance.screen_shake_duration <= 0:
                        game_instance.screen_shake_duration = 6
                        game_instance.screen_shake_intencity = 4
                    if self.lazer_attack.is_started:
                        self.boss_actual_sprite_id = 'Open_Mouse_Damaged'
                    else:
                        self.boss_actual_sprite_id = 'Damaged'
                    self.take_damage(1, 5)

                # Collision avec les tourrelle

                destroy = False
                if self.turret_colision_rect_left.colliderect(game_instance.player.bullets[i]) and not a_supprimer:
                    if self.turret_data['left']['invincibility_time'] == 0 and not self.turret_data['left']['is_broken']:
                        if game_instance.screen_shake_duration <= 0:
                            game_instance.screen_shake_duration = 3
                            game_instance.screen_shake_intencity = 4
                        destroy = self.turret_take_damage('left', 3, 1)
                        backup.append(i)
                    elif self.turret_data['left']['is_broken']:
                        backup.append(i)
                    if destroy:
                        for _ in range(random.randint(10, 20)):
                            game_instance.particle_list.append(Particle(20, 'circle', (195, 195, 195),
                                                               (random.randint(-11, 10) + 1, random.randint(-6, 5) + 1,),
                                                               [10, 10], [self.x + 70,
                                                                          self.y + 327],
                                                               'fade_out'))
                        if self.forcefield_broken:
                            for j in range(3):
                                game_instance.pile_liste.append(Pile(213 + j*106, 315))
                            
                elif not a_supprimer and self.turret_colision_rect_right.colliderect(game_instance.player.bullets[i]):
                    if self.turret_data['right']['invincibility_time'] == 0 and not self.turret_data['right']['is_broken']:
                        if game_instance.screen_shake_duration <= 0:
                            game_instance.screen_shake_duration = 3
                            game_instance.screen_shake_intencity = 4
                        destroy = self.turret_take_damage('right', 3, 1)
                        backup.append(i)
                    elif self.turret_data['right']['is_broken']:
                        backup.append(i)

                    if destroy:
                        for _ in range(random.randint(10, 20)):
                            game_instance.particle_list.append(Particle(20, 'circle', (195, 195, 195),
                                                               (random.randint(-11, 10) + 1, random.randint(-6, 5) + 1,),
                                                               [10, 10], [self.x + 580,
                                                                          self.y + 327],
                                                               'fade_out'))
                        if self.forcefield_broken:
                            for j in range(3):
                                game_instance.pile_liste.append(Pile(213 + j*106, 315))

            backup.sort(reverse=True)  # On inverse tri les valeur dans l'ordre decroissant pour faire disparaitre celle avec la valeur la plus haute d'abord (sinon il y a une erreur pop index out of range)

            for elt in backup:  # Pour tous les elements de la liste de disparition
                game_instance.player.delete_bullet(elt)  # On supprime la balles d'indice elt

            # Rebond du joueur sur les tourelles

            if not self.forcefield_broken:
                if game_instance.player.colision_rect.collidelist((self.turret_colision_rect_left, self.turret_colision_rect_right)) > -1:
                    game_instance.player.recul_x = -3 * game_instance.player.x_velocity
                    game_instance.player.recul_y = -3 * game_instance.player.y_velocity

            angle = self.calculer_angle_direction_tourelle(game_instance.player, self.turret_colision_rect_right)
            self.turret_update('right', -angle)
            angle = self.calculer_angle_direction_tourelle(game_instance.player, self.turret_colision_rect_left)
            self.turret_update('left', angle)

            self.bullet_update(game_instance)
            self.damaging_player(game_instance.player)
        else:
            self.fight_started = self.intro_sequence_update()
            if self.fight_started:
                game_instance.player.is_overheat = False
            else:
                game_instance.player.colision_rect.x = 295
                game_instance.player.colision_rect.y = 600
                game_instance.player.is_overheat = True

    def turret_take_damage(self, side: str, invincibility_value: int, damage_value: int) -> bool:
        self.turret_data[side]['pv'] -= damage_value
        self.turret_data[side]['invincibility_time'] = invincibility_value
        if self.turret_data[side]['pv'] == 0 and not self.turret_data[side]['is_broken']:
            self.turret_data[side]['is_broken'] = True
            if side == 'left':
                self.turret_colision_rect_left.x = 20
                self.turret_colision_rect_left.y = 270
            else:
                self.turret_colision_rect_right.x = 530
                self.turret_colision_rect_right.y = 270
            self.turret_actual_sprite_id[side] = "BrokenTurret"
        if self.turret_data['right']['is_broken'] and self.turret_data['left']['is_broken']:
            self.forcefield_broken = True
            self.lazer_cd = 0
            self.boss_actual_sprite_id = 'Open_Mouse'
            self.forcefield_regeneration_time = 1200
        return self.turret_data[side]['is_broken']

    def timer_decrease(self):
        BaseBoss.timer_decrease(self)

        if self.turret_data['left']['invincibility_time'] != 0:
            self.turret_data['left']['invincibility_time'] -= 1

        if self.turret_data['right']['invincibility_time'] != 0:
            self.turret_data['right']['invincibility_time'] -= 1

        elif self.boss_actual_sprite_id == 'Damaged' or self.boss_actual_sprite_id == 'Open_Mouse_Damaged':
            if self.lazer_attack.is_started:
                self.boss_actual_sprite_id = "Open_Mouse"
            else:
                self.boss_actual_sprite_id = "BossNormal"
        
        if self.lazer_cd == 0 and self.forcefield_regeneration_time - 300 >= 0 and not self.lazer_attack.is_started:
            self.lazer_attack.new()
            self.boss_actual_sprite_id = "Open_Mouse"
        else:
            self.lazer_cd -= 1
        
        if self.homing_attack_cd > 0:
            self.homing_attack_cd -= 1
        else:
            self.homing_attack_cd = 60
            self.homing_attack.new()

        if self.forcefield_broken:
            if self.forcefield_regeneration_time != 0:
                self.forcefield_regeneration_time -= 1
            else:
                self.forcefield_broken = False
                self.boss_actual_sprite_id = 'BossNormal'
                self.turret_data['right']['pv'] = self.turret_data['left']['pv'] = 20
                self.turret_data['right']['invincibility_time'] = self.turret_data['left']['invincibility_time'] = 0
                self.turret_data['right']['is_broken'] = self.turret_data['left']['is_broken'] = False

                self.turret_actual_sprite_id['left'] = "LeftTurret"
                self.turret_actual_sprite_id['right'] = "RightTurret"

        if self.boss_attack_delay != 0:
            self.boss_attack_delay -= 1
        else:
            self.sideway_attack.new()
            self.boss_attack_delay = 120

    def draw_boss(self, screen_buffer):
        self.homing_attack.draw(screen_buffer)
        self.sideway_attack.draw(screen_buffer)
        self.lazer_attack.draw(screen_buffer)
        screen_buffer.blit(self.sprite_dict[self.boss_actual_sprite_id], (self.x + 170, self.y))
        if self.fight_started:
            if not self.forcefield_broken:
                screen_buffer.blit(self.sprite_dict['Forcefield'], (self.x, self.y))
                screen_buffer.blit(self.sprite_dict[self.turret_actual_sprite_id['left']], (self.turret_colision_rect_left.x, self.turret_colision_rect_left.y))
                screen_buffer.blit(self.sprite_dict[self.turret_actual_sprite_id['right']], (self.turret_colision_rect_right.x, self.turret_colision_rect_right.y))
            self.hp_bar.draw(screen_buffer)
            

    def turret_update(self, side, rotation_angle):
        if not self.turret_data[side]['is_broken']:
            self.sprite_dict[self.turret_actual_sprite_id[side]] = pygame.transform.rotate(self.sprite_dict['Turret'], rotation_angle).convert_alpha()
            self.turret_data[side]['rotation_angle'] = rotation_angle
            if side == 'right':
                self.turret_colision_rect_right = self.sprite_dict[self.turret_actual_sprite_id[side]].get_rect(center=self.sprite_dict['Turret'].get_rect(center=(self.x + 580, self.y + 327)).center)
            elif side == 'left':
                self.turret_colision_rect_left = self.sprite_dict[self.turret_actual_sprite_id[side]].get_rect(center=self.sprite_dict['Turret'].get_rect(center=(self.x + 70, self.y + 327)).center)

    def bullet_update(self, game_instance):

        self.sideway_attack.update()
        self.homing_attack.update()
        if self.lazer_attack.is_started:
            if self.lazer_attack.update(game_instance):
                self.boss_actual_sprite_id = "BossNormal"
                self.lazer_cd = 120

    def damaging_player(self, player: Player):

        attack_bullets = [
            (self.sideway_attack.get_bullet_list(), self.sideway_attack),
            (self.homing_attack.get_bullet_list(), self.homing_attack)
        ]

        sideway_lengh = len(attack_bullets[0][0])

        for i in range(len(attack_bullets)):
            for j in range(len(attack_bullets[i][0])):
                if player.colision_rect.colliderect(attack_bullets[i][0][j][0]):
                    player.take_damage(1, 60, 'AttDeCote' if j < sideway_lengh else 'AttChercheuse')
                    attack_bullets[i][1].remove_bullet_from_index(j)
        if player.colision_rect.collidelist((self.lazer_attack.v_hitbox, self.lazer_attack.h_hitbox)) > -1 :
            player.take_damage(1, 60, "AnguilleMegaLazer")

    def get_functioning_turret(self) -> list:
        functioning_turret = []
        for key, turret in self.turret_data.items():
            if not turret['is_broken']:
                functioning_turret.append(key)
        return functioning_turret

    def get_turret_info(self, side: str) -> dict:
        turret_info = {
            'x': self.turret_colision_rect_left.centerx if side == 'left' else self.turret_colision_rect_right.centerx,
            'y': self.turret_colision_rect_left.centery if side == 'left' else self.turret_colision_rect_right.centery,
            'rotation_angle': self.turret_data[side]['rotation_angle']
        }
        return turret_info

    def reset(self, hard: bool = False, music_reload=False) -> None:
        BaseBoss.reset(self, hard)

        if music_reload:
            pygame.mixer.music.unload()
            pygame.mixer.music.load(ANGUILLE_INTRO_MUSIC)
            pygame.mixer.music.queue(ANGUILLE_FIGHT_MUSIC, loops=-1)
            pygame.mixer.music.play()
        
        if hard:
            with open("Source/Cutscenes/Introduction_Boss.json") as f:
                self.intro_cutscene.load_from_json_dict(json.load(f))

            if self.intro_cutscene.draw not in self.draw_func_list:
                self.add_draw_element(self.intro_cutscene.draw)
        
            self.intro_cutscene.progress = 0
            self.y = -400

        self.mega_lazer_delais = 90
        self.homing_attack_cd = 30

        self.lazer_attack.clear()
        self.homing_attack.clear()
        self.sideway_attack.clear()

        # Boss

        self.turret_data = {
            'left': {
                'pv': 20,
                'invincibility_time': 0,
                'is_broken': False,
                'rotation_angle': 0
            },
            'right':{
                'pv': 20,
                'invincibility_time': 0,
                'is_broken': False,
                'rotation_angle': 0
            }
        }
        self.forcefield_broken = False
        self.turret_actual_sprite_id = {
            'left': 'LeftTurret',
            'right': 'RightTurret'
        }
        self.boss_actual_sprite_id = 'Sleep'
        self.forcefield_regeneration_time = 0
        self.boss_attack_delay = 60
        self.lazer_cd = 0
