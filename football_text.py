# Football Text
#
# This module contains all of the Text sprites needed for 'Football.py'

# imports
from livewires import games
import time, shelve

# colors for text objects
BLUE = (0, 0, 200)
GRAY = (175, 175, 175)
GREEN = (0, 200, 0)
RED = (210, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (240, 240, 0)

# Base text class
class Click_text(games.Text):
    def __init__(self, game, value, size, color1, color2, x=0, y=0, top=None,
                 bottom=None, right=None, left=None, is_collideable=False,
                 color_func1=None, color_func2=None):
        """ Initializes object """
        super(Click_text, self).__init__(value=value, size=size, color=color1,
                                         x=x, y=y, top=top, bottom=bottom,
                                         right=right, left=left,
                                         is_collideable=is_collideable)
        self.game = game
        self.color1 = color1
        self.color2 = color2
        self.color_func1 = color_func1
        self.color_func2 = color_func2
        self.can_exec = False

        self.game.non_activated_sprites.append(self)
        self.game.do_not_destroy.append(self)

    def update(self):
        """
        Checks to see if mouse is over self. If so, it changes color to
        self.color2. If mouse button 0 is pressed, then func() is executed.
        """
        if self.color_func1:
            self.color1 = self.color_func1()
        if self.color_func2:
            self.color2 = self.color_func2()

        if self.left < games.mouse.x < self.right and self.top < games.mouse.y < self.bottom:
            self.set_color(self.color2)
            if games.mouse.is_pressed(0):
                if self.can_exec:
                    self.can_exec = False
                    self.func()
            else:
                self.can_exec = True

        else:
            self.set_color(self.color1)

    def func(self):
        """ Method invoked if self is clicked on """
        pass

    def destroy(self):
        try:
            self.game.non_activated_sprites.remove(self)
        except(ValueError):
            pass
        try:
            self.game.do_not_destroy.remove(self)
        except(ValueError):
            pass
        super(Click_text, self).destroy()

class Blink_text(games.Text):
    def __init__(self, game, value, size, color, rate, x=0, y=0, top=None,
                 bottom=None, right=None, left=None, is_collideable=False):
        super(Blink_text, self).__init__(value, size, color, x=x, y=y, top=top,
                                         bottom=bottom, right=right, left=left,
                                         is_collideable=is_collideable)
        self.game = game
        self.rate = rate
        self.timer = rate
        self.value1 = value

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.timer = self.rate
            if self.value == self.value1:
                self.set_value("")
            else:
                self.set_value(self.value1)

class Arrow(Click_text):
    def __init__(self, text, value, size, color1, color2, x=0, y=0,
                 top=None, bottom=None, right=None, left=None):
        self.text = text
        super(Arrow, self).__init__(text.game, value, size, color1, color2, x=x,
                                    y=y, top=top, bottom=bottom, right=right,
                                    left=left, is_collideable=False)
        self.can_change = True

    def update(self):
        if not games.mouse.is_pressed(0):
            self.can_change = True

        super(Arrow, self).update()

    def func(self):
        if self.can_change:
            self.text.update_choice(self.value)
            self.can_change = False

class Multi_choice(games.Text):
    def __init__(self, game, value, size, color1, color2, choices, choice, pad,
                 x=0, y=0, top=None, bottom=None, right=None, left=None):
        self.game = game
        self.choices = choices
        self.__choice = choice
        self.pad = pad
        super(Multi_choice, self).__init__(value=value + " ", size=size,
                                           color=color1, x=x, y=y, top=top,
                                           bottom=bottom, right=right, left=left,
                                           is_collideable=False)
        games.screen.add(self)
        self.larrow = Arrow(self, "<", size, color1, color2, y=y, top=top,
                            bottom=bottom, left=self.right)
        games.screen.add(self.larrow)
        self.text = games.Text(value=str(choice),
                               size=size, color=color1,
                               x=self.larrow.right + pad, y=y, top=top,
                               bottom=bottom, is_collideable=False)
        games.screen.add(self.text)
        self.rarrow = Arrow(self, ">", size, color1, color2, y=y, top=top,
                            bottom=bottom, left=self.text.x + pad)
        games.screen.add(self.rarrow)

    def update_choice(self, arrow):
        index = self.choices.index(self.__choice)
        if arrow == "<":
            if index == 0:
                index = len(self.choices) - 1
            else:
                index -= 1

        elif arrow == ">":
            if index == len(self.choices) - 1:
                index = 0
            else:
                index += 1

        self.__choice = self.choices[index]
        self.text.value = str(self.__choice)

    def get_choice(self):
        return self.__choice

# Text classes used in football game
class Text(games.Text):
    """ A text object """
    def __init__(self, game, value, size, color, x=0, y=0,
                 left=None, right=None, top=None, bottom=None):
        """ Initializes object """
        super(Text, self).__init__(value=value, size=size, color=color, x=x,
                                   y=y, left=left, right=right, top=top,
                                   bottom=bottom, is_collideable=False)

        self.game = game

        self.game.non_activated_sprites.append(self)
        self.game.do_not_destroy.append(self)

    def destroy(self):
        try:
            self.game.non_activated_sprites.remove(self)
        except(ValueError):
            pass
        try:
            self.game.do_not_destroy.remove(self)
        except(ValueError):
            pass
        super(Text, self).destroy()

class Name_text(Click_text):
    def func(self):
        if self.game.name1 == "":
            self.game.name1 = self.value
        elif self.game.name2 == "" and self.game.name1 != self.value:
            self.game.name2 = self.value
            self.game.display_teams()

class Ask_text(games.Text):
    def __init__(self, game, size, color):
        """ Initializes object """
        super(Ask_text, self).__init__(value="", size=size,
                 color=color, left=10, top=10, is_collideable=False)

        self.game = game

    def update(self):
        if not self.game.name1:
            self.value = "Player1, enter your name"
            self.left = 10
            self.color = YELLOW
            self.game.back_text.left = self.right + 10

        elif not self.game.name2:
            self.value = "Player2, enter your name"
            self.left = 10
            self.color = BLUE
            self.game.back_text.left = self.right + 10

        elif not self.game.team1:
            self.value = self.game.name1 + ", what team do you want?"
            self.left = 10
            self.color = YELLOW
            self.game.back_text.left = self.right + 10
                
        elif not self.game.team2:
            self.value = self.game.name2 + ", what team do you want?"
            self.left = 10
            self.color = BLUE
            self.game.back_text.left = self.right + 10

        else:
            for sprite in games.screen.get_all_objects():
                if sprite != self and sprite != self.game.set_text and sprite != self.game.exit_text and sprite != self.game.back_text and sprite != self.game.records_text:
                    sprite.destroy()

            text = Confirm_text(game = self.game, value = "Confirm",
                                size = 30, color1 = WHITE, color2 = GREEN,
                                left = 10, top = 10)
            games.screen.add(text)

            self.game.back_text.left = text.right + 10

            text = Text(self.game, self.game.name1 + " - " + self.game.team1,
                        30, YELLOW, left=10, top=40)
            games.screen.add(text)

            text = Text(self.game, self.game.name2 + " - " + self.game.team2,
                        30, BLUE, left=10, top=70)
            games.screen.add(text)

            self.destroy()            

class Confirm_text(Click_text):
    """ A text object that starts the game if the players have picked the
        teams they want"""
    def update(self):
        """ Lets players confirm the teams they picked """
        if games.keyboard.is_pressed(games.K_RETURN) or games.keyboard.is_pressed(games.K_KP_ENTER):
            self.func()

        super(Confirm_text, self).update()

    def func(self):
        self.game.load_images()

class Back_text(Click_text):
    """ A text object that lets the players go back and repick their teams """
    def update(self):
        """ Lets players repick their teams """
        if games.keyboard.is_pressed(games.K_BACKSPACE):
            self.func()

        super(Back_text, self).update()

    def func(self):
        if self.game.team2 != "":
            self.game.team2 = ""
            self.game.get_beginning_info()
        elif self.game.team1 != "":
            self.game.team1 = ""
        elif self.game.name2 != "":
            self.game.name2 = ""
            self.game.display_names()
        elif self.game.name1 != "":
            self.game.name1 = ""

class Change_text(Click_text):
    def func(self):
        if not self.game.team1:
            self.game.team1 = self.get_value()
        elif not self.game.team2:
            if not self.game.team1 == self.get_value():
                self.game.team2 = self.get_value()

class Play_again_text(Blink_text):
    def __init__(self, game, x=0, y=0, top=None, bottom=None, right=None,
                 left=None):
        super(Play_again_text, self).__init__(game=game,
                                              value="Press Enter to continue",
                                              size=50, color=RED, rate=30,
                                              x=x, y=y, top=top,
                                              bottom=bottom, right=right,
                                              left=left)

    def update(self):
        super(Play_again_text, self).update()
        if games.keyboard.is_pressed(games.K_RETURN) or games.keyboard.is_pressed(games.K_KP_ENTER):
            self.game.set_variables()
            self.game.get_beginning_info()

class Settings_text(Click_text):
    """ Text sprite that allows user to access the game settings """
    def func(self):
        self.game.show_settings()

class Add_text(Click_text):
    def func(self):
        self.game.add_name()

class Remove_text(Click_text):
    def func(self):
        self.game.remove_name()

class Clock_settings(Multi_choice):
    def __init__(self, game, choice):
        if choice == 60:
            string = "1 hour"
        elif choice == 30:
            string = "30 min"
        elif choice == 15:
            string = "15 min"
        elif choice == 5:
            string = "5 min"
        super(Clock_settings, self).__init__(game, "Length of game:", 40,
                                              WHITE, GRAY, ["5 min", "15 min",
                                               "30 min", "1 hour"], string, 50,
                                              left=10, top=10)

    def get_choice(self):
        settings = {"1 hour" : 60, "30 min" : 30, "15 min" : 15, "5 min" : 5}
        return settings[super(Clock_settings, self).get_choice()]

class Sound_settings(Multi_choice):
    def __init__(self, game, choice):
        if choice:
            string = "ON"
        else:
            string = "OFF"
        super(Sound_settings, self).__init__(game, "Sound:", 40, WHITE, GRAY,
                                             ["ON", "OFF"], string, 35, left=10,
                                             top=game.c_settings.bottom + 10)

    def get_choice(self):
        settings = {"ON" : True, "OFF" : False}
        return settings[super(Sound_settings, self).get_choice()]

class Type_text(games.Text):
    def __init__(self, size, color, x, y):
        super(Type_text, self).__init__(value="", size=size, color=color, x=x,
                                        y=y)
        self.pressed = []
        self.num_keys = ((games.K_1, games.K_KP1), (games.K_2, games.K_KP2),
                         (games.K_3, games.K_KP3), (games.K_4, games.K_KP4),
                         (games.K_5, games.K_KP5), (games.K_6, games.K_KP6),
                         (games.K_7, games.K_KP7), (games.K_8, games.K_KP8),
                         (games.K_9, games.K_KP9), (games.K_0, games.K_KP0))
        self.numbers = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")
        self.alpha_keys = (games.K_a, games.K_b, games.K_c, games.K_d,
                           games.K_e, games.K_f, games.K_g, games.K_h,
                           games.K_i, games.K_j, games.K_k, games.K_l,
                           games.K_m, games.K_n, games.K_o, games.K_p,
                           games.K_q, games.K_r, games.K_s, games.K_t,
                           games.K_u, games.K_v, games.K_w, games.K_x,
                           games.K_y, games.K_z)
        self.low_alpha = ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
                          "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
                          "w", "x", "y", "z")
        self.upper_alpha = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K",
                            "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
                            "W", "X", "Y", "Z")

        box = games.Sprite(games.load_image("images\\box.bmp"), x=x, y=y)
        games.screen.add(box)

    def update(self):
        if games.keyboard.is_pressed(games.K_BACKSPACE):
            if "B" not in self.pressed:
                self.value = self.value[:-1]
                self.pressed.append("B")
        else:
            if "B" in self.pressed:
                self.pressed.remove("B")

        if len(self.value) < 15:
            if games.keyboard.is_pressed(games.K_SPACE):
                if " " not in self.pressed:
                    self.value += " "
                    self.pressed.append(" ")
            else:
                if " " in self.pressed:
                    self.pressed.remove(" ")

            index = 0
            for key in self.alpha_keys:
                if games.keyboard.is_pressed(key):
                    if self.low_alpha[index] not in self.pressed:
                        if games.keyboard.is_pressed(games.K_LSHIFT) or games.keyboard.is_pressed(games.K_RSHIFT):
                            self.value += self.upper_alpha[index]
                        else:
                            self.value += self.low_alpha[index]
                        self.pressed.append(self.low_alpha[index])
                else:
                    if self.low_alpha[index] in self.pressed:
                        self.pressed.remove(self.low_alpha[index])
                index += 1

            index = 0
            for key in self.num_keys:
                if games.keyboard.is_pressed(key[0]) or games.keyboard.is_pressed(key[1]):
                    if self.numbers[index] not in self.pressed:
                        self.value += self.numbers[index]
                        self.pressed.append(self.numbers[index])
                else:
                    if self.numbers[index] in self.pressed:
                        self.pressed.remove(self.numbers[index])
                index += 1

