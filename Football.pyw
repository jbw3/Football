# Football
# Version 5
#
# A football game for two players. The player on offence controls the
# quarterback first, and then the player who catches the ball. The defence is
# controlled by the computer.
#
# To do:
# 1. make football players' arms
# 2. add sounds
# 3. make it a safety if defence runs out of its own end zone???

# import games module
from livewires import games

# initialize screen
games.init(screen_width=1020, screen_height=700, fps=50,
           screen_title="Football")

# import other modules
import random, shelve, football_text as ftxt, football_players as fplayers, time
pygame = games.pygame
# football_text is a module specially designed for this game. It has all of the
# text and message objects needed for this game.

# class definitions
class Bar(games.Sprite):
    def __init__(self, game):
        super(Bar, self).__init__(games.load_image("images\\meter.bmp", False),
                                   left=0, bottom=games.screen.height)
        self.__length = 0

        game.do_not_destroy.append(self) # add self to do_not_destroy list
        game.non_activated_sprites.append(self)

    def advance(self):
        if self.__length < self.width - 4:
            self.__length += 12
            if self.__length > self.width - 4:
                self.__length = self.width - 4
            self.update_display()

    def update_display(self):
        image = self.image
        for x in range(2, self.__length + 2):
            for y in range(2, self.height - 2):
                image.set_at((x, y), (0, 255, 0))
        self.image = image

    def reset(self):
        self.__length = 0
        self.image = games.load_image("images\\meter.bmp", False)

    def get_length(self):
        return self.__length
    length = property(get_length)

class Field(games.Sprite):
    """ The football field """
    TIMER = 120
    def __init__(self, game):
        """ Initializes object """
        self.game = game
        super(Field, self).__init__(image=games.load_image("images\\football_field.bmp", False),
                                    x=games.screen.width/2,
                                    y=games.screen.height/2,
                                    is_collideable=False)
        self.save = True
        self.timer = Field.TIMER

        self.game.do_not_destroy.append(self)  # add self to do_not_destroy list

    def update(self):
        if self.game.play_status == 1:
            self.timer -= 1
            if self.timer == 49:
                self.save_frame()
            elif self.timer == 0:
                self.timer = Field.TIMER
                if not self.game.sBoard.game_is_over():
                    self.game.pick_play()

        elif self.game.play_status == -1:
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

        else:
            if self.save:
                self.save_frame()
            self.save = not self.save

            if self.game.ball_carrier in self.game.o_players and self.game.ball_carrier.top < self.top + 360:
                self.game.line_of_scrimmage = 1083
                self.game.for_first_down = 360
                self.game.play_status = 1
                self.game.ball_carrier.speed = 0
                if self.game.team1_offence:
                    self.game.team1_score += 6
                else:
                    self.game.team2_score += 6
                self.game.sBoard.update_score()
                self.game.down = 0
                self.game.sBoard.stop_clock()
                self.game.change_offence()
                message = ftxt.Football_message(game=self.game,
                                                x=games.screen.width / 2,
                                                y=games.screen.height / 2,
                                                value="Touchdown!")
                games.screen.add(message)

            elif self.game.ball_carrier in self.game.o_players and self.game.ball_carrier.bottom > self.bottom:
                self.game.play_status = 1
                self.game.for_first_down = 360
                self.game.line_of_scrimmage = 1083
                if self.game.team1_offence:
                    self.game.team2_score += 2
                else:
                    self.game.team1_score += 2
                self.game.sBoard.update_score()
                self.game.down = 0
                self.game.sBoard.stop_clock()
                message = ftxt.Football_message(game=self.game,
                                                x=games.screen.width / 2,
                                                y=games.screen.height / 2,
                                                value="Safety!")
                games.screen.add(message)

            elif self.game.ball_carrier in self.game.d_players and self.game.ball_carrier.bottom > self.bottom - 360:
                self.game.line_of_scrimmage = 1083
                self.game.for_first_down = 360
                self.game.play_status = 1
                self.game.ball_carrier.speed = 0
                if self.game.team1_offence:
                    self.game.team2_score += 6
                else:
                    self.game.team1_score += 6
                self.game.sBoard.update_score()
                self.game.down = 0
                self.game.sBoard.stop_clock()
                message = ftxt.Football_message(game=self.game,
                                                x=games.screen.width / 2,
                                                y=games.screen.height / 2,
                                                value="Touchdown!")
                games.screen.add(message)

            elif self.game.ball_carrier in self.game.players and (self.game.ball_carrier.x < self.left or self.game.ball_carrier.x > self.right):
                self.game.sBoard.stop_clock()
                self.game.for_first_down -= self.bottom - self.game.line_of_scrimmage - 360 - self.game.ball_carrier.y
                self.game.line_of_scrimmage = self.bottom - self.game.ball_carrier.y - 360
                self.game.play_status = 1
                self.game.ball_carrier.speed = 0
                self.game.ball_carrier.x_change = 0
                self.game.ball_carrier.y_change = 0
                if self.game.ball_carrier in self.game.d_players:
                    self.game.change_offence()

    def save_frame(self):
        self.game.replay_list.append(games.screen.last_display)
        if len(self.game.replay_list) > 400:
            del self.game.replay_list[0]

class Scoreboard(object):
    """ The scoreboard """
    def __init__(self, game):
        """ Put all of the scoreboard items on the screen """
        # put the background on the screen
        self.background = games.Sprite(
            games.load_image("images\\scoreboard_background.bmp", False),
            left=0, top=0, is_collideable=False)
        games.screen.add(self.background)

        game.non_activated_sprites.append(self.background)
        game.do_not_destroy.append(self.background)

        # put the score on the screen
        self.score = ftxt.Score(game)
        games.screen.add(self.score)

        # put the number of downs on the screen
        self.downs_text = ftxt.Downs_text(game)
        games.screen.add(self.downs_text)

        # put the game clock on the screen
        self.game_clock = ftxt.Game_clock(game, game.get_game_length())
        games.screen.add(self.game_clock)

        # put the quarter on the screen
        self.quarter_text = ftxt.Quarter_text(game)
        games.screen.add(self.quarter_text)

    def elevate(self):
        """ Elevate all scoreboard sprites """
        self.background.elevate()
        self.score.elevate()
        self.downs_text.elevate()
        self.game_clock.elevate()
        self.quarter_text.elevate()

    def start_clock(self):
        """ Start game clock """
        self.game_clock.start()

    def stop_clock(self):
        """ Stop game clock """
        self.game_clock.stop()

    def reset_clock(self):
        """ Reset game clock """
        self.game_clock.reset()

    def game_is_over(self):
        """ Returns True or False based on whether or not the game is over """
        return self.game_clock.game_is_over()

    def show_play_clock(self):
        """ Put play clock on screen """
        text = ftxt.Play_clock(self.game, self.game_clock.bottom + 10)
        games.screen.add(text)

    def update_downs(self):
        self.downs_text.update_downs()

    def update_score(self):
        self.score.update_score()

    def update_quarter(self):
        self.quarter_text.update_value()

