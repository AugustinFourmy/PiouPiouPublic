import pygame


class Particle:
    def __init__(self, duration: int, shape: str, color, velocity: tuple, size: list, position: list, deasapear_mode: str):
        """
        duration : durré de vie d'une particule
        shape : forme de la particule
        color : couleur de la particule
        velocity : velocité d'un objet (x, y)
        size : taille (largeur, hauteur)
        position : emplacement initial de la particule (x, y)
        deasapear_mode : mode de disparition
        """
        assert shape in ('rectangle', 'circle'), "Forme inconnue"
        assert deasapear_mode in ('shrink', 'fade_out'), "Mode de disparition inconue"

        self.duration = duration
        self.shape = shape
        self.color = color
        self.position = position
        self.velocity = velocity
        self.size = size
        self.original_size = size
        self.disapear_mode = deasapear_mode
        if self.shape == 'circle':
            self.radius = size[0]/2
        elif self.shape == 'rectangle' and self.disapear_mode == 'fade_out':
            self.rect = pygame.rect.Rect(0, 0, self.size[0], self.size[1])
        elif self.shape == 'rectangle':
            self.rect = pygame.rect.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
        self.max_duration = duration
        if self.disapear_mode == 'fade_out':
            self.opacity = 255

    def update(self):
        """
        Met à jour le paramettre de la particule
        """
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.duration -= 1
        if self.disapear_mode == 'fade_out':
            self.opacity = int((self.duration/self.max_duration) * 255)
        elif self.disapear_mode == 'shrink':
            self.size[0] = self.size[0] - 0.1 * (self.max_duration/(self.duration + 1))
            self.size[1] = self.original_size[1] - 0.1 * (self.max_duration/(self.duration + 1))

            if self.shape == 'rectangle':
                self.rect.x = int(self.position[0])
                self.rect.y = int(self.position[1])
                self.rect.width = int(self.size[0])
                self.rect.height = int(self.size[1])
            elif self.shape == 'circle':
                self.radius = self.size[0]/2

    def draw(self, screen_buffer):
        if self.disapear_mode == 'fade_out':
            particle_surface = pygame.Surface((self.size[0], self.size[1]))
            particle_surface.set_colorkey((0, 0, 0))
            particle_surface.fill((0, 0, 0))
            if self.shape == 'circle':
                pygame.draw.circle(particle_surface, self.color, (0 + self.radius, 0 + self.radius), self.radius)
            elif self.shape == 'rectangle':
                pygame.draw.rect(particle_surface, self.color, self.rect)
            particle_surface.set_alpha(self.opacity)
            particle_surface.convert_alpha()
            screen_buffer.blit(particle_surface, self.position)
        elif self.disapear_mode == 'shrink':
            if self.shape == 'circle':
                pygame.draw.circle(screen_buffer, self.color, (abs(self.position[0] + self.radius), abs(self.position[1] + self.radius)), self.radius)
            elif self.shape == 'rectangle':
                pygame.draw.rect(screen_buffer, self.color, self.rect)

    def get_dead(self) -> bool:
        return self.duration <= 0


