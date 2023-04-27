import pygame
import random

from Source.CodeFile.Enemies.Attack import Attack


class HommingAttack(Attack):
    def __init__(self, sprite: pygame.Surface, boss_object):
        Attack.__init__(self, sprite)
        self.boss = boss_object

    def __get_turret_shooting(self) -> str:
        remaining_turret = self.boss.get_functioning_turret()
        if len(remaining_turret) == 2:
            return random.choice(remaining_turret)
        elif len(remaining_turret) == 1:
            return remaining_turret[0]
        else:
            return 'None'

    def new(self):
        shooting_turret = self.__get_turret_shooting()
        if shooting_turret == 'None':
            pass
        else:
            turret_info = self.boss.get_turret_info(shooting_turret)
            velocity = pygame.Vector2(0, 5)
            velocity = velocity.rotate(-1 * turret_info['rotation_angle'])
            self.bullet_list.append(
                (
                    pygame.rect.Rect(turret_info['x'], turret_info['y'], 30, 30), velocity, [turret_info['x'], turret_info['y']]
                )
            )

    def update(self):
        backup = []

        for i in range(len(self.bullet_list)):
            self.bullet_list[i][2][0] += self.bullet_list[i][1].x
            self.bullet_list[i][2][1] += self.bullet_list[i][1].y
            self.bullet_list[i][0].x = self.bullet_list[i][2][0]
            self.bullet_list[i][0].y = self.bullet_list[i][2][1]
            if self.bullet_list[i][0].x < -15 or self.bullet_list[i][0].x > 700:
                backup.append(i)
            elif self.bullet_list[i][0].y < -15 or self.bullet_list[i][0].y > 800:
                backup.append(i)
        backup.sort(reverse=True)

        for elt in backup:
            self.bullet_list.pop(elt)