class Confirm_set(Click_text):
    def func(self):
        self.game.game_length = self.game.c_settings.get_choice()
        self.game.sound_set = self.game.s_settings.get_choice()
        data = shelve.open("football_data.dat", "w")
        data["length"] = self.game.game_length
        data["sound"] = self.game.sound_set
        data.close()
        self.game.get_beginning_info()

class Confirm_add(Click_text):
    def func(self):
        data = shelve.open("football_data.dat", "c")
        if self.game.add_text.value not in data["names"].keys() and self.game.add_text.value.strip() != "":
            dict = data["names"]
            dict[self.game.add_text.value] = (0, 0, 0)
            data["names"] = dict
            data.close()
            self.game.get_beginning_info()
        data.close()

class Confirm_remove(Click_text):
    def func(self):
        data = shelve.open("football_data.dat", "c")
        if self.game.remove_text.value in data["names"].keys():
            dict = data["names"]
            del dict[self.game.remove_text.value]
            data["names"] = dict
            data.close()
            self.game.get_beginning_info()
        data.close()

class Main_back(Click_text):
    def func(self):
        self.game.get_beginning_info()

class Records_text(Click_text):
    def func(self):
        self.game.show_records()

class Game_exit(Click_text):
    def __init__(self, game):
        super(Game_exit, self).__init__(game, "Exit", 40, WHITE, RED, left=20,
                                        bottom=games.screen.height - 20)

    def func(self):
        games.screen.quit()

