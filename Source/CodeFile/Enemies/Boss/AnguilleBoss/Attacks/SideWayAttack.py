import pygame, random, math
from Source.CodeFile.Enemies.Attack import Attack


class SidewayAttack(Attack):
    def new(self):
        side = random.choice(("left", "right"))
        angles = tuple(random.randint(120, 150) if side == 'right' else random.randint(30, 60) for _ in range(3))
        x_start = -5 if side == 'left' else 685
        for i in range(1):
            self.bullet_list.append([pygame.rect.Rect(x_start, 600, 5, 5), math.cos(math.radians(angles[i])), math.sin(math.radians(angles[i])), x_start, 600])
            self.bullet_list.append([pygame.rect.Rect(x_start, 600, 5, 5), math.cos(math.radians(angles[i])), -1 * math.sin(math.radians(angles[i])), x_start, 600])
            if side == 'left':
                self.bullet_list.append([pygame.rect.Rect(x_start, 600, 5, 5), 1, 0, x_start, 600])
            else:
                self.bullet_list.append([pygame.rect.Rect(x_start, 600, 5, 5), -1, 0, x_start, 600])
    
    def update(self):
        backup = []
        for i in range(len(self.bullet_list)):
            self.bullet_list[i][3] += 3 * self.bullet_list[i][1]
            self.bullet_list[i][4] += 3 * self.bullet_list[i][2]
            self.bullet_list[i][0].x = self.bullet_list[i][3]
            self.bullet_list[i][0].y = self.bullet_list[i][4]
            if self.bullet_list[i][0].x < -15 or self.bullet_list[i][0].x > 700:
                backup.append(i)
            elif self.bullet_list[i][0].y < -15 or self.bullet_list[i][0].y > 800:
                backup.append(i)
        backup.sort(reverse=True)

        for elt in backup:
            self.bullet_list.pop(elt)
