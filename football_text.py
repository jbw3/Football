# Football Text
#
# This module contains all of the Text sprites needed for 'Football.py'

# imports
from livewires import games
import time

# colors for text objects
BLUE = (0, 0, 200, 0)
GRAY = (175, 175, 175, 0)
GREEN = (0, 200, 0, 0)
RED = (210, 0, 0, 0)
WHITE = (255, 255, 255, 0)
YELLOW = (240, 240, 0, 0)

# Base text class
class Click_text(games.Text):
    def __init__(self, game, value, size, color1, color2, x = 0, y = 0,
                 top = None, bottom = None, right = None, left = None,
                 is_collideable = False, color_func1 = None, color_func2 = None):
        """ Initializes object """
        super(Click_text, self).__init__(value = value, size = size, color = color1,
                                         x = x, y = y, top = top, bottom = bottom,
                                         right = right, left = left,
                                         is_collideable = is_collideable)
        self.game = game
        self.color1 = color1
        self.color2 = color2
        self.color_func1 = color_func1
        self.color_func2 = color_func2

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
                self.func()

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
    def __init__(self, game, value, size, color, rate, x = 0, y = 0,
                 top = None, bottom = None, right = None, left = None,
                 is_collideable = False):
        super(Blink_text, self).__init__(value = value, size = size,
                                         color = color, x = x, y = y,
                                         top = top, bottom = bottom,
                                         right = right, left = left,
                                         is_collideable = is_collideable)
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
    def __init__(self, game, value, size, color, x = 0, y = 0,
                 left = None, right = None, top = None, bottom = None):
        """ Initializes object """
        super(Text, self).__init__(value = value, size = size,
                 color = color, x = x, y = y, left = left, right = right,
                top = top, bottom = bottom, is_collideable = False)

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

class Ask_text(games.Text):
    """ Text object that gits the names of the teams the players want to be """
    def __init__(self, game, value, size, color, left, top):
        """ Initializes object """
        super(Ask_text, self).__init__(value = value, size = size,
                 color = color, left = left, top = top,
                is_collideable = False)

        self.game = game

    def update(self):
        """ Gets team names from players """
        if not self.game.team1:
            self.set_value("Player 1, what team do you want?")
            self.set_color(YELLOW)
                
        elif not self.game.team2:
            self.set_value("Player 2, what team do you want?")
            self.set_color(BLUE)

        else:
            for sprite in games.screen.get_all_objects():
                if sprite != self and sprite != self.game.set_text and sprite != self.game.exit_text:
                    sprite.destroy()

            text = Confirm_text(game = self.game, value = "Confirm",
                                size = 30, color1 = WHITE, color2 = GREEN,
                                left = 10, top = 10)
            games.screen.add(text)

            text = Cancel_text(game = self.game, value = "Cancel",
                               size = 30, color1 = WHITE, color2 = RED,
                               left = 100, top = 10)
            games.screen.add(text)

            text = Text(game = self.game, value = "Player 1 - " + self.game.team1,
                         size = 30, color = YELLOW, left = 10, top = 40)
            games.screen.add(text)

            text = Text(game = self.game,
                value = "Player 2 - " + self.game.team2, size = 30,
                         color = BLUE, left = 10, top = 70)
            games.screen.add(text)

            self.destroy()
            

class Confirm_text(Click_text):
    """ A text object that starts the game if the players have picked the
        teams they want"""
    def update(self):
        """ Lets players confirm the teams they picked """
        if games.keyboard.is_pressed(games.K_RETURN) or games.keyboard.is_pressed(games.K_KP_ENTER):
            self.game.start()

        super(Confirm_text, self).update()

    def func(self):
        self.game.start()

class Cancel_text(Click_text):
    """ A text object that lets the players go back and repick their teams """
    def update(self):
        """ Lets players repick their teams """
        if games.keyboard.is_pressed(games.K_BACKSPACE):
            self.func()

        super(Cancel_text, self).update()

    def func(self):
        self.game.team1 = ""
        self.game.team2 = ""
        self.game.pick_teams()        

