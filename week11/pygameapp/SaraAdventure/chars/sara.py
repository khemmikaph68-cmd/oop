import pygame
from pygame.sprite import Sprite

class Hero(Sprite):
    def __init__(self, name, filename, x, y, rows=2, cols=3, width=34, height=56):
        super().__init__()
        self.name = name
        self.sheet = pygame.image.load(filename).convert_alpha()
        self.row = 0
        self.col = 0
        self.elapsed_time = 0
        self.rect = pygame.Rect(x, y, width, height)
        self.so

    def update(self, elapsed_time):
        self.elapsed_time += elapsed_time
        if self.elapsed_time > 300:
            self.col = (self.col + 1) % 3
            if self.col == 0:
                self.row = (self.row + 1) % 2
            self.elapsed_time -= 300

    def draw(self, surface):
        frame = self.sheet.subsurface(
                    self.col * self.rect.width, 
                    self.row * self.rect.height, 
                    self.rect.width, self.rect.height)
        surface.blit(frame, self.rect)