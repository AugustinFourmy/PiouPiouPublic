import pygame
import json
import pathlib


class DialogueHandler:
    def __init__(self, dialog_ressource_path: str, font_path: str, screen_size: tuple):
        file = open(dialog_ressource_path, 'r', encoding="utf-8")
        self.dialogs_file = json.load(file)
        file.close()
        self.screen_size = screen_size
        self.global_suraface = pygame.Surface(screen_size)
        self.dialogs_surface = pygame.Surface((620, 120))
        self.dialogs_surface.set_colorkey((1, 1, 1))
        self.current_dialogs_data = dict()
        self.current_dialogs_speakers = []
        self.rect_surfface = pygame.Surface((620, 120))
        self.rect_surfface.set_colorkey((0, 0, 0))
        self.dialogs_box_rect = pygame.Rect(0, 30, 470, 90)
        self.name_box_rect = pygame.Rect(470, 0, 130, 30)
        self.character_sprites_list_right = []
        self.character_sprites_list_left = []
        self.current_dialogs_part = 0
        self.current_dialogs_box = 0
        self.left = False
        self.visible = True
        self.current_dialogs_texts = [["Error", "Text data not found"]]

        self.font = pygame.font.Font(pathlib.Path(font_path), 13)

        self.speaker_name = "error"
        self.speaker_name_render = self.font.render(self.speaker_name, True, 'white')

        test = "L"  *  35
        self.dialogs_render = self.font.render(test, True, 'white')

        self.lines_render = [self.font.render("Ligne 1", True, 'white'), self.font.render("Ligne 2", True, 'white'), self.font.render("Ligne 3", True, 'white')]

    def change_file(self, new_file):
        file = open(new_file, 'r')
        self.dialogs_file = json.load(file)
        file.close()

    def play_dialog(self, dialogs_id):
        self.current_dialogs_part = 0
        self.current_dialogs_data = self.dialogs_file[dialogs_id]["dialogs"]
        self.current_dialogs_speakers = self.dialogs_file[dialogs_id]["speakers"]
        self.character_sprites_list_left = []
        self.character_sprites_list_right = []
        for speaker in self.current_dialogs_speakers:
            path_left = 'Source/img/dialogue_spr/left/' + speaker['sprite']
            path_right = 'Source/img/dialogue_spr/right/' + speaker['sprite']
            self.character_sprites_list_left.append(pygame.image.load(path_left).convert())
            self.character_sprites_list_right.append(pygame.image.load(path_right).convert())
        self.speaker_name = self.dialogs_file[dialogs_id]["speakers"][self.current_dialogs_data[self.current_dialogs_part]["speaker_id"]]["name"]
        self.speaker_name_render = self.font.render(self.speaker_name, True, 'white')
        self.current_dialogs_texts = self.dialogs_text_sepparator(self.current_dialogs_data[self.current_dialogs_part]["dialog"])
        self.visible = True
        self.render_text_box()

    def dialogs_text_sepparator(self, txt: str) -> list:
        word_list = txt.split()
        current_line = ""
        line_list = []
        box_list = []
        for i in range(len(word_list)):
            if len(current_line) + len(word_list[i]) + 1 <= 35:
                current_line += " " + word_list[i]
            else:
                line_list.append(current_line)
                current_line = " " + word_list[i]
                if len(line_list) == 3:
                    box_list.append(line_list)
                    line_list = []
        if current_line != "":
            line_list.append(current_line)
        if len(line_list) > 0:
            box_list.append(line_list)
        return box_list

    def render_text_box(self):
        for i in range(len(self.current_dialogs_texts[self.current_dialogs_box])):
            self.lines_render[i] = self.font.render(self.current_dialogs_texts[self.current_dialogs_box][i], True, 'white').convert_alpha()
            
    def switch_side(self):
        self.left = not self.left
        self.dialogs_box_rect.x = 0 if not self.left else 130
        self.name_box_rect.x = 0 if self.left else 470

    def next(self):
        if self.current_dialogs_box + 1 < len(self.current_dialogs_texts):
            self.current_dialogs_box += 1
        else:
            self.switch_side()
            self.current_dialogs_part += 1
            self.current_dialogs_box = 0
            if self.current_dialogs_part < len(self.current_dialogs_data):
                self.current_dialogs_texts = self.dialogs_text_sepparator(self.current_dialogs_data[self.current_dialogs_part]["dialog"])
                self.speaker_name = self.current_dialogs_speakers[self.current_dialogs_data[self.current_dialogs_part]["speaker_id"]]["name"]
                self.speaker_name_render = self.font.render(self.speaker_name, True, 'white')
            else:
                self.hide()
                return True
        self.render_text_box()
        return False

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def draw(self, screen, x, y):
        if self.visible:
            self.global_suraface.fill((2, 61, 12))
            self.rect_surfface.fill((0, 0, 0))
            self.dialogs_surface.fill((1, 1, 1))
            
            pygame.draw.rect(self.rect_surfface, "#0000ff", self.dialogs_box_rect)
            pygame.draw.rect(self.rect_surfface, '#1e2169', self.name_box_rect)
            
            self.rect_surfface.set_alpha(90)
            self.rect_surfface.convert_alpha()
            
            a = 470 if not self.left else 0
            
            if not self.left:
                self.dialogs_surface.blit(self.character_sprites_list_left[self.current_dialogs_data[self.current_dialogs_part]["speaker_id"]], (470, 30))
            else:
                self.dialogs_surface.blit(self.character_sprites_list_right[self.current_dialogs_data[self.current_dialogs_part]["speaker_id"]], (0, 30))
                
            self.dialogs_surface.blit(self.rect_surfface, (0, 0))
            
            pygame.draw.rect(self.dialogs_surface, '#4d4d4d', (a, 30, 130, 90), 2)
            
            alignement = a + ((130 - self.speaker_name_render.get_width()) / 2) # Old 470 + 7 * (10 - len(self.speaker_name))
            
            self.dialogs_surface.blit(self.speaker_name_render, (alignement, 9))
            
            for i in range(len(self.current_dialogs_texts[self.current_dialogs_box])):
                self.dialogs_surface.blit(self.lines_render[i], (10 + 120 * int(self.left), 40 + (20 * i)))

            self.global_suraface.blit(self.dialogs_surface, (x, y))
            self.global_suraface.set_colorkey((2, 61, 12))
            screen.blit(self.global_suraface.convert_alpha(), (0, 0))




