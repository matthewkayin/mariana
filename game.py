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
        self.use_joystick = False

        # loop through sys args and set values as needed
        for argument in sys.argv:
            if argument == "--debug":
                self.debug = True
            if argument == "--joystick-enable":
                self.use_joystick = True

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
        Inputs are mapped using two collections
        The first collection, input_map, maps inputs from button name -> input name
        The second collection, states, maps inputs from input name -> input state
        """

        # Define game inputs
        self.input_names = ["Axis Player Horiz", "Axis Player Vert", "Fish Dash"]

        # Refill the input_names array, adding values for axis-as-button
        placeholder = self.input_names
        self.input_names = []
        for name in placeholder:
            self.input_names.append(name)
            if name.startswith("Axis "):
                self.input_names.append(name[5:] + " Pos")
                self.input_names.append(name[5:] + " Neg")

        # Other constants
        self.AXIS_THRESHOLD = 0.001  # This is because sometimes axes report back values that are really small but aren't technically 0

        # Keyboard controls for when joystick controls are turned off
        self.key_map = {}
        self.key_map[pygame.K_d] = "Player Horiz Pos"
        self.key_map[pygame.K_a] = "Player Horiz Neg"
        self.key_map[pygame.K_w] = "Player Vert Neg"
        self.key_map[pygame.K_s] = "Player Vert Pos"
        self.key_map[pygame.K_SPACE] = "Fish Dash"

        # Initialize joysticks
        self.joystick_labels = "ABCDEFGHIJ"
        self.joystick_count = pygame.joystick.get_count()
        self.joysticks = []
        for i in range(0, self.joystick_count):
            self.joysticks.append(pygame.joystick.Joystick(i))
            self.joysticks[i].init()

        # Initialize input map and states
        self.input_map = {}
        self.input_states = {}
        for i in range(0, len(self.input_names)):
            # This if statement is to exclude axis-as-button copies from the state list
            if self.input_names[i].endswith(" Pos") or self.input_names[i].endswith(" Neg"):
                continue
            # If the input is an axis, set its default value to 0, else set to False
            if self.input_names[i].startswith("Axis "):
                self.input_states[self.input_names[i]] = 0
            else:
                self.input_states[self.input_names[i]] = False
        self.input_queue = []

        # Attempt to load inputs from file
        self.load_joyconfig()

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
        self.gamestate = -1

        self.current_joystick = 0

        self.set_joyconfig_scroll()

        # Define UI positioning variables
        # We do this here so we can use the same vars in the input function and so that we can avoid calculating them each frame
        self.joy_button_width = 50
        self.joy_button_x = (self.SCREEN_WIDTH / 2) - ((self.joystick_count * self.joy_button_width) / 2)
        self.joy_button_y = 90
        self.text_y = self.joy_button_y + (self.joy_button_width / 4)

        self.base_y = 200
        self.inc_y = 60
        self.item_width = 200
        self.item_height = 40
        self.offsetx = -100
        self.item_x = (self.SCREEN_WIDTH / 2) - self.item_width + self.offsetx
        self.input_x = self.item_x + self.item_width + 150
        self.input_width = 300

        self.exit_button_x = self.SCREEN_WIDTH - 60
        self.exit_button_y = 10
        self.exit_button_w = 60
        self.exit_button_h = 22

    def set_joyconfig_scroll(self):
        # If there's no controllers, don't run this code
        if self.joystick_count == 0:
            return

        self.current_joyinput = 0

        # Set the max scroll offset based on the last element in the list of inputs
        self.scroll_offset = 0
        self.scroll_max = 0
        self.input_count = 0
        self.input_count += self.joysticks[self.current_joystick].get_numbuttons()
        self.input_count += self.joysticks[self.current_joystick].get_numaxes() * 3  # Times three, one for the axis and two for the axis as pos and neg buttons
        self.input_count += self.joysticks[self.current_joystick].get_numhats() * 2  # Times two because hats have two directional values on them in pygame
        final_y = 200 + (self.input_count * 60)
        if final_y > self.SCREEN_HEIGHT:
            self.scroll_max = final_y - self.SCREEN_HEIGHT

        # Set the max scroll offset based on the number of game inputs
        self.game_scroll_offset = 0
        self.game_scroll_max = 0
        final_y = 200 + (len(self.input_names) * 60)
        if final_y > self.SCREEN_HEIGHT:
            self.game_scroll_max = final_y - self.SCREEN_HEIGHT

    def input(self):
        """
        Handle input from the player, usually redirects to other functions for cleanliness
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
                break
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
                self.start_joyconfig()
                break
            elif self.gamestate == -1:
                self.input_joyconfig(event)
            else:
                self.handle_event(event)

    def handle_event(self, event):
        """
        This function handles key input when the input is for an actual game key / joystick press
        It then takes that input and changes the various state variables
        """
        if not self.use_joystick:
            if event.type == pygame.KEYDOWN:
                if event.key in self.key_map.keys():
                    name = self.key_map[event.key]
                    self.handle_button_press(name)
            elif event.type == pygame.KEYUP:
                if event.key in self.key_map.keys():
                    name = self.key_map[event.key]
                    opposite_down = False
                    if name.endswith(" Pos"):
                        opposite_name = name[:name.index(" Pos")] + " Neg"
                        opposite_key = list(self.key_map.keys())[list(self.key_map.values()).index(opposite_name)]
                        opposite_down = (pygame.key.get_pressed())[opposite_key]
                    elif name.endswith(" Neg"):
                        opposite_name = name[:name.index(" Neg")] + " Pos"
                        opposite_key = list(self.key_map.keys())[list(self.key_map.values()).index(opposite_name)]
                        opposite_down = (pygame.key.get_pressed())[opposite_key]
                    self.handle_button_release(name, opposite_down)
        else:
            if event.type == pygame.JOYBUTTONDOWN:
                input_name = self.joystick_labels[event.joy] + str(event.button)
                if input_name in self.input_map.keys():
                    name = self.input_map[input_name]
                    self.handle_button_press(name)
            elif event.type == pygame.JOYBUTTONUP:
                input_name = self.joystick_labels[event.joy] + str(event.button)
                if input_name in self.input_map.keys():
                    name = self.input_map[input_name]
                    opposite_down = False
                    if name.endswith(" Pos"):
                        opposite_name = name[:name.index(" Pos")] + " Neg"
                        opposite_key = list(self.input_map.keys())[list(self.input_map.values()).index(opposite_name)]
                        opposite_down = (pygame.key.get_pressed())[opposite_key]
                    elif name.endswith(" Neg"):
                        opposite_name = name[:name.index(" Neg")] + " Pos"
                        opposite_key = list(self.input_map.keys())[list(self.input_map.values()).index(opposite_name)]
                        opposite_down = (pygame.key.get_pressed())[opposite_key]
                    self.handle_button_release(name, opposite_down)
            elif event.type == pygame.JOYAXISMOTION:
                input_name = self.joystick_labels[event.joy] + "x" + event.axis
                # TODO use the handle button press with the joystick values to also simulate a press of Ax#+ and Ax#-
                # while also updating the value of the axis input

    def handle_button_press(self, name):
        if name.endswith(" Pos"):
            name_as_axis = "Axis " + name[:name.index(" Pos")]
            if self.input_states[name_as_axis] != 1:
                self.input_queue.append("AxisMoved:" + name_as_axis)
                self.input_states[name_as_axis] = 1
        elif name.endswith(" Neg"):
            name_as_axis = "Axis " + name[:name.index(" Neg")]
            if self.input_states[name_as_axis] != -1:
                self.input_queue.append("AxisMoved:" + name_as_axis)
                self.input_states[name_as_axis] = -1
        else:
            if not self.input_states[name]:
                self.input_queue.append("ButtonDown:" + name)
                self.input_states[name] = True

    def handle_button_release(self, name, opposite_down):
        if name.endswith(" Pos"):
            name_as_axis = "Axis " + name[:name.index(" Pos")]
            if self.input_states[name_as_axis] == 1:
                self.input_queue.append("AxisMoved:" + name_as_axis)
                # If the opposite key is being held, axis state is -1, else it's 0
                if opposite_down:
                    self.input_states[name_as_axis] = -1
                else:
                    self.input_states[name_as_axis] = 0
        elif name.endswith(" Neg"):
            name_as_axis = "Axis " + name[:name.index(" Neg")]
            if self.input_states[name_as_axis] != -1:
                self.input_queue.append("AxisMoved:" + name_as_axis)
                # If the opposite key is being held, axis state is -1, else it's 0
                if opposite_down:
                    self.input_states[name_as_axis] = 1
                else:
                    self.input_states[name_as_axis] = 0
        else:
            if self.input_states[name]:
                self.input_queue.append("ButtonUp:" + name)
                self.input_states[name] = False

    def input_joyconfig(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_WHEELUP:
                # Get mouse coords
                coords = pygame.mouse.get_pos()
                mousex = coords[0]
                mousey = coords[1]

                # If the player is within the bounds of the input scroll field, scroll up
                if mousex >= self.item_x and mousex <= self.item_x + 300 and mousey >= self.base_y:
                    self.scroll_offset -= 15
                    if self.scroll_offset < 0:
                        self.scroll_offset = 0
                elif mousex >= self.input_x and mousex <= self.input_x + 300 and mousey >= self.base_y:
                    self.game_scroll_offset -= 15
                    if self.game_scroll_offset < 0:
                        self.game_scroll_offset = 0
            elif event.button == pygame.BUTTON_WHEELDOWN:
                # Get mouse coords
                coords = pygame.mouse.get_pos()
                mousex = coords[0]
                mousey = coords[1]

                # If the player is within the bounds of the input scroll field, scroll down
                if mousex >= self.item_x and mousex <= self.item_x + 300 and mousey >= self.base_y:
                    self.scroll_offset += 15
                    if self.scroll_offset > self.scroll_max:
                        self.scroll_offset = self.scroll_max
                elif mousex >= self.input_x and mousex <= self.input_x + 300 and mousey >= self.base_y:
                    self.game_scroll_offset += 15
                    if self.game_scroll_offset > self.game_scroll_max:
                        self.game_scroll_offset = self.game_scroll_max
            elif event.button == pygame.BUTTON_LEFT:
                # Get mouse coords
                coords = pygame.mouse.get_pos()
                mousex = coords[0]
                mousey = coords[1]

                click_handled = False

                # Check to see if user clicked on the exit button
                if mousex >= self.exit_button_x and mousex <= self.exit_button_x + self.exit_button_w and mousey >= self.exit_button_y and mousey <= self.exit_button_y + self.exit_button_h:
                    self.save_joyconfig()
                    self.gamestate = 0
                    click_handled = True

                # Check to see if the user clicked on one of the controller tabs
                for i in range(0, self.joystick_count):
                    if click_handled:
                        break
                    button_rect = (self.joy_button_x + (self.joy_button_width * i), self.joy_button_y, self.joy_button_width, self.joy_button_width)
                    if mousex >= button_rect[0] and mousex < button_rect[0] + button_rect[2] and mousey >= button_rect[1] and mousey < button_rect[1] + button_rect[3]:
                        if i != self.current_joystick:
                            self.current_joystick = i
                            self.set_joyconfig_scroll()
                        click_handled = True

                # If we already handled the click, stop processing this event
                if click_handled:
                    return

                # Check to see if user clicked on one of the joystick inputs
                if mousex >= self.item_x and mousex <= self.item_x + 300:
                    for i in range(0, self.input_count):
                        if click_handled:
                            break
                        item_y = self.base_y + (self.inc_y * i) - self.scroll_offset
                        if item_y >= self.SCREEN_HEIGHT or item_y + self.item_height <= self.base_y:
                            continue
                        elif mousey >= item_y and mousey <= item_y + self.item_height:
                            self.current_joyinput = i
                            click_handled = True

                # Check to see if user clicked on one of the game inputs
                if mousex >= self.input_x and mousex <= self.input_x + 300:
                    for i in range(0, len(self.input_names)):
                        if click_handled:
                            break
                        input_y = self.base_y + (self.inc_y * i) - self.game_scroll_offset
                        if input_y >= self.SCREEN_HEIGHT or input_y + self.item_height <= self.base_y:
                            continue
                        elif mousey >= input_y and mousey <= input_y + self.item_height:
                            self.map_input(self.input_names[i])
                            click_handled = True

                # If there was a left click but no button click was handled, reset input selection
                if not click_handled:
                    self.map_input(None)

    def update(self, delta):
        """
        Update game logic
        """
        print(self.input_states)

    def get_curr_input_name(self):
        name = self.joystick_labels[self.current_joystick]
        if self.current_joyinput < self.joysticks[self.current_joystick].get_numbuttons():
            name += str(self.current_joyinput)
        elif self.current_joyinput < self.joysticks[self.current_joystick].get_numbuttons() + (self.joysticks[self.current_joystick].get_numaxes() * 3):
            axis_number = self.current_joyinput - self.joysticks[self.current_joystick].get_numbuttons()
            name += "x" + str(axis_number)
            if axis_number % 3 == 1:
                name += "+"
            elif axis_number % 3 == 2:
                name += "-"
        elif self.current_joyinput < self.input_count:
            name += "t" + str(self.current_joyinput - self.joysticks[self.current_joystick].get_numbuttons() - self.joysticks[self.current_joystick].get_numaxes())
        return name

    def map_input(self, game_input):
        name = self.get_curr_input_name()
        if game_input is None:
            if name in self.input_map:
                del self.input_map[name]
        else:
            # If you try to map a button to an axis, or an axis to a button, don't perform the mapping
            if ("x" in name and not game_input.startswith("Axis ")) or ("x" not in name and game_input.startswith("Axis ")):
                return
            self.input_map[name] = game_input

    def save_joyconfig(self):
        map_file = open("keyconfig.txt", "w")
        for i in range(0, len(self.input_names)):
            name = self.input_names[i]
            if name in self.input_map.values():
                mapping = list(self.input_map.keys())[list(self.input_map.values()).index(name)]
                map_file.write(name + "=" + mapping + "\n")
        map_file.close()

    def load_joyconfig(self):
        if not os.path.isfile("keyconfig.txt"):
            return
        map_file = open("keyconfig.txt", "r")
        for line in map_file.read().splitlines():
            if "=" not in line:
                continue
            index = line.index("=")
            name = line[:index]
            mapping = line[(index + 1):]
            self.input_map[mapping] = name
        map_file.close()
        print(self.input_map)

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
        self.render_text("Exit", (self.exit_button_x, self.exit_button_y), 22)

        # Render the "tab" buttons for each controller
        for i in range(0, self.joystick_count):
            curr_x = self.joy_button_x + (i * self.joy_button_width)
            text_x = curr_x + (self.joy_button_width / 4)
            color_mod = not (self.current_joystick == i)  # If i is the current joystick, render the text black
            # We can also use color mod for the draw rect thickness. If color mod == 0 it means we're currently focusing on this rect, so fill the rect
            # If not than color mod will be == 1, in which case 1 as the thickness will only give us a border for the rect
            pygame.draw.rect(self.screen, self.WHITE, (curr_x, self.joy_button_y, self.joy_button_width, self.joy_button_width), color_mod)
            self.render_text(self.joystick_labels[i], (text_x, self.text_y), 30, (255 * color_mod, 255 * color_mod, 255 * color_mod))

        # Go ahead and skip the rest of the rendering if there are no joysticks
        if self.joystick_count == 0:
            return

        # Render the list of controller inputs
        for i in range(0, self.joysticks[self.current_joystick].get_numbuttons()):
            draw_y = self.base_y + (self.inc_y * i) - self.scroll_offset
            # If the item is out of view after scrolling, don't draw it
            if draw_y >= self.SCREEN_HEIGHT or draw_y + self.item_height <= self.base_y:
                continue
            color_mod = not (self.current_joyinput == i)
            pygame.draw.rect(self.screen, self.WHITE, (self.item_x, draw_y, self.item_width, self.item_height), color_mod)
            self.render_text("BUTTON " + str(i), (self.item_x + 20, draw_y + 5), 22, (255 * color_mod, 255 * color_mod, 255 * color_mod))
            pygame.draw.rect(self.screen, self.WHITE, ((self.SCREEN_WIDTH / 2) + self.offsetx + 20, draw_y, 60, self.item_height), not self.joysticks[self.current_joystick].get_button(i))

        for i in range(0, self.joysticks[self.current_joystick].get_numaxes()):
            for j in range(0, 3):
                draw_y = self.base_y + (self.inc_y * ((i * 3) + j + self.joysticks[self.current_joystick].get_numbuttons())) - self.scroll_offset
                # If the item is out of view after scrolling, don't draw it
                if draw_y >= self.SCREEN_HEIGHT or draw_y + self.item_height <= self.base_y:
                    continue
                text = "AXIS " + str(i)
                if j == 1:
                    text += " POS"
                elif j == 2:
                    text += " NEG"
                color_mod = not (self.current_joyinput == (i * 3) + j + self.joysticks[self.current_joystick].get_numbuttons())
                pygame.draw.rect(self.screen, self.WHITE, (self.item_x, draw_y, self.item_width, self.item_height), color_mod)
                self.render_text(text, (self.item_x + 20, draw_y + 5), 22, (255 * color_mod, 255 * color_mod, 255 * color_mod))
                if j == 0:
                    pygame.draw.rect(self.screen, self.WHITE, ((self.SCREEN_WIDTH / 2) + self.offsetx + 20, draw_y, 60, self.item_height), True)
                    self.render_text("{0:.2f}".format(self.joysticks[self.current_joystick].get_axis(i)), ((self.SCREEN_WIDTH / 2) + self.offsetx + 25, draw_y + 5), 22)
                elif j == 1:
                    pygame.draw.rect(self.screen, self.WHITE, ((self.SCREEN_WIDTH / 2) + self.offsetx + 20, draw_y, 60, self.item_height), not self.joysticks[self.current_joystick].get_axis(i) > self.AXIS_THRESHOLD)
                elif j == 2:
                    pygame.draw.rect(self.screen, self.WHITE, ((self.SCREEN_WIDTH / 2) + self.offsetx + 20, draw_y, 60, self.item_height), not self.joysticks[self.current_joystick].get_axis(i) < -self.AXIS_THRESHOLD)

        hat_keys = "AB"
        for i in range(0, self.joysticks[self.current_joystick].get_numhats()):
            for j in range(0, 2):
                draw_y = self.base_y + (self.inc_y * ((i * 2) + j + self.joysticks[self.current_joystick].get_numbuttons() + self.joysticks[self.current_joystick].get_numaxes())) - self.scroll_offset
                # If the item is out of view after scrolling, don't draw it
                if draw_y >= self.SCREEN_HEIGHT or draw_y + self.item_height <= self.base_y:
                    continue
                color_mod = not (self.current_joyinput == i + j + self.joysticks[self.current_joystick].get_numbuttons() + self.joysticks[self.current_joystick].get_numaxes())
                pygame.draw.rect(self.screen, self.WHITE, (self.item_x, draw_y, self.item_width, self.item_height), color_mod)
                self.render_text("HAT " + str(i) + "-" + hat_keys[j], (self.item_x + 20, draw_y + 5), 22, (255 * color_mod, 255 * color_mod, 255 * color_mod))
                pygame.draw.rect(self.screen, self.WHITE, ((self.SCREEN_WIDTH / 2) + self.offsetx + 20, draw_y, 60, self.item_height), True)
                self.render_text(str(self.joysticks[self.current_joystick].get_hat(i)[j]), ((self.SCREEN_WIDTH / 2) + self.offsetx + 25, draw_y + 5), 22)

        # Now let's render the list of game inputs
        name = self.get_curr_input_name()
        selected_input = None
        if name in self.input_map:
            selected_input = self.input_map[name]
        for i in range(0, len(self.input_names)):
            draw_y = self.base_y + (self.inc_y * i) - self.game_scroll_offset
            # If the item is out of view after scrolling, doin't draw it
            if draw_y >= self.SCREEN_HEIGHT or draw_y + self.item_height <= self.base_y:
                continue
            color_mod = not (selected_input == self.input_names[i])
            pygame.draw.rect(self.screen, self.WHITE, (self.input_x, draw_y, self.input_width, self.item_height), color_mod)
            self.render_text(self.input_names[i], (self.input_x + 20, draw_y + 5), 22, (255 * color_mod, 255 * color_mod, 255 * color_mod))

        # This is a simple hack solution to make my scrolling look a little nicer
        pygame.draw.rect(self.screen, self.BLACK, (self.item_x, self.base_y - 60, 700, 60), False)

        # And we render the header on top of our hack otherwise the hack would go over the header
        self.render_text("Controller Inputs", (self.item_x + 40, self.base_y - 50), 22)
        self.render_text("Game Inputs", (self.input_x + 70, self.base_y - 50), 22)

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