class Coin_text(Click_text):
    def func(self):
        self.game.flip_coin(self.value)

        for text in self.game.texts[1:]:
            text.destroy()

        if self.game.team1_offence:
            value = self.game.name1 + ", do you want to go first?"
            color = YELLOW
        else:
            value = self.game.name2 + ", do you want to go first?"
            color = BLUE
        text = games.Text(value, 50, color, x=games.screen.width / 2, y=300)
        games.screen.add(text)
        self.game.texts.append(text)
        text = Side_text(self.game, "Yes", 40, WHITE, color,
                         games.screen.width / 2, 400)
        games.screen.add(text)
        self.game.texts.append(text)
        text = Side_text(self.game, "No", 40, WHITE, color,
                         games.screen.width / 2, 500)
        games.screen.add(text)
        self.game.texts.append(text)

class Side_text(Click_text):
    def func(self):
        if self.value == "No":
            self.game.team1_offence = not self.game.team1_offence
        self.game.team1_half = not self.game.team1_offence

        for text in self.game.texts:
            text.destroy()
        del self.game.texts

        games.mouse.is_visible = False
        self.game.pick_play()

class Play_text(games.Text):
    def __init__(self, game):
        self.game = game

        if self.game.team1_offence:
            value = self.game.name1 + ", pick your play"
            color = YELLOW
        else:
            value = self.game.name2 + ", pick your play"
            color = BLUE
        super(Play_text, self).__init__(value=value, size=75, color=color,
                                        x=games.screen.width / 2,
                                        y=games.screen.height / 2,
                                        is_collideable=False)

        self.game.non_activated_sprites.append(self)

    def update(self):
        if games.keyboard.is_pressed(games.K_F1):
            self.game.view_replay()
            return

        if games.keyboard.is_pressed(games.K_q) and self.game.blitz == 0:
            if games.keyboard.is_pressed(games.K_LSHIFT):
                if games.keyboard.is_pressed(games.K_LCTRL):
                    self.game.blitz = 4
                else:
                    self.game.blitz = 2
            elif games.keyboard.is_pressed(games.K_LCTRL):
                self.game.blitz = 3
            else:
                self.game.blitz = 1

        if games.keyboard.is_pressed(games.K_0):
            self.game.play_num = 0
            self.game.new_play()
            self.destroy()
        elif games.keyboard.is_pressed(games.K_1):
            self.game.play_num = 1
            self.game.new_play()
            self.destroy()
        elif games.keyboard.is_pressed(games.K_2):
            self.game.play_num = 2
            self.game.new_play()
            self.destroy()
        elif games.keyboard.is_pressed(games.K_3):
            self.game.play_num = 3
            self.game.new_play()
            self.destroy()
        elif games.keyboard.is_pressed(games.K_4):
            self.game.play_num = 4
            self.game.new_play()
            self.destroy()
        elif games.keyboard.is_pressed(games.K_5):
            self.game.play_num = 5
            self.game.new_play()
            self.destroy()
        elif games.keyboard.is_pressed(games.K_6):
            self.game.play_num = 6
            self.game.new_play()
            self.destroy()

    def destroy(self):
        try:
            self.game.non_activated_sprites.remove(self)
        except(ValueError):
            pass
        super(Play_text, self).destroy()

