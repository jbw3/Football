# Football Text
#
# This module contains all of the Text sprites needed for 'game_test3.py'

# imports
from livewires import games

# colors
blue = (0, 0, 200, 0)
gray = (175, 175, 175, 0)
green = (0, 200, 0, 0)
red = (210, 0, 0, 0)
white = (255, 255, 255, 0)
yellow = (240, 240, 0, 0)

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
            self.set_color(yellow)
                
        elif not self.game.team2:
            self.set_value("Player 2, what team do you want?")
            self.set_color(blue)

        else:
            for sprite in games.screen.get_all_objects():
                if sprite != self:
                    sprite.destroy()

            text = Confirm_text(game = self.game, value = "Confirm",
                                size = 30, color1 = white, color2 = green,
                                left = 10, top = 10)
            games.screen.add(text)

            text = Cancel_text(game = self.game, value = "Cancel",
                               size = 30, color1 = white, color2 = red,
                               left = 100, top = 10)
            games.screen.add(text)

            text = Text(game = self.game, value = "Player 1 - " + self.game.team1,
                         size = 30, color = yellow, left = 10, top = 40)
            games.screen.add(text)

            text = Text(game = self.game,
                value = "Player 2 - " + self.game.team2, size = 30,
                         color = blue, left = 10, top = 70)
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

class Settings_text(Click_text):
    """ Text sprite that allows user to access the game settings """
    def func(self):
        self.game.show_settings()

class Clock_settings(Click_text):
    def __init__(self, game):
        self.game = game
        self.can_change = True
        if self.game.clock_rate == 1:
            self.index = 0
        elif self.game.clock_rate == 2:
            self.index = 1
        elif self.game.clock_rate == 4:
            self.index = 2
        elif self.game.clock_rate == 12:
            self.index = 3

        self.options = (("1 hour", 1), ("30 min", 2), ("15 min", 4), ("5 min", 12))

        super(Clock_settings, self).__init__(game = self.game,
                                             value = "Length of game: " + self.options[self.index][0],
                                             size = 40, color1 = white,
                                             color2 = gray, left = 10, top = 10)        

    def update(self):
        if not games.mouse.is_pressed(0):
            self.can_change = True

        super(Clock_settings, self).update()

    def func(self):
        if self.can_change:
            self.index += 1

            if self.index > 3:
                self.index = 0
            elif self.index < 0:
                self.index = 3

            self.game.clock_rate = self.options[self.index][1]
            self.set_value("Length of game: " + self.options[self.index][0])
            self.top = 10
            self.left = 10

            self.can_change = False

class Settings_exit(Click_text):
    def __init__(self, game):
        super(Settings_exit, self).__init__(game = game,
                                            value = "Exit settings",
                                            size = 40, color1 = white,
                                            color2 = red,
                                            right = games.screen.width - 10,
                                            bottom = games.screen.height - 10)

    def func(self):
        self.game.pick_teams()

class Game_exit(Click_text):
    def __init__(self, game):
        super(Game_exit, self).__init__(game = game, value = "Exit",
                                        size = 40, color1 = white,
                                        color2 = red,
                                        left = 20,
                                        bottom = games.screen.height - 20)

    def func(self):
        games.screen.quit()

class Play_text(games.Text):
    def __init__(self, game):
        self.game = game

        if self.game.team1_offence:
            value = "Player 1, pick your play"
            color = yellow
        else:
            value = "Player 2, pick your play"
            color = blue
        super(Play_text, self).__init__(value = value,
                                        size = 75, color = color,
                                        x = games.screen.width / 2,
                                        y = games.screen.height / 2,
                                        is_collideable = False)

        self.game.non_activated_sprites.append(self)

    def update(self):
        if games.keyboard.is_pressed(games.K_0):
            self.game.play_num = 0
            self.game.new_play()
            self.destroy()
        if games.keyboard.is_pressed(games.K_1):
            self.game.play_num = 1
            self.game.new_play()
            self.destroy()
        if games.keyboard.is_pressed(games.K_2):
            self.game.play_num = 2
            self.game.new_play()
            self.destroy()
        if games.keyboard.is_pressed(games.K_3):
            self.game.play_num = 3
            self.game.new_play()
            self.destroy()

# scoreboard text objects
class Score(games.Text):
    def __init__(self, game):
        self.game = game
        super(Score, self).__init__(
        value = self.game.team1 + ": 0     " + self.game.team2 + ": 0",
            size = 30, color = red, left = 10, top = 10, is_collideable = False)

        self.game.non_activated_sprites.append(self)
        self.game.do_not_destroy.append(self)

    def update_score(self):
        self.set_value(self.game.team1 + ": " + str(self.game.team1_score) + "     " + self.game.team2 + ": " + str(self.game.team2_score))
        self.left = 10
        self.top = 10

class Downs_text(games.Text):
    def __init__(self, game):
        self.game = game
        super(Downs_text, self).__init__(value = "Down: 1", size = 30,
                                         color = red,
                                         right = games.screen.width - 10,
                                         top = 10, is_collideable = False)

        self.game.non_activated_sprites.append(self)
        self.game.do_not_destroy.append(self)

    def update_downs(self):
        self.set_value("Down: " + str(self.game.down))
        self.right = games.screen.width - 10
        self.top = 10