class Change_text(Click_text):
    def func(self):
        if not self.game.team1:
            self.game.team1 = self.get_value()
        elif not self.game.team2:
            if not self.game.team1 == self.get_value():
                self.game.team2 = self.get_value()

class Play_again_text(Blink_text):
    def __init__(self, game, x = 0, y = 0, top = None, bottom = None,
                 right = None, left = None):
        super(Play_again_text, self).__init__(game = game,
                                              value = "Press Enter to continue",
                                              size = 50, color = RED, rate = 30,
                                              x = x, y = y, top = top,
                                              bottom = bottom, right = right,
                                              left = left)

    def update(self):
        super(Play_again_text, self).update()
        if games.keyboard.is_pressed(games.K_RETURN) or games.keyboard.is_pressed(games.K_KP_ENTER):
            self.game.set_variables()
            self.game.pick_teams()

class Settings_text(Click_text):
    """ Text sprite that allows user to access the game settings """
    def update(self):
        super(Settings_text, self).update()
        if games.keyboard.is_pressed(games.K_F1):
            self.func()

    def func(self):
        self.game.show_settings()

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

class Settings_exit(Click_text):
    def __init__(self, game):
        super(Settings_exit, self).__init__(game = game,
                                            value = "Exit settings",
                                            size = 40, color1 = WHITE,
                                            color2 = RED,
                                            right = games.screen.width - 10,
                                            bottom = games.screen.height - 10)

    def func(self):
        self.game.game_length = self.game.c_settings.get_choice()
        self.game.sound_set = self.game.s_settings.get_choice()
        self.game.pick_teams()

class Game_exit(Click_text):
    def __init__(self, game):
        super(Game_exit, self).__init__(game = game, value = "Exit",
                                        size = 40, color1 = WHITE,
                                        color2 = RED,
                                        left = 20,
                                        bottom = games.screen.height - 20)

    def func(self):
        games.screen.quit()

class Play_text(games.Text):
    def __init__(self, game):
        self.game = game

        if self.game.team1_offence:
            value = "Player 1, pick your play"
            color = YELLOW
        else:
            value = "Player 2, pick your play"
            color = BLUE
        super(Play_text, self).__init__(value = value,
                                        size = 75, color = color,
                                        x = games.screen.width / 2,
                                        y = games.screen.height / 2,
                                        is_collideable = False)

        self.game.non_activated_sprites.append(self)

    def update(self):
        if self.game.sBoard.game_is_over():
            self.game.end_game()

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
            string += "Goal"
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
        super(Game_clock, self).__init__(value = str(self.minutes) + ":" + sec_str,
                                         size = 30, color = RED,
                                         x = games.screen.width / 2,
                                         top = 5, is_collideable = False)

        self.game.non_activated_sprites.append(self)
        self.game.do_not_destroy.append(self)

    def update(self):
        if self.is_running:
            if self.time_second != time.localtime()[5]:
                if self.seconds == 0:
                    if self.minutes == 0:
                        self.is_running = False
                    else:
                        self.minutes -= 1
                        self.seconds = 59
                else:
                    self.seconds -= 1
                self.time_second = time.localtime()[5]
                self.update_value()

        if self.minutes == 0 and self.seconds == 0 and not self.game.play_status == 0:
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
        super(Quarter_text, self).__init__(value = "1st Quarter", size = 30,
                                         color = RED,
                                         x = games.screen.width * 3 / 4,
                                         top = 5, is_collideable = False)

        self.game.non_activated_sprites.append(self)
        self.game.do_not_destroy.append(self)

    def update_value(self):
        if self.game.quarter == 2:
            self.set_value("2nd Quarter")
        elif self.game.quarter == 3:
            self.set_value("3rd Quarter")
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
        super(Football_message, self).__init__(value = value, size = size,
                                               color = color,
                                               x = x, y = y, top = top,
                                               bottom = bottom, left = left,
                                               right = right, lifetime = lifetime,
                                               is_collideable = is_collideable,
                                               after_death = after_death)
        Football_message.previous = self
        self.game = game

        self.game.non_activated_sprites.append(self)

    def destroy(self):
        try:
            self.game.non_activated_sprites.remove(self)
        except(ValueError):
            pass
        super(Football_message, self).destroy()