class Half_text(Blink_text):
    def update(self):
        super(Half_text, self).update()
        if games.keyboard.is_pressed(games.K_RETURN) or games.keyboard.is_pressed(games.K_KP_ENTER):
            self.game.sBoard.reset_clock()
            self.game.sBoard.update_quarter()
            self.game.pick_play()

class Yard_line(games.Text):
    def __init__(self, game):
        self.game = game
        line = int(game.line_of_scrimmage / 36)
        angle = 180
        if line < 1:
            line = 1
        elif line == 100:
            line = 99
        if line > 50:
            line = 50 - (line - 50)
            angle = 0
        elif line == 50:
            angle = None
        super(Yard_line, self).__init__(str(line) + " yard line", 40, RED,
                               x=games.screen.width / 2,
                               y=games.screen.height / 4,
                               is_collideable=False)
        if angle != None:
            self.arrow = games.Text("^", 40, RED, angle,
                                    y=games.screen.height / 4,
                                    right=self.left - 5, is_collideable=False)
            games.screen.add(self.arrow)
        else:
            self.arrow = None

    def update(self):
        if self.game.play_status == 0:
            if self.arrow != None:
                self.arrow.destroy()
            self.destroy()

# scoreboard text objects
class Score(games.Text):
    def __init__(self, game):
        self.game = game
        super(Score, self).__init__(
        value = self.game.team1 + ": 0     " + self.game.team2 + ": 0",
            size = 30, color = RED, left = 10, top = 5, is_collideable = False)

        self.game.non_activated_sprites.append(self)
        self.game.do_not_destroy.append(self)

    def update_score(self):
        self.set_value(self.game.team1 + ": " + str(self.game.team1_score) + "     " + self.game.team2 + ": " + str(self.game.team2_score))
        self.left = 10
        self.top = 5

