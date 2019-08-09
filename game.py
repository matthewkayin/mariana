# Mariana
# Code - Matt Madden and Zubair Khan
# game.py -- Main Class

import sys
import os
import pygame


class Game():
    def __init__(self):
        """
        Default constructor for Game class, handles pygame init and starts
        the main game loop
        """

        self.handle_sysargs()
        self.init_engine()
        self.init_input()
        self.init_fonts()

        self.gamestate = 0
        self.running = True  # When this becomes false, main loop inside run() will quit

        self.run()
        self.quit()

    def handle_sysargs(self):
        """
        Sets Game class variables to their respective values depending on whether
        the user has passed any flags when running the game. Most common is the
        debug flag
        """

        # init all sys args to their default values
        self.debug = False

        # loop through sys args and set values as needed
        for argument in sys.argv:
            if argument == "--debug":
                self.debug = True

    def init_engine(self):
        """
        Initializes pygame
        """

        # Basic game constants
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720
        self.TITLE = "mariana"
        self.TARGET_FPS = 60

        # Color constants (RGB)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)

        # Actually init pygame
        pygame.init()
        pygame_flags = pygame.HWSURFACE  # we need to experiment to see if this or any other flags are any good
        if self.debug:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame_flags)
        else:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame_flags | pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()

        # If in debug mode, show fps and other info in top left corner
        self.show_fps = self.debug
        self.fps = 0

    def init_input(self):
        """
        Initializes input variables and joysticks
        """

        # Input constants, these serve as IDs and as array indices
        self.NO_INPUTS = 2
        self.INPUT_PLAYER_LEFT = 0
        self.INPUT_PLAYER_RIGHT = 1
        self.AXIS = []  # put an input constant into the list to treat it as an axis

        # Other constants
        self.AXIS_THRESHOLD = 0.001  # This is because sometimes axes report back values that are really small but aren't technically 0

        # Initialize joysticks
        self.joystick_labels = "ABCDEFGHIJ"
        self.joystick_count = pygame.joystick.get_count()
        self.joysticks = []
        for i in range(0, self.joystick_count):
            self.joysticks.append(pygame.joystick.Joystick(i))
            self.joysticks[i].init()

        # Initialize input map and states
        self.input_map = []
        self.input_states = [False] * self.NO_INPUTS
        # If the input is an axis, set its default value to 0
        for i in range(0, len(self.AXIS)):
            self.input_states[self.AXIS[i]] = 0

    def init_fonts(self):
        """
        Init fonts and renderable text objects
        Kind of a smol function because we're using an object cache now
        """

        # This cache idea was really clever I had no idea python had these collections
        # I mean keyed arrays as a language feature? That's stupid useful 10/10 well done
        self.font_cache = {}
        self.text_cache = {}

    def start_joyconfig(self):
        self.current_joystick = 0
        self.gamestate = -1
        self.set_joyconfig_scroll()

    def set_joyconfig_scroll(self):
        # Set the max scroll offset based on the last element in the list of inputs
        self.scroll_offset = 0
        self.scroll_max = 0
        input_count = 0
        input_count += self.joysticks[self.current_joystick].get_numbuttons()
        input_count += self.joysticks[self.current_joystick].get_numaxes()
        input_count += self.joysticks[self.current_joystick].get_numhats() * 2  # Times two because hats have two directional values on them in pygame
        final_y = 200 + (input_count * 60)
        if final_y <= self.SCREEN_HEIGHT:
            self.scroll_max = 0  # Disable scrolling, there's not enough buttons to justify it
        else:
            self.scroll_max = final_y - self.SCREEN_HEIGHT

    def input(self):
        """
        Handle input from the player
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F2:
                    self.start_joyconfig()
                    break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.gamestate == -1:
                    if event.button == pygame.BUTTON_WHEELUP:
                        self.scroll_offset -= 15
                        if self.scroll_offset < 0:
                            self.scroll_offset = 0
                    elif event.button == pygame.BUTTON_WHEELDOWN:
                        self.scroll_offset += 15
                        if self.scroll_offset > self.scroll_max:
                            self.scroll_offset = self.scroll_max
                    elif event.button == pygame.BUTTON_LEFT:
                        coords = pygame.mouse.get_pos()
                        mousex = coords[0]
                        mousey = coords[1]
                        for i in range(0, self.joystick_count):
                            button_rect = ((self.SCREEN_WIDTH / 2) - (((self.joystick_count) * 50) / 2) + (50 * i), 90, 50, 50)
                            if mousex >= button_rect[0] and mousex < button_rect[0] + button_rect[2] and mousey >= button_rect[1] and mousey < button_rect[1] + button_rect[3]:
                                if i != self.current_joystick:
                                    self.current_joystick = i
                                    self.set_joyconfig_scroll()
                                break

    def update(self, delta):
        """
        Update game logic
        """
        x = 5

    def render(self):
        """
        Draw to the game screen here
        """
        pygame.draw.rect(self.screen, self.BLACK, (0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT), False)

        if self.gamestate == -1:
            self.render_joyconfig()

        if self.show_fps:
            self.render_text("FPS: " + str(self.fps), (0, 0), 14, self.GREEN)
            self.render_text("Joysticks: " + str(self.joystick_count), (0, 20), 14, self.GREEN)

        pygame.display.flip()

    def render_joyconfig(self):
        """
        Seperate render function for organization.
        Renders the joystick config menu
        """

        # Render the joyconfig header
        self.render_text("Configure Joysticks", ("CENTERED", 22), 22)
        self.render_text(str(self.joystick_count) + " Joysticks Connected", ("CENTERED", 54), 22)

        # Render the "tab" buttons for each controller
        joy_button_width = 50
        joy_button_x = (self.SCREEN_WIDTH / 2) - ((self.joystick_count * joy_button_width) / 2)
        joy_button_y = 90
        half_text_w = 0  # Assumed value for 22 point font, doesn't need to be too perfect so it should be ok
        text_y = joy_button_y + (joy_button_width / 4) - half_text_w
        for i in range(0, self.joystick_count):
            curr_x = joy_button_x + (i * joy_button_width)
            text_x = curr_x + (joy_button_width / 4) - half_text_w
            color_mod = not (self.current_joystick == i)  # If i is the current joystick, render the text black
            # We can also use color mod for the draw rect thickness. If color mod == 0 it means we're currently focusing on this rect, so fill the rect
            # If not than color mod will be == 1, in which case 1 as the thickness will only give us a border for the rect
            pygame.draw.rect(self.screen, self.WHITE, (curr_x, joy_button_y, joy_button_width, joy_button_width), color_mod)
            self.render_text(self.joystick_labels[i], (text_x, text_y), 30, (255 * color_mod, 255 * color_mod, 255 * color_mod))

        # Go ahead and skip the rest of the rendering if there are no joysticks
        if self.joystick_count == 0:
            return

        # Render the list of inputs
        base_y = 200
        inc_y = 60
        item_width = 200
        item_height = 40
        offsetx = -100
        item_x = (self.SCREEN_WIDTH / 2) - item_width + offsetx

        for i in range(self.joysticks[self.current_joystick].get_numbuttons()):
            draw_y = base_y + (inc_y * i) - self.scroll_offset
            # If the item is out of view after scrolling, don't draw it
            if draw_y >= self.SCREEN_HEIGHT or draw_y + item_height <= base_y:
                continue
            self.render_text("BUTTON " + str(i), (item_x + 20, draw_y + 5), 22)
            pygame.draw.rect(self.screen, self.WHITE, (item_x, draw_y, item_width, item_height), True)
            pygame.draw.rect(self.screen, self.WHITE, ((self.SCREEN_WIDTH / 2) + offsetx + 20, draw_y, 60, item_height), not self.joysticks[self.current_joystick].get_button(i))

        for i in range(self.joysticks[self.current_joystick].get_numaxes()):
            draw_y = base_y + (inc_y * (i + self.joysticks[self.current_joystick].get_numbuttons())) - self.scroll_offset
            # If the item is out of view after scrolling, don't draw it
            if draw_y >= self.SCREEN_HEIGHT or draw_y + item_height <= base_y:
                continue
            self.render_text("AXIS " + str(i), (item_x + 20, draw_y + 5), 22)
            pygame.draw.rect(self.screen, self.WHITE, (item_x, draw_y, item_width, item_height), True)
            self.render_text("{0:.2f}".format(self.joysticks[self.current_joystick].get_axis(i)), ((self.SCREEN_WIDTH / 2) + offsetx + 25, draw_y + 5), 22)
            pygame.draw.rect(self.screen, self.WHITE, ((self.SCREEN_WIDTH / 2) + offsetx + 20, draw_y, 60, item_height), True)

        hat_keys = "AB"
        for i in range(self.joysticks[self.current_joystick].get_numhats()):
            for j in range(0, 2):
                draw_y = base_y + (inc_y * (i + j + self.joysticks[self.current_joystick].get_numbuttons() + self.joysticks[self.current_joystick].get_numaxes())) - self.scroll_offset
                # If the item is out of view after scrolling, don't draw it
                if draw_y >= self.SCREEN_HEIGHT or draw_y + item_height <= base_y:
                    continue
                self.render_text("HAT " + str(i) + "-" + hat_keys[j], (item_x + 20, draw_y + 5), 22)
                pygame.draw.rect(self.screen, self.WHITE, (item_x, draw_y, item_width, item_height), True)
                self.render_text(str(self.joysticks[self.current_joystick].get_hat(i)[j]), ((self.SCREEN_WIDTH / 2) + offsetx + 25, draw_y + 5), 22)
                pygame.draw.rect(self.screen, self.WHITE, ((self.SCREEN_WIDTH / 2) + offsetx + 20, draw_y, 60, item_height), True)

        # This is a simple hack solution to make my scrolling look a little nicer
        pygame.draw.rect(self.screen, self.BLACK, (item_x, base_y - 60, 300, 60), False)

        # And we render the header on top of our hack otherwise the hack would go over the header
        self.render_text("Controller Inputs", (item_x + 40, base_y - 50), 22)

    def render_text(self, text, pos, size=14, color=(255, 255, 255)):
        """
        Renders a text to the screen
        This function abuses the dynamic typing of python so that x and y can be position values
        or they can be "CENTERED" (i.e. not an integer), that way I can center an image without
        having to do the math on each render text call
        """

        # If the font / text object for the passed string isn't in the cache, add it to the cache
        if size not in self.font_cache:
            self.font_cache[size] = pygame.font.SysFont("Serif", size)
        # This variable prevents us from using an object of the same message but a different size/color than requested
        text_id = text + "&sz=" + str(size) + "&colo=" + str(color)
        if text_id not in self.text_cache:
            self.text_cache[text_id] = self.font_cache[size].render(text, False, color)

        draw_x = 0
        draw_y = 0

        if pos[0] == "CENTERED":
            draw_x = (self.SCREEN_WIDTH / 2) - (self.text_cache[text_id].get_rect().w / 2)
        else:
            draw_x = pos[0]
        if pos[1] == "CENTERED":
            draw_y = (self.SCREEN_HEIGHT / 2) - (self.text_cache[text_id].get_rect().h / 2)
        else:
            draw_y = pos[1]

        self.screen.blit(self.text_cache[text_id], (draw_x, draw_y))

    def run(self):
        """
        Sets up all the timing variables and calls the main game loop
        """
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
                self.fps = frames
                frames = 0
                before_sec += SECOND
            before_time = pygame.time.get_ticks()

    def quit(self):
        """
        It quits the game
        """
        pygame.quit()


os.environ['SDL_VIDEO_CENTERED'] = '1'  # centers the pygame window
game = Game()
