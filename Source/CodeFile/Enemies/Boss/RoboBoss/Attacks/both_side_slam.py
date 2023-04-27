import pygame
from Source.CodeFile.Enemies.Attack import Attack
from Source.CodeFile.GameConstant import SIDE_PUNCH_SPEED
from Source.CodeFile.Utility import Timer


class BothSideSlam(Attack):
    def __init__(self, poing_gauche, poing_droit):
        Attack.__init__(self)

        self.p_gauche = poing_gauche
        self.v_gauche = pygame.Vector2(0, 0)

        self.p_droit = poing_droit
        self.v_droit = pygame.Vector2(0, 0)

        self.targeting_timer = Timer(350)

        self.started = False
        self.off_screen = False
        self.waiting = False
        self.comming_back = False
        self.attacking = False

        self.player = None

    def clear(self) -> None:
        self.started = False
        self.off_screen = False
        self.waiting = False
        self.comming_back = False
        self.attacking = False
        self.v_gauche = pygame.Vector2(0, 0)
        self.v_droit = pygame.Vector2(0, 0)
        self.targeting_timer.restart()

        self.p_gauche.collision_rect.x = self.p_gauche.start_point[0]
        self.p_gauche.collision_rect.y = self.p_gauche.start_point[1]
        self.p_gauche.drawing_sprite = self.p_gauche.sprite
        self.p_gauche.liste_de_poing = []

        self.p_droit.collision_rect.x = self.p_droit.start_point[0]
        self.p_droit.collision_rect.y = self.p_droit.start_point[1]
        self.p_droit.drawing_sprite = self.p_droit.sprite
        self.p_droit.liste_de_poing = []

    def new(self, player) -> None:
        self.started = True
        self.v_gauche.x = -3
        self.v_droit.x = 3
        self.player = player
        self.p_droit.drawing_sprite = pygame.transform.rotate(self.p_droit.sprite, 90)
        self.p_gauche.drawing_sprite = pygame.transform.rotate(self.p_droit.sprite, -90)

    def update(self, *a) -> bool:
        if not self.off_screen and not self.comming_back and not self.waiting and not self.attacking:
            self.p_gauche.collision_rect.x += self.v_gauche.x
            self.p_droit.collision_rect.x += self.v_droit.x
            if self.p_gauche.collision_rect.x < - 100:
                self.off_screen = True

        elif not self.comming_back and not self.waiting and not self.attacking:
            self.p_gauche.collision_rect.y = self.player.sprite_y
            self.p_droit.collision_rect.y = self.player.sprite_y
            self.targeting_timer.tick()
            if self.targeting_timer.getTimeLeft() < 120:
                self.waiting = True

        elif not self.comming_back and not self.attacking:
            timeout = self.targeting_timer.tick()
            if timeout:
                self.attacking = True
                self.p_droit.drawing_sprite = pygame.transform.rotate(self.p_droit.sprite, -90)
                self.p_gauche.drawing_sprite = pygame.transform.rotate(self.p_droit.sprite, 90)

        elif not self.comming_back:
            self.p_gauche.collision_rect.x += SIDE_PUNCH_SPEED
            self.p_gauche.point_placement([0, self.p_droit.collision_rect.y + 42], center_height=True)
            self.p_droit.collision_rect.x += -SIDE_PUNCH_SPEED
            self.p_droit.point_placement([640, self.p_droit.collision_rect.y + 42],  center_height=True)
            if self.p_gauche.collision_rect.x in range(self.p_droit.collision_rect.x-SIDE_PUNCH_SPEED * 2, self.p_droit.collision_rect.x):
                self.comming_back = True

        else:
            self.p_gauche.collision_rect.x += -SIDE_PUNCH_SPEED
            self.p_gauche.point_placement([0, self.p_droit.collision_rect.y + 42], center_height=True)
            self.p_droit.collision_rect.x += SIDE_PUNCH_SPEED
            self.p_droit.point_placement([640, self.p_droit.collision_rect.y + 42] , center_height=True)
            if self.p_gauche.collision_rect.x < -100:
                self.clear()
                return False
        return True

    def draw(self, screen_buffer):
        if not(self.attacking) and self.off_screen:
            pygame.draw.rect(screen_buffer, "#ff6600", (0, self.p_droit.collision_rect.y, 640, 64), 2)