class Downs_text(games.Text):
    def __init__(self, game):
        self.game = game
        super(Downs_text, self).__init__(value = "1st & 10", size = 30,
                                         color = RED,
                                         right = games.screen.width - 10,
                                         top = 5, is_collideable = False)

        self.game.non_activated_sprites.append(self)
        self.game.do_not_destroy.append(self)

    def update_downs(self):
        if self.game.down == 1:
            string = "1st"
        elif self.game.down == 2:
            string = "2nd"
        elif self.game.down == 3:
            string = "3rd"
        elif self.game.down == 4:
            string = "4th"
        string += " & "
        if self.game.field.bottom - self.game.line_of_scrimmage - 360 - self.game.for_first_down <= self.game.field.top + 360:
            string += "goal"
        else:
            if int(self.game.for_first_down / 36) == 0:
                string += "inches"
            else:
                string += str(int(self.game.for_first_down / 36))
        self.set_value(string)
        self.right = games.screen.width - 10
        self.top = 5

class Game_clock(games.Text):
    def __init__(self, game, length):
        self.game = game
        if length == 60:
            self.start_min = 15
            self.start_sec = 0
        elif length == 30:
            self.start_min = 7
            self.start_sec = 30
        elif length == 15:
            self.start_min = 3
            self.start_sec = 45
        elif length == 5:
            self.start_min = 1
            self.start_sec = 15

        self.is_running = False
        self.minutes = self.start_min
        self.seconds = self.start_sec
        self.time_second = time.localtime()[5]
        self.ended_game = False

        if len(str(self.seconds)) < 2:
            sec_str = "0" + str(self.seconds)
        else:
            sec_str = str(self.seconds)
        super(Game_clock, self).__init__(value=str(self.minutes) + ":" + sec_str,
                                         size=30, color=RED,
                                         x=games.screen.width / 2,
                                         top=5, is_collideable=False)

        self.game.non_activated_sprites.append(self)
        self.game.do_not_destroy.append(self)

    def update(self):
        if self.is_running:
            if self.time_second != time.localtime()[5]:
                if self.seconds == 0:
                    if self.minutes == 0:
                        self.stop()
                    else:
                        self.minutes -= 1
                        self.seconds = 59
                else:
                    self.seconds -= 1
                self.time_second = time.localtime()[5]
                self.update_value()

        if self.minutes == 0 and self.seconds == 0 and not self.game.play_status == 0 and self.game.sBoard.quarter_text.value != "Halftime":
            self.game.change_quarter()

        if self.game_is_over() and not self.ended_game:
            self.ended_game = True
            self.game.end_game()

    def update_value(self):
        if len(str(self.seconds)) < 2:
            sec_str = "0" + str(self.seconds)
        else:
            sec_str = str(self.seconds)

        self.set_value(str(self.minutes) + ":" + sec_str)
        self.x = games.screen.width / 2
        self.top = 5

    def start(self):
        if self.minutes > 0 or self.seconds > 0:
            self.is_running = True

    def stop(self):
        self.is_running = False

    def reset(self):
        self.is_running = False
        self.minutes = self.start_min
        self.seconds = self.start_sec
        if len(str(self.seconds)) < 2:
            sec_str = "0" + str(self.seconds)
        else:
            sec_str = str(self.seconds)
        self.set_value(str(self.minutes) + ":" + sec_str)
        self.x = games.screen.width / 2
        self.top = 10

    def game_is_over(self):
        return (self.minutes == 0 and self.seconds == 0 and ((self.game.quarter == 4 and self.game.team1_score != self.game.team2_score) or self.game.quarter > 4) and not self.game.play_status == 0) or (self.game.quarter == 5 and self.game.team1_score != self.game.team2_score)

