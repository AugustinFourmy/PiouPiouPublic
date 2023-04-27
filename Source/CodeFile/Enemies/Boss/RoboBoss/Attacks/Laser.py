import pygame.rect
from Source.CodeFile.Enemies.Attack import Attack
from Source.CodeFile.Utility import Timer
from Source.CodeFile.player import Player


class BeamAttack(Attack):
    def __init__(self, poing_gauche, poing_droit):
        Attack.__init__(self)
        self.p_gauche = poing_gauche
        self.p_droit = poing_droit
        self.activate_timer = Timer(1)
        self.deactivate_timer = Timer(1)
        self.y = -100
        self.colision_rect = pygame.rect.Rect(60, -100, 540, 64)
        self.sprite = pygame.transform.scale(pygame.image.load('Source/img/Boss/spr_47_lazer_roboboss.png'), (1, 64))
        self.is_started = False
        self.is_active = False
        self.already_stopped = False

    def clear(self) -> None:
        self.is_started = False
        self.colision_rect.y = self.p_gauche.collision_rect.y

        self.p_droit.collision_rect.y = self.p_droit.start_point[1]
        self.p_droit.drawing_sprite = self.p_droit.sprite

        self.p_gauche.drawing_sprite = self.p_gauche.sprite
        self.p_gauche.collision_rect.y = self.p_gauche.start_point[1]

        self.colision_rect.y = -100
        self.y = -100
        self.is_active = False
        self.already_stopped = False
        
        self.p_gauche.liste_de_point = []
        self.p_droit.liste_de_point = []
        
    def new(self, activate_duration, deactivate_duration) -> None:
        self.activate_timer.setDuration(activate_duration)
        self.activate_timer.restart()

        self.deactivate_timer.setDuration(deactivate_duration)
        self.deactivate_timer.restart()

        self.p_gauche.drawing_sprite = self.p_gauche.laser_poing_sprite
        self.p_droit.drawing_sprite = self.p_droit.laser_poing_sprite

        self.colision_rect.y = self.y = self.p_gauche.collision_rect.y + 15

        self.is_started = True
        self.is_active = True

    def update(self, player: Player) -> bool:
        if self.is_started:
            if self.is_active:
                self.y += 1.5
                self.colision_rect.y = int(self.y)
                self.p_gauche.collision_rect.y = self.p_droit.collision_rect.y = int(self.y - 15)
                self.p_droit.point_placement(offset=[30, 0])
                self.p_gauche.point_placement(offset=[20, 0])
                if player.colision_rect.colliderect(self.colision_rect):
                    player.take_damage(1, 60, "RoboBossLaser")
            if self.is_active and not self.already_stopped:
                timemout = self.activate_timer.tick()
                if timemout:
                    self.is_active = False
            elif not self.already_stopped:
                timeout = self.deactivate_timer.tick()
                if timeout:
                    self.is_active = True
                    self.already_stopped = True

                
            
            if not(0 < self.colision_rect.y < 780):
                self.clear()
                return False
        return True

    def draw(self, screen_buffer):
        if self.is_active:
            for i in range(60, 601):
                screen_buffer.blit(self.sprite, (i, self.colision_rect.y))
