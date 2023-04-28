from Source.CodeFile.Menu import Menu
from Source.CodeFile.PlayerData import PlayerDeath, PlayerData
from Source.CodeFile.Utility import Timer, SaveLoadHandler
from Source.CodeFile.Achievement import Achievement, AchievementHandler
from Source.CodeFile.GameConstant import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ENEMY_HEIGHT,
    ENEMY_WIDTH,
    ENEMY_LOW_SHOOT_SPEED,
    ENEMY_VERTICAL_LIMIT,
    ALIEN_HIGH_SHOOT_SPEED,   
    SP_HIGH_SHOOT_SPEED,
    GREEN_ENEMY_HP,
    YELLOW_ENEMY_HP,
    RED_ENEMY_HP,
    SP_ENEMY_HP,
    LOW_OVERHEAT,
    MEDIUM_OVERHEAT,
    HIGH_OVERHEAT,
    MENU_MUSIC,
    FIGHT_MUSIC,
    GAME_OVER_MUSIC,
    MAIN_MENU_MARGIN,
    PAUSE_MENU_MARGIN,
    SAVE_PATH
)

from Source.CodeFile.Enemies.spacePirate import SpacePirate
from Source.CodeFile.player import Player
from Source.CodeFile.Enemies.enemies import Alien, TirAttaque
from Source.CodeFile.Enemies.Ovni import OvniEnemy, OvniBomb
from Source.CodeFile.drops import Pile, FragementOverdrive
from Source.CodeFile.waves import Wave
from Source.CodeFile.Enemies.Boss.AnguilleBoss.Anguille import Anguille
from Source.CodeFile.Enemies.Boss.RoboBoss.Attacks.Spawn_enemy import BlackAlien
from Source.CodeFile.particle import Particle
from Source.CodeFile.dialogue_system import DialogueHandler
from Source.CodeFile.Enemies.Boss.RoboBoss.Roboboss import RoboBoss
from Source.CodeFile.Cutscene.cutscene import Cutscene
import pygame
import sys, json
import logging
import random
import pathlib
  
logging.basicConfig(filename="debug.log", filemode="w", encoding='utf-8', level=logging.DEBUG,
                    format="[%(asctime)s][%(levelname)s] - %(message)s",
                    datefmt='%d/%m/%y - %H:%M:%S')

KONAMI_CODE = (pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT,
               pygame.K_RIGHT, pygame.K_b, pygame.K_a)