class Button(games.Sprite):
    def __init__(self, m_image, p_image, func, x=0, y=0, top=None, bottom=None,
                 right=None, left=None):
        self.m_image = m_image
        self.m_image.set_alpha(0)
        self.p_image = p_image
        self.p_image.set_alpha(100)
        super(Button, self).__init__(self.m_image, x=x, y=y, top=top,
                                     bottom=bottom, right=right, left=left,
                                     is_collideable=False)
        self.func = func
        self.bool = False

    def update(self):
        if games.mouse.is_pressed(0) and self.left <= games.mouse.x < self.right and self.top <= games.mouse.y < self.bottom:
            if not self.bool:
                self.image = self.p_image
                self.bool = True
            self.func()
        else:
            if self.bool:
                self.image = self.m_image
                self.bool = False

class Replay_menu(games.Sprite):
    DALPHA = 10
    def __init__(self, game, replay):
        self.game = game
        image = games.load_image("images\\replay_menu.bmp")
        image.set_alpha(0)
        super(Replay_menu, self).__init__(image, x=games.screen.width / 2,
                                          bottom=games.screen.height - 10,
                                          is_collideable=False)
        play = Button(games.load_image("images\\play_bttn.bmp"),
                      games.load_image("images\\play_bttnp.bmp"), replay.play, y=self.y,
                      right=self.x - 7)
        games.screen.add(play)
        pause = Button(games.load_image("images\\pause_bttn.bmp"),
                       games.load_image("images\\pause_bttnp.bmp"), replay.pause,
                       y=self.y, left=self.x + 7)
        games.screen.add(pause)
        fastforward = Button(games.load_image("images\\ff_bttn.bmp"),
                             games.load_image("images\\ff_bttnp.bmp"),
                             replay.fastforward, y=self.y,
                             left=pause.right + 14)
        games.screen.add(fastforward)
        rewind = Button(games.load_image("images\\rewind_bttn.bmp"),
                        games.load_image("images\\rewind_bttnp.bmp"), replay.rewind,
                        y=self.y, right=play.left - 14)
        games.screen.add(rewind)
        first = Button(games.load_image("images\\first_bttn.bmp"),
                       games.load_image("images\\first_bttnp.bmp"),
                       replay.first_image, y=self.y, right=rewind.left - 14)
        games.screen.add(first)
        last = Button(games.load_image("images\\last_bttn.bmp"),
                      games.load_image("images\\last_bttnp.bmp"),
                      replay.last_image, y=self.y, left=fastforward.right + 14)
        games.screen.add(last)
        resume = Button(games.load_image("images\\resume_bttn.bmp"),
                        games.load_image("images\\resume_bttn.bmp"),
                        self.game.resume, y=self.y, right=first.left - 14)
        games.screen.add(resume)
        self.buttons = [play, pause, fastforward, rewind, first, last, resume]

    def update(self):
        if self.left <= games.mouse.x < self.right and self.top <= games.mouse.y < self.bottom:
            for sprite in [self] + self.buttons:
                if sprite.alpha < 100:
                    alpha = sprite.alpha
                    alpha += Replay_menu.DALPHA
                    if alpha > 100:
                        alpha = 100
                    sprite.alpha = alpha
        else:
            for sprite in [self] + self.buttons:
                if sprite.alpha > 0:
                    alpha = sprite.alpha
                    alpha -= Replay_menu.DALPHA
                    if alpha < 0:
                        alpha = 0
                    sprite.alpha = alpha

class Replay(games.Sprite):
    def __init__(self, images):
        self.images = images
        super(Replay, self).__init__(self.images[0], x=games.screen.width / 2,
                                     y=games.screen.height / 2,
                                     is_collideable=False)
        self.index = 0
        self.dindex = 1
        self.playing = False
        self.temp_playing = False

    def update(self):
        if self.playing or self.temp_playing:
            self.index += self.dindex
            if self.index >= len(self.images) - 1:
                self.index = len(self.images) - 1
                self.pause()
            if self.index <= 0:
                self.index = 0
                self.pause()
            self.image = self.images[int(self.index)]
            self.temp_playing = False

    def play(self):
        if self.index < len(self.images) - 1:
            self.playing = True
            self.dindex = .4

    def pause(self):
        self.playing = False

    def fastforward(self):
        if self.index < len(self.images) - 1:
            self.temp_playing = True
            self.playing = False
            self.dindex = 3

    def rewind(self):
        if self.index > 0:
            self.temp_playing = True
            self.playing = False
            self.dindex = -3

    def first_image(self):
        self.index = 0
        self.image = self.images[self.index]

    def last_image(self):
        self.index = len(self.images) - 1
        self.image = self.images[self.index]

