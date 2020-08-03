# Football
# Version 4
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
games.init(screen_width=1020, screen_height=700, fps=50)

# import other modules
import math, random, football_text as ftxt, football_players as fplayers
# football_text is a module specially designed for this game. It has all of the
# text and message objects needed for this game.

# class definitions
class Bar(games.Sprite):
    def __init__(self, game):
        super(Bar, self).__init__(image=games.load_image("images\\bar.bmp", False),
                                  right=0, y=games.screen.height - 30)
        self.game = game

        self.game.do_not_destroy.append(self) # add self to do_not_destroy list
        self.game.non_activated_sprites.append(self)

class Field(games.Sprite):
    """ The football field """
    def __init__(self, game):
        """ Initializes object """
        self.game = game
        super(Field, self).__init__(image=games.load_image("images\\football_field.bmp", False),
                                    x=games.screen.width/2,
                                    y=games.screen.height/2,
                                    is_collideable=False)

        self.timer = 150

        self.game.do_not_destroy.append(self)  # add self to do_not_destroy list

    def update(self):
        if self.game.play_status == 1:
            self.timer -= 1
            if self.timer == 0:
                self.timer = 150
                if not self.game.sBoard.game_is_over():
                    self.game.pick_play()

        elif self.game.play_status != 0:
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
                if self.game.quarter == 5:
                    self.game.end_game()
                else:
                    message = ftxt.Football_message(game = self.game,
                                                    x = games.screen.width / 2,
                                                    y = games.screen.height / 2,
                                                    value = "Touchdown!")
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
                if self.game.quarter == 5:
                    self.game.end_game()
                else:
                    message = ftxt.Football_message(game = self.game,
                                                    x = games.screen.width / 2,
                                                    y = games.screen.height / 2,
                                                    value = "Safety!")
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
                if self.game.quarter == 5:
                    self.game.end_game()
                else:
                    message = ftxt.Football_message(game = self.game,
                                                    x = games.screen.width / 2,
                                                    y = games.screen.height / 2,
                                                    value = "Touchdown!")
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

class Scoreboard(object):
    """ The scoreboard """
    def __init__(self, game):
        """ Put all of the scoreboard items on the screen """
        self.game = game

        # put the background on the screen
        self.background = games.Sprite(
            image=games.load_image("images\\scoreboard_background.bmp", transparent=False),
            left=0, top=0, is_collideable=False)
        games.screen.add(self.background)

        self.game.non_activated_sprites.append(self.background)
        self.game.do_not_destroy.append(self.background)

        # put the score on the screen
        self.score = ftxt.Score(game=self.game)
        games.screen.add(self.score)

        # put the number of downs on the screen
        self.downs_text = ftxt.Downs_text(game=self.game)
        games.screen.add(self.downs_text)

        # put the game clock on the screen
        self.game_clock = ftxt.Game_clock(game=self.game,
                                          length=self.game.get_game_length())
        games.screen.add(self.game_clock)

        # put the quarter on the screen
        self.quarter_text = ftxt.Quarter_text(game = self.game)
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
        text = ftxt.Play_clock(game=self.game, top=self.game_clock.bottom + 10)
        games.screen.add(text)

    def update_downs(self):
        self.downs_text.update_downs()

    def update_score(self):
        self.score.update_score()

    def update_quarter(self):
        self.quarter_text.update_value()

