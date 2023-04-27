import logging
import pygame
import pathlib
import Source.CodeFile.Utility as Utility
from Source.CodeFile.GameConstant import SCREEN_WIDTH


class Achievement:
    def __init__(self, nom: str, desc: str, code: str, icon_path:str):
        assert len(code) == 3, "Code Invalide"
        self.nom = nom
        self.desc = desc
        self.multiline_nom = Utility.text_sepparator(self.nom, 20, 3)
        self.multiline_desc = Utility.text_sepparator(self.desc, 25, 6)
        self.small_font = pygame.font.Font(pathlib.Path("Source/Font/prstart.ttf"), 9)
        self.title_font = pygame.font.Font(pathlib.Path("Source/Font/prstart.ttf"), 35)
        self.description_font = pygame.font.Font(pathlib.Path("Source/Font/prstart.ttf"), 20)
        self.__code = code
        self.__unlocked = False
        self.small_render_nom = [self.small_font.render(ligne, True, '#ffffff').convert_alpha() for ligne in self.multiline_nom]
        self.big_title_render = [self.title_font.render(ligne, True, '#ffffff').convert_alpha() for ligne in self.multiline_nom]
        self.desc_render = [self.description_font.render(ligne, True, '#ffffff').convert_alpha() for ligne in self.multiline_desc]
        self.unknown_title = self.title_font.render("???", True, '#ffffff').convert_alpha()
        self.unknown_desc = self.description_font.render("???", True, '#ffffff').convert_alpha()
        self.unknown_icon = pygame.transform.scale(pygame.image.load('Source/img/achievement/spr_46_ach_locked.png'), (256, 256)).convert()
        self.icon = pygame.transform.scale(pygame.image.load(icon_path), (64, 64)).convert()
        self.big_icon = pygame.transform.scale(pygame.image.load(icon_path), (256, 256)).convert()
        max_ligne_width = 0
        for ligne in self.desc_render:
            if ligne.get_width() > max_ligne_width:
                max_ligne_width = ligne.get_width()
        self.desc_bg = pygame.Surface((max_ligne_width + 30, self.desc_render[0].get_height() * len(self.desc_render) + 30))
        self.desc_bg.fill('#5435b0')
        self.desc_bg.set_alpha(75)
        self.desc_bg = self.desc_bg.convert_alpha()

    def __str__(self):
        return f"{self.nom} : {self.desc}"

    def unlock(self, code):
        self.__unlocked = code == self.__code
        return self.__unlocked

    def force_unlock(self):
        self.__unlocked = True

    def is_unlock(self):
        return self.__unlocked

    def draw_menu(self, surface_size: tuple[int, int]):
        surface = pygame.Surface(surface_size)
        surface.fill((1, 1, 1))
        if self.__unlocked:
            y_pos = 240 // 2 - ((len(self.big_title_render) * (self.big_title_render[0].get_height()) )// 2)
            for ligne in self.big_title_render:
                x_pos = surface.get_width() // 2 - ligne.get_width() // 2  
                surface.blit(ligne, (x_pos, y_pos))
                y_pos += ligne.get_height()
            surface.blit(self.big_icon, (surface.get_width() // 2 - self.big_icon.get_width() // 2, surface.get_height() // 2 - self.big_icon.get_height() // 2))
            y_pos = 620 + ((len(self.desc_render) * (self.desc_render[0].get_height()) )// 2)
            surface.blit(self.desc_bg, (surface.get_width() // 2 - self.desc_bg.get_width() // 2  ,y_pos - 15))
            for ligne in self.desc_render:
                x_pos = surface.get_width() // 2 - ligne.get_width() // 2  
                surface.blit(ligne, (x_pos, y_pos))
                y_pos += ligne.get_height()
        else:
            surface.blit(
                self.unknown_title,
                (
                    surface.get_width() // 2 - self.unknown_title.get_width() // 2,
                    120 - self.unknown_title.get_height() // 2
                )
                )
            surface.blit(
                self.unknown_desc,
                (
                    surface.get_width() // 2 - self.unknown_desc.get_width() // 2,
                    620 + self.unknown_desc.get_height() // 2
                )
                )
            
            surface.blit(self.unknown_icon, (surface.get_width() // 2 - self.unknown_icon.get_width() // 2, surface.get_height() // 2 - self.unknown_icon.get_height() // 2))
        
        surface.set_colorkey((1, 1, 1))
        return surface


class AchievementHandler:
    def __init__(self, *achievement : Achievement):
        self.__achievement_liste = list(achievement)
        self.__menu_selected = 0
        self.__achievement_popup = pygame.Surface((242, 103))
        self.__quit_font = pygame.font.Font(pathlib.Path("Source/font/prstart.ttf"), 15)
        self.__quit_text_render = self.__quit_font.render("Appuyer sur 'ECHAP' pour quitter", True, "#ffffff").convert_alpha()
        self.__selected_achievement_x = 0
        self.__popup_x = -250
        self.__popup_y = -250
        self.__popup_opacity = 255
        self.__is_playing_animation = False
        self.__achievement_playing = None
        self.__transition_direction = 0

    def unlock(self, code):
        for achievement in self.__achievement_liste:
            if not achievement.is_unlock():
                if achievement.unlock(code):
                    logging.info(f"Succès débloqué : {achievement}")
                    self.__popup_x = SCREEN_WIDTH + 250
                    self.__popup_y = 50
                    self.__popup_opacity = 255  
                    self.__is_playing_animation = True
                    self.__achievement_playing = achievement
                    return True
        return False
    
    def is_playing_animation(self):
        return self.__is_playing_animation

    def get_unlocked_list(self):
        unlock_list = []
        for succes in self.__achievement_liste:
            unlock_list.append(succes.is_unlock())
        return unlock_list

    def unlock_from_list(self, unlocked_list: list[bool]):
        for i in range(len(unlocked_list)):
            if unlocked_list[i]:
                self.__achievement_liste[i].force_unlock()

    def play_animation(self):
        if self.__popup_x > SCREEN_WIDTH - 250:
            self.__popup_x -= 10
        elif self.__popup_opacity > 0:
            self.__popup_opacity -= 1
        else:
            self.__is_playing_animation = False
        if self.__popup_opacity < 0:
            self.__popup_opacity = 0

    def draw_popup(self, screen_buffer: pygame.Surface):
        self.__achievement_popup.fill((0, 0, 0))
        self.__achievement_popup.blit(self.__achievement_playing.icon, (87, 3))
        if len(self.__achievement_playing.small_render_nom) == 1:
            alignement_horizontal = int((242 - self.__achievement_playing.small_render_nom[0].get_width()) / 2)
            alignement_vertical = int(69 + (34 - self.__achievement_playing.small_render_nom[0].get_height()) / 2)
            self.__achievement_popup.blit(self.__achievement_playing.small_render_nom[0], (alignement_horizontal, alignement_vertical))
        else:
            last_delta_y = 69
            for i in range(len(self.__achievement_playing.small_render_nom)):
                alignement_horizontal = int((242 - self.__achievement_playing.small_render_nom[i].get_width()) / 2)
                alignement_vertical =  last_delta_y + self.__achievement_playing.small_render_nom[i].get_height()
                last_delta_y = alignement_vertical
                self.__achievement_popup.blit(self.__achievement_playing.small_render_nom[i], (alignement_horizontal, alignement_vertical))
        self.__achievement_popup.set_alpha(self.__popup_opacity)
        self.__achievement_popup.convert_alpha()
        screen_buffer.blit(self.__achievement_popup, (self.__popup_x, self.__popup_y))
    
    def next_in_menu(self):
        if self.__transition_direction == 0:
            self.__menu_selected += 1
            if self.__menu_selected == len(self.__achievement_liste):
                self.__menu_selected = 0
            self.__transition_direction = -1
    
    def previous_in_menu(self):
        if self.__transition_direction == 0:
            self.__menu_selected -= 1
            if self.__menu_selected < 0:
                self.__menu_selected = len(self.__achievement_liste) - 1
            self.__transition_direction = 1
    
    def get_menu_selected(self):
        return self.__menu_selected
    
    def reset_menu_pos(self):
        self.__menu_selected = 0
        self.__is_playing_animation = False
    
    def draw_achievent_menu(self, screen_buffer):
        screen_buffer.blit(self.__quit_text_render, (15, 15))
        if self.__transition_direction != 0:
            self.__selected_achievement_x += self.__transition_direction * 32
            if self.__menu_selected != len(self.__achievement_liste) - 1:
                screen_buffer.blit(
                    self.__achievement_liste[self.__menu_selected + self.__transition_direction].draw_menu((screen_buffer.get_width(), screen_buffer.get_height())),
                    (self.__selected_achievement_x, 0)
                )
            elif self.__transition_direction > 0:
                screen_buffer.blit(
                    self.__achievement_liste[0].draw_menu((screen_buffer.get_width(), screen_buffer.get_height())),
                    (self.__selected_achievement_x, 0)
                )
            else:
                screen_buffer.blit(
                    self.__achievement_liste[self.__menu_selected + self.__transition_direction].draw_menu((screen_buffer.get_width(), screen_buffer.get_height())),
                    (self.__selected_achievement_x, 0)
                )

            screen_buffer.blit(
                    self.__achievement_liste[self.__menu_selected].draw_menu((screen_buffer.get_width(), screen_buffer.get_height())),
                    (self.__selected_achievement_x - self.__transition_direction * screen_buffer.get_width(), 0)
                )
            if abs(self.__selected_achievement_x) > screen_buffer.get_width():
                self.__transition_direction = 0
                self.__selected_achievement_x = 0
        else:
            screen_buffer.blit(
                self.__achievement_liste[self.__menu_selected].draw_menu((screen_buffer.get_width(), screen_buffer.get_height())),
                (self.__selected_achievement_x, 0)
            )
        pygame.draw.polygon(screen_buffer, '#ffffff', ((0, 405), (30, 420), (30, 390)))
        pygame.draw.polygon(screen_buffer, '#ffffff', ((615, 390), (615, 420), (640, 405)))