class Play_clock(games.Text):
    def __init__(self, game, top):
        self.game = game
        self.set_top = top
        super(Play_clock, self).__init__(value = ":25", size = 30,
                                         color = RED,
                                         x = games.screen.width / 2,
                                         top = top,
                                         is_collideable = False)

        self.game.non_activated_sprites.append(self)

        self.time_second = time.localtime()[5]
        self.seconds = 25

    def update(self):
        if self.game.sBoard.quarter_text.value == "Game Finished":
            self.destroy()

        if self.time_second != time.localtime()[5]:
            self.time_second = time.localtime()[5]
            self.seconds -= 1
            self.update_value()

        if self.seconds == 0:
            self.game.down -= 1
            self.game.penalize(yards=5, string="Delay of game")
            self.destroy()

        if self.game.play_status == 0:
            self.destroy()

    def update_value(self):
        string = ":"
        if self.seconds < 10:
            string += "0"
        string += str(self.seconds)
        self.set_value(string)
        self.x = games.screen.width / 2
        self.top = self.set_top

    def destroy(self):
        try:
            self.game.non_activated_sprites.remove(self)
        except(ValueError):
            pass
        super(Play_clock, self).destroy()

class Quarter_text(games.Text):
    def __init__(self, game):
        self.game = game
        super(Quarter_text, self).__init__("1st Quarter", 30, RED,
                                           x=games.screen.width * 3 / 4,
                                           top=5, is_collideable=False)

        self.game.non_activated_sprites.append(self)
        self.game.do_not_destroy.append(self)

    def update_value(self):
        if self.game.quarter == 2:
            self.set_value("2nd Quarter")
        elif self.game.quarter == 3:
            if self.game.sBoard.game_clock.minutes == 0:
                self.value = "Halftime"
            else:
                self.value = "3rd Quarter"
        elif self.game.quarter == 4:
            self.set_value("4th Quarter")
        elif self.game.quarter == 5:
            self.set_value("OT")
        else:
            self.set_value("Game Finished")

        self.x = games.screen.width * 3 / 4
        self.top = 5

# Message class used in game
class Football_message(games.Message):
    previous = None
    def __init__(self, game, value, size=120, color=RED, x=0, y=0, top=None,
                 bottom=None, left=None, right=None, lifetime=125,
                 is_collideable=False, after_death=None):
        if Football_message.previous != None:
            Football_message.previous.destroy()
        super(Football_message, self).__init__(value, size, color, x=x, y=y,
                                               top=top, bottom=bottom,
                                               left=left, right=right,
                                               lifetime=lifetime,
                                               is_collideable=is_collideable,
                                               after_death=after_death)
        Football_message.previous = self
        self.game = game

        self.game.non_activated_sprites.append(self)

    def destroy(self):
        try:
            self.game.non_activated_sprites.remove(self)
        except(ValueError):
            pass
        super(Football_message, self).destroy()