class Game(object):
    """ The game """
    def __init__(self):
        self.game_length = 60
        self.sound_set = True
        self.teams = ("Colts", "Packers", "Patriots", "Titans")

    def set_variables(self):
        self.team1 = ""
        self.team2 = ""
        self.team1_score = 0
        self.team2_score = 0
        self.team1_offence = True
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
        self.qb = None
        self.rb1 = None
        self.rb2 = None
        self.wr1 = None
        self.wr2 = None
        self.punter = None

    def pick_teams(self):
        """ Display text objects so that players can pick their teams """
        # clear the screen of other sprites
        games.screen.clear()

        # add text sprites to get the teams the players want to be
        self.set_text = ftxt.Settings_text(game=self, value="Settings",
                                           size=30, color1=ftxt.WHITE,
                                           color2=ftxt.GRAY,
                                           right=games.screen.width - 10,
                                           top=10)
        games.screen.add(self.set_text)

        self.ask_text = ftxt.Ask_text(game=self, value="Player 1, what team do you want?",
                                    size=30, color=ftxt.YELLOW, left=10, top=10)
        games.screen.add(self.ask_text)

        top = 40
        for value in self.teams:
            text = ftxt.Change_text(game=self, value=value,
                                    size=25, color1=ftxt.WHITE,
                                    color2=self.ask_text.get_color(),
                                    color_func2=self.ask_text.get_color,
                                    left=10, top=top)
            games.screen.add(text)

            top = 10 + text.bottom

        self.exit_text = ftxt.Game_exit(game=self)
        games.screen.add(self.exit_text)

    def start(self):
        """ Puts the field on the screen """        
        # clear the screen of other sprites
        games.screen.clear()

        self.reset_base_speeds()
        
        # put the field on the screen
        self.field = Field(game=self)
        games.screen.add(self.field)

        self.sBoard = Scoreboard(game=self)

        self.bar = Bar(game=self)
        games.screen.add(self.bar)

        self.pick_play()

    def pick_play(self):
        for sprite in games.screen.all_objects:
            if sprite not in self.do_not_destroy:
                sprite.destroy()
        self.players = []
        self.o_players = []
        self.d_players = []
        self.can_not_catch = []
        self.blitz = 0
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
        self.bar.right = 0

        # adjust the field on the screen
        self.field.x = games.screen.width / 2
        self.field.bottom = (games.screen.height * 3 / 4) + self.line_of_scrimmage + 360

        text = ftxt.Play_text(game = self)
        games.screen.add(text)

        text = ftxt.Play_clock(game = self, top = self.sBoard.game_clock.bottom + 10)
        games.screen.add(text)

    def new_play(self):
        """ Puts all of the football players on the screen for a new play """
        self.ball_incomplete = False

        # --- put the players on the screen ---
        if self.play_num == 0:
            self.field.y -= 150
            # center tackle
            self.ctackle = fplayers.STTackle(game=self, x=games.screen.width / 2,
                                  y=games.screen.height * 3 / 4 - 170, side="c")
            games.screen.add(self.ctackle)
            # left tackle 1
            self.ltackle = fplayers.STTackle(game=self, x=games.screen.width / 2 + 40,
                                    y=games.screen.height * 3 / 4 - 170, side="l")
            games.screen.add(self.ltackle)
            # right tackle 1
            self.rtackle = fplayers.STTackle(game=self, x=games.screen.width / 2 - 40,
                                    y=games.screen.height * 3 / 4 - 170, side="r")
            games.screen.add(self.rtackle)
            # punt returner
            self.pr = fplayers.PR(game=self, x=games.screen.width / 2,
                         y=self.field.top + 400)
            games.screen.add(self.pr)

            # center
            self.center = fplayers.STCenter(game = self, x = games.screen.width / 2,
                                   y = games.screen.height * 3 / 4 - 150)
            games.screen.add(self.center)
            # left guard 1
            self.lol = fplayers.STOL(game=self, x=games.screen.width / 2 - 40,
                                  y=games.screen.height * 3 / 4 - 150, side="l")
            games.screen.add(self.lol)
            # right guard 1
            self.rol = fplayers.STOL(game=self, x=games.screen.width / 2 + 40,
                                  y=games.screen.height * 3 / 4 - 150, side="r")
            games.screen.add(self.rol)
            # punter
            self.punter = fplayers.Punter(game=self, x=games.screen.width / 2,
                                 y=games.screen.height * 3 / 4 + 50)
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
            self.ltackle = fplayers.Tackle(game=self, x=games.screen.width / 2 + 40,
                                  y =games.screen.height * 3 / 4 - 20, side="l")
            games.screen.add(self.ltackle)
            # left tackle 2
            self.lltackle = fplayers.Tackle(game=self, x=games.screen.width / 2 + 80,
                                  y=games.screen.height * 3 / 4 - 20, side="ll")
            games.screen.add(self.lltackle)
            # right tackle 1
            self.rtackle = fplayers.Tackle(game=self, x=games.screen.width / 2 - 40,
                                  y=games.screen.height * 3 / 4 - 20, side="r")
            games.screen.add(self.rtackle)
            # right tackle 2
            self.rrtackle = fplayers.Tackle(game=self, x=games.screen.width / 2 - 80,
                                  y=games.screen.height * 3 / 4 - 20, side="rr")
            games.screen.add(self.rrtackle)
            # right tackle 3
            self.rrrtackle = fplayers.Tackle(game = self, x = games.screen.width / 2 - 120,
                                y = games.screen.height * 3 / 4 - 20, side = "rrr")
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
            self.llol = fplayers.OL(game = self, x = games.screen.width / 2 - 80,
                                 y = games.screen.height * 3 / 4, side = "ll")
            games.screen.add(self.llol)
            # quarterback
            self.qb = fplayers.QB(game = self, x = games.screen.width / 2,
                    y = games.screen.height * 3 / 4 + 50)
            games.screen.add(self.qb)
            # runningback
            self.rb1 = fplayers.RB(game = self, x = games.screen.width / 2,
                         y = games.screen.height - 6, num="1")
            games.screen.add(self.rb1)
            # runningback 1
            self.rb2 = fplayers.RB(game = self, x = games.screen.width / 2,
                         y = games.screen.height + 40, num="2")
            games.screen.add(self.rb2)
            # right wide recicver
            self.wr2 = fplayers.WR(game = self, x = games.screen.width * 3 / 4,
                          y = games.screen.height * 3 / 4, side="r")
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
            self.ltackle = fplayers.Tackle(game = self, x = games.screen.width / 2 + 40,
                                  y = games.screen.height * 3 / 4 - 20, side = "l")
            games.screen.add(self.ltackle)
            # left tackle 2
            self.lltackle = fplayers.Tackle(game = self, x = games.screen.width / 2 + 80,
                                  y = games.screen.height * 3 / 4 - 20, side = "ll")
            games.screen.add(self.lltackle)
            # right tackle 1
            self.rtackle = fplayers.Tackle(game = self, x = games.screen.width / 2 - 40,
                                  y = games.screen.height * 3 / 4 - 20, side = "r")
            games.screen.add(self.rtackle)
            # right tackle 2
            self.rrtackle = fplayers.Tackle(game = self, x = games.screen.width / 2 - 80,
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
            # quarterback
            self.qb = fplayers.QB(game = self, x = games.screen.width / 2,
                    y = games.screen.height * 3 / 4 + 50)
            games.screen.add(self.qb)
            # runningback
            self.rb1 = fplayers.RB(game = self, x = games.screen.width / 2,
                         y = games.screen.height - 6, num="1")
            games.screen.add(self.rb1)
            # left wide recicver
            self.wr1 = fplayers.WR(game = self, x = games.screen.width / 4,
                          y = games.screen.height * 3 / 4, side="l")
            games.screen.add(self.wr1)
            # right wide recicver
            self.wr2 = fplayers.WR(game = self, x = games.screen.width * 3 / 4,
                          y = games.screen.height * 3 / 4, side="r")
            games.screen.add(self.wr2)

        # elevate bar sprite and scoreboard sprites above all other sprites
        self.bar.elevate()
        self.sBoard.elevate()

    def change_offence(self):
        """ Changes the team that is on offence """
        self.team1_offence = not self.team1_offence

    def change_quarter(self):
        if self.quarter < 4:
            self.sBoard.reset_clock()
        elif self.quarter == 4:
            if self.team1_score == self.team2_score:
                self.sBoard.reset_clock()
            else:
                self.quarter += 1
        self.quarter += 1
        self.sBoard.update_quarter()

    def penalize(self, yards, string):
        """ Moves penalized team 'yards' back and displays a message object
        with the value of 'string' """
        self.remove_players()
        self.sBoard.stop_clock()
        self.play_status = 1
        self.line_of_scrimmage -= 36 * yards
        self.for_first_down += 36 * yards
        message = ftxt.Football_message(game = self, value = string,
                                        x = games.screen.width / 2,
                                        y = games.screen.height / 2)
        games.screen.add(message)

    def end_game(self):
        """ Method evoked at the end of the game """
        for sprite in games.screen.all_objects:
            if sprite not in self.do_not_destroy:
                sprite.destroy()

        # adjust the bar on the screen
        self.bar.right = 0

        # adjust the field on the screen
        self.field.x = games.screen.width / 2
        self.field.y = games.screen.height / 2

        if self.team1_score > self.team2_score:
            string = "The " + self.team1 + " win!"
        elif self.team2_score > self.team1_score:
            string = "The " + self.team2 + " win!"
        else:
            string = "Tie!"

        text = ftxt.Text(game = self, value = string, size = 100,
                    color = ftxt.RED, x = games.screen.width / 2,
                    y = games.screen.height / 2)
        games.screen.add(text)

        text = ftxt.Play_again_text(game = self, x = games.screen.width / 2,
                                    bottom = games.screen.height - 10)
        games.screen.add(text)

    def reset_base_speeds(self):
        fplayers.QB.base_speed = 5 + random.randrange(0, 2) / 10.0
        fplayers.QB.base_speed1 = 5 + random.randrange(0, 2) / 10.0
        fplayers.WR.base_speed = 5 + random.randrange(0, 3) / 10.0
        fplayers.WR.base_speed1 = 5 + random.randrange(0, 3) / 10.0
        fplayers.RB.base_speed = 5.1 + random.randrange(0, 2) / 10.0
        fplayers.RB.base_speed1 = 5.1 + random.randrange(0, 2) / 10.0
        fplayers.Center.base_speed = 5 + random.randrange(-3, 1) / 10.0
        fplayers.Center.base_speed1 = 5 + random.randrange(-3, 1) / 10.0
        fplayers.Center.block = 3 + random.randrange(0, 3)
        fplayers.Center.block1 = 3 + random.randrange(0, 3)
        fplayers.OL.base_speed = 5 + random.randrange(-3, 1) / 10.0
        fplayers.OL.base_speed1 = 5 + random.randrange(-3, 1) / 10.0
        fplayers.OL.block = 3 + random.randrange(0, 3)
        fplayers.OL.block1 = 3 + random.randrange(0, 3)
        fplayers.Punter.base_speed = 5 + random.randrange(0, 2) / 10.0
        fplayers.Punter.base_speed1 = 5 + random.randrange(0, 2) / 10.0
        fplayers.STCenter.base_speed = 5 + random.randrange(0, 3) / 10.0
        fplayers.STCenter.base_speed1 = 5 + random.randrange(0, 3) / 10.0
        fplayers.STCenter.block = 3 + random.randrange(0, 3)
        fplayers.STCenter.block1 = 3 + random.randrange(0, 3)
        fplayers.STOL.base_speed = 5 + random.randrange(0, 3) / 10.0
        fplayers.STOL.base_speed1 = 5 + random.randrange(0, 3) / 10.0
        fplayers.STOL.block = 3 + random.randrange(0, 3)
        fplayers.STOL.block1 = 3 + random.randrange(0, 3)
        fplayers.Noseguard.base_speed = 5 + random.randrange(-3, 1) / 10.0
        fplayers.Noseguard.base_speed1 = 5 + random.randrange(-3, 1) / 10.0
        fplayers.Tackle.base_speed = 5 + random.randrange(-3, 1) / 10.0
        fplayers.Tackle.base_speed1 = 5 + random.randrange(-3, 1) / 10.0
        fplayers.LB.base_speed = 5 + random.randrange(-1, 2) / 10.0
        fplayers.LB.base_speed1 = 5 + random.randrange(-1, 2) / 10.0
        fplayers.CB.base_speed = 5 + random.randrange(0, 3) / 10.0
        fplayers.CB.base_speed1 = 5 + random.randrange(0, 3) / 10.0
        fplayers.Safety.base_speed = 5 + random.randrange(0, 3) / 10.0
        fplayers.Safety.base_speed1 = 5 + random.randrange(0, 3) / 10.0
        fplayers.Safety.base_speed2 = 5 + random.randrange(0, 3) / 10.0
        fplayers.Safety.base_speed3 = 5 + random.randrange(0, 3) / 10.0
        fplayers.STTackle.base_speed = 5 + random.randrange(-3, 1) / 10.0
        fplayers.STTackle.base_speed1 = 5 + random.randrange(-3, 1) / 10.0
        fplayers.PR.base_speed = 5.1 + random.randrange(0, 2) / 10.0
        fplayers.PR.base_speed1 = 5.1 + random.randrange(0, 2) / 10.0

    def show_settings(self):
        games.screen.clear()

        self.c_settings = ftxt.Clock_settings(self, self.game_length)
        games.screen.add(self.c_settings)

        self.s_settings = ftxt.Sound_settings(self, self.sound_set)
        games.screen.add(self.s_settings)

        text = ftxt.Settings_exit(game = self)
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
    football.set_variables()
    football.pick_teams()
    games.screen.mainloop()

# run program
main()
