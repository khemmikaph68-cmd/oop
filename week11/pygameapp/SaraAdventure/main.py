import sys, os
import pygame

class Saraadventure:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((400, 300))
        self.cation = "Sara's Adventure"
        self.hero = Hero
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        pygame.display.set_caption(self.cation)

    def handle_close(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


    def draw_text(self, text, position, color=(0, 0, 0)):
        surface = self.font.render(text, True, color)
        self.screen.blit(surface, position)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if key

    def start(self):
        while True:
            self.handle_close()
            elapsed_time = self.clock.get_time()
            self.screen.fill((255, 255, 255))
            self.hero.update(elapsed_time)


            elapsed_time = pygame.time.get_ticks() - start
            self.draw_text("Sara's Adventure", (100, 100))
            self.hero.update(self.clock.get_time()-start)
            self.hero.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    game = Saraadventure()
    game.start()

    