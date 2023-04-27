import pygame

class Menu:
    def __init__(self, font: pygame.font.Font):

        self.__selected = -1

        self.___font = font

        self.__element_list = []

    def add_element(self, title: str, command, pos: tuple[int, int]):
        self.__element_list.append((pos, command, self.___font.render(" " + title, False, '#ffffff'), self.___font.render(">" + title, False, '#ffffff')))
        if self.__selected < 0:
            self.__selected = 0

    def next_element(self):
        if self.__selected + 1 < len(self.__element_list):
            self.__selected += 1

    def previous_element(self):
        if self.__selected - 1 > -1:
            self.__selected -= 1

    def draw(self, screen_buffer):
        for i in range(len(self.__element_list)):
            if i == self.__selected:
                screen_buffer.blit(self.__element_list[i][3], self.__element_list[i][0])
            else:
                screen_buffer.blit(self.__element_list[i][2], self.__element_list[i][0])

    def activate_selected(self):
        self.__element_list[self.__selected][1]()