class Game_clock(games.Text):
    def __init__(self, game, rate):
        self.game = game
        super(Game_clock, self).__init__(value = "15:00", size = 30,
                                         color = red,
                                         x = games.screen.width / 2,
                                         top = 10, is_collideable = False)

        self.game.non_activated_sprites.append(self)
        self.game.do_not_destroy.append(self)

        self.ONE_SECOND = 45
        self.SPEED = self.ONE_SECOND / rate

        self.is_running = False
        self.timer = self.SPEED
        self.minutes = 15
        self.seconds = 60
        self.loop = True
        self.min_str = ""
        self.sec_str = ""

    def update(self):
        if self.is_running:
            if self.timer > 0:
                self.timer -= 1
            else:
                self.seconds -= 1
                self.timer = self.SPEED
                self.update_value()

            if self.seconds == 0:
                if self.minutes == 0:
                    self.is_running = False
                    self.game.quarter += 1
                    self.game.quarter_text.update_value()
                    if self.game.quarter <= 4:
                        self.reset()
                else:
                    self.seconds = 60
                    self.update_value()

            if self.loop:
                if self.seconds == 59:
                    self.minutes -= 1
                    self.loop = False
                    self.update_value()

            if self.seconds == 58:
                self.loop = True

    def update_value(self):
        self.min_str = str(self.minutes)
        if len(str(self.seconds)) < 2:
            self.sec_str = "0" + str(self.seconds)
        else:
            if self.seconds == 60:
                self.sec_str = "00"
            else:
                self.sec_str = str(self.seconds)

        self.set_value(self.min_str + ":" + self.sec_str)
        self.x = games.screen.width / 2
        self.top = 10

    def start(self):
        if self.minutes > 0 or self.seconds > 0:
            self.is_running = True

    def stop(self):
        self.is_running = False

    def reset(self):
        self.is_running = False
        self.timer = self.SPEED
        self.minutes = 15
        self.seconds = 60
        self.loop = True
        self.min_str = ""
        self.sec_str = ""
        self.set_value("15:00")
        self.x = games.screen.width / 2
        self.top = 10

class Play_clock(games.Text):
    def __init__(self, game):
        self.game = game
        super(Play_clock, self).__init__(value = ":25", size = 30,
                                         color = red,
                                         x = games.screen.width / 2,
                                         top = self.game.game_clock.bottom + 10,
                                         is_collideable = False)

        self.game.non_activated_sprites.append(self)
        self.game.do_not_destroy.append(self)

        self.ONE_SECOND = 45

        self.timer = self.ONE_SECOND
        self.seconds = 25
        self.string = ""

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.seconds -= 1
            self.timer = self.ONE_SECOND
            self.update_value()

        if self.seconds == 0:
            self.game.penalize(yards = 5, string = "Delay of game")
            self.destroy()

        if self.game.play_is_running:
            self.destroy()

    def update_value(self):
        self.string = ":"
        if self.seconds < 10:
            self.string += "0"
        self.string += str(self.seconds)
        self.set_value(self.string)
        self.x = games.screen.width / 2
        self.top = self.game.game_clock.bottom + 10

class Quarter_text(games.Text):
    def __init__(self, game):
        self.game = game
        super(Quarter_text, self).__init__(value = "1st Quarter", size = 30,
                                         color = red,
                                         x = games.screen.width * 3 / 4,
                                         top = 10, is_collideable = False)

        self.string = ""

        self.game.non_activated_sprites.append(self)
        self.game.do_not_destroy.append(self)

    def update_value(self):
        if self.game.quarter == 2:
            self.string = "2nd"
        elif self.game.quarter == 3:
            self.string = "3rd"
        elif self.game.quarter == 4:
            self.string = "4th"
        elif self.game.quarter > 4:
            self.string = "Game Finished"

        if self.string != "Game Finished":
            self.string += " Quarter"

        self.set_value(self.string)

        self.x = games.screen.width * 3 / 4
        self.top = 10

# Message class used in game
class Football_message(games.Message):
    def __init__(self, game, value, size = 120, color = red,
                 x = 0,
                 y = 0, top = None, bottom = None, left = None, right = None,
                 lifetime = 125, is_collideable = False, after_death = None):
        super(Football_message, self).__init__(value = value, size = size,
                                               color = color,
                                               x = x, y = y, top = top,
                                               bottom = bottom, left = left,
                                               right = right, lifetime = lifetime,
                                               is_collideable = is_collideable,
                                               after_death = after_death)
        self.game = game

        self.game.non_activated_sprites.append(self)
        self.game.do_not_destroy.append(self)

################################################################################
################################################################################

if __name__ == "__main__":
    print \
"""
This is a module designed for a football game. It contains all of Text
objects needed for the game.
"""
    raw_input("\n\nPress the enter key to exit.")
    