class Game(object):
    """ The game """
    def __init__(self):
        data = shelve.open("football_data.dat", "r")
        self.game_length = data["length"]
        self.sound_set = data["sound"]
        data.close()

        self.set_variables()
        self.get_beginning_info()

    def set_variables(self):
        self.name1 = ""
        self.name2 = ""
        self.team1 = ""
        self.team2 = ""
        self.team1_score = 0
        self.team2_score = 0
        self.team1_images = []
        self.team2_images = []
        self.team1_offence = True
        self.team1_half = True
        self.down = 0
        self.quarter = 1
        self.non_activated_sprites = []
        self.ball_carrier = None
        self.players = []
        self.o_players = []
        self.d_players = []
        self.can_not_catch = []
        self.do_not_destroy = []
        self.blitz = 0
        self.play_num = 0
        self.play_status = -1
        self.ball_incomplete = False
        self.line_of_scrimmage = 1083
        self.for_first_down = 360
        self.passed_line = False
        self.replay_list = []

        self.ltackle = None
        self.lltackle = None
        self.ctackle = None
        self.rtackle = None
        self.rrtackle = None
        self.rrrtackle = None
        self.rlb = None
        self.clb = None
        self.llb = None
        self.cbl = None
        self.cbr = None
        self.safety1 = None
        self.safety2 = None
        self.pr = None
        self.lol = None
        self.llol = None
        self.center = None
        self.rol = None
        self.rrol = None
        self.te1 = None
        self.qb = None
        self.rb1 = None
        self.rb2 = None
        self.wr1 = None
        self.wr2 = None
        self.punter = None

    def get_beginning_info(self):
        games.screen.clear()

        games.mouse.is_visible = True

        self.set_text = ftxt.Settings_text(self, "Settings", 30, ftxt.WHITE,
                                           ftxt.GRAY,
                                           right=games.screen.width - 10, top=10)
        games.screen.add(self.set_text)

        self.records_text = ftxt.Records_text(game=self, value="Records",
                                              size=30, color1=ftxt.WHITE,
                                              color2=ftxt.GRAY,
                                              right=games.screen.width - 10,
                                              top=self.set_text.bottom + 10)
        games.screen.add(self.records_text)

        self.exit_text = ftxt.Game_exit(self)
        games.screen.add(self.exit_text)

        self.ask_text = ftxt.Ask_text(game=self, size=30, color=ftxt.YELLOW)
        games.screen.add(self.ask_text)

        self.back_text = ftxt.Back_text(self, "Back", 30, ftxt.WHITE, ftxt.RED,
                                        left=self.ask_text.right + 10, top=10)
        games.screen.add(self.back_text)

        self.add_text = ftxt.Add_text(self, "Add Name", 30, color1=ftxt.WHITE,
                                      color2=ftxt.GREEN,
                                      x=games.screen.width / 2, top=10)
        games.screen.add(self.add_text)

        self.remove_text = ftxt.Remove_text(self, "Remove Name", 30,
                                            color1=ftxt.WHITE, color2=ftxt.RED,
                                            x=658,
                                            top=10)
        games.screen.add(self.remove_text)

        if self.name1 == "" or self.name2 == "":
            self.display_names()
        else:
            self.display_teams()

    def display_names(self):
        for sprite in games.screen.all_objects:
            if sprite != self.ask_text and sprite != self.set_text and sprite != self.exit_text and sprite != self.back_text and sprite != self.records_text and sprite != self.add_text and sprite != self.remove_text:
                sprite.destroy()

        data = shelve.open("football_data.dat", "r")
        names = data["names"].keys()
        data.close()

        names.sort()

        if names == []:
            text = ftxt.Text(self, "(No names available)", 25, ftxt.GRAY,
                             top=self.ask_text.bottom + 10, left=30)
            games.screen.add(text)

        else:
            number = 1
            top = self.ask_text.bottom + 10
            left = 30
            for name in names:
                text = ftxt.Name_text(self, name, 30, ftxt.WHITE,
                                      self.ask_text.get_color(),
                                      color_func2=self.ask_text.get_color, top=top,
                                      left=left)
                games.screen.add(text)
                if number == 15:
                    top = self.ask_text.bottom + 10
                    left += 200
                    number = 1
                else:
                    top = text.bottom + 10
                    number += 1

    def display_teams(self):
        for sprite in games.screen.all_objects:
            if sprite != self.ask_text and sprite != self.set_text and sprite != self.exit_text and sprite != self.back_text and sprite != self.records_text and sprite != self.add_text and sprite != self.remove_text:
                sprite.destroy()

        top = 40
        data = shelve.open("football_data.dat", "r")
        teams = data["teams"].keys()
        data.close()
        for value in teams:
            text = ftxt.Change_text(game=self, value=value,
                                    size=25, color1=ftxt.WHITE,
                                    color2=self.ask_text.get_color(),
                                    color_func2=self.ask_text.get_color,
                                    left=10, top=top)
            games.screen.add(text)

            top = 10 + text.bottom

    def add_name(self):
        games.screen.clear()

        self.add_text = ftxt.Type_text(90, ftxt.RED, games.screen.width / 2,
                                       games.screen.height / 2)
        games.screen.add(self.add_text)

        text = ftxt.Main_back(self, "Cancel", 40, color1=ftxt.WHITE,
                              color2=ftxt.RED, right=games.screen.width - 10,
                              bottom=games.screen.height - 10)
        games.screen.add(text)

        text = ftxt.Confirm_add(self, "Confirm", 40, color1=ftxt.WHITE,
                                color2=ftxt.GREEN, right=text.left - 25,
                                bottom=games.screen.height - 10)
        games.screen.add(text)

    def remove_name(self):
        games.screen.clear()

        self.remove_text = ftxt.Type_text(90, ftxt.RED, games.screen.width / 2,
                                       games.screen.height / 2)
        games.screen.add(self.remove_text)

        text = ftxt.Main_back(self, "Cancel", 40, color1=ftxt.WHITE,
                              color2=ftxt.RED, right=games.screen.width - 10,
                              bottom=games.screen.height - 10)
        games.screen.add(text)

        text = ftxt.Confirm_remove(self, "Confirm", 40, color1=ftxt.WHITE,
                                   color2=ftxt.GREEN, right=text.left - 25,
                                   bottom=games.screen.height - 10)
        games.screen.add(text)

    def draw_numbers(self, image, image1, image2, number, color1, color2, color3):
        # arms
        arms = (" X  XXX XXX XXXXXXX XXX XXX ", "  X  XXX XXXXXXX XXX XXX XXX")
        numbers = {
        "0" : "XXXXXX   XXXXXX",
        "1" : "     XXXXX     ",
        "2" : "XXX XX X XX XXX",
        "3" : "X X XX X XXXXXX",
        "4" : "  XXX  X  XXXXX",
        "5" : "X XXXX X XXXX X",
        "6" : "XXXXXX X XXXX X",
        "7" : "    X    XXXXXX",
        "8" : "XXXXXX X XXXXXX",
        "9" : "X XXXX X XXXXXX"}
        numbers1 = {
        "0" : " XX X  XX  XX  XX  XX  X XX ",
        "1" : "  X  XX   X   X   X   X  XXX",
        "2" : " XX X  X   X  X  X  X   XXXX",
        "3" : " XX X  X   X XX    XX  X XX ",
        "4" : "X  XX  XX  XXXXX   X   X   X",
        "5" : "XXXXX   X    XX    XX  X XX ",
        "6" : " XX X  XX   XXX X  XX  X XX ",
        "7" : "XXXX   X  X  X   X   X   X  ",
        "8" : " XX X  XX  X XX X  XX  X XX ",
        "9" : " XX X  XX  X XXX   XX  X XX "}
        base_x = 4
        for string in arms:
            x = base_x
            y = 0
            for i in string:
                if i != " ":
                    image1.set_at((x, y), color3)
                if x == base_x + 3:
                    x = base_x
                    y += 1
                else:
                    x += 1
            base_x = 22
        arms =     ("XXX     XXX     XXX     XXX     XXX     XXX     XXXX    XXX     XXX      X      ",
                    "   XXX     XXX     XXX     XXX     XXX     XXX    XXXX     XXX     XXX      X   ")
        base_y = 13                
        base_x = 3
        for string in arms:
            x = base_x
            y = base_y
            for i in string:
                if i != " ":
                    image2.set_at((x, y), color3)
                if x == base_x + 7:
                    x = base_x
                    y += 1
                else:
                    x += 1
            base_x = 21
        # face
        face = " XXXXXX XX XX XXXXXXXXXX          XXXX  "
        base_x = 11
        x = base_x
        y = 2
        for i in face:
            if i != " ":
                image2.set_at((x, y), color3)
            if x == base_x + 7:
                x = base_x
                y += 1
            else:
                x += 1
        if number == "":
            image2 = pygame.transform.rotate(image2, 180)
            return image, image1, image2
        # shoulder numbers
        list = []
        for num in number:
            list.append(numbers[num])
        base_x = 3
        for j in range(2):
            if len(number) == 2:
                if j == 0:
                    if number[0] != "1" and number[1] == "1":
                        y = 4
                    else:
                        y = 3
                else:
                    if number[0] == "1" and number[1] != "1":
                        y = 4
                    else:
                        y = 3
            else:
                y = 5
            for num in list:
                x = base_x
                for i in num:
                    if i != " ":
                        image.set_at((x, y), color1)
                    if x == base_x + 4:
                        x = base_x
                        y += 1
                    else:
                        x += 1
                if (len(number) == 2) and (not ((number[0] == "1" and number[1] != "1") or (number[0] != "1" and number[1] == "1"))):
                    y += 1
            if j == 0:
                for num in list:
                    copy = ""
                    for i in num:
                        copy = i + copy
                    list[list.index(num)] = copy
                list.reverse()
                base_x = 22
        # back numbers
        if len(number) == 2:
            if number[0] != "1" and number[1] == "1":
                base_x = 11
            else:
                base_x = 10
        else:
            base_x = 13
        x = base_x
        y = 10
        for num in number:
            for i in numbers1[num]:
                if i != " ":
                    image1.set_at((x, y), color2)
                if x == base_x + 3:
                    x = base_x
                    y += 1
                else:
                    x += 1
            if (len(number) == 2) and number[0] != "1" and number[1] != "1":
                base_x = 16
            else:
                base_x = 15
            x = base_x
            y = 10
        # front numbers
        if len(number) == 2:
            if number[0] != "1" and number[1] == "1":
                base_x = 11
            else:
                base_x = 10
        else:
            base_x = 13
        x = base_x
        y = 10
        for num in number:
            for i in numbers1[num]:
                if i != " ":
                    image2.set_at((x, y), color2)
                if x == base_x + 3:
                    x = base_x
                    y += 1
                else:
                    x += 1
            if (len(number) == 2) and number[0] != "1" and number[1] != "1":
                base_x = 16
            else:
                base_x = 15
            x = base_x
            y = 10

        image2 = pygame.transform.rotate(image2, 180)
        return image, image1, image2

    def load_images(self):
        games.screen.clear()

        data = shelve.open("football_data.dat", "r")
        t1info = data["teams"][self.team1]
        t2info = data["teams"][self.team2]
        data.close()
        t1colors = (t1info[0], t1info[1])
        t2colors = (t2info[2], t2info[3])
        t1info = t1info[4:]
        t2info = t2info[4:]
        image = games.load_image("images/" + self.team1.lower() + "h.bmp")
        image1 = games.load_image("images/" + self.team1.lower() + "ht.bmp")
        image2 = games.load_image("images/" + self.team1.lower() + "ht1.bmp")
        for info in t1info:
            self.team1_images.append(self.draw_numbers(image.convert(), image1.convert(), image2.convert(), info[0], t1colors[0], t1colors[1], info[1]))
        image = games.load_image("images/" + self.team2.lower() + "a.bmp")
        image1 = games.load_image("images/" + self.team2.lower() + "at.bmp")
        image2 = games.load_image("images/" + self.team2.lower() + "at1.bmp")
        for info in t2info:
            self.team2_images.append(self.draw_numbers(image.convert(), image1.convert(), image2.convert(), info[0], t2colors[0], t2colors[1], info[1]))

        self.start()

    def start(self):
        """ Puts the field on the screen """        
        # clear the screen of other sprites
        games.screen.clear()

        self.reset_base_speeds()

        # put the field on the screen
        self.field = Field(self)
        games.screen.add(self.field)

        self.sBoard = Scoreboard(self)

        self.bar = Bar(self)
        games.screen.add(self.bar)

        fplayers.Basic_defense.reset_intercept()

        self.coin_toss()

    def coin_toss(self):
        games.mouse.is_visible = True
        self.texts = []
        text = games.Text("COIN TOSS", 60, ftxt.RED, x=games.screen.width / 2,
                          y=200)
        games.screen.add(text)
        self.texts.append(text)
        text = games.Text(self.name2 + ":", 50, ftxt.BLUE,
                          x=games.screen.width / 2, y=300)
        games.screen.add(text)
        self.texts.append(text)
        text = ftxt.Coin_text(self, "Heads", 40, ftxt.WHITE, ftxt.BLUE,
                              games.screen.width / 2, 400)
        games.screen.add(text)
        self.texts.append(text)
        text = ftxt.Coin_text(self, "Tails", 40, ftxt.WHITE, ftxt.BLUE,
                              games.screen.width / 2, 500)
        games.screen.add(text)
        self.texts.append(text)

    def flip_coin(self, side):
        sides = ("Heads", "Tails")
        self.team1_offence = sides[random.randrange(2)] != side

    def pick_play(self):
        self.remove_players()

        self.players = []
        self.o_players = []
        self.d_players = []
        self.can_not_catch = []
        self.blitz = 0
        self.passed_line = False
        self.play_status = -1

        self.ltackle = None
        self.lltackle = None
        self.ctackle = None
        self.rtackle = None
        self.rrtackle = None
        self.rrrtackle = None
        self.rlb = None
        self.clb = None
        self.llb = None
        self.cbl = None
        self.cbr = None
        self.safety1 = None
        self.safety2 = None
        self.pr = None
        self.lol = None
        self.llol = None
        self.center = None
        self.rol = None
        self.rrol = None
        self.te1 = None
        self.qb = None
        self.rb1 = None
        self.rb2 = None
        self.wr1 = None
        self.wr2 = None
        self.punter = None

        # update the downs
        if self.for_first_down <= 0:
                self.down = 1
                self.for_first_down = 360
        else:
            self.down += 1
            if self.down > 4:
                self.down = 1
                self.change_offence()
                self.line_of_scrimmage = 3600 - self.line_of_scrimmage
                self.for_first_down = 360

        self.sBoard.update_downs()

        # adjust the bar
        self.bar.reset()

        # adjust the field on the screen
        self.field.x = games.screen.width / 2
        self.field.bottom = (games.screen.height * 3 / 4) + self.line_of_scrimmage + 360

        text = ftxt.Play_text(self)
        games.screen.add(text)

        text = ftxt.Yard_line(self)
        games.screen.add(text)

        text = ftxt.Play_clock(self, self.sBoard.game_clock.bottom + 10)
        games.screen.add(text)

    def new_play(self):
        """ Puts all of the football players on the screen for a new play """
        self.replay_list = []
        self.ball_incomplete = False

        # --- put the players on the screen --- #
        if self.play_num == 0:
            self.field.y -= 150
            # center tackle
            self.ctackle = fplayers.STDL(self, games.screen.width / 2,
                                         games.screen.height * 3 / 4 - 170, "c")
            games.screen.add(self.ctackle)
            # left tackle 1
            self.ltackle = fplayers.STDL(self, games.screen.width / 2 + 40,
                                         games.screen.height * 3 / 4 - 170, "l")
            games.screen.add(self.ltackle)
            # left dl 2
            self.lltackle = fplayers.STDL(self, games.screen.width / 2 + 80,
                                          games.screen.height * 3 / 4 - 170, "ll")
            games.screen.add(self.lltackle)
            # right tackle 1
            self.rtackle = fplayers.STDL(self, games.screen.width / 2 - 40,
                                         games.screen.height * 3 / 4 - 170, "r")
            games.screen.add(self.rtackle)
            # right dl 2
            self.rrtackle = fplayers.STDL(self, games.screen.width / 2 - 80,
                                          games.screen.height * 3 / 4 - 170, "rr")
            games.screen.add(self.rrtackle)
            # linbacker
            self.llb = fplayers.STLB(self, games.screen.width / 2 + 60,
                                     games.screen.height * 3 / 4 - 220, "l")
            games.screen.add(self.llb)
            # linbacker
            self.clb = fplayers.STLB(self, games.screen.width / 2,
                                     games.screen.height * 3 / 4 - 220, "c")
            games.screen.add(self.clb)
            # linbacker
            self.rlb = fplayers.STLB(self, games.screen.width / 2 - 60,
                                     games.screen.height * 3 / 4 - 220, "r")
            games.screen.add(self.rlb)
            # punt returner
            self.pr = fplayers.PR(self, games.screen.width / 2,
                                  self.field.top + 400)
            games.screen.add(self.pr)

            # center
            self.center = fplayers.STCenter(self, games.screen.width / 2,
                                            games.screen.height * 3 / 4 - 150)
            games.screen.add(self.center)
            # left guard 1
            self.lol = fplayers.STOL(self, games.screen.width / 2 - 40,
                                     games.screen.height * 3 / 4 - 150, "l")
            games.screen.add(self.lol)
            # left guard 2
            self.llol = fplayers.STOL(self, games.screen.width / 2 - 80,
                                      games.screen.height * 3 / 4 - 150, "ll")
            games.screen.add(self.llol)
            # right guard 1
            self.rol = fplayers.STOL(self, games.screen.width / 2 + 40,
                                     games.screen.height * 3 / 4 - 150, "r")
            games.screen.add(self.rol)
            # right guard 2
            self.rrol = fplayers.STOL(self, games.screen.width / 2 + 80,
                                      games.screen.height * 3 / 4 - 150, "rr")
            games.screen.add(self.rrol)
            # punter
            self.punter = fplayers.Punter(self, games.screen.width / 2,
                                          games.screen.height * 3 / 4 + 50)
            games.screen.add(self.punter)
        elif self.play_num == 1:
            # linebacker
            self.clb = fplayers.LB(game=self, x=games.screen.width / 2,
                                   y=games.screen.height * 3 / 4 - 70, side="c")
            games.screen.add(self.clb)
            # linebacker
            self.llb = fplayers.LB(game=self, x=games.screen.width / 2 + 60,
                                   y=games.screen.height * 3 / 4 - 70, side="l")
            games.screen.add(self.llb)
            # linebacker
            self.rlb = fplayers.LB(game=self, x=games.screen.width / 2 - 60,
                                   y=games.screen.height * 3 / 4 - 70, side="r")
            games.screen.add(self.rlb)
            # left tackle 1
            self.ltackle = fplayers.DL(game=self, x=games.screen.width / 2 + 40,
                                  y =games.screen.height * 3 / 4 - 20, side="l")
            games.screen.add(self.ltackle)
            # left tackle 2
            self.lltackle = fplayers.DL(game=self, x=games.screen.width / 2 + 80,
                                  y=games.screen.height * 3 / 4 - 20, side="ll")
            games.screen.add(self.lltackle)
            # right tackle 1
            self.rtackle = fplayers.DL(game=self, x=games.screen.width / 2 - 40,
                                  y=games.screen.height * 3 / 4 - 20, side="r")
            games.screen.add(self.rtackle)
            # right tackle 2
            self.rrtackle = fplayers.DL(game=self, x=games.screen.width / 2 - 80,
                                  y=games.screen.height * 3 / 4 - 20, side="rr")
            games.screen.add(self.rrtackle)
            # right tackle 3
            self.rrrtackle = fplayers.DL(game=self, x=games.screen.width / 2 - 120,
                                y=games.screen.height * 3 / 4 - 20, side="rrr")
            games.screen.add(self.rrrtackle)
            # left cornerback
            self.cbl = fplayers.CB(game = self, x = games.screen.width * 3 / 4,
                          y = games.screen.height * 3 / 4 - 70, side="l")
            games.screen.add(self.cbl)
            # safety 1
            self.safety1 = fplayers.Safety(game=self, x=games.screen.width / 2 - 200,
                                  y=games.screen.height * 3 / 4 - 275, num="1")
            games.screen.add(self.safety1)
            # safety 2
            self.safety2 = fplayers.Safety(game=self, x=games.screen.width / 2 + 200,
                                  y=games.screen.height * 3 / 4 - 275, num="2")
            games.screen.add(self.safety2)

            # center
            self.center = fplayers.Center(game = self, x = games.screen.width / 2,
                                 y = games.screen.height * 3 / 4)
            games.screen.add(self.center)
            # right guard 1
            self.rol = fplayers.OL(game = self, x = games.screen.width / 2 + 40,
                                y = games.screen.height * 3 / 4, side = "r")
            games.screen.add(self.rol)
            # right guard 2
            self.rrol = fplayers.OL(game = self, x = games.screen.width / 2 + 80,
                                 y = games.screen.height * 3 / 4, side = "rr")
            games.screen.add(self.rrol)
            # left guard 1
            self.lol = fplayers.OL(game = self, x = games.screen.width / 2 - 40,
                                y = games.screen.height * 3 / 4, side = "l")
            games.screen.add(self.lol)
            # left guard 2
            self.llol = fplayers.OL(game=self, x=games.screen.width / 2 - 80,
                                 y=games.screen.height * 3 / 4, side="ll")
            games.screen.add(self.llol)
            # tight end
            self.te1 = fplayers.TE(game=self, x=games.screen.width / 2 - 120,
                                   y=games.screen.height * 3 / 4, num="1")
            games.screen.add(self.te1)
            # quarterback
            self.qb = fplayers.QB(game=self, x=games.screen.width / 2,
                    y=games.screen.height * 3 / 4 + 50)
            games.screen.add(self.qb)
            # runningback
            self.rb1 = fplayers.RB(game=self, x=games.screen.width / 2,
                                   y=games.screen.height - 6, num="1")
            games.screen.add(self.rb1)
            # runningback 1
            self.rb2 = fplayers.RB(game = self, x = games.screen.width / 2,
                         y = games.screen.height + 40, num="2")
            games.screen.add(self.rb2)
            # right wide recicver
            self.wr2 = fplayers.WR(game = self, x = games.screen.width * 3 / 4,
                          y = games.screen.height * 3 / 4, side="r")
            games.screen.add(self.wr2)
        elif self.play_num == 3 or self.play_num == 6:
            # linebacker
            self.rlb = fplayers.LB(self, games.screen.width / 2 - 60,
                                   games.screen.height * 3 / 4 - 70, "r")
            games.screen.add(self.rlb)
            # linebacker
            self.clb = fplayers.LB(self, games.screen.width / 2,
                                   games.screen.height * 3 / 4 - 70, "c")
            games.screen.add(self.clb)
            # linebacker
            self.llb = fplayers.LB(self, games.screen.width / 2 + 60,
                                   games.screen.height * 3 / 4 - 70, "l")
            games.screen.add(self.llb)
            # left tackle 1
            self.ltackle = fplayers.DL(self, games.screen.width / 2 + 40,
                                       games.screen.height * 3 / 4 - 20, "l")
            games.screen.add(self.ltackle)
            # left tackle 2
            self.lltackle = fplayers.DL(self, games.screen.width / 2 + 80,
                                        games.screen.height * 3 / 4 - 20, "ll")
            games.screen.add(self.lltackle)
            # right tackle 1
            self.rtackle = fplayers.DL(self, games.screen.width / 2 - 40,
                                       games.screen.height * 3 / 4 - 20, "r")
            games.screen.add(self.rtackle)
            # right tackle 2
            self.rrtackle = fplayers.DL(self, games.screen.width / 2 - 80,
                                        games.screen.height * 3 / 4 - 20, "rr")
            games.screen.add(self.rrtackle)
            # left cornerback
            self.cbl = fplayers.CB(self, games.screen.width * 3 / 4,
                                   games.screen.height * 3 / 4 - 70, "l")
            games.screen.add(self.cbl)
            # right cornerback
            self.cbr = fplayers.CB(game = self, x = games.screen.width / 4,
                          y = games.screen.height * 3 / 4 - 70, side="r")
            games.screen.add(self.cbr)
            # safety 1
            self.safety1 = fplayers.Safety(game=self, x=games.screen.width / 2 - 200,
                                  y=games.screen.height * 3 / 4 - 275, num="1")
            games.screen.add(self.safety1)
            # safety 2
            self.safety2 = fplayers.Safety(game=self, x=games.screen.width / 2 + 200,
                                  y=games.screen.height * 3 / 4 - 275, num="2")
            games.screen.add(self.safety2)

            # center
            self.center = fplayers.Center(self, games.screen.width / 2,
                                          games.screen.height * 3 / 4)
            games.screen.add(self.center)
            # right guard 1
            self.rol = fplayers.OL(game=self, x=games.screen.width / 2 + 40,
                                   y=games.screen.height * 3 / 4, side="r")
            games.screen.add(self.rol)
            # right guard 2
            self.rrol = fplayers.OL(game=self, x=games.screen.width / 2 + 80,
                                    y=games.screen.height * 3 / 4, side="rr")
            games.screen.add(self.rrol)
            # left guard 1
            self.lol = fplayers.OL(game=self, x=games.screen.width / 2 - 40,
                                   y=games.screen.height * 3 / 4, side="l")
            games.screen.add(self.lol)
            # left guard 2
            self.llol = fplayers.OL(game=self, x=games.screen.width / 2 - 80,
                                    y=games.screen.height * 3 / 4, side="ll")
            games.screen.add(self.llol)
            # tight end
            self.te1 = fplayers.TE(game=self, x=games.screen.width / 2 + 120,
                                   y=games.screen.height * 3 / 4, num="1")
            games.screen.add(self.te1)
            # quarterback
            self.qb = fplayers.QB(game=self, x=games.screen.width / 2,
                                  y=games.screen.height * 3 / 4 + 50)
            games.screen.add(self.qb)
            # runningback
            self.rb1 = fplayers.RB(game=self, x=games.screen.width / 2,
                                   y=games.screen.height - 6, num="1")
            games.screen.add(self.rb1)
            # left wide recicver
            self.wr1 = fplayers.WR(game=self, x=games.screen.width / 4,
                                   y=games.screen.height * 3 / 4, side="l")
            games.screen.add(self.wr1)
            # right wide recicver
            self.wr2 = fplayers.WR(game=self, x=games.screen.width * 3 / 4,
                                   y=games.screen.height * 3 / 4, side="r")
            games.screen.add(self.wr2)
        else:
            # linebacker
            self.rlb = fplayers.LB(game=self, x=games.screen.width / 2 - 60,
                                   y=games.screen.height * 3 / 4 - 70, side="r")
            games.screen.add(self.rlb)
            # linebacker
            self.clb = fplayers.LB(game=self, x=games.screen.width / 2,
                                   y=games.screen.height * 3 / 4 - 70, side="c")
            games.screen.add(self.clb)
            # linebacker
            self.llb = fplayers.LB(game=self, x=games.screen.width / 2 + 60,
                                   y=games.screen.height * 3 / 4 - 70, side="l")
            games.screen.add(self.llb)
            # left tackle 1
            self.ltackle = fplayers.DL(game = self, x = games.screen.width / 2 + 40,
                                  y = games.screen.height * 3 / 4 - 20, side = "l")
            games.screen.add(self.ltackle)
            # left tackle 2
            self.lltackle = fplayers.DL(game = self, x = games.screen.width / 2 + 80,
                                  y = games.screen.height * 3 / 4 - 20, side = "ll")
            games.screen.add(self.lltackle)
            # right tackle 1
            self.rtackle = fplayers.DL(game = self, x = games.screen.width / 2 - 40,
                                  y = games.screen.height * 3 / 4 - 20, side = "r")
            games.screen.add(self.rtackle)
            # right tackle 2
            self.rrtackle = fplayers.DL(game = self, x = games.screen.width / 2 - 80,
                                  y = games.screen.height * 3 / 4 - 20, side = "rr")
            games.screen.add(self.rrtackle)
            # left cornerback
            self.cbl = fplayers.CB(game = self, x = games.screen.width * 3 / 4,
                          y = games.screen.height * 3 / 4 - 70, side="l")
            games.screen.add(self.cbl)
            # right cornerback
            self.cbr = fplayers.CB(game = self, x = games.screen.width / 4,
                          y = games.screen.height * 3 / 4 - 70, side="r")
            games.screen.add(self.cbr)
            # safety 1
            self.safety1 = fplayers.Safety(game=self, x=games.screen.width / 2 - 200,
                                  y=games.screen.height * 3 / 4 - 275, num="1")
            games.screen.add(self.safety1)
            # safety 2
            self.safety2 = fplayers.Safety(game=self, x=games.screen.width / 2 + 200,
                                  y=games.screen.height * 3 / 4 - 275, num="2")
            games.screen.add(self.safety2)

            # center
            self.center = fplayers.Center(game = self, x = games.screen.width / 2,
                                 y = games.screen.height * 3 / 4)
            games.screen.add(self.center)
            # right guard 1
            self.rol = fplayers.OL(game=self, x=games.screen.width / 2 + 40,
                                   y=games.screen.height * 3 / 4, side="r")
            games.screen.add(self.rol)
            # right guard 2
            self.rrol = fplayers.OL(game=self, x=games.screen.width / 2 + 80,
                                    y=games.screen.height * 3 / 4, side="rr")
            games.screen.add(self.rrol)
            # left guard 1
            self.lol = fplayers.OL(game=self, x=games.screen.width / 2 - 40,
                                   y=games.screen.height * 3 / 4, side="l")
            games.screen.add(self.lol)
            # left guard 2
            self.llol = fplayers.OL(game=self, x=games.screen.width / 2 - 80,
                                    y=games.screen.height * 3 / 4, side="ll")
            games.screen.add(self.llol)
            # quarterback
            self.qb = fplayers.QB(game=self, x=games.screen.width / 2,
                                  y=games.screen.height * 3 / 4 + 50)
            games.screen.add(self.qb)
            # runningback
            self.rb1 = fplayers.RB(game=self, x=games.screen.width / 2,
                                   y=games.screen.height - 6, num="1")
            games.screen.add(self.rb1)
            # left wide recicver
            self.wr1 = fplayers.WR(game=self, x=games.screen.width / 4,
                                   y=games.screen.height * 3 / 4, side="l")
            games.screen.add(self.wr1)
            # right wide recicver
            self.wr2 = fplayers.WR(game=self, x=games.screen.width * 3 / 4,
                                   y=games.screen.height * 3 / 4, side="r")
            games.screen.add(self.wr2)

        # elevate bar sprite and scoreboard sprites above all other sprites
        self.bar.elevate()
        self.sBoard.elevate()

    def halftime(self):
        self.remove_players()
        self.field.timer = Field.TIMER
        self.play_status = -1
        self.team1_offence = self.team1_half
        self.down = 0
        self.for_first_down = 360
        self.line_of_scrimmage = 1083
        text = ftxt.Half_text(self, "Press Enter to continue", 60, ftxt.RED, 30,
                              games.screen.width / 2, games.screen.height / 2)
        games.screen.add(text)

    def overtime(self):
        self.remove_players()
        self.field.timer = Field.TIMER
        self.play_status = -1
        self.down = 0
        self.for_first_down = 360
        self.line_of_scrimmage = 1083
        self.coin_toss()

    def change_offence(self):
        """ Changes the team that is on offence """
        self.team1_offence = not self.team1_offence

    def change_quarter(self):
        if self.quarter < 4:
            if self.quarter == 2:
                self.halftime()
            else:
                self.sBoard.reset_clock()
        elif self.quarter == 4:
            if self.team1_score == self.team2_score:
                self.sBoard.reset_clock()
                self.overtime()
            else:
                self.quarter += 1
        self.quarter += 1
        self.sBoard.update_quarter()

        self.player_fatigue()

    def penalize(self, yards, string):
        """ Moves penalized team 'yards' back and displays a message object
        with the value of 'string' """
        self.remove_players()
        self.sBoard.stop_clock()
        self.play_status = 1
        self.line_of_scrimmage -= 36 * yards
        self.for_first_down += 36 * yards
        message = ftxt.Football_message(game=self, value=string,
                                        x=games.screen.width / 2,
                                        y=games.screen.height / 2)
        games.screen.add(message)

    def view_replay(self):
        games.mouse.is_visible = True
        self.sprite_list = games.screen.all_objects
        for sprite in games.screen.all_objects:
            games.screen.remove(sprite)
        replay = Replay(self.replay_list)
        games.screen.add(replay)
        menu = Replay_menu(self, replay)
        games.screen.add(menu)

    def resume(self):
        games.mouse.is_visible = False
        games.screen.clear()
        for sprite in self.sprite_list:
            games.screen.add(sprite)
        del self.sprite_list

    def end_game(self):
        """ Method evoked at the end of the game """
        self.remove_players()

        # adjust the bar on the screen
        self.bar.reset()

        # adjust the field on the screen
        self.field.x = games.screen.width / 2
        self.field.y = games.screen.height / 2

        data = shelve.open("football_data.dat", "w")
        tuple = data["names"][self.name1]
        tuple1 = data["names"][self.name2]
        if self.team1_score > self.team2_score:
            tuple = (tuple[0] + 1, tuple[1], tuple[2])
            tuple1 = (tuple1[0], tuple1[1] + 1, tuple1[2])
            string = "The " + self.team1 + " win!"
        elif self.team2_score > self.team1_score:
            tuple = (tuple[0], tuple[1] + 1, tuple[2])
            tuple1 = (tuple1[0] + 1, tuple1[1], tuple1[2])
            string = "The " + self.team2 + " win!"
        else:
            tuple = (tuple[0], tuple[1], tuple[2] + 1)
            tuple1 = (tuple1[0], tuple1[1], tuple1[2] + 1)
            string = "Tie!"
        dict = data["names"]
        dict[self.name1] = tuple
        dict[self.name2] = tuple1
        data["names"] = dict
        data.close()

        text = ftxt.Text(game=self, value=string, size=100,
                         color=ftxt.RED, x=games.screen.width / 2,
                         y=games.screen.height / 2)
        games.screen.add(text)

        text = ftxt.Play_again_text(game=self, x=games.screen.width / 2,
                                    bottom=games.screen.height - 10)
        games.screen.add(text)

    def reset_base_speeds(self):
        fplayers.QB.base_speed = 5.5 + random.randrange(0, 2) / 10.0
        fplayers.QB.base_speed1 = 5.5 + random.randrange(0, 2) / 10.0
        fplayers.WR.base_speed = 5.5 + random.randrange(0, 3) / 10.0
        fplayers.WR.base_speed1 = 5.5 + random.randrange(0, 3) / 10.0
        fplayers.RB.base_speed = 5.6 + random.randrange(0, 2) / 10.0
        fplayers.RB.base_speed1 = 5.6 + random.randrange(0, 2) / 10.0
        fplayers.Center.base_speed = 5.5 + random.randrange(-3, 1) / 10.0
        fplayers.Center.base_speed1 = 5.5 + random.randrange(-3, 1) / 10.0
        fplayers.Center.block = 3 + random.randrange(0, 4)
        fplayers.Center.block1 = 3 + random.randrange(0, 4)
        fplayers.OL.base_speed = 5.5 + random.randrange(-3, 1) / 10.0
        fplayers.OL.base_speed1 = 5.5 + random.randrange(-3, 1) / 10.0
        fplayers.OL.block = 3 + random.randrange(0, 4)
        fplayers.OL.block1 = 3 + random.randrange(0, 4)
        fplayers.TE.base_speed = 5.5 + random.randrange(0, 2) / 10.0
        fplayers.TE.base_speed1 = 5.5 + random.randrange(0, 2) / 10.0
        fplayers.TE.block = 3 + random.randrange(0, 4)
        fplayers.TE.block1 = 3 + random.randrange(0, 4)        
        fplayers.Punter.base_speed = 5.5 + random.randrange(0, 2) / 10.0
        fplayers.Punter.base_speed1 = 5.5 + random.randrange(0, 2) / 10.0
        fplayers.STCenter.base_speed = 5.5 + random.randrange(0, 3) / 10.0
        fplayers.STCenter.base_speed1 = 5.5 + random.randrange(0, 3) / 10.0
        fplayers.STCenter.block = 3 + random.randrange(0, 4)
        fplayers.STCenter.block1 = 3 + random.randrange(0, 4)
        fplayers.STOL.base_speed = 5.5 + random.randrange(0, 3) / 10.0
        fplayers.STOL.base_speed1 = 5.5 + random.randrange(0, 3) / 10.0
        fplayers.STOL.block = 3 + random.randrange(0, 4)
        fplayers.STOL.block1 = 3 + random.randrange(0, 4)
        fplayers.DL.base_speed = 5.5 + random.randrange(-3, 1) / 10.0
        fplayers.DL.base_speed1 = 5.5 + random.randrange(-3, 1) / 10.0
        fplayers.LB.base_speed = 5.5 + random.randrange(-1, 2) / 10.0
        fplayers.LB.base_speed1 = 5.5 + random.randrange(-1, 2) / 10.0
        fplayers.CB.base_speed = 5.5 + random.randrange(0, 3) / 10.0
        fplayers.CB.base_speed1 = 5.5 + random.randrange(0, 3) / 10.0
        fplayers.Safety.base_speed = 5.5 + random.randrange(0, 3) / 10.0
        fplayers.Safety.base_speed1 = 5.5 + random.randrange(0, 3) / 10.0
        fplayers.Safety.base_speed2 = 5.5 + random.randrange(0, 3) / 10.0
        fplayers.Safety.base_speed3 = 5.5 + random.randrange(0, 3) / 10.0
        fplayers.STDL.base_speed = 5.5 + random.randrange(-3, 1) / 10.0
        fplayers.STDL.base_speed1 = 5.5 + random.randrange(-3, 1) / 10.0
        fplayers.STLB.base_speed = 5.5 + random.randrange(-1, 2) / 10.0
        fplayers.STLB.base_speed1 = 5.5 + random.randrange(-1, 2) / 10.0
        fplayers.PR.base_speed = 5.6 + random.randrange(0, 2) / 10.0
        fplayers.PR.base_speed1 = 5.6 + random.randrange(0, 2) / 10.0

    def player_fatigue(self):
        classes = (fplayers.QB, fplayers.WR, fplayers.RB, fplayers.Punter,
                   fplayers.LB, fplayers.STLB, fplayers.CB, fplayers.Safety,
                   fplayers.PR, fplayers.DL, fplayers.STDL, fplayers.Center,
                   fplayers.OL, fplayers.STCenter, fplayers.STOL, fplayers.TE)
        for a_class in classes:
            if random.randrange(3) == 0:
                a_class.base_speed -= .1
            if random.randrange(3) == 0:
                a_class.base_speed1 -= .1
        for a_class in classes[11:]:
            if random.randrange(3) == 0:
                a_class.block += 1
            if random.randrange(3) == 0:
                a_class.block1 += 1

    def show_settings(self):
        games.screen.clear()

        self.c_settings = ftxt.Clock_settings(self, self.game_length)
        games.screen.add(self.c_settings)

        self.s_settings = ftxt.Sound_settings(self, self.sound_set)
        games.screen.add(self.s_settings)

        text = ftxt.Main_back(game=self, value="Cancel", size=40,
                               color1=ftxt.WHITE, color2=ftxt.RED,
                               right=games.screen.width - 10,
                               bottom=games.screen.height - 10)
        games.screen.add(text)

        text = ftxt.Confirm_set(game=self, value="Confirm", size=40,
                                color1=ftxt.WHITE, color2=ftxt.GREEN,
                                right=text.left - 25,
                                bottom=games.screen.height - 10)
        games.screen.add(text)

    def show_records(self):
        games.screen.clear()

        data = shelve.open("football_data.dat", "r")
        names = data["names"].keys()
        names.sort()
        left = 10
        top = 10
        number = 1
        for name in names:
            text = ftxt.Text(self, name + ": " + str(data["names"][name][0]) + "-" + str(data["names"][name][1]) + "-" + str(data["names"][name][2]),
                             25, ftxt.WHITE, left=left, top=top)
            games.screen.add(text)
            top = text.bottom + 10
            if number == 20:
                left += 300
                top = 10
                number = 1
            else:
                number += 1
        data.close()

        text = ftxt.Main_back(self, "Back", 40, ftxt.WHITE, ftxt.RED,
                              right=games.screen.width - 10,
                              bottom=games.screen.height - 10)
        games.screen.add(text)

    def play_sound(self, sound, loop=0):
        """ Plays 'sound' if sound setting is on """
        if self.sound_set:
            sound.play(loop)

    def remove_players(self):
        """ Removes all football players from the screen """
        for sprite in games.screen.all_objects:
            if sprite not in self.do_not_destroy:
                sprite.destroy()

    def get_game_length(self):
        return self.game_length

    def get_sound_set(self):
        return self.sound_set

def main():
    football = Game()
    games.screen.mainloop()

# run program
main()
