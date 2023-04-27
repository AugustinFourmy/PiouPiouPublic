import pygame
from Source.CodeFile.Enemies.Attack import Attack
from Source.CodeFile.Utility import Timer
from Source.CodeFile.player import Player


class ChargePoing(Attack):
    def __init__(self, poing):
        Attack.__init__(self)
        self.poing = poing
        self.velocite = [0, 0]
        self.comming_back = False
        self.started = False
        self.true_start = False
        self.player = None
        self.speed = 0
        self.before_the_start = Timer(360)
        self.target = pygame.Vector2(0, -100)

    def clear(self) -> None:
        self.poing.collision_rect.x = self.poing.start_point[0]
        self.poing.collision_rect.y = self.poing.start_point[1]
        self.velocite = [0, 0]
        self.comming_back = False
        self.started = False
        self.true_start = False
        self.poing.liste_de_point = []
        self.poing.drawing_sprite = self.poing.sprite.convert_alpha()
        self.target = pygame.Vector2(0, -100)
        self.before_the_start.restart()

    def new(self, player: Player, speed: int):
        self.started = True
        self.player = player
        self.speed = speed

    def __start(self):
        self.velocite[1] = self.target.y - self.poing.collision_rect.y - 15
        self.velocite[0] = int(((self.target.x - self.poing.collision_rect.x - 12) / self.velocite[1]) * self.speed)
        self.velocite[1] = (self.velocite[1] / abs(self.velocite[1])) * self.speed
        self.poing.collision_rect.x += self.velocite[0]
        self.poing.collision_rect.y += self.velocite[1]
        vec_velo = pygame.Vector2(self.velocite)
        vec_horizontale = pygame.Vector2(0, 1)
        self.poing.drawing_sprite = pygame.transform.rotate(
            self.poing.sprite, vec_velo.angle_to(vec_horizontale)
        ).convert_alpha()
        self.true_start = True

    def update(self, *a) -> bool:
        if self.true_start:

            self.poing.collision_rect.x += self.velocite[0]
            self.poing.collision_rect.y += self.velocite[1]

            vec_poing_boule = pygame.Vector2(
                self.poing.collision_rect.x - self.poing.start_point[0],
                self.poing.collision_rect.y - self.poing.start_point[1]
                )

            distance_point = vec_poing_boule / 5

            start_point_co = pygame.Vector2(self.poing.start_point)

            self.poing.liste_de_point = [
                (
                    start_point_co.x + i*distance_point.x + 24 + 21 * int(not self.poing.flipped),
                    start_point_co.y + i*distance_point.y + 21 * int(not self.poing.flipped)

                ) for i in range(1, 6)
                ]

            if (not(640 > self.poing.collision_rect.x > -72) or not(780 > self.poing.collision_rect.y > -72))\
                    and not self.comming_back:
                self.velocite = [-1/2 * self.velocite[0], -1/2 * self.velocite[1]]
                self.comming_back = True
            if self.poing.collision_rect.y in range(self.poing.start_point[1] - 30, self.poing.start_point[1] + 30)\
                    and self.comming_back:
                self.clear()
                return False
        else:
            timeout = self.before_the_start.tick()

            if timeout:
                self.__start()
            elif self.before_the_start.getTimeLeft() > 60:
                self.target.x = self.player.sprite_x
                self.target.y = self.player.sprite_y
                vec_velo = pygame.Vector2(
                    self.target.x - self.poing.collision_rect.x,
                    self.target.y - self.poing.collision_rect.y
                )
                vec_horizontale = pygame.Vector2(0, 1)
                self.poing.drawing_sprite = pygame.transform.rotate(
                    self.poing.sprite, vec_velo.angle_to(vec_horizontale)
                ).convert_alpha()
        return True
