import pygame

class Attack:
    def __init__(self, sprite: pygame.Surface = None):
        if sprite is not None:
            self.sprite = sprite
            self.drawing_rect = False
        else:
            self.drawing_rect = True
        self.bullet_list = []

    def new(self, *a) -> None:
        pass

    def update(self, *a) -> None:
        pass

    def draw(self, screen_buffer):
        if self.drawing_rect:
            for bullet in self.bullet_list:
                pygame.draw.rect(screen_buffer, '#b85b04', bullet)
        else:
            for bullet in self.bullet_list:
                screen_buffer.blit(self.sprite, (bullet[0].x, bullet[0].y))

    def get_bullet_list(self):
        return tuple(self.bullet_list)

    def clear(self) -> None:
        self.bullet_list = []

    def remove_bullet_from_index(self, index):
        assert 0 <= index < len(self.bullet_list), f"{index} is out of range {len(self.bullet_list)}"
        self.bullet_list.pop(index)