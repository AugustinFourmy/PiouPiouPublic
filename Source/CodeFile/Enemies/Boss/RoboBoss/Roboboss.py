import pygame, random
from Source.CodeFile.Enemies.Boss.BaseBossCode import BaseBoss
from Source.CodeFile.Enemies.Boss.RoboBoss.Attacks.ChargePoing import ChargePoing
from Source.CodeFile.Enemies.Boss.RoboBoss.Attacks.Laser import BeamAttack
from Source.CodeFile.Enemies.Boss.RoboBoss.Attacks.Spawn_enemy import SpawnAttack
from Source.CodeFile.GameConstant import ROBOBOSS_FIGHT_MUSIC, ROBOBOSS_INTRO_MUSIC, VITESSE_CDP
from Source.CodeFile.Utility import Timer
from Source.CodeFile.Animation.teste_animation import animated_sprite
from Source.CodeFile.Enemies.Boss.RoboBoss.Attacks.both_side_slam import BothSideSlam


class Poing:
    def __init__(self, start_point_x: int, start_point_y: int, flipped: bool=False):
        self.bullets = []
        self.velocities = []
        self.start_point = (start_point_x, start_point_y)
        self.collision_rect = pygame.rect.Rect(start_point_x, start_point_y, 84, 84)
        self.boule = pygame.image.load("Source/img/Boss/RoboBoss/boule_liaison_poing.png").convert_alpha()
        self.sprite = pygame.transform.scale(pygame.transform.rotate(
            pygame.image.load("Source/img/Boss/RoboBoss/Poing.png"),
            -90
            ),
            (84, 84)
            )
        self.laser_poing_sprite = pygame.transform.scale(pygame.transform.rotate(
            pygame.image.load("Source/img/Boss/RoboBoss/lazerpoing.png"),
            -90
            ),
            (84, 84)
            )
        if flipped:
            self.sprite = pygame.transform.flip(self.sprite, True, False)
            self.laser_poing_sprite = pygame.transform.flip(self.laser_poing_sprite, True, False)
        self.openning = animated_sprite("Source/img/Boss/RoboBoss/poingspawn-Sheet.png", False, width=72)
        self.target_sprite = pygame.image.load("Source/img/Boss/RoboBoss/cible.png")
        self.openning.scale((84, 84))
        self.openning.rotate(180)
        self.off_screen_failsafe = Timer(180)
        self.is_openning = False
        self.drawing_sprite = self.sprite.convert_alpha()
        self.__charge_attaque = ChargePoing(self)
        self.__spawn_attaque = SpawnAttack(self)
        self.flipped = flipped
        self.retourner = False
        self.liste_de_point = []
        self.occupe = False
    
    def point_placement(self, initial_point: list = None, offset: list = (0, 0), center_height: bool = False, center_width: bool = False):
        if initial_point == None:
            initial_point = self.start_point
        
        vec_poing_boule = pygame.Vector2(
            self.collision_rect.x - initial_point[0] + 42 * int(center_width),
            self.collision_rect.y - initial_point[1] + 42 * int(center_height)
        )
        distance_point = vec_poing_boule / 5

        self.liste_de_point = [
            (
                initial_point[0] + distance_point.x * i  + offset[0],
                initial_point[1] + distance_point.y * i  + offset[1]
                
            ) for i in range(1, 6)
        ]

    def draw_bg(self, screen_buffer):
        for point in self.liste_de_point:
            screen_buffer.blit(self.boule, (point[0], point[1]))
        if self.retourner:
            self.is_openning = self.openning.draw(screen_buffer, (self.collision_rect.x, self.collision_rect.y))

    def draw(self, screen_buffer):
        screen_buffer.blit(self.boule, (self.start_point[0] + 21 + 21 * int(not self.flipped), self.start_point[1]+ 21 * int(not self.flipped)))
        if not self.retourner:
            screen_buffer.blit(self.drawing_sprite, (self.collision_rect.x, self.collision_rect.y))

    def draw_fg(self, screen_buffer):
        if self.__charge_attaque.started:
            screen_buffer.blit(self.target_sprite, self.__charge_attaque.target)

    def coup_de_poing(self, player):
        self.occupe = True
        self.__charge_attaque.new(player, VITESSE_CDP)
    
    def spawn_enemy(self, player, boss):
        self.occupe = self.__spawn_attaque.new(player, boss)

    def off_screen(self):
        return not(-1 < self.collision_rect.x < 641) or not(-1 < self.collision_rect.y < 781)

    def update(self, boss, player):
        if self.__charge_attaque.started:
            self.occupe = self.__charge_attaque.update()
        if self.__spawn_attaque.started:
            self.occupe = self.__spawn_attaque.update()
        if self.off_screen() and not boss.is_dual_attacking:
            timeout = self.off_screen_failsafe.tick()
            if timeout:
                self.collision_rect.x = self.start_point[0]
                self.collision_rect.y = self.start_point[0]        
        elif self.off_screen_failsafe.getTimeLeft() != self.off_screen_failsafe.getDuration():
            self.off_screen_failsafe.restart()
            
        off_screen = []

        
        for i in range(len(self.bullets)):
            self.bullets[i].x += self.velocities[i][0]
            self.bullets[i].y += self.velocities[i][1]
            if not(-10 < self.bullets[i].x < 640) or not(-44 < self.bullets[i].y < 780):
                off_screen.append(i)

        off_screen.sort(reverse=True)

        for elt in off_screen:
            self.bullets.pop(elt)
            self.velocities.pop(elt)

        collided_bullet = player.colision_rect.collidelist(self.bullets)
        if collided_bullet != -1 and player.invincibility_timer == 0:
            player.take_damage(1, 60, "AttaqueTir9")
            self.bullets.pop(collided_bullet)
            self.velocities.pop(collided_bullet)
    
    def reset(self):
        self.__charge_attaque.clear()
        self.occupe = False
    

