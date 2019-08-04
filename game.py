# Seeker (working title)
# Code - Matt Madden and Zubair Khan
# game.py -- Main Class

import sys
import os
import pygame


class Game():
    def __init__(self):
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720
        self.TITLE = "seeker"
        self.TARGET_FPS = 60

        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)

        self.debug = False

        for argument in sys.argv:
            if argument == "--debug":
                self.debug = True

        pygame.init()
        pygame_flags = pygame.HWSURFACE  # we need to experiment to see if this or any other flags are any good
        if self.debug:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame_flags)
        else:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame_flags | pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()

        self.smallfont = pygame.font.SysFont("monospace", 14)
        self.fps_text = self.smallfont.render("FPS", False, self.GREEN)

        self.running = True
        self.show_fps = self.debug

        self.run()
        self.quit()

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False

    def update(self, delta):
        string = "I'm only making this so that python will count this as a function while it's empty"

    def render(self):
        pygame.draw.rect(self.screen, self.BLACK, (0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT), False)

        if self.show_fps:
            self.screen.blit(self.fps_text, (0, 0))

        pygame.display.flip()

    def run(self):
        SECOND = 1000
        UPDATE_TIME = SECOND / 60

        before_time = pygame.time.get_ticks()
        before_sec = before_time
        frames = 0
        delta = 0

        while self.running:
            self.clock.tick(self.TARGET_FPS)

            self.input()
            self.update(delta)
            self.render()
            frames += 1

            after_time = pygame.time.get_ticks()
            delta = (after_time - before_time) / UPDATE_TIME
            if after_time - before_sec >= SECOND:
                self.fps_text = self.smallfont.render('FPS: ' + str(frames), False, self.GREEN)
                frames = 0
                before_sec += SECOND
            before_time = pygame.time.get_ticks()

    def quit(self):
        pygame.quit()


os.environ['SDL_VIDEO_CENTERED'] = '1'  # centers the pygame window
game = Game()
