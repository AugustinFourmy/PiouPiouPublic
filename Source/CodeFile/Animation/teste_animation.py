
import pygame
import sys

class animated_sprite:
    def __init__(self, sprite_sheet_path: str, vertical: bool, width: int = -1, height: int = -1):
        assert (vertical and not height < 0) or (not vertical and not width < 0)

        self.liste_de_sprite = []
        self.delais_max = 1
        self.delais = 1
        
        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        if vertical:
            actual_y = 0
            img_width = sprite_sheet.get_width()
            while abs(actual_y) <= sprite_sheet.get_height():
                surface = pygame.Surface((img_width, height))
                surface.fill((0,0,1))
                surface.set_colorkey((0,0,1))
                surface.blit(sprite_sheet, (0, actual_y))
                surface.set_colorkey((0,0,1))
                self.liste_de_sprite.append(surface.convert_alpha())
                actual_y -= height
        else:
            actual_x = 0
            img_height = sprite_sheet.get_height()
            while abs(actual_x) <= sprite_sheet.get_width():
                surface = pygame.Surface((width, img_height))
                surface.fill((0,0,1))
                surface.set_colorkey((0,0,1))
                surface.blit(sprite_sheet, (actual_x, 0))
                self.liste_de_sprite.append(surface.convert_alpha())
                actual_x -= width
        
        self.avencement = 0
        self.playing = False
        self.reversed = False

    def play(self, speed: float, reversed: bool = False):
        assert speed <= 6, f"Vittesse trop élevé ({speed} > 6)"
        assert speed >= 0.125, f"Vittesse trop basse ({speed} < 0.125)"
        self.playing = True
        self.delais_max = int(60/(speed * 10))
        self.delais = self.delais_max
        self.reversed = reversed
        if reversed:
            self.avencement = len(self.liste_de_sprite) - 1
        else:
            self.avencement = 0

    def draw(self, screen_buffer, pos):
        screen_buffer.blit(self.liste_de_sprite[self.avencement], pos)
        self.delais -= 1
        if self.playing and self.delais < 0:
            self.avencement += (-1)**int(self.reversed)
            self.delais = self.delais_max
            if self.avencement in (len(self.liste_de_sprite) - 1, 0):
                self.playing = False
            self.delais = self.delais_max
        return self.playing
    
    def reset(self):
        self.playing = False
    
    def scale(self, new_scale: tuple[int, int]) -> None:
        for i in range(len(self.liste_de_sprite)):
            self.liste_de_sprite[i] = pygame.transform.scale(self.liste_de_sprite[i], new_scale).convert_alpha()

    def rotate(self, angle: float):
        for i in range(len(self.liste_de_sprite)):
            self.liste_de_sprite[i] = pygame.transform.rotate(self.liste_de_sprite[i], angle).convert_alpha()
    
    def flip(self, h, v):
        for i in range(len(self.liste_de_sprite)):
            self.liste_de_sprite[i] = pygame.transform.flip(self.liste_de_sprite[i], h, v).convert_alpha()
        

    def set_alpha(self, new_alpha):
        for i in range(len(self.liste_de_sprite)):
            self.liste_de_sprite[i].set_alpha(new_alpha)

    def get_size(self):
        return self.liste_de_sprite[0].get_size()

if __name__ == '__main__':
    class Game:
        def __init__(self, screen):
            self.screen = screen
            self.running = True
            self.truc = animated_sprite("../../img/Boss/RoboBoss/Cockpit2-sheet.png", False, width=90)
            self.clock = pygame.time.Clock()

        def update(self):
            if not self.truc.playing:
                self.truc.play()
                
        def display(self):
            self.screen.fill("#ffffff")
            self.truc.draw(self.screen, (64, 64))
            pygame.display.flip()
        
        def handle_input(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.running = False
                    sys.exit()
        
        def run(self):
            while self.running:
                self.handle_input()
                self.update()
                self.display()
                self.clock.tick(60)

    screen = pygame.display.set_mode((500, 500))
    game = Game(screen)
    game.run()        