class RoboBoss(BaseBoss):
    def __init__(self):
        BaseBoss.__init__(self, "M.E.C.H.A", 550, 0, 0)
        self.pods = (
            pygame.rect.Rect(110, 90, 90, 90),
            pygame.rect.Rect(430, 90, 90, 90),
            pygame.rect.Rect(270, 190, 90, 90)
        )
        self.open_sprite = animated_sprite("Source/img/Boss/RoboBoss/Cockpit2-sheet.png", False, width=90)
        self.closed_sprite = pygame.image.load("Source/img/Boss/RoboBoss/Trou.png").convert_alpha()
        self.robot_bg = pygame.transform.scale(pygame.image.load("Source/img/Boss/RoboBoss/base_robot-export.png"), (640, 360)).convert_alpha()
        self.pod_sprite_active = animated_sprite("Source/img/Boss/RoboBoss/Cockpitdescente-sheet.png", False, width=90)
        self.pod_sprite_decscending = animated_sprite("Source/img/Boss/RoboBoss/Cockpitdescente-sheet.png", False, width=90)
        self.active_pod_id = 2
        self.decending_pod_id = -1
        self.ascending_pod_id = -1
        self.next_attack_planned = False
        self.is_dual_attacking = False
        self.add_draw_element(self.drawing)
        self.change_timer = Timer(600)
        self.attack_timer = Timer(240)
        self.poing_gauche = Poing(16, 260, True)
        self.poing_droit = Poing(552, 260)
        self.__attaque_lateral = BothSideSlam(self.poing_gauche, self.poing_droit)
        self.__attaque_laser = BeamAttack(self.poing_gauche, self.poing_droit)
        self.saved_next_attaque = 0
        self.colonne_taken = []
        self.aliens = []

    def intro_sequence_update(self) -> bool:
        pygame.mixer.music.unload()
        pygame.mixer.music.load(ROBOBOSS_INTRO_MUSIC)
        pygame.mixer.music.queue(ROBOBOSS_FIGHT_MUSIC, loops=-1)
        pygame.mixer.music.play()
        return True

    def reset(self, hard: bool = False, music_reload: bool = False) -> None:
        BaseBoss.reset(self, hard)

        if music_reload:
            pygame.mixer.music.unload()
            pygame.mixer.music.load(ROBOBOSS_INTRO_MUSIC)
            pygame.mixer.music.queue(ROBOBOSS_FIGHT_MUSIC, loops=-1)
            pygame.mixer.music.play()
        
        self.poing_droit.reset()
        self.poing_gauche.reset()
        
        self.aliens = []
        self.saved_next_attaque = 0
        self.colonne_taken = []
        
        self.__attaque_lateral.clear()
        self.__attaque_laser.clear()
        self.change_timer.restart()
        self.attack_timer.restart()
        self.active_pod_id = 2
        self.decending_pod_id = -1
        self.ascending_pod_id = -1

        self.next_attack_planned = False
        self.is_dual_attacking = False



    def update(self, game):
        BaseBoss.update(self)

        self.poing_droit.update(self, game.player)
        self.poing_gauche.update(self, game.player)
        timeout = False
        if not self.__attaque_lateral.started:
            timeout = self.attack_timer.tick()
        if timeout:
            attaque = random.randint(0, 3)
            if attaque < 2 and not self.next_attack_planned:
                if random.randint(0, 1) == 1 and not self.poing_droit.occupe:
                    if attaque == 1:
                        self.poing_droit.coup_de_poing(game.player)
                    else:
                        self.poing_droit.spawn_enemy(game.player, self)
                elif not self.poing_gauche.occupe:
                    if attaque == 1:
                        self.poing_gauche.coup_de_poing(game.player)
                    else:
                        self.poing_gauche.spawn_enemy(game.player, self)
                self.attack_timer.restart()

            elif (not(self.poing_droit.occupe) and not(self.poing_gauche.occupe)):
                if self.next_attack_planned:
                    if self.saved_next_attaque == 2:
                        self.__attaque_lateral.new(game.player)
                    else:
                        duree_active = random.randint(50, 150)
                        self.__attaque_laser.new(duree_active, 150 - duree_active + 70)
                    self.next_attack_planned = False
                else:
                    if attaque == 2:
                        self.__attaque_lateral.new(game.player)
                    else:
                        self.__attaque_laser.new(random.randint(50, 150), random.randint(50, 95))
                self.next_attack_planned = False
                self.poing_droit.occupe = True
                self.poing_gauche.occupe = True
                self.attack_timer.restart()
            elif self.poing_droit.occupe or self.poing_gauche.occupe and not self.next_attack_planned and not self.__attaque_lateral.started:
                self.next_attack_planned = True
                self.saved_next_attaque = attaque

        if self.__attaque_lateral.started:
            self.is_dual_attacking = self.poing_gauche.occupe = self.poing_droit.occupe = self.__attaque_lateral.update()
        elif self.__attaque_laser.is_started:
            self.is_dual_attacking = self.poing_droit.occupe = self.poing_gauche.occupe = self.__attaque_laser.update(
                game.player
            )

        if not self.open_sprite.playing:
            self.open_sprite.play(0.5)

        if game.player.colision_rect.collidelist(
                (self.poing_droit.collision_rect, self.poing_gauche.collision_rect)) > -1:
            game.player.take_damage(1, 60, "CollisionPoing")

        dead_alien = []

        for i in range(len(self.aliens)):
            self.aliens[i].update(game.player)
            if self.aliens[i].hp == 0:
                dead_alien.append(i)

        dead_alien.sort(reverse=True)

        for alien in dead_alien:
            self.aliens.pop(alien)
            self.colonne_taken.pop(alien)
        
        timeout = self.change_timer.tick()
        collided_bullet = self.pods[self.active_pod_id].collidelist(game.player.bullets)
        if collided_bullet != -1 and self.invincibility_time == 0:
            game.player.delete_bullet(collided_bullet)
            game.screen_shake_intencity = 5
            game.screen_shake_duration = 3
            if random.randint(0, 4) == 1 and timeout:
                new_active_pod = random.randint(0, 2)
                while new_active_pod == self.active_pod_id:
                    new_active_pod = random.randint(0, 2)
                self.decending_pod_id = self.active_pod_id
                self.pod_sprite_decscending.play(speed=6)
                self.active_pod_id = new_active_pod
                self.change_timer.restart()
                self.open_sprite.reset()
            self.take_damage(1, 3)

    def draw_bg(self, screen_buffer):
        screen_buffer.blit(self.robot_bg, (0, -10)) 
        self.poing_droit.draw_bg(screen_buffer)
        self.poing_gauche.draw_bg(screen_buffer)
        for i in range(len(self.pods)):
            if i != self.active_pod_id or (self.ascending_pod_id != -1 or self.decending_pod_id != -1):
                screen_buffer.blit(self.closed_sprite, (self.pods[i].x, self.pods[i].y))
        self.__attaque_laser.draw(screen_buffer)

    def drawing(self, screen_buffer):
        if self.ascending_pod_id == -1 and self.decending_pod_id == -1:
            self.open_sprite.draw(screen_buffer, (self.pods[self.active_pod_id].x, self.pods[self.active_pod_id].y))
        elif self.decending_pod_id != -1:
            still_playing = self.pod_sprite_decscending.draw(screen_buffer, (self.pods[self.decending_pod_id].x, self.pods[self.decending_pod_id].y))
            if not still_playing:
                self.ascending_pod_id = self.active_pod_id
                self.pod_sprite_active.play(speed=6, reversed=True)
                self.decending_pod_id = -1
        elif self.ascending_pod_id != -1:
            stil_playing = self.pod_sprite_active.draw(screen_buffer, (self.pods[self.ascending_pod_id].x, self.pods[self.ascending_pod_id].y))
            if not stil_playing:
                self.ascending_pod_id = -1

        self.poing_droit.draw(screen_buffer)
        self.poing_gauche.draw(screen_buffer)

        for alien in self.aliens:
            alien.draw(screen_buffer)

        self.hp_bar.draw(screen_buffer)

    def draw_fg(self, screen_buffer):
        self.poing_droit.draw_fg(screen_buffer)
        self.poing_gauche.draw_fg(screen_buffer)
        if self.__attaque_lateral.started:
            self.__attaque_lateral.draw(screen_buffer)
