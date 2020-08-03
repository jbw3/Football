# Football
# Version 6
#
# A football game for two players. The player on offence controls the
# quarterback first, and then the player who catches the ball. The defence is
# controlled by the second player.
#
# To do:
# 1. make football players' arms
# 2. add sounds
# 3. make it a safety if defence runs out of its own end zone???
# 4. make defence able to face player with ball
# 5. make two minute warning
# 6. change game length settings so user can pick minutes per quarter
# 7. pause after each quarter
# 8. end play when football goes out of bounds
# 9. make min angle change per player per frame
# 10. fix penalties so line of scrimmage will not be in end zone

# import games module
import games

# initialize screen
games.init(screen_width=1020, screen_height=700, fps=50)

# import other modules
import sys, random, shelve, football_text as ftxt, players
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
    VPAD = 720
    HPAD = 520
    VPAD1 = 360
    TIMER = 100
    def __init__(self, game):
        """ Initializes object """
        self.game = game
        super(Field, self).__init__(games.load_image("images\\field.bmp", False),
                                    x=games.screen.width/2,
                                    y=games.screen.height/2,
                                    is_collideable=False)
        self.save = True
        self.reset_timer()

        self.game.do_not_destroy.append(self)  # add self to do_not_destroy list

    def update(self):
        if not self.game.timeout:
            if self.game.play_status == 1:
                if self.timer == Field.TIMER:
                    self.save_frame()
                self.timer -= 1
                if self.timer == 0:
                    self.reset_timer()
                    if not self.game.sBoard.game_is_over():
                        self.game.pick_play()

            elif self.game.play_status == -1:
                if self.game.blitz == 0:
                    for controller in self.game.d_controllers:
                        if controller.get_hat(0)[0] == 1:
                            self.game.blitz = 3
                        elif controller.get_hat(0)[0] == -1:
                            self.game.blitz = 2
                        elif controller.get_hat(0)[1] == 1:
                            self.game.blitz = 1
                        elif controller.get_hat(0)[1] == -1:
                            self.game.blitz = 4

            elif self.game.play_status == 0:
                if self.save:
                    self.save_frame()
                self.save = not self.save

                if self.game.ball_carrier in self.game.o_players and self.game.ball_carrier.top < self.top + Field.VPAD:
                    self.game.touchdown(True)

                elif self.game.ball_carrier in self.game.o_players and self.game.ball_carrier.bottom > self.bottom - Field.VPAD1:
                    self.game.safety()

                elif self.game.ball_carrier in self.game.d_players and self.game.ball_carrier.bottom > self.bottom - Field.VPAD:
                    self.game.touchdown(False)

                elif self.game.ball_carrier in self.game.players and (self.game.ball_carrier.x < self.left + Field.HPAD or self.game.ball_carrier.x > self.right - Field.HPAD):
                    self.game.sBoard.stop_clock()
                    self.game.for_first_down -= self.bottom - self.game.line_of_scrimmage - Field.VPAD - self.game.ball_carrier.y
                    self.game.line_of_scrimmage = self.bottom - self.game.ball_carrier.y - Field.VPAD
                    self.game.end_play()
                    self.game.ball_carrier.speed = 0
                    self.game.ball_carrier.x_change = 0
                    self.game.ball_carrier.y_change = 0
                    if self.game.ball_carrier in self.game.d_players:
                        self.game.change_offence()

            if self.game.play_status != 0:
                for controller in self.game.team1_ctrls + self.game.team2_ctrls:
                    if controller.get_button(8):
                        if controller in self.game.o_controllers:
                            if self.game.team1_offence:
                                team = self.game.team1
                            else:
                                team = self.game.team2
                        else:
                            if self.game.team1_offence:
                                team = self.game.team2
                            else:
                                team = self.game.team1
                        self.game.call_timeout(team)

    def center_adjust(self):
        self.x = games.screen.width / 2
        self.y = games.screen.height / 2

    def line_adjust(self, padding=0):
        self.x = games.screen.width / 2
        self.bottom = (games.screen.height * .75) + self.game.line_of_scrimmage + Field.VPAD + padding

    def save_frame(self):
        self.game.replay_list.append(games.screen.last_display)
        if len(self.game.replay_list) > 400:
            del self.game.replay_list[0]

    def reset_timer(self):
        self.timer = Field.TIMER 