class Shmup:
    def __init__(self, screen: pygame.Surface) -> None:
        """
        Constructeur de la classe Shmup
        La classe Shmup représente le jeu
        Cette fontion prend pour argument:
            -  screen: une surface qui représente la fenettre sur lequel sera afficher le jeu  
        """

        self.save_handler = SaveLoadHandler(SAVE_PATH)

        self.player_data = self.save_handler.load()
        if self.player_data is None:
            self.player_data = PlayerData()

        self.achievement_handler = AchievementHandler(
            Achievement(
                "Double Fun",
                "Débloquer le tir double pour la 1ère fois",
                "2TR",
                "Source/img/achievement/spr_45_ach_double_fun.png"
            ),
            Achievement(
                "Octoshot !",
                "Débloquer le tir octo pour la 1ère fois",
                "8TR",
                "Source/img/achievement/spr_47_ach_octo.png"
            ),
            Achievement(
                "CHEATER !",
                "Essayer d'utiliser le Konami Code",
                "KCD",
                "Source/img/achievement/spr_48_ach_cheat_code.png"
            ),
            Achievement(
                "Maître du Jeu",
                "Battre le jeu avec seulement le x1 et sans mourir",
                "GDG",
                "Source/img/achievement/Achievement_13.png"
            ),
            Achievement(
                "CryBaby",
                "Mourir à la vague 1",
                "V1M",
                "Source/img/achievement/Achievement_11.png"
            ),
            Achievement(
                "Sherlock !",
                "Appuyer sur espace sur cette case dans le menu des succès",
                "SHH",
                "Source/img/achievement/Achievement_5.png"
            ),
            Achievement(
                "Vainqueur de l'A.N.G.U.I.L.L.E",
                "Vaincre l'A.N.G.U.I.L.L.E pour la 1ère fois",
                "VDA",
                "Source/img/achievement/Achievement_7.png"
            ),
            Achievement(
                "Tireur d'élite",
                "Détruire un OVNI",
                "OVN",
                "Source/img/achievement/Achievement_6.png"
            ),
            Achievement(
                "J'ai glissé Chef",
                "Tuer un ennemi grâce de la bombe d'un OVNI",
                "SMB",
                "Source/img/achievement/Achievement_10.png"
            ),
            Achievement(
                "C'est pas sympa",
                "Quiter le jeu sans y jouer",
                "QMM",
                "Source/img/achievement/Achievement_9.png"
            ),
            Achievement(
                "Vainqueur du M.E.C.H.A",
                "Vaincre le M.E.C.H.A pour la 1ère fois",
                "VDM",
                "Source/img/achievement/Achievement_8.png"
            )
        )

        self.achievement_handler.unlock_from_list(self.player_data.get_unlock_list())

        self.dialogue_handler = DialogueHandler(
            "Source/dialogue.json",
            "Source/Font/prstart.ttf",
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        # Surfaces

        self.screen_buffer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))  # Contient la surface qu'est la fenêtre
        self.screen = screen
        self.s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))  # Surface qui permet d'afficher des truc transparent

        # Etat de jeu

        self.debug_mode = 0  # Vérifie si le débug mode est actif1

        """
        0: Désactiver
        1: All upgrade + cheat
        2: Enemy test
        3: Boss test
        """

        self.game_state = 0  # Store l'état de jeu actuel

        """
        0 : Ecran titre
        1 : Menu Succès 
        2 : Jeu démaré
        3 : Jeu en pause
        4 : Game Over 
        5 : Boss Fight
        6 : Credit
        """

        # Booléen (Autre)

        # Booleen qui stock si le texte 'Press start' est afficher

        self.afficher = True

        # Booleen qui stock si le joueurs a relacher la barre espace avant de la presser pour passer l'ecran de gameover

        self.space_lock = False
        
        self.played = False
        
        self.roboboss_end = False
        # Chargements des images

        # Les balles des ennemis
        self.bullet_sprite = pygame.transform.scale(
            pygame.image.load('Source/img/enemies/spr_28_alien_bullet.png').convert_alpha(), (10, 44)
        )
        # Fond du jeu
        self.fond = pygame.transform.scale(pygame.image.load('Source/img/spr_00_background.png').convert(), (640, 780))
        self.fond_menu = pygame.transform.scale(
            pygame.image.load('Source/img/spr_47_main_menu_background.png').convert(), (640, 780))

        # Image qui apparait quand il y a un game over
        self.game_over_logo = pygame.transform.scale(
            pygame.image.load('Source/img/spr_03_game_over.png').convert_alpha(), (420, (406 / 831) * 420))

        # Pile Doré

        self.sprite_overdrive_fragment = pygame.image.load('Source/img/player/Doré.png')

        # Polices d'ecritures

        # Police principale
        self.main_font = pygame.font.Font(pathlib.Path('Source/Font/prstart.ttf'), 28)

        # Police pour les pv du HUD(Heads-Up display) du joueur
        self.pv_font = pygame.font.Font(pathlib.Path('Source/Font/prstart.ttf'), 20)

        # Police pour le HUD(Heads-Up display) du joueur
        self.hud_font = pygame.font.Font(pathlib.Path('Source/Font/prstart.ttf'), 16)

        # Police du titre
        self.title_font = pygame.font.Font(pathlib.Path('Source/Font/prstart.ttf'), 58)

        # Police des copyright de l'ecran titre
        self.copyright_font = pygame.font.Font(pathlib.Path('Source/Font/prstart.ttf'), 10)

        self.main_menu = Menu(self.main_font)
        self.main_menu.add_element("Jouer", self.game_start, (MAIN_MENU_MARGIN, 620))
        self.main_menu.add_element("Succès", self.load_achievement_menu, (MAIN_MENU_MARGIN, 670))
        self.main_menu.add_element("Quitter", self.quitter, (MAIN_MENU_MARGIN, 720))

        self.pause_menu = Menu(self.main_font)
        self.pause_menu.add_element("Continuer", self.unpause, (PAUSE_MENU_MARGIN, 520))
        self.pause_menu.add_element("Écran Titre", self.back_to_title_screen, (PAUSE_MENU_MARGIN, 590))

        self.menu_game_over = Menu(self.main_font)
        self.menu_game_over.add_element("Recommencer", self.restart, (PAUSE_MENU_MARGIN, 520))
        self.menu_game_over.add_element("Écran Titre", self.back_to_title_screen, (PAUSE_MENU_MARGIN, 590))

        # Textes

        self.text_compteur_overdrive = self.pv_font.render("0/3", True, "#ffdf00")

        # Utilise deux fois pour le titre (Piou Piou)
        self.title_txt = self.title_font.render("Piou", True, '#b0b0b0').convert_alpha()

        # Utilisé sur l'ecran titre pour les droit d'auteur
        self.copyright_txt = self.copyright_font.render(
            "Ce jeu est la proriété de Guillaume x 2 & Augustin Fourmy", True, 'white').convert_alpha()

        # Texte pause qui clignote sur l'ecran titre
        self.press_start_txt = self.main_font.render('Press start', True, 'white').convert_alpha()

        # S'affiche sur l'ecran de pause
        self.pause_txt = self.main_font.render("Pause", True, 'white').convert_alpha()

        # Fait partit du HUD et indique les points de vie
        self.hp_txt = self.pv_font.render("PV", True, 'white').convert_alpha()

        # Fait partit du HUD et indique la surchauffe
        self.overheat_text = self.hud_font.render("Surchauffe", True, 'white').convert_alpha()
        self.overdrive_text = self.hud_font.render("OVERDRIVE", True, 'white').convert_alpha()

        self.boss_txt = self.hud_font.render("Boss", True, 'white').convert_alpha()
        
        self.end_cutscene = Cutscene()
        with open("Source/Cutscenes/Roboboss_fin.json") as f:
            self.dict_cutscene = json.load(f)

        self.credit_cutscene = Cutscene()
        with open("Source/Cutscenes/EndCredit.json") as f:
            self.credit_dict = json.load(f)

        self.dialogue_music = pygame.mixer.Sound("Source/music/msc_10_dialogue.ogg")

        # Vagues

        self.waves = (
            Wave(False, self.title_font, self.hud_font,
                 vague_num=1, green=10, yellow=1, spawn_delais=130,
                 has_starting_dialogue=True, dialogue_id="Intro_Wave_1"),
            Wave(False, self.title_font, self.hud_font,
                 vague_num=2, green=15, yellow=3, ovni_frequency=1450, ovni_sp=2, spawn_delais=120,
                 has_starting_dialogue=True, dialogue_id="Intro_Wave_2"),
            Wave(False, self.title_font, self.hud_font,
                 vague_num=3, green=15, yellow=5, red=1, ovni_frequency=1200, ovni_sp=2, spawn_delais=110,
                 has_starting_dialogue=True, dialogue_id="Intro_Wave_3"),
            Wave(False, self.title_font, self.hud_font,
                 vague_num=4, green=20, yellow=8, red=2, ovni_frequency=900, ovni_sp=3, spawn_delais=110,
                 has_starting_dialogue=True, dialogue_id="Intro_Wave_4"),
            Wave(False, self.title_font, self.hud_font,
                 vague_num=5, green=20, yellow=10, red=4, ovni_frequency=600, ovni_sp=4, spawn_delais=90,
                 has_starting_dialogue=True, dialogue_id="Intro_Wave_5"),
            Wave(True, self.title_font, self.hud_font,
                 boss=Anguille(self.title_font),
                 has_starting_dialogue=True, dialogue_id="Intro_Anguille"),
            Wave(False, self.title_font, self.hud_font,
                 vague_num=6, green=10, yellow=6, red=2, sp=2, spawn_delais=95,
                 has_starting_dialogue=True, dialogue_id="Intro_Wave_6"),
            Wave(False, self.title_font, self.hud_font,
                 vague_num=7, green=16, yellow=8, red=2, sp=3, spawn_delais=95),
            Wave(False, self.title_font, self.hud_font,
                 vague_num=8, green=15, yellow=8, red=3, sp=4, spawn_delais=90),
            Wave(True, self.title_font, self.hud_font,
                 boss=RoboBoss(),
                 has_starting_dialogue=True, dialogue_id="Intro_Roboboss")
            )
        self.actual_wave = 0
        
        self.final_achievement = True

        # Musique

        pygame.mixer.music.load(MENU_MUSIC)  # Charge la musique de l'écran titre
        # Minuteurs (1 unite = 1/60 seconde)

        self.txt_start_timer = Timer(30)  # Timer qui gere le clignottement du texte 'Press Start'

        # Delais entre le moment ou le joueur appuis sur le bouton start et le moment ou le jeu demarre
        # (defaut = -1 -> n'a pa encore ete demarre)
        # self.start_timer = -1

        # Timer entre les apparitions des ennemis
        self.spawn_timer = Timer(60)

        # Delais entre chaque changement de mode de tire (0 = vous pouvez changer de mode de tire)
        self.cooldown = Timer(30)
        self.cooldown.tick(29)

        # Delais avant de pouvoire re-appuyer sur le bouton pause
        self.pause_cd = Timer(30)

        # Variable relative aux ennemis

        self.enemy_list = []  # Liste des ennemis presents
        self.colonne_dispo = [0, 1, 2, 3, 4, 5]  # Liste des collones disponible pour qu'un ennemi apparaisse
        self.ovni_spawn = self.waves[self.actual_wave].ovni_frequency  # Delais entre l'aparistion
        self.next_enemy_color = (255, 255, 255)
        self.next_enemy_column_id = int()
        self.next_enemy_hp_id = int()
        self.enemy_color_dict = {
            0: '#00EA4E',
            1: '#FFFF00',
            2: '#800D0D',
            3: '#AAAAAA'
        }
        self.alien_hp = (GREEN_ENEMY_HP, YELLOW_ENEMY_HP, RED_ENEMY_HP, SP_ENEMY_HP)
        self.alien_attaque = {
            GREEN_ENEMY_HP: TirAttaque(self.bullet_sprite, 1, 0, 4),
            YELLOW_ENEMY_HP: TirAttaque(self.bullet_sprite, 3, 2, 6),
            RED_ENEMY_HP: TirAttaque(self.bullet_sprite, 5, 2, 6),
        }
        # self.sp_pirate_attaque = CornerLaserAttack()
        self.ovni = None  # Objet enemis (si il y a)
        self.bomb = None  # Objet Bombe si il y en a une

        self.konami_code_avencement = 0

        # Sprite des ennemis

        self.alien_sprites = (pygame.image.load('Source/img/enemies/spr_23_alien_green.png'),
                              pygame.image.load('Source/img/enemies/spr_24_alien_yellow.png'),
                              pygame.image.load('Source/img/enemies/spr_25_alien_red.png'),
                              pygame.image.load('Source/img/enemies/spr_26_alien_damage.png'),
                              pygame.image.load('Source/img/enemies/spr_49_alien_blinde_niv1.png'),
                              pygame.image.load('Source/img/enemies/spr_50_alien_blinde_niv2.png'),
                              pygame.image.load('Source/img/enemies/spr_48_alien_blinde_max.png'),
                              )
        self.alien_sprites = (
            pygame.transform.scale(self.alien_sprites[0], (ENEMY_WIDTH, ENEMY_HEIGHT)).convert_alpha(),
            pygame.transform.scale(self.alien_sprites[1], (ENEMY_WIDTH, ENEMY_HEIGHT)).convert_alpha(),
            pygame.transform.scale(self.alien_sprites[2], (ENEMY_WIDTH, ENEMY_HEIGHT)).convert_alpha(),
            pygame.transform.scale(self.alien_sprites[3], (ENEMY_WIDTH, ENEMY_HEIGHT)).convert_alpha(),
            pygame.transform.scale(self.alien_sprites[4], (ENEMY_WIDTH, ENEMY_HEIGHT)).convert_alpha(),
            pygame.transform.scale(self.alien_sprites[5], (ENEMY_WIDTH, ENEMY_HEIGHT)).convert_alpha(),
            pygame.transform.scale(self.alien_sprites[6], (ENEMY_WIDTH, ENEMY_HEIGHT)).convert_alpha()
        )
        self.space_pirate_sprite = pygame.image.load('Source/img/enemies/spr_42_laser_bot_red.png')
        self.space_pirate_damaged_sprite = pygame.image.load('Source/img/enemies/spr_42_laser_bot_red_dégat.png')
        self.space_pirate_sprite = pygame.transform.scale(self.space_pirate_sprite, (ENEMY_WIDTH, ENEMY_HEIGHT))
        self.space_pirate_damaged_sprite = pygame.transform.scale(self.space_pirate_damaged_sprite, (ENEMY_WIDTH, ENEMY_HEIGHT))
        self.ovni_sprites = {
            "ovni": pygame.transform.scale(
                pygame.image.load('Source/img/Ovni/spr_16_ovni.png'), (ENEMY_WIDTH, 53)).convert_alpha(),
            "explosion_croisement": pygame.transform.scale(
                pygame.image.load('Source/img/Ovni/spr_21_ovni_bomb_explosion_center.png'), (60, 60)).convert_alpha(),
            "explosion_fire_horizontal": pygame.transform.scale(
                pygame.image.load('Source/img/Ovni/spr_22_ovni_bomb_explosion_bar.png'), (640, 60)).convert_alpha(),
            "explosion_fire_vertical": pygame.transform.rotate(
                pygame.transform.scale(pygame.image.load('Source/img/Ovni/spr_22_ovni_bomb_explosion_bar.png'),
                                       (780, 60)), 90).convert_alpha(),
            "bomb": pygame.transform.scale(
                pygame.image.load('Source/img/Ovni/spr_17_ovni_bomb.png'), (60, 60)).convert_alpha(),
            "bomb_red": pygame.transform.scale(
                pygame.image.load('Source/img/Ovni/spr_18_ovni_bomb_red.png'), (60, 60)).convert_alpha(),
            "warning": pygame.transform.scale(
                pygame.image.load('Source/img/Ovni/spr_19_ovni_bomb_warning_sign.png'), (50, 39)).convert_alpha(),
        }

        # Joueur

        self.player = Player((305, 670))  # Contient l'objet du joueur
        if self.debug_mode == 0:
            self.shot_type_list = ['simple', ]  # Different type de tire debloquer par le joueur
        else:
            self.shot_type_list = ['simple', 'double', 'diagonal']

        self.shot_rate_dict = {'simple': 5, 'double': 5, 'diagonal': 5}  # Frequence de tire de chaque mode
        self.pv_x = tuple(465 + 35 * i for i in range(5))  # Tuple des position horisontale des images de pointe de vie

        # Variable lié aux splash screen de début du jeu

        self.splash_screen_sprites = (
            pygame.image.load("Source/img/PiouPiouIntro.png").convert_alpha(),
            pygame.image.load("Source/img/splash_screen_2.png").convert_alpha()
        )
        self.splash_screen_sprites_x = SCREEN_WIDTH // 2 - self.splash_screen_sprites[0].get_width() // 2
        self.splash_screen_sprites_y = SCREEN_HEIGHT // 2 - self.splash_screen_sprites[0].get_height() // 2
        self.actual_splash_screen = 0
        self.splash_screen_opacity = 255
        self.is_in_splash_screen = True

        # Particules

        self.particle_list = []

        # Screen shake

        self.screen_shake_duration = -1
        self.screen_shake_intencity = 10
        self.offset = [0, 0]

        # Autre

        self.clock = pygame.time.Clock()  # Objet qui regule le framerate
        self.pile_liste = []  # Liste des piles (objet de soin)
        self.overdrive_fragement_liste = []
        self.overdrive_fragement_collected = 0
        self.overheat_rect = pygame.rect.Rect(20, 730, 150, 40)  # Rectangle d'affichage de la surchauffe
        self.fragment_hud_showing = False
        self.fragment_hud_timer = Timer(180)

    def load_achievement_menu(self):
        self.game_state = 1
    
    def win(self):
        self.back_to_title_screen()
        self.actual_wave = 0
        self.player_data.add_win()
        if self.final_achievement:
            self.achievement_handler.unlock("GDG")

    def restart(self):
        """
        Procédure qui s'éxécute lorsque le joueur recommence une partie après avoir eu un game over
        """
        self.player_reset()
        for attack in self.alien_attaque.values():
            attack.clean()

        self.particle_list = []
        self.pile_liste = []
        self.overdrive_fragement_liste = []
        self.overdrive_fragement_collected = 0

        if self.waves[self.actual_wave].boss_wave and self.waves[self.actual_wave].boss.fight_started:
            self.game_state = 5
            self.waves[self.actual_wave].boss.reset(music_reload=True)
        else:
            self.game_state = 2
            pygame.mixer.music.load(FIGHT_MUSIC)
            pygame.mixer.music.play(loops=-1)
            self.waves[self.actual_wave].reset()
            self.enemy_reset()


    def player_reset(self):
        """
        Procedure qui remet les donnés du joueur à leur état initial
        """
        self.player.dead = False
        self.player.hp = self.player.max_hp
        self.player.colision_rect.x = 305
        self.player.colision_rect.y = 670
        self.player.invincibility_timer = 0
        self.player.shot_mode = 0
        self.player.bullets = []
        self.player.bullets_velocity = []
        self.player.point_overheat = self.player.base_point_overheat

        if self.debug_mode == 0:
            self.shot_type_list = ['simple', ]
        else:
            self.shot_type_list = ['simple', 'double', 'diagonal']
        if self.debug_mode == 0:
            if self.actual_wave > 1:
                self.shot_type_list.append('double')
            if self.actual_wave > 3:
                self.shot_type_list.append('diagonal')

    def enemy_reset(self):
        """
        Procédure qui remet à leur valeur initial toute les donnés liés aux enemis
        """
        self.enemy_list = []
        self.spawn_timer.setDuration(60)
        self.spawn_timer.restart()
        self.colonne_dispo = [0, 1, 2, 3, 4, 5]
        self.ovni_spawn = self.waves[self.actual_wave].ovni_frequency
        self.ovni = None
        self.bomb = None
        for attack in self.alien_attaque.values():
            attack.clean()

    def quitter(self) -> None:
        """
        Procédure qui sauvegarde les information importantes avant de quitter le jeu
        """
        if not self.played:
            self.achievement_handler.unlock("QMM")
        self.player_data.set_unlocked_list(self.achievement_handler.get_unlocked_list())
        self.player_data.set_current_wave(self.actual_wave + 1)
        self.save_handler.save(self.player_data)
        pygame.quit()
        sys.exit()

    def unpause(self) -> None:
        """
        Procédure qui gère le changement d'état après avoir quitter la pause
        """
        if self.waves[self.actual_wave].boss_wave and self.waves[self.actual_wave].boss.fight_started:
            self.game_state = 5
        else:
            self.game_state = 2

        if self.player.is_overdrive:
            pygame.mixer.music.stop()
            pygame.mixer.Channel(14).unpause()

    def game_start(self) -> None:
        """
        Procedure qui remet à leur etat initial toutes les variables de jeu
        et qui démarre ce dernier
        """

        # Donné du joueur
        
        self.played = True
        
        self.roboboss_end = False

        # Fais un fondu de la musique de l'ecran titre  durant 1/2 seconde
        self.game_state = 2 if self.debug_mode != 3 else 5

        self.space_lock = False

        # Vagues

        for wave in self.waves:
            wave.reset(hard=True)
        
        if self.actual_wave != 0:
            self.final_achievement = False
        else:
            self.final_achievement = True

        self.actual_wave = self.player_data.get_current_wave() - 1
        if self.waves[self.actual_wave].boss_wave:
            self.game_state = 5
            self.waves[self.actual_wave].boss.reset(music_reload=True)
        else:
            self.game_state = 2
            pygame.mixer.music.load(FIGHT_MUSIC)
            pygame.mixer.music.play(loops=-1)
        self.player_reset()
        self.enemy_reset()

        # Screen shake

        self.screen_shake_duration = -1
        self.screen_shake_intencity = 10
        self.offset = [0, 0]

        # Autres

        self.pause_cd = Timer(15)
        self.pile_liste = []
        
        if self.debug_mode == 0 and self.waves[self.actual_wave].is_playing_dialogue:
            self.waves[self.actual_wave].load_dialogue(self.dialogue_handler)
            pygame.mixer.music.pause()
            self.dialogue_music.play(loops=-1)

    def screen_shake_update(self) -> None:
        self.offset = [0, 0]
        if self.screen_shake_duration > 0:
            self.screen_shake_duration -= 1
            self.offset[0] = random.randint(0, self.screen_shake_intencity) - (self.screen_shake_intencity / 2)
            self.offset[1] = random.randint(0, self.screen_shake_intencity) - (self.screen_shake_intencity / 2)

    def is_player_already_dead_wave_one(self):
        for i in range(self.player_data.get_death_count()):
            death = self.player_data.get_death(i)
            if death.get_moment() == 1:
                return True
        return False

    def screenshot_pause_mode(self):

        self.s = self.screen_buffer
        filtre_transparent = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        filtre_transparent.fill((255, 137, 82))
        filtre_transparent.set_alpha(50)
        filtre_transparent = filtre_transparent.convert_alpha()
        self.s.blit(filtre_transparent, (0, 0))
        self.s = self.s.convert()

    def game_over_check(self) -> None:
        """
        Verifie la mort du joueur
        """
        self.player_data.set_current_wave(self.actual_wave + 1)
        if self.player.hp <= 0:  # Verifie si les pv du joueur sont egal a 0
            if self.actual_wave == 0:
                self.achievement_handler.unlock("V1M")
            self.player.dead = True
            self.screenshot_pause_mode()
            self.screen_shake_duration = 10
            self.screen_shake_intencity = 50
            mort = PlayerDeath(self.actual_wave + 1, self.player.last_damage_source)
            self.final_achievement = False

            logging.info(mort.__str__())

            self.player_data.add_death(mort)
            if self.player.is_overdrive:
                self.player.unoverdrive()

            pygame.mixer.music.load(GAME_OVER_MUSIC)
            pygame.mixer.music.play(-1)
            self.offset = [0, 0]
            # Changement de l'etat du jeu
            self.game_state = 4

    def enemy_update(self) -> None:
        dead_bullet = []  # Liste qui va stocker les balles du joueur qui vont disparaitre
        dead_enemy = []

        for i in range(len(self.enemy_list)):  # Parcours tous les ennemis
            # Deplacement
            if self.enemy_list[i].y <= ENEMY_VERTICAL_LIMIT:  # Si l'ennemis n'a pas depasser la limite vertical
                self.enemy_list[i].move()  # Il se deplace
            elif self.enemy_list[i].base_timer == ENEMY_LOW_SHOOT_SPEED:
                if type(self.enemy_list[i]) == Alien:
                    self.enemy_list[i].base_timer = ALIEN_HIGH_SHOOT_SPEED
                else:
                    self.enemy_list[i].base_timer = SP_HIGH_SHOOT_SPEED

            #  Degat recu des balles du joueur

            for j in range(len(self.player.bullets)):  # Parcours toutes les balles du joueur
                if self.enemy_list[i].collision_rect.colliderect(self.player.bullets[j]) and \
                        not self.enemy_list[i].is_invincible:
                    dead_bullet.append(j)  # On ajoute l'indice de la balle du joueur a la liste de disparition
                    self.enemy_list[i].take_damage(2)  # On fais prendre un degat à l'ennemi
                    if self.screen_shake_duration <= 0:
                        self.screen_shake_duration = 3
                        self.screen_shake_intencity = 4

            if self.enemy_list[i].timer == 0:  # Si le timer de tire de l'ennemi arrive a son terme
                # On verifie quel paterne d'attaque l'enemie possede
                # On verifie quel paterne d'attaque l'enemie possede
                # Format des tuples des balles -> (Rectangle de Colision, (velocite horizontal, velocite vertical))
                if isinstance(self.enemy_list[i], Alien):
                    self.alien_attaque[self.enemy_list[i].max_hp].new(self.enemy_list[i])
                elif isinstance(self.enemy_list[i], SpacePirate):
                    if self.player.get_colonne() == self.enemy_list[i].colonne:
                        self.alien_attaque[GREEN_ENEMY_HP].new(self.enemy_list[i])
                    elif self.player.sprite_y < ENEMY_VERTICAL_LIMIT + ENEMY_HEIGHT:
                        self.alien_attaque[GREEN_ENEMY_HP].new(self.enemy_list[i])
                    else:
                        self.enemy_list[i].attack.new(self.player, bool(random.randint(0, 1)))

                self.enemy_list[i].timer = self.enemy_list[i].base_timer + random.randint(
                    0, self.enemy_list[i].base_timer // 2)
            else:
                # Sinon on decrement d'une unite le timer de tire
                self.enemy_list[i].timer -= 1

            if isinstance(self.enemy_list[i], Alien):
                # Remet le sprite des ennemis a leur etat initial
                self.enemy_list[i].actual_sprite = self.enemy_list[i].base_sprite
                if self.enemy_list[i].is_invincible:
                    self.enemy_list[i].actual_sprite = 3
            elif isinstance(self.enemy_list[i], SpacePirate):
                self.enemy_list[i].attack.update(SCREEN_WIDTH, self.player)

            self.enemy_list[i].invincibility_decrease()  # On reduit le temps d'invincibilite restant
            if self.enemy_list[i].hp <= 0:
                # Si l'ennemis est mort on l'ajoute a la liste des ennemis mort pour le supprimer
                dead_enemy.append(i)
                # On ajoute le colonne de l'ennemi dans la liste de celle qui sont disponible
                self.colonne_dispo.append(self.enemy_list[i].colonne)
                # 4 chances sur 25 de laisser tomber une pile (Soin) si il y en a moin de 3 sur l'ecran
                valeur_aleatoire = random.randint(0, 100)
                if valeur_aleatoire < 40 and len(self.pile_liste) < 3:
                    self.pile_liste.append(Pile(self.enemy_list[i].x + 10, self.enemy_list[i].y))
                elif 39 < valeur_aleatoire < 55 \
                        and len(self.overdrive_fragement_liste) < 3 \
                        and not self.player.is_overdrive:
                    self.overdrive_fragement_liste.append(
                        FragementOverdrive(self.enemy_list[i].x + 10, self.enemy_list[i].y)
                    )

                for _ in range(random.randint(10, 30)):
                    self.particle_list.append(Particle(30, 'rectangle', self.enemy_list[i].color,
                                                       (random.randint(0, 20) / 5 - 3, random.randint(0, 20) / 5 - 3),
                                                       [9, 9], [self.enemy_list[i].x + 50, self.enemy_list[i].y + 20],
                                                       'fade_out'))

                    self.particle_list.append(Particle(30, 'circle', self.enemy_list[i].color,
                                                       (random.randint(0, 20) / 5 - 3, random.randint(0, 20) / 5 - 3),
                                                       [9, 9], [self.enemy_list[i].x + 50, self.enemy_list[i].y + 20],
                                                       'shrink'))

            enemy_player_collision = self.enemy_list[i].collision_rect.colliderect(self.player.colision_rect)
            if enemy_player_collision:
                # Si il y a une collision avec le joueur lorsqu'il n'est pas invincible
                self.player.take_damage(1, 60, "EnnemisCollision")

        # On inverse tri les valeur dans l'ordre decroissant pour faire disparaitre celle avec
        # la valeur la plus haute d'abord (sinon il y a une erreur pop index out of range)
        dead_bullet.sort(reverse=True)
        dead_enemy.sort(reverse=True)

        for elt in dead_bullet:  # Pour tous les elements de la liste de disparition
            self.player.delete_bullet(elt)  # On supprime la balles d'indice elt

        for elt in dead_enemy:
            self.enemy_list.pop(elt)

    def only_red_left(self):
        for enemy_type in self.waves[self.actual_wave].enemies_type:
            if enemy_type != 2:
                return False
        return True

    def enemy_spawn(self) -> None:
        if self.spawn_timer.getTimeLeft() == 60:
            while True:
                # Choisis une colonne le la liste des conlonne disponible
                colonne_id = random.randint(0, len(self.colonne_dispo) - 1)
                self.next_enemy_hp_id = random.randint(0, len(self.waves[self.actual_wave].enemies_type) - 1)
                already_red = False
                if self.waves[self.actual_wave].enemies_type[self.next_enemy_hp_id] == 2:
                    for i in range(len(self.enemy_list)):
                        if self.enemy_list[i].max_hp == RED_ENEMY_HP:
                            already_red = True
                            break
                if already_red and not self.only_red_left():
                    while True:
                        new_enemy_id = random.randint(0, len(self.waves[self.actual_wave].enemies_type) - 1)
                        if new_enemy_id != self.next_enemy_hp_id:
                            self.next_enemy_hp_id = new_enemy_id
                            self.spawn_timer.cancelTick()
                            break
                elif already_red:
                    self.spawn_timer.cancelTick(10)
                    break
                else:
                    break
            self.next_enemy_column_id = colonne_id
            test = self.waves[self.actual_wave].enemies_type[self.next_enemy_hp_id]
            self.next_enemy_color = self.enemy_color_dict[test]
        elif 0 < self.spawn_timer.getTimeLeft() < 60 and self.spawn_timer.getTimeLeft() % 4 == 0:
            for i in range(random.randint(10, 20)):
                random_coordonne = [
                    (self.colonne_dispo[self.next_enemy_column_id] * ENEMY_WIDTH) + 40 + random.randint(-30, 30),
                    40 + random.randint(-30, 30)
                ]
                central_velocity = (
                    -2 if (self.colonne_dispo[self.next_enemy_column_id] * ENEMY_WIDTH) + 40 < random_coordonne[0]
                    else 2,
                    -2 if 40 < random_coordonne[1] else 2
                )
                self.particle_list.append(Particle(
                    20, 'rectangle', self.next_enemy_color, central_velocity, [9, 9], random_coordonne, 'shrink'
                ))
            for i in range(random.randint(10, 20)):
                random_coordonne = [
                    (self.colonne_dispo[self.next_enemy_column_id] * ENEMY_WIDTH) + 40 + random.randint(-30, 30),
                    40 + random.randint(-30, 30)
                ]
                central_velocity = (
                    -2 if (self.colonne_dispo[self.next_enemy_column_id] * ENEMY_WIDTH) + 40 < random_coordonne[0]
                    else 2,
                    -2 if 40 < random_coordonne[1] else 2
                )
                self.particle_list.append(Particle(
                    20, 'circle', self.next_enemy_color, central_velocity, [9, 9], random_coordonne, 'fade_out')
                )
        timeout = self.spawn_timer.tick()
        if timeout:
            hp = self.alien_hp[self.waves[self.actual_wave].enemies_type[self.next_enemy_hp_id]]
            if hp != SP_ENEMY_HP:
                # Tire un nombre de pv au hasard pour un ennemi
                self.enemy_list.append(Alien(
                    hp, self.colonne_dispo[self.next_enemy_column_id], self.waves[self.actual_wave].enemies_shoot_speed
                ))
            else:
                self.enemy_list.append(SpacePirate(
                    hp, self.colonne_dispo[self.next_enemy_column_id], self.waves[self.actual_wave].enemies_shoot_speed
                ))
            self.waves[self.actual_wave].enemies_type.pop(self.next_enemy_hp_id)
            # Retire la colonne choisi pour l'apparition des ennemis des colonne disponible
            self.colonne_dispo.pop(self.next_enemy_column_id)
            self.spawn_timer.setDuration(
                self.waves[self.actual_wave].enemies_spawn_delais + random.randint(
                    0, self.waves[self.actual_wave].enemies_spawn_delais)
            )  # Met un delais aleatoire entre cette apparition et la suivante
            self.spawn_timer.restart()

    def wave_handler(self) -> None:
        if len(self.waves[self.actual_wave].enemies_type) == 0 \
                and len(self.enemy_list) == 0 \
                and self.ovni is None \
                and self.bomb is None:
            if self.actual_wave + 1 < len(self.waves):
                self.actual_wave += 1
                self.ovni_spawn = self.waves[self.actual_wave].ovni_frequency
                if self.actual_wave == 2:
                    self.achievement_handler.unlock("2TR")
                    self.shot_type_list.append('double')
                elif self.actual_wave == 4:
                    self.achievement_handler.unlock("8TR")
                    self.shot_type_list.append('diagonal')
                if self.debug_mode == 0 and self.waves[self.actual_wave].is_playing_dialogue:
                    pygame.mixer.music.pause()
                    pygame.mixer.Channel(14).pause()
                    self.dialogue_music.play(loops=-1)
                    self.waves[self.actual_wave].load_dialogue(self.dialogue_handler)
            else:
                self.back_to_title_screen()
                self.actual_wave = 0
                self.player_data.add_win()
            if self.waves[self.actual_wave].boss_wave:
                self.game_state = 5
                if self.player.is_overdrive:
                    self.player.unoverdrive()
            elif self.player.is_overdrive and not self.waves[self.actual_wave].is_playing_dialogue:
                pygame.mixer.pause()
                pygame.mixer.music.play(-1)

            logging.info(f'Vague {self.actual_wave} terminer, début de la vague {self.actual_wave + 1}')
            print(f'is_started = {self.waves[self.actual_wave].is_started}\nis_playing_dialogue= {self.waves[self.actual_wave].is_playing_dialogue}')

            self.waves[self.actual_wave - 1].reset()

    def spawn_ovni(self) -> None:
        line_id = random.randint(0, 5)
        if (4, 5, 6, 9, 10, 11)[line_id] != self.player.get_line():
            if self.debug_mode == 2:
                self.ovni = OvniEnemy(self.player.get_colonne(), (4, 5, 6, 9, 10, 11)[line_id], 3)
            else:
                self.ovni = OvniEnemy(
                    self.player.get_colonne(), (4, 5, 6, 9, 10, 11)[line_id], self.waves[self.actual_wave].ovni_speed
                )

        else:
            if line_id != 5:
                line_id += 1
            else:
                line_id -= 1
            if self.debug_mode == 2:
                self.ovni = OvniEnemy(self.player.get_colonne(), (4, 5, 6, 9, 10, 11)[line_id], 3)
            else:
                self.ovni = OvniEnemy(
                    self.player.get_colonne(), (4, 5, 6, 9, 10, 11)[line_id], self.waves[self.actual_wave].ovni_speed
                )

    def ovni_spawning(self) -> None:
        if self.ovni_spawn == 0 and self.ovni is None:
            self.spawn_ovni()
        elif self.ovni_spawn > 0:
            self.ovni_spawn -= 1

    def ovni_mouvment_and_bomb_placement(self) -> None:
        if not self.ovni.came_back:
            self.ovni.move_to_place(self.ovni.end_move)

            # Placement de la bombe

            if self.ovni.end_move and self.bomb is None:
                self.bomb = OvniBomb(self.ovni.x + 23, self.ovni.y)
        else:
            self.ovni = None
            if self.debug_mode != 2:
                self.ovni_spawn = self.waves[self.actual_wave].ovni_frequency + random.randint(1, 500)
            return None

        backup = []

        for i in range(len(self.player.bullets)):
            if self.ovni.colision_rect.colliderect(self.player.bullets[i]):
                self.ovni.hp -= 1
                self.ovni.draw = False
                if self.screen_shake_duration <= 0:
                    self.screen_shake_duration = 3
                    self.screen_shake_intencity = 4
                backup.append(i)

        backup.sort(reverse=True)

        for elt in backup:
            self.player.delete_bullet(elt)

        # Mort

        if self.ovni.hp == 0:
            self.achievement_handler.unlock("OVN")
            self.ovni_spawn = self.waves[self.actual_wave].ovni_speed * random.randint(1, 4)
            self.ovni = None

    def bomb_explosion_colision(self) -> None:
        for i in range(len(self.enemy_list)):
            if type(self.enemy_list[i]) == Alien:
                if self.bomb.damage_rect_vertical.colliderect(self.enemy_list[i].collision_rect) \
                        or self.bomb.damage_rect_horizontal.colliderect(self.enemy_list[i].collision_rect):
                    if not self.enemy_list[i].is_invincible:
                        is_dead = self.enemy_list[i].take_damage(invincibility_timer=10)
                        if is_dead:
                            self.achievement_handler.unlock('SMB')

        # Collision avec un joueur

        if self.bomb.damage_rect_vertical.colliderect(
                self.player.colision_rect) or self.bomb.damage_rect_horizontal.colliderect(self.player.colision_rect):
            self.player.take_damage(2, 30, "OvniBombe")

    def bomb_flash(self) -> None:
        if self.bomb.affichage_timer < -1 * self.bomb.base_affichage_timer:
            self.bomb.affichage_timer = self.bomb.base_affichage_timer

        self.bomb.affichage_timer -= 1

        if 60 > self.bomb.explosion_timer > 30:
            self.bomb.base_affichage_timer = 4
        elif self.bomb.explosion_timer < 30:
            self.bomb.base_affichage_timer = 3

    def bomb_explosion(self) -> None:
        if self.bomb.explosion_timer == 0 and not self.bomb.has_explode:
            self.bomb.explode()
            self.screen_shake_duration = self.bomb.explosion_duration
            self.screen_shake_intencity = 16
        elif not self.bomb.has_explode:
            self.bomb.explosion_timer -= 1

        if self.bomb.has_explode:
            if self.bomb.explosion_duration == 0:
                self.bomb = None
            else:
                self.bomb.explosion_duration -= 1

    def pile_update(self) -> None:
        backup = []  # Liste qui va stocker les piles qui seront supprimer

        for i in range(len(self.pile_liste)):
            self.pile_liste[i].move()  # Deplacement de la pile

            # Colision avec le joueur

            if self.pile_liste[i].colision_rect.colliderect(self.player.colision_rect):
                backup.append(i)  # Ajout à liste de suppression

                # Soin du joueur

                if self.player.hp < self.player.max_hp:
                    self.player.hp += 1

            # Sortie de l'ecran

            elif self.pile_liste[i].y >= 780:
                backup.append(i)  # Ajout à liste de suppression

        # On inverse tri les valeur dans l'ordre decroissant pour faire disparaitre celle avec la valeur la plus haute
        # d'abord (sinon il y a une erreur pop index out of range)
        backup.sort(reverse=True)

        for elt in backup:  # Pour tous les elements de la liste de disparition
            self.pile_liste.pop(elt)  # On supprime la Pile d'indice elt

    def fragment_update(self):
        backup = []  # Liste qui va stocker les fragement qui seront supprimer

        for i in range(len(self.overdrive_fragement_liste)):
            self.overdrive_fragement_liste[i].move()  # Deplacement du fragement

            # Colision avec le joueur

            if self.overdrive_fragement_liste[i].colision_rect.colliderect(self.player.colision_rect):
                backup.append(i)  # Ajout à liste de suppression
                
                if self.player_data.get_first_time_overdrive_fragment():
                    self.player_data.set_first_time_of(False)
                    self.waves[self.actual_wave].is_playing_dialogue = True
                    self.dialogue_handler.play_dialog("Gold_Pile")
                    
                self.overdrive_fragement_collected += 1
                
                self.text_compteur_overdrive = self.pv_font.render(f"{self.overdrive_fragement_collected}/3", True, "#ffdf00")
                self.fragment_hud_showing = True
                self.fragment_hud_timer.restart()

                if self.overdrive_fragement_collected == 3:
                    self.player.overdrive()
                    self.overdrive_fragement_collected = 0

            # Sortie de l'ecran

            elif self.overdrive_fragement_liste[i].y >= 780:
                backup.append(i)  # Ajout à liste de suppression

        # On inverse tri les valeur dans l'ordre decroissant pour faire disparaitre celle avec la valeur la plus haute
        # d'abord (sinon il y a une erreur pop index out of range)
        backup.sort(reverse=True)

        for elt in backup:  # Pour tous les elements de la liste de disparition
            self.overdrive_fragement_liste.pop(elt)  # On supprime la Pile d'indice elt

    def back_to_title_screen(self) -> None:
        self.offset = [0, 0]
        if self.player.is_overdrive:
            self.player.unoverdrive()
        if self.waves[self.actual_wave].is_playing_dialogue:
            pygame.mixer.stop()
        if pygame.mixer.get_busy():
            pygame.mixer.music.fadeout(500)
        pygame.mixer.music.load(MENU_MUSIC)
        pygame.mixer.music.play(-1)
        # Changement de l'etat du jeu
        self.game_state = 0
        # self.start_timer = -1

    def debuging_spawn_enemy(self, max_hp) -> None:
        if len(self.colonne_dispo) != 0:
            # Choisis une colonne le la liste des conlonne disponible
            colonne_id = random.randint(0, len(self.colonne_dispo) - 1)
            if max_hp in self.alien_hp:
                self.enemy_list.append(Alien(max_hp, self.colonne_dispo[colonne_id], ENEMY_LOW_SHOOT_SPEED))
            elif max_hp == 1:
                self.enemy_list.append(BlackAlien(self.colonne_dispo[colonne_id], 6))
            else:
                self.enemy_list.append(SpacePirate(35, self.colonne_dispo[colonne_id], ENEMY_LOW_SHOOT_SPEED))
            self.colonne_dispo.pop(colonne_id)

    def handling_event(self) -> None:
        """Procedure qui gères les inputs du joueur"""
        key_pressed = pygame.key.get_pressed()

        if self.debug_mode != 0 and key_pressed[pygame.K_q]:
            self.quitter()

        # Dev command
        if self.debug_mode in [1, 3]:
            if key_pressed[pygame.K_KP0]:
                if self.player.hp != 0:
                    self.player.take_damage(1, 0, "DebugCheat")
            if key_pressed[pygame.K_KP3]:
                if self.player.hp != 10:
                    self.player.hp += 1
            if key_pressed[pygame.K_KP1]:
                self.enemy_list = []
                self.colonne_dispo = [0, 1, 2, 3, 4, 5]
            if key_pressed[pygame.K_KP2]:
                for attack in self.alien_attaque.values():
                    attack.clean()
            if key_pressed[pygame.K_KP5]:
                self.actual_wave = 5
                self.game_state = 5
            if key_pressed[pygame.K_KP8]:
                print("Debug mode")
        # Evenement faisable à nimporte quelle moment ou à l'ecran titre
        for event in pygame.event.get():  # Parcours des evenement
            if event.type == pygame.QUIT:
                # Si le joueur clic sur la croix on ferme la fenêtre
                self.quitter()
            elif event.type == pygame.KEYDOWN and not self.is_in_splash_screen:
                key_pressed = pygame.key.get_pressed()
                if self.debug_mode == 1:
                    if key_pressed[pygame.K_KP4] and self.actual_wave > 0:
                        self.waves[self.actual_wave].reset()
                        self.waves[self.actual_wave - 1].is_playing_dialogue = False
                        self.actual_wave -= 1
                        if self.game_state == 5 and not self.waves[self.actual_wave].boss_wave:
                            self.game_state = 2
                        elif self.waves[self.actual_wave].boss_wave:
                            self.game_state = 5
                        self.ovni_spawn = self.waves[self.actual_wave].ovni_frequency
                    elif key_pressed[pygame.K_KP6] and self.actual_wave < len(self.waves) - 1:
                        self.waves[self.actual_wave].reset()
                        self.waves[self.actual_wave - 1].is_playing_dialogue = False
                        self.actual_wave += 1
                        if self.game_state == 5 and not self.waves[self.actual_wave].boss_wave:
                            self.game_state = 2
                        elif self.waves[self.actual_wave].boss_wave:
                            self.game_state = 5
                        self.ovni_spawn = self.waves[self.actual_wave].ovni_frequency
                    elif key_pressed[pygame.K_KP7]:
                        self.player.overdrive()
                elif self.debug_mode == 2:
                    if key_pressed[pygame.K_KP1]:
                        self.debuging_spawn_enemy(GREEN_ENEMY_HP)
                    if key_pressed[pygame.K_KP2]:
                        self.debuging_spawn_enemy(YELLOW_ENEMY_HP)
                    if key_pressed[pygame.K_KP3]:
                        self.debuging_spawn_enemy(RED_ENEMY_HP)
                    if key_pressed[pygame.K_KP4]:
                        self.debuging_spawn_enemy(0)
                    if key_pressed[pygame.K_KP5]:
                        self.debuging_spawn_enemy(1)
                    if key_pressed[pygame.K_KP6]:
                        for alien in self.enemy_list:
                            if isinstance(alien, BlackAlien):
                                alien.attaque.new(bool(random.randint(0, 1)))
                    if key_pressed[pygame.K_KP0]:
                        self.spawn_ovni()

                if self.konami_code_avencement < 10 and key_pressed[KONAMI_CODE[self.konami_code_avencement]]:
                    self.konami_code_avencement += 1
                    if self.konami_code_avencement == 10:
                        self.achievement_handler.unlock('KCD')
                elif self.konami_code_avencement < 10:
                    self.konami_code_avencement = 0

                if key_pressed[pygame.K_m]:
                    if pygame.mixer.get_busy():
                        pygame.mixer.pause()
                    else:
                        pygame.mixer.unpause()
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                if self.game_state == 0:
                    if key_pressed[pygame.K_DOWN]:
                        self.main_menu.next_element()
                    elif key_pressed[pygame.K_UP]:
                        self.main_menu.previous_element()
                    elif key_pressed[pygame.K_SPACE]:
                        self.main_menu.activate_selected()
                elif self.waves[self.actual_wave].is_playing_dialogue and self.game_state in (2, 5):
                    if key_pressed[pygame.K_SPACE]:
                        is_finished = self.dialogue_handler.next()
                        if is_finished:
                            self.waves[self.actual_wave].is_playing_dialogue = False
                            self.dialogue_music.stop()
                            pygame.mixer.music.unpause()
                            if self.player.is_overdrive:
                                pygame.mixer.music.stop()
                                pygame.mixer.Channel(14).unpause()
                        return
                elif self.game_state == 3:
                    if key_pressed[pygame.K_DOWN]:
                        self.pause_menu.next_element()
                    if key_pressed[pygame.K_UP]:
                        self.pause_menu.previous_element()
                    if key_pressed[pygame.K_SPACE]:
                        self.pause_menu.activate_selected()
                elif self.game_state == 1:
                    if key_pressed[pygame.K_ESCAPE]:
                        self.game_state = 0
                        self.achievement_handler.reset_menu_pos()
                    if key_pressed[pygame.K_RIGHT]:
                        self.achievement_handler.next_in_menu()
                    elif key_pressed[pygame.K_LEFT]:
                        self.achievement_handler.previous_in_menu()
                    if key_pressed[pygame.K_SPACE]:
                        if self.achievement_handler.get_menu_selected() == 5:
                            self.achievement_handler.unlock('SHH')
                elif self.game_state == 4:
                    if key_pressed[pygame.K_DOWN]:
                        self.menu_game_over.next_element()
                    if key_pressed[pygame.K_UP]:
                        self.menu_game_over.previous_element()
                    if key_pressed[pygame.K_SPACE]:
                        self.menu_game_over.activate_selected()

        if self.is_in_splash_screen:
            return None
    
        if self.waves[self.actual_wave].has_starting_dialogue and self.debug_mode != 0:
            self.waves[self.actual_wave].is_playing_dialogue = False

        # Evenement faisable en jeu lorsqu'il n'est pas en pause et quand le joueur n'est pas mort mais est lancer

        if self.game_state in (2, 5) and not self.player.is_overheat:
            # Gestion du changement de ,mode de tire

            timeout = self.cooldown.tick()

            if key_pressed[pygame.K_c] and timeout:
                if self.player.shot_mode + 1 < len(self.shot_type_list):
                    # Mode suivant
                    self.player.shot_mode += 1
                    self.cooldown.restart()  # Cooldowm pour eviter que le joueur ai le temps de relacher le bouton
            if key_pressed[pygame.K_x] and timeout:
                if self.player.shot_mode - 1 >= 0:
                    # Mode précédent + mise en place du cooldowm
                    self.player.shot_mode -= 1
                    self.cooldown.restart()

            # Gestion des tires du joueurs

            if key_pressed[pygame.K_SPACE] and self.player.timer_bullets == 0:
                self.player.shot(self.shot_type_list[self.player.shot_mode])  # Le joueur tire
                # On met a jour le delais entre les tires
                self.player.timer_bullets = self.shot_rate_dict[self.shot_type_list[self.player.shot_mode]]
                # On bloc la barre n'espace pour que le joueur ai a la relacher avant de la presser
                # a nouveau pour le gameover
                self.space_lock = True
                if not self.player.is_overdrive:
                    if self.player.shot_mode == 0:
                        self.player.point_overheat -= LOW_OVERHEAT
                    elif self.player.shot_mode == 1:
                        if self.player.point_overheat - MEDIUM_OVERHEAT > 0:
                            self.player.point_overheat -= MEDIUM_OVERHEAT
                        else:
                            self.player.point_overheat = 0
                    elif self.player.shot_mode == 2:
                        if self.player.point_overheat - HIGH_OVERHEAT > 0:
                            self.player.point_overheat -= HIGH_OVERHEAT
                        else:
                            self.player.point_overheat = 0
                    if self.player.point_overheat < 0:
                        self.player.point_overheat = 0
                    if self.player.point_overheat == 0:
                        for _ in range(random.randint(30, 40)):
                            self.particle_list.append(Particle(
                                30,
                                'circle',
                                '#a84242',
                                ((random.randint(-5, 5) + 1) / 2, (random.randint(-5, 5) + 1) / 2),
                                [10, 10],
                                [self.player.colision_rect.x + 9, self.player.colision_rect.y + 12],
                                'shrink'
                            ))
                            self.particle_list.append(Particle(
                                30,
                                'rectangle',
                                '#a84242',
                                ((random.randint(-5, 5) + 1) / 2, (random.randint(-5, 5) + 1) / 2),
                                [10, 10],
                                [self.player.colision_rect.x + 9, self.player.colision_rect.y + 12],
                                'shrink'
                            ))
                        self.screen_shake_duration = 10
                        self.screen_shake_intencity = 25
                        self.player.is_overheat = True
            # Si le joueur a relacher la barre d'espace on la debloque (toujours pour le game over)
            elif not key_pressed[pygame.K_SPACE]:
                self.space_lock = False
                if self.player.point_overheat < self.player.base_point_overheat:  # 4f4848
                    self.player.point_overheat += 0.25

            # Gestion des déplacements du joueur

            if key_pressed[pygame.K_LEFT]:  # Gauche
                self.player.x_velocity = -5
            if key_pressed[pygame.K_RIGHT]:  # Droite
                self.player.x_velocity = 5
            if key_pressed[pygame.K_UP]:  # Haut
                self.player.y_velocity = -5
            if key_pressed[pygame.K_DOWN]:  # Bas
                self.player.y_velocity = 5

        elif self.player.is_overheat and self.game_state != 3:
            if self.player.point_overheat < self.player.base_point_overheat:
                if random.randint(0, 20) == 15:
                    self.particle_list.append(Particle(
                        60,
                        'circle',
                        '#4f4848',
                        (0, -5),
                        [30, 30],
                        [self.player.colision_rect.x + 3, self.player.colision_rect.y - 10],
                        'fade_out'
                    ))
                self.player.point_overheat += 0.25

        if self.player.point_overheat == self.player.base_point_overheat:
            self.player.is_overheat = False

        self.overheat_rect.width = self.player.point_overheat * 3.38

        # Evnement qui sont faisable en jeu meme si il est en pause

        if self.game_state in (2, 3) or \
                (self.game_state == 5
                 and self.waves[self.actual_wave].boss_wave
                 and self.waves[self.actual_wave].boss.fight_started):

            cd_timeout = self.pause_cd.tick()

            # Mise en pause
            if key_pressed[pygame.K_ESCAPE] and cd_timeout and self.game_state != 3:
                self.screenshot_pause_mode()
                if self.game_state in (2, 5):
                    self.game_state = 3
                    if self.player.is_overdrive:
                        pygame.mixer.Channel(14).pause()
                        pygame.mixer.music.play(loops=-1)
                self.pause_cd.restart()  # Delais avant de pouvoir re-pauser / de-pauser

    def update(self) -> None:
        """Procedure qui met à jour les valeur en jeu"""

        if not self.player.dead:

            if self.roboboss_end:
                self.end_cutscene.play()
                self.roboboss_end = self.end_cutscene.playing
                if not self.roboboss_end:
                    self.credit_cutscene.load_from_json_dict(self.credit_dict)
                    self.game_state = 6
                return

            if self.game_state == 6:
                self.credit_cutscene.play()
                if not self.credit_cutscene.playing:
                    self.win()
                return


            # Balles du joueur
            
            if self.debug_mode == 2:
                for alien in self.enemy_list:
                    if isinstance(alien, BlackAlien):
                        alien.update(self.player)

            self.player.bullet_move()  # Déplacement  des balles émise par le joueurs

            # Mort du joueur

            self.game_over_check()

            # Delais / Timer du joueur

            self.player.timer_decrease()

            # Ennemis

            self.enemy_update()

            # balles

            for att in self.alien_attaque.values():
                att.update(self.player)

            # Apparition des ennemis

            if self.game_state != 5 and self.debug_mode < 2:

                if len(self.colonne_dispo) != 0 \
                        and len(self.waves[self.actual_wave].enemies_type) != 0 \
                        and self.waves[self.actual_wave].is_started:
                    self.enemy_spawn()

                if self.game_state != 4:
                    # Sequence de début de vague
                    if not self.waves[self.actual_wave].is_started and not self.waves[self.actual_wave].is_playing_dialogue:
                        self.waves[self.actual_wave].intro_seq()

                    self.wave_handler()
                # Apparition d'un ovni

                self.ovni_spawning()

            if self.ovni is not None:
                # Mouvement de l'ovni et placement de la bombe

                self.ovni_mouvment_and_bomb_placement()

            if self.bomb is not None:

                # Colision avec un ennemi

                if self.bomb.damage_rect_vertical is not None and self.bomb.damage_rect_horizontal is not None:
                    self.bomb_explosion_colision()

                # Gestion du clignotement de la bombe

                self.bomb_flash()
                # Explosion

                self.bomb_explosion()

            # Piles

            self.pile_update()

            self.fragment_update()

            if self.game_state == 5 and self.waves[self.actual_wave].boss_wave:
                if self.waves[self.actual_wave].boss.fight_started:
                    self.waves[self.actual_wave].boss.update(self)

                    if self.waves[self.actual_wave].boss.hp_bar.boss_hp <= 0:
                        if isinstance(self.waves[self.actual_wave].boss, Anguille):
                            self.achievement_handler.unlock("VDA")
                            pygame.mixer.music.load(FIGHT_MUSIC)
                            pygame.mixer.music.play(loops=-1)
                        elif isinstance(self.waves[self.actual_wave].boss, RoboBoss):
                            self.achievement_handler.unlock("VDM")
                            pygame.mixer.music.unload()
                            self.roboboss_end = True
                            self.end_cutscene.load_from_json_dict(self.dict_cutscene)

                        self.player.hp = self.player.max_hp

                        for i in range(60):
                            self.particle_list.append(
                                Particle(duration=30,
                                         shape='circle',
                                         color='#109119',
                                         velocity=(
                                             -5 ** random.randint(0, 1),
                                             -5 ** random.randint(0, 1)

                                         ),
                                         size=[10, 10],
                                         position=[self.player.sprite_x + 30, self.player.sprite_y + 27],
                                         deasapear_mode='fade_out'
                                         )
                            )

                        self.waves[self.actual_wave].boss.reset(music_reload=False)
                        self.waves[self.actual_wave].reset(hard=True)
                        if self.actual_wave + 1 < len(self.waves):
                            self.actual_wave += 1
                            self.game_state = 2
                            self.offset = [0, 0]
                            self.waves[self.actual_wave].load_dialogue(self.dialogue_handler)
                        logging.info(f'Vague {self.actual_wave} terminer, début de la vague {self.actual_wave + 1}')
                        self.ovni_spawn = self.waves[self.actual_wave].ovni_frequency
                elif not self.waves[self.actual_wave].is_playing_dialogue:
                    self.waves[self.actual_wave].boss.fight_started \
                        = self.waves[self.actual_wave].boss.intro_sequence_update()
                    if self.waves[self.actual_wave].boss.fight_started:
                        self.player.is_overheat = False
                    else:
                        self.player.colision_rect.x = 295
                        self.player.colision_rect.y = 600
                        self.player.is_overheat = True

                self.player.recul()

            # Movement du joueur
            if self.game_state != 5:
                self.player.move(15)  # Déplace le joueur
            else:
                self.player.move(315)

            self.player.x_velocity = 0  # Reinitialise la velocité horizontale
            self.player.y_velocity = 0  # Reinitialise la velocité vertical.

        # Particule
        backup = []

        for i in range(len(self.particle_list)):
            self.particle_list[i].update()
            if self.particle_list[i].get_dead():
                backup.append(i)

        backup.sort(reverse=True)

        for elt in backup:
            self.particle_list.pop(elt)

        self.screen_shake_update()

    def display(self) -> None:
        """Procédure qui permet de mettre à jour l'affichage"""

        if self.game_state < 2:
            self.screen_buffer.blit(self.fond_menu, (0, 0))
        else:
            self.screen_buffer.blit(self.fond, (0, 0))  # On dessine le fond

        if self.roboboss_end:
            self.end_cutscene.draw(self.screen_buffer)
            self.screen_buffer.convert()
            self.screen.blit(self.screen_buffer, (0, 0))
            pygame.display.flip()
            return

        if self.game_state == 6 and self.credit_cutscene.playing:
            self.credit_cutscene.draw(self.screen)
            pygame.display.flip()
            return

        if self.game_state == 6:
            self.screen.fill((0, 0, 0))
            pygame.display.flip()
            return

        if self.game_state == 5 and not self.waves[self.actual_wave].is_playing_dialogue \
                or (self.waves[self.actual_wave].boss_wave
                    and self.waves[self.actual_wave].boss.fight_started
                    and self.game_state in (3, 4)):
            self.waves[self.actual_wave].boss.draw_bg(self.screen_buffer)

        # Affichage lorque le jeu est lance ou quand le joueur est mort
        for bullet in self.player.bullets:
            self.screen_buffer.blit(self.player.bullet_sprite, (bullet.x, bullet.y))

        if self.game_state in (2, 5):
            if self.game_state == 5 and not self.waves[self.actual_wave].is_playing_dialogue \
                    or (self.waves[self.actual_wave].boss_wave
                        and self.waves[self.actual_wave].boss.fight_started
                        and self.game_state in (3, 4)):
                self.waves[self.actual_wave].boss.draw(self.screen_buffer)
            if not self.waves[self.actual_wave].is_started:
                self.screen_buffer.blit(
                    self.waves[self.actual_wave].big_wave_txt,
                    (130, self.waves[self.actual_wave].big_txt_y)
                )

            if self.bomb is not None:
                if self.bomb.affichage_timer > 0:
                    self.screen_buffer.blit(self.ovni_sprites["bomb"], (self.bomb.x, self.bomb.y))
                elif self.bomb.affichage_timer <= 0:
                    self.screen_buffer.blit(self.ovni_sprites["bomb_red"], (self.bomb.x, self.bomb.y))

                if self.bomb.damage_rect_horizontal is not None:
                    self.screen_buffer.blit(
                        self.ovni_sprites["explosion_fire_horizontal"],
                        (self.bomb.damage_rect_horizontal.x, self.bomb.damage_rect_horizontal.y)
                    )
                    self.screen_buffer.blit(
                        self.ovni_sprites["explosion_fire_vertical"],
                        (self.bomb.damage_rect_vertical.x, self.bomb.damage_rect_vertical.y)
                    )
                    self.screen_buffer.blit(self.ovni_sprites["explosion_croisement"], (self.bomb.x, self.bomb.y))
                else:
                    pygame.draw.rect(self.screen_buffer, '#de4604', (0, self.bomb.y, 640, 60), 2)
                    pygame.draw.rect(self.screen_buffer, '#de4604', (self.bomb.x, 0, 60, 780), 2)
                    if self.bomb.y != 477 or self.bomb.get_column() in self.colonne_dispo:
                        self.screen_buffer.blit(self.ovni_sprites["warning"], (self.bomb.x + 5, self.bomb.y - 70))
                    else:
                        self.screen_buffer.blit(self.ovni_sprites["warning"], (self.bomb.x + 5, self.bomb.y - 140))
                    if self.bomb.y != 318 or self.bomb.get_column() in self.colonne_dispo:
                        self.screen_buffer.blit(self.ovni_sprites["warning"], (self.bomb.x + 5, self.bomb.y + 70))
                    else:
                        self.screen_buffer.blit(self.ovni_sprites["warning"], (self.bomb.x + 5, self.bomb.y + 140))
                    if self.bomb.x != 641:
                        self.screen_buffer.blit(self.ovni_sprites["warning"], (self.bomb.x + 70, self.bomb.y + 7))
                    if self.bomb.x != 23:
                        self.screen_buffer.blit(self.ovni_sprites["warning"], (self.bomb.x - 70, self.bomb.y + 7))

            if self.ovni is not None:
                if self.ovni.draw:
                    self.screen_buffer.blit(self.ovni_sprites["ovni"], (self.ovni.x, self.ovni.y))
                else:
                    self.ovni.draw = True

            # Affichage des points de vies

            for enemy in self.enemy_list:
                if isinstance(enemy, BlackAlien):
                    enemy.draw(self.screen_buffer)

            self.screen_buffer.blit(self.hp_txt, (410, 737))  # Texte du HUD

            # PV paire (sans demi-barre)

            if self.player.hp % 2 == 0:

                # Barre(s) complette(s)

                for i in range(self.player.hp // 2):
                    self.screen_buffer.blit(self.player.hp_bar[0], (self.pv_x[i], 710))

                # Barre(s) vide(s)

                for i in range((self.player.max_hp // 2) - (self.player.hp // 2)):
                    self.screen_buffer.blit(self.player.hp_bar[2], (self.pv_x[i + (self.player.hp // 2)], 710))

            # PV impaire (avec demi-barre)

            else:

                # Barre(s) complette(s)

                for i in range(self.player.hp // 2):
                    self.screen_buffer.blit(self.player.hp_bar[0], (self.pv_x[i], 710))

                # Demi-Barre

                self.screen_buffer.blit(self.player.hp_bar[1], (self.pv_x[(self.player.hp // 2)], 710))

                # Barre(s) vide(s)

                if (self.player.hp // 2) + 1 < self.player.max_hp // 2:
                    for i in range((self.player.max_hp // 2) - ((self.player.hp // 2) + 1)):
                        self.screen_buffer.blit(
                            self.player.hp_bar[2], (self.pv_x[i + ((self.player.hp // 2) + 1)], 710)
                        )

            # Affichage des ameliorations

            self.screen_buffer.blit(self.waves[self.actual_wave].small_wave_txt, (250, 710))
            for i in range(len(self.shot_type_list)):
                if self.shot_type_list[self.player.shot_mode] == self.shot_type_list[i]:
                    self.screen_buffer.blit(self.player.upgrade_dict[self.shot_type_list[i]]['toggle'],
                                            (210 + (33 * (3 - len(self.shot_type_list)) + 60 * i), 730))
                else:
                    self.screen_buffer.blit(self.player.upgrade_dict[self.shot_type_list[i]]['untoggle'],
                                            (210 + (33 * (3 - len(self.shot_type_list)) + 60 * i), 730))

            if self.player.is_overdrive:
                self.screen_buffer.blit(self.overdrive_text, (23, 710))
            else:
                self.screen_buffer.blit(self.overheat_text, (18, 710))

            if self.player.is_overdrive:
                pygame.draw.rect(
                    self.screen_buffer,
                    (
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255)
                    ),
                    self.overheat_rect
                )
            else:
                pygame.draw.rect(
                    self.screen_buffer,
                    (
                        255 - int(self.player.point_overheat * 5.66),
                        0 + int(self.player.point_overheat * 5.66),
                        0
                    ),
                    self.overheat_rect
                )

            if self.player.invincibility_timer % 2 == 0 or 4 >= self.game_state >= 4:
                if self.player.is_overheat \
                        and (not self.game_state == 5 or self.waves[self.actual_wave].boss.fight_started):
                    self.screen_buffer.blit(self.player.overheat_sprite, (self.player.sprite_x, self.player.sprite_y))
                else:
                    self.screen_buffer.blit(self.player.sprite, (self.player.sprite_x, self.player.sprite_y))

            for enemy in self.enemy_list:
                if isinstance(enemy, Alien):
                    if self.actual_wave > 5 and enemy.actual_sprite != 3:
                        self.screen_buffer.blit(self.alien_sprites[enemy.actual_sprite + 4], (enemy.x, enemy.y))
                    else:
                        self.screen_buffer.blit(self.alien_sprites[enemy.actual_sprite], (enemy.x, enemy.y))
                elif isinstance(enemy, SpacePirate):
                    if enemy.is_invincible:
                        self.screen_buffer.blit(self.space_pirate_damaged_sprite, (enemy.x, enemy.y))
                    else:
                        self.screen_buffer.blit(self.space_pirate_sprite, (enemy.x, enemy.y))
                    enemy.attack.draw(self.screen_buffer)

                # pygame.draw.rect(self.screen_buffer, '#ff0000', enemy.collision_rect)
            # pygame.draw.rect(self.screen_buffer, '#ff0000', self.player.colision_rect)
            for attack in self.alien_attaque.values():
                attack.draw(self.screen_buffer)

            for pile in self.pile_liste:
                self.screen_buffer.blit(pile.img, (pile.x, pile.y))

            for fragement in self.overdrive_fragement_liste:
                self.screen_buffer.blit(self.sprite_overdrive_fragment, (fragement.x, fragement.y))

            if  self.game_state == 5 and not self.waves[self.actual_wave].is_playing_dialogue \
                or (self.waves[self.actual_wave].boss_wave
                    and self.waves[self.actual_wave].boss.fight_started
                    and self.game_state in (3, 4)):
                self.waves[self.actual_wave].boss.draw_fg(self.screen_buffer)

            for particle in self.particle_list:
                particle.draw(self.screen_buffer)

        elif self.game_state == 3:
            self.screen_buffer.blit(self.s, (0, 0))
            self.screen_buffer.blit(self.pause_txt, (260, 370))
            self.pause_menu.draw(self.screen_buffer)
        elif self.game_state == 0:
            self.screen_buffer.blit(self.title_txt, (208, 350))
            self.screen_buffer.blit(self.title_txt, (208, 270))
            self.main_menu.draw(self.screen_buffer)
            if self.afficher:
                self.screen_buffer.blit(self.press_start_txt, (175, 420))
                timeout = self.txt_start_timer.tick()
                if timeout:
                    self.afficher = False
                    self.txt_start_timer.setDuration(15)
                    self.txt_start_timer.restart()
            else:
                timeout = self.txt_start_timer.tick()
                if timeout:
                    self.txt_start_timer.setDuration(25)
                    self.txt_start_timer.restart()
                    self.afficher = True
            self.screen_buffer.blit(self.copyright_txt, (12, 760))
        if self.game_state == 4 and self.screen_shake_duration < 1:
            if self.offset != [0, 0]:
                self.offset = [0, 0]
            self.screen_buffer.blit(self.s, (0, 0))
            self.screen_buffer.blit(self.game_over_logo, (115, 270))
            self.menu_game_over.draw(self.screen_buffer)

        if self.waves[self.actual_wave].is_playing_dialogue \
            and self.game_state in (2, 5) \
                and self.debug_mode == 0:
            self.dialogue_handler.draw(self.screen_buffer, 20, 500)
        if self.game_state == 1:
            self.achievement_handler.draw_achievent_menu(self.screen_buffer)
        if self.achievement_handler.is_playing_animation():
            self.achievement_handler.draw_popup(self.screen_buffer)
        if self.fragment_hud_showing:
            self.screen_buffer.blit(self.text_compteur_overdrive, (530, 30))
            self.screen_buffer.blit(self.sprite_overdrive_fragment, (600, 20))
            timeout = self.fragment_hud_timer.tick()
            if timeout:
                self.fragment_hud_showing = False

        if self.is_in_splash_screen:
            self.screen.fill("#000000")
            self.screen.blit(
                self.splash_screen_sprites[self.actual_splash_screen],
                (self.splash_screen_sprites_x, self.splash_screen_sprites_y)
            )
            self.splash_screen_sprites[self.actual_splash_screen].set_alpha(self.splash_screen_opacity)
            self.splash_screen_opacity -= 2
            if self.splash_screen_opacity < 1:
                self.actual_splash_screen += 1
                if self.actual_splash_screen == len(self.splash_screen_sprites):
                    pygame.mixer.music.play(-1)  # Fais jouer la musique (argument: -1 -> Repetition infini)
                    self.is_in_splash_screen = False
                else:
                    self.splash_screen_opacity = 255
                    self.splash_screen_sprites_x = SCREEN_WIDTH // 2 - self.splash_screen_sprites[
                        self.actual_splash_screen].get_width() // 2
                    self.splash_screen_sprites_y = SCREEN_HEIGHT // 2 - self.splash_screen_sprites[
                        self.actual_splash_screen].get_height() // 2

        else:
            self.screen_buffer.convert()
            self.screen.blit(self.screen_buffer, self.offset)

        if self.debug_mode != 0 and self.clock.get_time() != 0:
            fps = int(60/(self.clock.get_time()/16))
            self.screen.blit(self.hud_font.render(f'{fps} fps', False, '#aa0000'), (0, 0))

        pygame.display.flip()

    def pause_cd_decrease(self) -> None:
        if self.pause_cd.getTimeLeft() >= 0:
            self.pause_cd.tick()

    def run_loop(self) -> None:
        """Procedure qui appel dans l'ordre la fonction handling_event puis update puis display (boucle de jeu)"""
        pygame.display.set_caption("Piou Piou")
        logging.info(f"Jeu démarré avec le mode de debug {self.debug_mode}")
        while True:
            self.handling_event()
            if self.game_state == 2 and not self.waves[self.actual_wave].is_playing_dialogue \
                    or self.game_state == 5 and not self.waves[self.actual_wave].is_playing_dialogue:
                self.update()
            elif self.screen_shake_duration > 0:

                self.update()
            else:
                self.pause_cd_decrease()
            if self.achievement_handler.is_playing_animation():
                self.achievement_handler.play_animation()
            self.display()
            self.clock.tick(60)


pygame.init()
pygame.mixer.set_num_channels(15)

icone = pygame.image.load('Source/img/icon.png')
icone = pygame.transform.scale(icone, (64, 64))
pygame.display.set_icon(icone)

screen_var = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

game = Shmup(screen_var)
game.run_loop()