class Scoreboard(object):
    """ The scoreboard """
    def __init__(self, game):
        """ Put all of the scoreboard items on the screen """
        self.game = game
        # put the background on the screen
        self.background = games.Sprite(
            games.load_image("images\\scoreboard_background.bmp", False),
            left=0, top=0, is_collideable=False)
        games.screen.add(self.background)

        game.non_activated_sprites.append(self.background)
        game.do_not_destroy.append(self.background)

        self.play_clock = None

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
        self.play_clock = ftxt.Play_clock(self.game, self.game_clock.bottom + 10)
        games.screen.add(self.play_clock)

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
    def __init__(self, master):
        self.master = master
        data = shelve.open("football_data.dat", "r")
        self.game_length = data["length"]
        self.sound_set = data["sound"]
        data.close()

        self.set_variables()
        self.get_beginning_info()

    def set_variables(self):
        self.team1_ctrls = []
        self.team1_ctrls.append(self.master.joysticks[0])  # <- temporary
        self.team2_ctrls = []
        self.team2_ctrls.append(self.master.joysticks[1])  # <- temporary
        self.o_controllers = []
        self.d_controllers = []
        self.do_not_destroy = []
        self.circles = []
        # create circles
        for i in range(pygame.joystick.get_count()):
            circle = players.Circle(self, i)
            self.circles.append(circle)
        self.name1 = ""
        self.name2 = ""
        self.team1 = ""
        self.team2 = ""
        self.team1_score = 0
        self.team2_score = 0
        self.team1_to = 0
        self.team2_to = 0
        self.team1_images = []
        self.team2_images = []
        self.team1_offence = True
        self.team1_half = True
        self.timeout = False
        self.down = 0
        self.quarter = 1
        self.non_activated_sprites = []
        self.ball_carrier = None
        self.extra_point = False
        self.players = []
        self.o_players = []
        self.d_players = []
        self.can_not_catch = []
        self.blitz = 0
        self.play_num = None
        self.play_status = -1
        self.ball_incomplete = False
        self.line_of_scrimmage = 1083
        self.for_first_down = 360
        self.passed_line = False
        self.replay_list = []
        # interceptions thrown, sacks made
        self.stats = [[0, 0], [0, 0]]

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
        self.kicker = None

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
        teams.sort()
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

    def set_timeouts(self, num):
        self.team1_to = num
        self.team2_to = num

    def start(self):
        """ Puts the field on the screen """        
        # clear the screen of other sprites
        games.screen.clear()

        self.reset_base_speeds()
        players.Basic_defense.reset_intercept()
        players.Basic_defense.reset_intercept1()

        # put the field on the screen
        self.field = Field(self)
        games.screen.add(self.field)

        self.sBoard = Scoreboard(self)

        self.bar = Bar(self)
        games.screen.add(self.bar)

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
        self.play_num = None

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
        self.kicker = None

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
        self.field.line_adjust()

        text = ftxt.Play_text(self)
        games.screen.add(text)

        images = []
        for i in range(8):
            images.append("images\\play"+str(i)+".bmp")
        text = ftxt.Play_selector(self, images, self.o_controllers[0],
                                  games.screen.height * .6)

        text = ftxt.Yard_line(self)
        games.screen.add(text)

        self.sBoard.show_play_clock()

    def start_play(self):
        for player in self.d_players:
            if player.bottom > self.field.bottom - self.line_of_scrimmage - Field.VPAD:
                self.penalize(-5, "Offsides")
                break
        else:
            self.play_status = 0
            if not self.extra_point:
                self.sBoard.start_clock()

    def end_play(self, end_xp=True):
        self.play_status = 1
        if self.extra_point and end_xp:
            self.change_offence()
            self.line_of_scrimmage = 1080
            self.for_first_down = 360
            self.down = 0
            self.extra_point = False

    def touchdown(self, offence):
        self.for_first_down = 360
        ep = self.extra_point
        self.end_play(offence)
        self.ball_carrier.speed = 0
        self.down = 0
        if offence:
            if ep:
                if self.team1_offence:
                    self.team2_score += 2
                else:
                    self.team1_score += 2
                self.line_of_scrimmage = 1080
            else:
                if self.team1_offence:
                    self.team1_score += 6
                else:
                    self.team2_score += 6
                self.extra_point = True
                self.line_of_scrimmage = 3528
        else:
            if self.team1_offence:
                self.team2_score += 6
            else:
                self.team1_score += 6
            self.extra_point = True
            self.line_of_scrimmage = 3528
            self.change_offence()
        self.sBoard.update_score()
        self.sBoard.stop_clock()
        message = ftxt.Football_message(self, "Touchdown!",
                                        x=games.screen.width / 2,
                                        y=games.screen.height / 2)
        games.screen.add(message)

    def safety(self):
        self.end_play()
        self.for_first_down = 360
        self.line_of_scrimmage = 1083
        if self.team1_offence:
            self.team2_score += 2
        else:
            self.team1_score += 2
        self.sBoard.update_score()
        self.down = 0
        self.sBoard.stop_clock()
        self.change_offence()
        message = ftxt.Football_message(self, "Safety!",
                                        x=games.screen.width / 2,
                                        y=games.screen.height / 2)
        games.screen.add(message)

    def add_offence(self):
        """ Put the offence on the screen """
        if self.play_num == 7:
            self.field.line_adjust(-150)
            # center
            self.center = players.STCenter(self, games.screen.width / 2,
                                            games.screen.height * 3 / 4 - 150)
            games.screen.add(self.center)
            # left guard 1
            self.lol = players.STOL(self, games.screen.width / 2 - 40,
                                     games.screen.height * 3 / 4 - 150, "l")
            games.screen.add(self.lol)
            # left guard 2
            self.llol = players.STOL(self, games.screen.width / 2 - 80,
                                      games.screen.height * 3 / 4 - 150, "ll")
            games.screen.add(self.llol)
            # right guard 1
            self.rol = players.STOL(self, games.screen.width / 2 + 40,
                                     games.screen.height * 3 / 4 - 150, "r")
            games.screen.add(self.rol)
            # right guard 2
            self.rrol = players.STOL(self, games.screen.width / 2 + 80,
                                      games.screen.height * 3 / 4 - 150, "rr")
            games.screen.add(self.rrol)
            # punter
            self.punter = players.Punter(self, games.screen.width / 2,
                                          games.screen.height * 3 / 4 + 50)
            games.screen.add(self.punter)
        elif self.play_num == 0:
            # center
            self.center = players.Center(game = self, x = games.screen.width / 2,
                                 y = games.screen.height * 3 / 4)
            games.screen.add(self.center)
            # right guard 1
            self.rol = players.OL(game = self, x = games.screen.width / 2 + 40,
                                y = games.screen.height * 3 / 4, side = "r")
            games.screen.add(self.rol)
            # right guard 2
            self.rrol = players.OL(game = self, x = games.screen.width / 2 + 80,
                                 y = games.screen.height * 3 / 4, side = "rr")
            games.screen.add(self.rrol)
            # left guard 1
            self.lol = players.OL(game = self, x = games.screen.width / 2 - 40,
                                y = games.screen.height * 3 / 4, side = "l")
            games.screen.add(self.lol)
            # left guard 2
            self.llol = players.OL(game=self, x=games.screen.width / 2 - 80,
                                 y=games.screen.height * 3 / 4, side="ll")
            games.screen.add(self.llol)
            # tight end
            self.te1 = players.TE(game=self, x=games.screen.width / 2 - 120,
                                   y=games.screen.height * 3 / 4, num="1")
            games.screen.add(self.te1)
            # quarterback
            self.qb = players.QB(game=self, x=games.screen.width / 2,
                    y=games.screen.height * 3 / 4 + 50)
            games.screen.add(self.qb)
            # runningback
            self.rb1 = players.RB(game=self, x=games.screen.width / 2,
                                   y=games.screen.height - 6, num="1")
            games.screen.add(self.rb1)
            # runningback 1
            self.rb2 = players.RB(game = self, x = games.screen.width / 2,
                         y = games.screen.height + 40, num="2")
            games.screen.add(self.rb2)
            # right wide recicver
            self.wr2 = players.WR(game = self, x = games.screen.width * 3 / 4,
                          y = games.screen.height * 3 / 4, side="r")
            games.screen.add(self.wr2)
        elif self.play_num == 2 or self.play_num == 5:
            # center
            self.center = players.Center(self, games.screen.width / 2,
                                          games.screen.height * 3 / 4)
            games.screen.add(self.center)
            # right guard 1
            self.rol = players.OL(game=self, x=games.screen.width / 2 + 40,
                                   y=games.screen.height * 3 / 4, side="r")
            games.screen.add(self.rol)
            # right guard 2
            self.rrol = players.OL(game=self, x=games.screen.width / 2 + 80,
                                    y=games.screen.height * 3 / 4, side="rr")
            games.screen.add(self.rrol)
            # left guard 1
            self.lol = players.OL(game=self, x=games.screen.width / 2 - 40,
                                   y=games.screen.height * 3 / 4, side="l")
            games.screen.add(self.lol)
            # left guard 2
            self.llol = players.OL(game=self, x=games.screen.width / 2 - 80,
                                    y=games.screen.height * 3 / 4, side="ll")
            games.screen.add(self.llol)
            # tight end
            self.te1 = players.TE(game=self, x=games.screen.width / 2 + 120,
                                   y=games.screen.height * 3 / 4, num="1")
            games.screen.add(self.te1)
            # quarterback
            self.qb = players.QB(game=self, x=games.screen.width / 2,
                                  y=games.screen.height * 3 / 4 + 50)
            games.screen.add(self.qb)
            # runningback
            self.rb1 = players.RB(game=self, x=games.screen.width / 2,
                                   y=games.screen.height - 6, num="1")
            games.screen.add(self.rb1)
            # left wide recicver
            self.wr1 = players.WR(game=self, x=games.screen.width / 4,
                                   y=games.screen.height * 3 / 4, side="l")
            games.screen.add(self.wr1)
            # right wide recicver
            self.wr2 = players.WR(game=self, x=games.screen.width * 3 / 4,
                                   y=games.screen.height * 3 / 4, side="r")
            games.screen.add(self.wr2)
        elif self.play_num == 6:
            # center
            self.center = players.Center(game = self, x = games.screen.width / 2,
                                 y = games.screen.height * 3 / 4)
            games.screen.add(self.center)
            # right guard 1
            self.rol = players.OL(game=self, x=games.screen.width / 2 + 40,
                                   y=games.screen.height * 3 / 4, side="r")
            games.screen.add(self.rol)
            # right guard 2
            self.rrol = players.OL(game=self, x=games.screen.width / 2 + 80,
                                    y=games.screen.height * 3 / 4, side="rr")
            games.screen.add(self.rrol)
            # left guard 1
            self.lol = players.OL(game=self, x=games.screen.width / 2 - 40,
                                   y=games.screen.height * 3 / 4, side="l")
            games.screen.add(self.lol)
            # left guard 2
            self.llol = players.OL(game=self, x=games.screen.width / 2 - 80,
                                    y=games.screen.height * 3 / 4, side="ll")
            games.screen.add(self.llol)
            # tight end
            self.te1 = players.TE(game=self, x=games.screen.width / 2 + 120,
                                   y=games.screen.height * 3 / 4, num="1")
            games.screen.add(self.te1)
            # quarterback
            self.qb = players.QB(game=self, x=games.screen.width / 2,
                                  y=games.screen.height * 3 / 4 + 50)
            games.screen.add(self.qb)
            # runningback
            self.rb1 = players.RB(game=self, x=games.screen.width / 2 + 30,
                                  y=games.screen.height - 20, num="2")
            games.screen.add(self.rb1)
            # left wide recicver
            self.wr1 = players.WR(game=self, x=games.screen.width / 4,
                                   y=games.screen.height * 3 / 4, side="l")
            games.screen.add(self.wr1)
            # right wide recicver
            self.wr2 = players.WR(game=self, x=games.screen.width * 3 / 4,
                                   y=games.screen.height * 3 / 4, side="r")
            games.screen.add(self.wr2)
        else:
            # center
            self.center = players.Center(game = self, x = games.screen.width / 2,
                                 y = games.screen.height * 3 / 4)
            games.screen.add(self.center)
            # right guard 1
            self.rol = players.OL(game=self, x=games.screen.width / 2 + 40,
                                   y=games.screen.height * 3 / 4, side="r")
            games.screen.add(self.rol)
            # right guard 2
            self.rrol = players.OL(game=self, x=games.screen.width / 2 + 80,
                                    y=games.screen.height * 3 / 4, side="rr")
            games.screen.add(self.rrol)
            # left guard 1
            self.lol = players.OL(game=self, x=games.screen.width / 2 - 40,
                                   y=games.screen.height * 3 / 4, side="l")
            games.screen.add(self.lol)
            # left guard 2
            self.llol = players.OL(game=self, x=games.screen.width / 2 - 80,
                                    y=games.screen.height * 3 / 4, side="ll")
            games.screen.add(self.llol)
            # quarterback
            self.qb = players.QB(game=self, x=games.screen.width / 2,
                                  y=games.screen.height * 3 / 4 + 50)
            games.screen.add(self.qb)
            # runningback
            self.rb1 = players.RB(game=self, x=games.screen.width / 2,
                                   y=games.screen.height - 6, num="1")
            games.screen.add(self.rb1)
            # left wide recicver
            self.wr1 = players.WR(game=self, x=games.screen.width / 4,
                                   y=games.screen.height * 3 / 4, side="l")
            games.screen.add(self.wr1)
            # right wide recicver
            self.wr2 = players.WR(game=self, x=games.screen.width * 3 / 4,
                                   y=games.screen.height * 3 / 4, side="r")
            games.screen.add(self.wr2)

    def add_defense(self):
        """ Put the defense on the screen """
        if self.play_num == 7:
            # punt returner
            self.pr = players.PR(self, games.screen.width / 2,
                                  self.field.top + Field.VPAD + 100)
            games.screen.add(self.pr)
            # linbacker
            self.rlb = players.STLB(self, games.screen.width / 2 - 60,
                                     games.screen.height * 3 / 4 - 220, "r")
            games.screen.add(self.rlb)
            # linbacker
            self.clb = players.STLB(self, games.screen.width / 2,
                                     games.screen.height * 3 / 4 - 220, "c")
            games.screen.add(self.clb)
            # linbacker
            self.llb = players.STLB(self, games.screen.width / 2 + 60,
                                     games.screen.height * 3 / 4 - 220, "l")
            games.screen.add(self.llb)
            # right dl 2
            self.rrtackle = players.STDL(self, games.screen.width / 2 - 80,
                                          games.screen.height * 3 / 4 - 170, "rr")
            games.screen.add(self.rrtackle)
            # right dl 1
            self.rtackle = players.STDL(self, games.screen.width / 2 - 40,
                                         games.screen.height * 3 / 4 - 170, "r")
            games.screen.add(self.rtackle)
            # center tackle
            self.ctackle = players.STDL(self, games.screen.width / 2,
                                         games.screen.height * 3 / 4 - 170, "c")
            games.screen.add(self.ctackle)
            # left tackle 1
            self.ltackle = players.STDL(self, games.screen.width / 2 + 40,
                                         games.screen.height * 3 / 4 - 170, "l")
            games.screen.add(self.ltackle)
            # left dl 2
            self.lltackle = players.STDL(self, games.screen.width / 2 + 80,
                                          games.screen.height * 3 / 4 - 170, "ll")
            games.screen.add(self.lltackle)
        elif self.play_num == 0:
            # safety 1
            self.safety1 = players.Safety(game=self, x=games.screen.width / 2 - 200,
                                  y=games.screen.height * 3 / 4 - 275, num="1")
            games.screen.add(self.safety1)
            # safety 2
            self.safety2 = players.Safety(game=self, x=games.screen.width / 2 + 200,
                                  y=games.screen.height * 3 / 4 - 275, num="2")
            games.screen.add(self.safety2)
            # left cornerback
            self.cbl = players.CB(game = self, x = games.screen.width * 3 / 4,
                          y = games.screen.height * 3 / 4 - 70, side="l")
            games.screen.add(self.cbl)
            # linebacker
            self.rlb = players.LB(game=self, x=games.screen.width / 2 - 80,
                                   y=games.screen.height * 3 / 4 - 70, side="r")
            games.screen.add(self.rlb)
            # linebacker
            self.clb = players.LB(game=self, x=games.screen.width / 2,
                                   y=games.screen.height * 3 / 4 - 70, side="c")
            games.screen.add(self.clb)
            # linebacker
            self.llb = players.LB(game=self, x=games.screen.width / 2 + 80,
                                   y=games.screen.height * 3 / 4 - 70, side="l")
            games.screen.add(self.llb)
            # right tackle 3
            self.rrrtackle = players.DL(game=self, x=games.screen.width / 2 - 120,
                                y=games.screen.height * 3 / 4 - 20, side="rrr")
            games.screen.add(self.rrrtackle)
            # right tackle 2
            self.rrtackle = players.DL(game=self, x=games.screen.width / 2 - 80,
                                  y=games.screen.height * 3 / 4 - 20, side="rr")
            games.screen.add(self.rrtackle)
            # right tackle 1
            self.rtackle = players.DL(game=self, x=games.screen.width / 2 - 40,
                                  y=games.screen.height * 3 / 4 - 20, side="r")
            games.screen.add(self.rtackle)
            # left tackle 1
            self.ltackle = players.DL(game=self, x=games.screen.width / 2 + 40,
                                  y =games.screen.height * 3 / 4 - 20, side="l")
            games.screen.add(self.ltackle)
            # left tackle 2
            self.lltackle = players.DL(game=self, x=games.screen.width / 2 + 80,
                                  y=games.screen.height * 3 / 4 - 20, side="ll")
            games.screen.add(self.lltackle)
        else:
            # safety 1
            self.safety1 = players.Safety(self, games.screen.width / 2 - 200,
                                         games.screen.height * 3 / 4 - 275, "1")
            games.screen.add(self.safety1)
            # safety 2
            self.safety2 = players.Safety(self, games.screen.width / 2 + 200,
                                         games.screen.height * 3 / 4 - 275, "2")
            games.screen.add(self.safety2)
            # right cornerback
            self.cbr = players.CB(game = self, x = games.screen.width / 4,
                          y = games.screen.height * 3 / 4 - 70, side="r")
            games.screen.add(self.cbr)
            # left cornerback
            self.cbl = players.CB(game = self, x = games.screen.width * 3 / 4,
                          y = games.screen.height * 3 / 4 - 70, side="l")
            games.screen.add(self.cbl)
            # linebacker
            self.rlb = players.LB(game=self, x=games.screen.width / 2 - 80,
                                   y=games.screen.height * 3 / 4 - 70, side="r")
            games.screen.add(self.rlb)
            # linebacker
            self.clb = players.LB(game=self, x=games.screen.width / 2,
                                   y=games.screen.height * 3 / 4 - 70, side="c")
            games.screen.add(self.clb)
            # linebacker
            self.llb = players.LB(game=self, x=games.screen.width / 2 + 80,
                                   y=games.screen.height * 3 / 4 - 70, side="l")
            games.screen.add(self.llb)
            # right tackle 2
            self.rrtackle = players.DL(self, games.screen.width / 2 - 80,
                                       games.screen.height * 3 / 4 - 20, "rr")
            games.screen.add(self.rrtackle)
            # right tackle 1
            self.rtackle = players.DL(self, games.screen.width / 2 - 40,
                                      games.screen.height * 3 / 4 - 20, "r")
            games.screen.add(self.rtackle)
            # left tackle 1
            self.ltackle = players.DL(self, games.screen.width / 2 + 40,
                                      games.screen.height * 3 / 4 - 20, "l")
            games.screen.add(self.ltackle)
            # left tackle 2
            self.lltackle = players.DL(self, games.screen.width / 2 + 80,
                                       games.screen.height * 3 / 4 - 20, "ll")
            games.screen.add(self.lltackle)

    def new_play(self):
        """ Puts all of the football players on the screen for a new play """
        self.replay_list = []
        self.ball_incomplete = False

        # put the players on the screen
        self.add_defense()
        self.add_offence()

        # put circles on screen
        for circle in self.circles:
            circle.reveal()

        # elevate bar sprite and scoreboard sprites above all other sprites
        self.bar.elevate()
        self.sBoard.elevate()

    def halftime(self):
        self.remove_players()
        self.field.timer = Field.TIMER
        self.play_status = -1
        self.team1_offence = self.team1_half
        if self.team1_offence:
            self.o_controllers = self.team1_ctrls
            self.d_controllers = self.team2_ctrls
        else:
            self.o_controllers = self.team2_ctrls
            self.d_controllers = self.team1_ctrls
        self.down = 0
        self.set_timeouts(0)
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
        self.set_timeouts(0)
        self.for_first_down = 360
        self.line_of_scrimmage = 1083
        self.coin_toss()

    def get_o_controller(self, index):
        controller = self.o_controllers[index]
        for player in self.o_players:
            if player.controller == controller:
                player.controller = None
                break
        return controller

    def get_d_controller(self, index):
        controller = self.d_controllers[index]
        for player in self.d_players:
            if player.controller == controller:
                player.controller = None
                break
        return controller

    def change_offence(self):
        """ Changes the team that is on offence """
        self.team1_offence = not self.team1_offence
        # swap controller lists
        temp = self.o_controllers
        self.o_controllers = self.d_controllers
        self.d_controllers = temp

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
        self.end_play(False)
        self.line_of_scrimmage -= 36 * yards
        self.for_first_down += 36 * yards
        self.down -= 1
        message = ftxt.Football_message(self, string, x=games.screen.width / 2,
                                        y=games.screen.height / 2)
        games.screen.add(message)

    def call_timeout(self, team):
        """ Call a timeout """
        if team == self.team1:
            if self.team1_to == 0:
                return
            else:
                self.team1_to -= 1
        elif team == self.team2:
            if self.team2_to == 0:
                return
            else:
                self.team2_to -= 1
        self.remove_players()
        self.sBoard.stop_clock()
        self.timeout = True
        self.field.reset_timer() # resets field's timer in case play_status is 1
        if self.play_status == -1:
            self.down -= 1
        def func():
            self.timeout = False
            self.pick_play()
        text = ftxt.Football_message(self, "Timeout: " + team,
                                     x=games.screen.width / 2,
                                     y=games.screen.height / 2, lifetime=150,
                                     after_death=func)
        games.screen.add(text)

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
        self.sBoard.play_clock.replay_reset()
        self.sBoard.game_clock.replay_reset()

    def end_game(self):
        """ Method evoked at the end of the game """
        self.remove_players()
        self.set_timeouts(0)

        # adjust the bar on the screen
        self.bar.reset()

        # adjust the field on the screen
        self.field.center_adjust()

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

        text = ftxt.Text(game=self, value=string, size=80,
                         color=ftxt.RED, x=games.screen.width / 2,
                         top=50)
        games.screen.add(text)

        text = ftxt.Play_again_text(game=self, x=games.screen.width / 2,
                                    bottom=games.screen.height - 10)
        games.screen.add(text)

        self.show_stats()

    def show_stats(self):
        text = ftxt.Text(self, "Stats", 70, ftxt.RED, x=games.screen.width / 2,
                         top=150)
        games.screen.add(text)

        text = ftxt.Text(self, self.team1, 50, ftxt.RED,
                         x=games.screen.width * .4, top=200)
        games.screen.add(text)

        text = ftxt.Text(self, self.team2, 50, ftxt.RED,
                         x=games.screen.width * .6, top=200)
        games.screen.add(text)

        top = 250
        strings = ("Int. Thrown", "Sacks Made")
        for i in range(len(strings)):
            text = ftxt.Text(self, strings[i], 50, ftxt.RED, left=50, top=top)
            games.screen.add(text)
            text = ftxt.Text(self, str(self.stats[i][0]), 50, ftxt.RED,
                             x=games.screen.width * .4, top=top)
            games.screen.add(text)
            text = ftxt.Text(self, str(self.stats[i][1]), 50, ftxt.RED,
                             x=games.screen.width * .6, top=top)
            games.screen.add(text)
            top += 50

    def reset_base_speeds(self):
        players.QB.base_speed = players.Basic_player.BASE_SPEED + random.randrange(0, 2) / 10.0
        players.QB.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(0, 2) / 10.0
        players.WR.base_speed = players.Basic_player.BASE_SPEED + random.randrange(0, 3) / 10.0
        players.WR.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(0, 3) / 10.0
        players.RB.base_speed = players.Basic_player.BASE_SPEED + random.randrange(1, 3) / 10.0
        players.RB.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(1, 3) / 10.0
        players.Center.base_speed = players.Basic_player.BASE_SPEED + random.randrange(-2, 1) / 10.0
        players.Center.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(-2, 1) / 10.0
        players.Center.block = 3 + random.randrange(0, 4)
        players.Center.block1 = 3 + random.randrange(0, 4)
        players.OL.base_speed = players.Basic_player.BASE_SPEED + random.randrange(-2, 1) / 10.0
        players.OL.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(-2, 1) / 10.0
        players.OL.block = 3 + random.randrange(0, 4)
        players.OL.block1 = 3 + random.randrange(0, 4)
        players.TE.base_speed = players.Basic_player.BASE_SPEED + random.randrange(0, 2) / 10.0
        players.TE.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(0, 2) / 10.0
        players.TE.block = 3 + random.randrange(0, 4)
        players.TE.block1 = 3 + random.randrange(0, 4)        
        players.Punter.base_speed = players.Basic_player.BASE_SPEED + random.randrange(0, 2) / 10.0
        players.Punter.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(0, 2) / 10.0
        players.Kicker.base_speed = players.Basic_player.BASE_SPEED + random.randrange(0, 2) / 10.0
        players.Kicker.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(0, 2) / 10.0 
        players.STCenter.base_speed = players.Basic_player.BASE_SPEED + random.randrange(0, 2) / 10.0
        players.STCenter.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(0, 2) / 10.0
        players.STCenter.block = 3 + random.randrange(0, 4)
        players.STCenter.block1 = 3 + random.randrange(0, 4)
        players.STOL.base_speed = players.Basic_player.BASE_SPEED + random.randrange(0, 2) / 10.0
        players.STOL.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(0, 2) / 10.0
        players.STOL.block = 3 + random.randrange(0, 4)
        players.STOL.block1 = 3 + random.randrange(0, 4)
        players.DL.base_speed = players.Basic_player.BASE_SPEED + random.randrange(-2, 1) / 10.0
        players.DL.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(-2, 1) / 10.0
        players.LB.base_speed = players.Basic_player.BASE_SPEED + random.randrange(-1, 2) / 10.0
        players.LB.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(-1, 2) / 10.0
        players.CB.base_speed = players.Basic_player.BASE_SPEED + random.randrange(0, 3) / 10.0
        players.CB.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(0, 3) / 10.0
        players.Safety.base_speed = players.Basic_player.BASE_SPEED + random.randrange(0, 3) / 10.0
        players.Safety.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(0, 3) / 10.0
        players.Safety.base_speed2 = players.Basic_player.BASE_SPEED + random.randrange(0, 3) / 10.0
        players.Safety.base_speed3 = players.Basic_player.BASE_SPEED + random.randrange(0, 3) / 10.0
        players.STDL.base_speed = players.Basic_player.BASE_SPEED + random.randrange(0, 2) / 10.0
        players.STDL.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(0, 2) / 10.0
        players.STLB.base_speed = players.Basic_player.BASE_SPEED + random.randrange(-1, 2) / 10.0
        players.STLB.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(-1, 2) / 10.0
        players.PR.base_speed = players.Basic_player.BASE_SPEED + random.randrange(1, 3) / 10.0
        players.PR.base_speed1 = players.Basic_player.BASE_SPEED + random.randrange(1, 3) / 10.0

    def player_fatigue(self):
        classes = (players.QB, players.WR, players.RB, players.Punter,
                   players.LB, players.STLB, players.CB, players.Safety,
                   players.PR, players.DL, players.STDL, players.Center,
                   players.OL, players.STCenter, players.STOL, players.TE)
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
            w, l, t = data["names"][name]
            value = name + ": " + str(w) + "-" + str(l) + "-" + str(t) + "   "
            total = w + l + t
            if total != 0:
                string = str((float(w) / total) * 100)
                value += "(" + string[:string.index(".") + 2] + "%)"
            text = ftxt.Text(self, value, 30, ftxt.WHITE, left=left, top=top)
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
        for circle in self.circles:
            games.screen.remove(circle)

    def get_game_length(self):
        return self.game_length

    def get_sound_set(self):
        return self.sound_set

class Master(object):
    def __init__(self):
        self.joysticks = []
        self.check_joysticks()
        self.init_joysticks()
        self.start_game()
        games.screen.mainloop()

    def check_joysticks(self):
        if pygame.joystick.get_count() < 2:
            text = ftxt.Joystick_check(self, 2)
            games.screen.add(text)
            games.screen.mainloop()
            if pygame.joystick.get_count() == 0:  # if no joysticks user wants
                sys.exit(1)                       # to exit

    def init_joysticks(self):
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            jstick = pygame.joystick.Joystick(i)
            jstick.init()
            self.joysticks.append(jstick)

    def start_game(self):
        game = Game(self)

def main():
    master = Master()

# run program
main()
