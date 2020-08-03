# Football
#
# A football game for two players. The player on offence controls the
# quarterback first, and then the player who catches the ball. The defence is
# controlled by the computer.
#
# To do:
#
# 1. take out variable ball_incomplete
# 2. make players return to their position after play is over
# 3. move list of plays to Game object
# 4. see if QB.five_pressed can be deleted
#
# Note: Noseguard movement problem might be in Basic_defence

# imports
from livewires import games
import math, random
import football_text as ftxt

# initialize screen
games.init(screen_width = 1020, screen_height = 706, fps = 50)

class Adjuster(games.Sprite):
    """ Moves object to make it look like activated object is moving """
    def update(self):
        """ Moves sprite """
        for sprite in games.screen.get_all_objects():
            if sprite not in self.game.non_activated_sprites:
                if sprite.is_activated:
                    self.x -= sprite.x_change
                    self.y -= sprite.y_change                    

class Adjuster1(games.Animation):
    """ Does the same thing as Adjuster only for Animation objects """
    def update(self):
        """ Moves sprite """
        for sprite in games.screen.get_all_objects():
            if sprite not in self.game.non_activated_sprites:
                if sprite.is_activated:
                    self.x -= sprite.x_change
                    self.y -= sprite.y_change

class Basic_player(Adjuster1):
    def turn(self, angle):
        """ Rotate sprite """
        self.angle += angle
        for player in self.game.players:
            if self.overlaps(player) and player != self:
                if player.top < self.top < player.bottom:
                    self.top = player.bottom
                if player.bottom > self.bottom > player.top:
                    self.bottom = player.top
                if player.right > self.right > player.left:
                    self.right = player.left
                if player.left < self.left < player.right:
                    self.left = player.right

    def adjust(self):
        """ Calculate sprites x_change and y_change """
        self.x_change = self.speed * math.sin(math.radians(self.angle))
        self.y_change = self.speed * -math.cos(math.radians(self.angle))
        if self.direction == "-":
            self.x_change = -self.x_change
            self.y_change = -self.y_change

        # set image
        if self.has_ball:
            if self.get_image() not in self.running_i:
                self.images = self.running_i
        else:
            if self.get_image() not in self.running_i2:
                self.images = self.running_i2

    def move(self):
        """ Moves sprite """
        if self.direction == "+":
            self.x += self.speed * math.sin(math.radians(self.angle))
            self.y += self.speed * -math.cos(math.radians(self.angle))
        else:
            self.x -= self.speed * math.sin(math.radians(self.angle))
            self.y -= self.speed * -math.cos(math.radians(self.angle))

        # set image
        if self.has_ball:
            if self.get_image() not in self.running_i:
                self.images = self.running_i
        else:
            if self.get_image() not in self.running_i2:
                self.images = self.running_i2

        self.do_not_overlap()

    def slide(self, amount):
        """ Moves sprite to the left or right """
        self.x += amount * math.sin(math.radians(self.angle - 90))
        self.y += amount * -math.cos(math.radians(self.angle - 90))

class Basic_offence(Basic_player):
    """ Basic moves for an offincive player """
    def update(self):
        """
        If the player has control of the sprite, this class will allow the
        player to rotate the sprite, to move the sprite forward and backward,
        and to allow the player to set the speed at which the sprite moves.
        If the sprite is moving, it does not allow the sprite to overlap any
        other football player sprites.
        """
        if not self.game.is_paused:
            if self.game.play_is_running:
                # convert self.angle to radians                
                self.r_angle = self.angle * math.pi / 180
                
                # --- allow sprite to move based on keys pressed if activated ---
                
                if self.is_activated:
                    # rotate sprite based on keys pressed
                    if games.keyboard.is_pressed(games.K_RIGHT):
                        self.turn(3)

                    if games.keyboard.is_pressed(games.K_LEFT):
                        self.turn(-3)

                    # sets sprite's speed based on keys pressed
                    if games.keyboard.is_pressed(games.K_RALT) or games.keyboard.is_pressed(games.K_LALT):
                        self.speed = self.speed_r
                        self.set_interval(9)
                    else:
                        self.speed = self.speed_w
                        self.set_interval(14)

                    # --- make sprite move based on keys pressed ---

                    # make sprite move in the direction it is pointing
                    if games.keyboard.is_pressed(games.K_UP):
                        self.direction = "+"
                        self.adjust()

                    # make sprite move in the opposite direction it is pointing
                    if games.keyboard.is_pressed(games.K_DOWN):
                        self.direction = "-"
                        self.adjust()

                    # sets sprite's x_change and y_change to 0 if sprite is not moving
                    if not games.keyboard.is_pressed(games.K_UP) and not games.keyboard.is_pressed(games.K_DOWN) and not games.keyboard.is_pressed(games.K_m):
                        self.x_change = 0
                        self.y_change = 0
                        # set image
                        if self.get_image() not in self.standing_i:
                            self.images = self.standing_i

                else:
                    # move sprite
                    self.move()

                    # get Adjuster1's update method
                    super(Basic_offence, self).update()

    def do_not_overlap(self):
        """ Do not allow sprite to overlap another football player """
        for player in self.game.players:
            if self.overlaps(player) and player != self:
                if player.has_ball and player in self.game.d_players:
                    self.tackle(player)

                else:
                    if self.direction == "-":
                        self.x += self.speed * math.sin(math.radians(self.angle))
                        self.y += self.speed * -math.cos(math.radians(self.angle))
                    else:
                        self.x -= self.speed * math.sin(math.radians(self.angle))
                        self.y -= self.speed * -math.cos(math.radians(self.angle))

    def tackle(self, player):
        self.game.line_of_scrimmage = self.game.field.bottom - player.y - 360
        self.game.play_is_running = False
        self.game.play_is_over = True
        self.is_activated = False
        player.x_change = 0
        player.y_change = 0
        self.x_change = 0
        self.y_change = 0
        player.images = player.tackled_i
        self.images = self.tackled_i

class Basic_defense(Basic_player):
    def update(self):
        if not self.game.is_paused:
            if self.game.play_is_running:
                if not self.is_activated:
                    self.move()

                    # get Adjuster1's update method
                    super(Basic_defense, self).update()

    def do_not_overlap(self):
        for player in self.game.players:
            if self.overlaps(player) and player != self:
                if player.has_ball and player in self.game.o_players:
                    self.tackle(player)

                else:
                    if self.direction == "-":
                        self.x += self.speed * math.sin(math.radians(self.angle))
                        self.y += self.speed * -math.cos(math.radians(self.angle))
                    else:
                        self.x -= self.speed * math.sin(math.radians(self.angle))
                        self.y -= self.speed * -math.cos(math.radians(self.angle))

    def tackle(self, player):
        self.game.for_first_down -= self.game.field.bottom - self.game.line_of_scrimmage - 360 - player.y
        self.game.line_of_scrimmage = self.game.field.bottom - player.y - 360
        self.game.play_is_running = False
        self.game.play_is_over = True
        player.is_activated = False
        player.x_change = 0
        player.y_change = 0
        player.images = player.tackled_i
        self.images = self.tackled_i

class Bar(games.Sprite):
    def __init__(self, game):
        super(Bar, self).__init__(image = games.load_image("bar2.bmp",
                                                           transparent = False),
                                  right = 0, y = games.screen.height - 30)
        self.game = game

        self.game.do_not_destroy.append(self) # add self to do_not_destroy list

class Field(Adjuster):
    """ The football field """
    def __init__(self, game):
        """ Initializes object """
        self.game = game
        super(Field, self).__init__(image = games.load_image("football_field.bmp", transparent = False),
                                    x = games.screen.width/2,
                                    y = games.screen.height/2)

        self.is_activated = False
        self.timer = 150

        self.game.do_not_destroy.append(self) # add self to do_not_destroy list

    def update(self):
        if not self.game.is_paused:
            super(Field, self).update()

        if self.game.game_clock.minutes == 0 and self.game.game_clock.seconds == 0 and self.game.quarter_text > 4 and not self.game.play_is_running:
            self.game.play_is_over = True
            self.game.center.can_snap = False

        if self.game.play_is_over:
            self.timer -= 1
            if self.timer == 0:
                self.game.play_is_over = False
                self.game.play_is_running = False
                self.timer = 150
                if self.game.game_clock.minutes == 0 and self.game.game_clock.seconds == 0 and self.game.quarter_text > 4:
                    self.game.end_game()
                else:
                    self.game.pick_play()

        else:
            for sprite in self.game.o_players:
                if sprite.top < self.top + 360 and sprite.has_ball:
                    self.game.line_of_scrimmage = 1083
                    self.for_first_down = 360
                    self.game.play_is_over = True
                    self.game.play_is_running = False
                    sprite.speed = 0
                    if self.game.team1_offence:
                        self.game.team1_score += 6
                    else:
                        self.game.team2_score += 6
                    self.game.score.update_score()
                    self.game.down = 0
                    self.game.game_clock.stop()
                    self.game.change_offence()

            for sprite in self.game.d_players:
                if sprite.bottom > self.bottom - 360 and sprite.has_ball:
                    self.game.line_of_scrimmage = 1083
                    self.game.play_is_over = True
                    self.game.play_is_running = False
                    sprite.speed = 0
                    if self.game.team1_offence:
                        self.game.team2_score += 6
                    else:
                        self.game.team1_score += 6
                    self.game.score.update_score()
                    self.game.down = 0
                    self.game.game_clock.stop()

class Football(games.Animation):
    """ The football """
    def __init__(self, play, game, x, y, angle):
        """ Initializes object """
        self.game = game
        self.play = play
        self.loop = True
        if self.play == "pass":
            images = ["football1.bmp",
                      "football2.bmp",
                      "football3.bmp",
                      "football3.bmp",
                      "football4.bmp"]
            self.is_activated = True
            self.to_go = self.game.bar.right * 3
            
        elif self.play == "hike":
            images = ["football1.bmp"]
            self.is_activated = False
            self.game.play_is_running = True
            self.game.game_clock.start()
            
        super(Football, self).__init__(images = images, x = x, y = y,
                                       angle = angle, repeat_interval = 2,
                                       n_repeats = 0)

        angle_r = angle * math.pi / 180
        self.x_change = 7 * math.sin(angle_r)
        self.y_change = 7 * -math.cos(angle_r)

    def update(self):
        if not self.game.is_paused:
            if self.loop:
                if self.play == "pass":
                    self.to_go -= 7
                    if self.to_go <= 0:
                        self.x_change = 0
                        self.y_change = 0
                        self.game.ball_incomplete = True
                        self.game.play_is_running = False
                        self.game.play_is_over = True
                        self.loop = False
                        self.images = [games.load_image("football1.bmp")]
                        self.game.game_clock.stop()

                    # check to see if self overlaps a football player
                    if not self.game.ball_incomplete:
                        for sprite in self.overlapping_sprites:
                            if sprite in self.game.players and sprite != self.game.qb and sprite not in self.game.can_not_catch:
                                sprite.is_activated = True
                                sprite.has_ball = True
                                self.destroy()

                elif self.play == "hike":
                    self.x += self.x_change
                    self.y += self.y_change
                    for sprite in self.overlapping_sprites:
                        if sprite in self.game.players and sprite != self.game.center:
                            sprite.is_activated = True
                            sprite.has_ball = True
                            self.destroy()
                

class QB(Basic_offence):
    """ The quarterback """
    SPEED = 5 + random.randrange(0, 2) / 10.0
    SPEED2 = 5 + random.randrange(0, 2) / 10.0
    
    def __init__(self, game, x, y):
        """ Initializes object """
        self.game = game
        if self.game.team1_offence:
            if self.game.team1 == "Titans":
                # animation lists
                self.standing_i = [games.load_image("titans_qb_h.bmp")]
                self.standing_i2 = [games.load_image("titans_qb_h(wb).bmp")]
                self.running_i = [games.load_image("titans_qb_h_r1.bmp"),
                                  games.load_image("titans_qb_h.bmp"),
                                  games.load_image("titans_qb_h_r2.bmp"),
                                  games.load_image("titans_qb_h.bmp")]
                self.running_i2 = [games.load_image("titans_qb_h_r1(wb).bmp"),
                                      games.load_image("titans_qb_h(wb).bmp"),
                                      games.load_image("titans_qb_h_r2(wb).bmp"),
                                      games.load_image("titans_qb_h(wb).bmp")]
                self.throwing_i = [games.load_image("titans_qb_h_th2.bmp")]
                self.tackled_i = [games.load_image("titans_qb_h_t1.bmp")]
            elif self.game.team1 == "Colts":
                # animation lists
                self.standing_i = [games.load_image("colts_qb_h.bmp")]
                self.standing_i2 = [games.load_image("colts_qb_h(wb).bmp")]
                self.running_i = [games.load_image("colts_qb_h_r1.bmp"),
                                  games.load_image("colts_qb_h.bmp"),
                                  games.load_image("colts_qb_h_r2.bmp"),
                                  games.load_image("colts_qb_h.bmp")]
                self.running_i2 = [games.load_image("colts_qb_h_r1(wb).bmp"),
                                      games.load_image("colts_qb_h(wb).bmp"),
                                      games.load_image("colts_qb_h_r2(wb).bmp"),
                                      games.load_image("colts_qb_h(wb).bmp")]
                self.throwing_i = [games.load_image("colts_qb_h_th2.bmp")]
                self.tackled_i = [games.load_image("colts_qb_h_t1.bmp")]
            elif self.game.team1 == "Patriots":
                # animation lists
                self.standing_i = [games.load_image("patriots_qb_h.bmp")]
                self.standing_i2 = [games.load_image("patriots_qb_h(wb).bmp")]
                self.running_i = [games.load_image("patriots_qb_h_r1.bmp"),
                                  games.load_image("patriots_qb_h.bmp"),
                                  games.load_image("patriots_qb_h_r2.bmp"),
                                  games.load_image("patriots_qb_h.bmp")]
                self.running_i2 = [games.load_image("patriots_qb_h_r1(wb).bmp"),
                                  games.load_image("patriots_qb_h(wb).bmp"),
                                  games.load_image("patriots_qb_h_r2(wb).bmp"),
                                  games.load_image("patriots_qb_h(wb).bmp")]
                self.throwing_i = [games.load_image("patriots_qb_h_th2.bmp")]
                self.tackled_i = [games.load_image("patriots_qb_h_t1.bmp")]
        else:
            if self.game.team2 == "Titans":
                self.standing_i = [games.load_image("titans_qb_a(wb).bmp")]
                self.standing_i2 = [games.load_image("titans_qb_a(wb).bmp")]
                self.running_i = [games.load_image("titans_qb_a(wb).bmp")]
                self.running_i2 = [games.load_image("titans_qb_a(wb).bmp")]
                self.throwing_i = [games.load_image("titans_qb_a(wb).bmp")]
                self.tackled_i = [games.load_image("titans_qb_a_t1.bmp")]
            elif self.game.team2 == "Colts":
                image = games.load_image("colts_qb_h.bmp")
            elif self.game.team2 == "Patriots":
                image = games.load_image("patriots_qb_h.bmp")
        
        super(QB, self).__init__(images = self.standing_i2,
                                 x = x, y = y, repeat_interval = 9,
                                 n_repeats = 0)

        self.game.players.append(self) # add self to list of all players
        self.game.o_players.append(self) # add self to list of offencive players
        
        self.is_activated = False
        self.has_ball = False
        self.five_pressed = False
        self.x_change = 0
        self.y_change = 0
        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = QB.SPEED / 2
            self.speed_r = QB.SPEED
        else:
            self.speed_w = QB.SPEED2 / 2
            self.speed_r = QB.SPEED2
        self.direction = "+"

    def update(self):
        if not self.game.is_paused:
            if self.is_activated:
                if self.five_pressed:
                    if not self.has_ball:
                        self.standing_i = self.standing_i2
                        self.running_i = self.running_i2
                    self.five_pressed = False

                if games.keyboard.is_pressed(games.K_SPACE) and self.game.bar.left < 0:
                    self.game.bar.x += 5
                if games.keyboard.is_pressed(games.K_KP7) or games.keyboard.is_pressed(games.K_KP9):
                    self.game.bar.right = 0

                # makes quarterback throw the football
                if games.keyboard.is_pressed(games.K_m) and self.has_ball:
                    self.images = self.throwing_i
                    self.is_activated = False
                    self.football = Football(game = self.game, play = "pass",
                        x = 10 * math.sin((self.angle + 90) * math.pi / 180) + self.x,
                        y = 10 * -math.cos((self.angle + 90) * math.pi / 180) + self.y,
                        angle = self.angle)
                    games.screen.add(self.football)
                    self.has_ball = False
                    self.five_pressed = True

            else:
                self.game.bar.right = 0

        super(QB, self).update()

class WR(Basic_offence):
    """ A wide receiver """
    SPEED = 5 + random.randrange(0, 3) / 10.0
    SPEED2 = 5 + random.randrange(0, 3) / 10.0
    
    def __init__(self, game, x, y):
        """ Initializes object """
        self.game = game
        if self.game.team1_offence:
            if self.game.team1 == "Titans":
                # animation lists
                self.standing_i = [games.load_image("titans_wr_h.bmp")]
                self.standing_i2 = [games.load_image("titans_wr_h(wb).bmp")]
                self.running_i = [games.load_image("titans_wr_h_r1.bmp"),
                                  games.load_image("titans_wr_h.bmp"),
                                  games.load_image("titans_wr_h_r2.bmp"),
                                  games.load_image("titans_wr_h.bmp")]
                self.running_i2 = [games.load_image("titans_wr_h_r1(wb).bmp"),
                                   games.load_image("titans_wr_h(wb).bmp"),
                                   games.load_image("titans_wr_h_r2(wb).bmp"),
                                   games.load_image("titans_wr_h(wb).bmp")]
                if not random.randrange(2):
                    self.tackled_i = [games.load_image("titans_wr_h_t1.bmp")]
                else:
                    self.tackled_i = [games.load_image("titans_wr_h_t2.bmp")]
            elif self.game.team1 == "Colts":
                # animation lists
                self.standing_i = [games.load_image("colts_wr_h(wb).bmp")]
                self.standing_i2 = [games.load_image("colts_wr_h(wb).bmp")]
                self.running_i = [games.load_image("colts_wr_h(wb).bmp")]
                self.running_i2 = [games.load_image("colts_wr_h(wb).bmp")]
                if not random.randrange(2):
                    self.tackled_i = [games.load_image("colts_wr_h_t1.bmp")]
                else:
                    self.tackled_i = [games.load_image("colts_wr_h_t2.bmp")]
            elif self.game.team1 == "Patriots":
                # animation lists
                self.standing_i = [games.load_image("patriots_wr_h(wb).bmp")]
                self.standing_i2 = [games.load_image("patriots_wr_h(wb).bmp")]
                self.running_i = [games.load_image("patriots_wr_h(wb).bmp")]
                self.running_i2 = [games.load_image("patriots_wr_h(wb).bmp")]
                self.tackled_i = []

        else:
            if self.game.team2 == "Titans":
                # animation lists
                self.standing_i = [games.load_image("titans_wr_a(wb).bmp")]
                self.standing_i2 = [games.load_image("titans_wr_a(wb).bmp")]
                self.running_i = [games.load_image("titans_wr_a(wb).bmp")]
                self.running_i2 = [games.load_image("titans_wr_a(wb).bmp")]
                self.tackled_i = [games.load_image("titans_wr_a_t1.bmp")]

        super(WR, self).__init__(images = self.standing_i2,
                                 x = x, y = y, repeat_interval = 9,
                                 n_repeats = 0)

        self.game.players.append(self) # add self to list of all players
        self.game.o_players.append(self) # add self to list of offencive players

        self.is_activated = False
        self.has_ball = False
        self.x_change = 0
        self.y_change = 0
        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = WR.SPEED / 2
            self.speed_r = WR.SPEED
        else:
            self.speed_w = WR.SPEED2 / 2
            self.speed_r = WR.SPEED2
        self.direction = "+"
        if self.x < self.game.qb.x:
            self.side = "l"
        else:
            self.side = "r"

    def update(self):        
        if not self.game.is_paused:
            if not self.is_activated:
                if self.game.play_is_running:
                    #-------------------- plays --------------------
                    if self.game.play_num == 0:
                        self.speed = self.speed_r

                    elif self.game.play_num == 1:
                        self.speed = self.speed_r
                        if self.side == "l":
                            self.angle = 40
                        else:
                            self.angle = 310

                    elif self.game.play_num == 2:
                        self.speed = self.speed_r
                        if self.side == "l":
                            if self.angle < 90:
                                self.angle += 2
                            else:
                                self.angle = 90
                        else:
                            if self.angle > 270 or self.angle == 0:
                                self.angle -= 2
                            else:
                                self.angle = 270

                    elif self.game.play_num == 3:
                        self.speed = self.speed_r
                        if self.side == "r":
                            if self.angle > 270 or self.angle == 0:
                                self.angle -= 2
                            else:
                                self.angle = 270
                    #-----------------------------------------------

        # get Basic_offence's update method
        super(WR, self).update()

class Center(Basic_offence):
    """ The center """
    SPEED = 5 + random.randrange(-3, 1) / 10.0
    SPEED2 = 5 + random.randrange(-3, 1) / 10.0
    
    def __init__(self, game, x, y):
        """ Initializes object """
        self.game = game
        if self.game.team1_offence:
            if self.game.team1 == "Titans":
                # animation lists
                self.standing_i = [games.load_image("titans_c_h(wb).bmp")]
                self.standing_i2 = [games.load_image("titans_c_h(wb).bmp")]
                self.running_i = [games.load_image("titans_c_h(wb).bmp")]
                self.running_i2 = [games.load_image("titans_c_h(wb).bmp")]
                self.tackled_i = []
            elif self.game.team1 == "Colts":
                # animation lists
                self.standing_i = [games.load_image("colts_c_h(wb).bmp")]
                self.standing_i2 = [games.load_image("colts_c_h(wb).bmp")]
                self.running_i = [games.load_image("colts_c_h(wb).bmp")]
                self.running_i2 = [games.load_image("colts_c_h(wb).bmp")]
                self.tackled_i = [games.load_image("colts_c_h_t1.bmp")]
            elif self.game.team1 == "Patriots":
                # animation lists
                self.standing_i = [games.load_image("patriots_c_h(wb).bmp")]
                self.standing_i2 = [games.load_image("patriots_c_h(wb).bmp")]
                self.running_i = [games.load_image("patriots_c_h(wb).bmp")]
                self.running_i2 = [games.load_image("patriots_c_h(wb).bmp")]
                self.tackled_i = []

        else:
            if self.game.team2 == "Titans":
                # animation lists
                self.standing_i = [games.load_image("titans_c_a(wb).bmp")]
                self.standing_i2 = [games.load_image("titans_c_a(wb).bmp")]
                self.running_i = [games.load_image("titans_c_a(wb).bmp")]
                self.running_i2 = [games.load_image("titans_c_a(wb).bmp")]
                self.tackled_i = []

        super(Center, self).__init__(images = self.standing_i2,
                                 x = x, y = y, repeat_interval = 9,
                                 n_repeats = 0)

        self.game.players.append(self) # add self to list of all players
        self.game.o_players.append(self) # add self to list of offencive players
        self.game.can_not_catch.append(self)

        self.is_activated = False
        self.has_ball = False
        self.x_change = 0
        self.y_change = 0
        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = Center.SPEED / 2
            self.speed_r = Center.SPEED
        else:
            self.speed_w = Center.SPEED2 / 2
            self.speed_r = Center.SPEED2
        self.direction = "+"
        self.can_snap = True

    def update(self):
        if not self.game.is_paused:
            if self.can_snap:
                if games.keyboard.is_pressed(games.K_SPACE) and not self.game.play_is_running:
                    football = Football(play = "hike", game = self.game,
                                        x = self.x, y = self.y + 10, angle = 180)
                    games.screen.add(football)
                    self.can_snap = False

            if self.game.play_is_running:
                self.speed = self.speed_r
                self.angle = 90 + math.degrees(math.atan2(self.game.noseg.y - self.y, self.game.noseg.x - self.x))
                self.move()

        super(Center, self).update()

class Noseguard(Basic_defense):
    SPEED = 5 + random.randrange(-3, 1) / 10.0
    SPEED2 = 5 + random.randrange(-3, 1) / 10.0
    
    def __init__(self, game, x, y):
        """ Initializes sprite """
        self.game = game
        if self.game.team1_offence:
            if self.game.team2 == "Titans":
                # animation lists
                self.standing_i = [games.load_image("titans_ng_a_(wb).bmp")]
                self.standing_i2 = [games.load_image("titans_ng_a_(wb).bmp")]
                self.running_i = [games.load_image("titans_ng_a_(wb).bmp")]
                self.running_i2 = [games.load_image("titans_ng_a_(wb).bmp")]
                self.tackled_i = [games.load_image("titans_ng_a_t1.bmp")]
            elif self.game.team2 == "Colts":
                # animation lists
                self.standing_i = [games.load_image("colts_ng_a_(wb).bmp")]
                self.standing_i2 = [games.load_image("colts_ng_a_(wb).bmp")]
                self.running_i = [games.load_image("colts_ng_a_(wb).bmp")]
                self.running_i2 = [games.load_image("colts_ng_a_(wb).bmp")]
                self.tackled_i = [games.load_image("colts_ng_a_t1.bmp")]
            elif self.game.team2 == "Patriots":
                # animation lists
                self.standing_i = []
                self.standing_i2 = []
                self.running_i = []
                self.running_i2 = []
                self.tackled_i = []

        else:
            if self.game.team1 == "Colts":
                # animation lists
                self.standing_i = [games.load_image("colts_ng_h(wb).bmp")]
                self.standing_i2 = [games.load_image("colts_ng_h(wb).bmp")]
                self.running_i = [games.load_image("colts_ng_h(wb).bmp")]
                self.running_i2 = [games.load_image("colts_ng_h(wb).bmp")]
                self.tackled_i = [games.load_image("colts_ng_h_t1.bmp")]
            elif self.game.team1 == "Titans":
                # animation lists
                self.standing_i = [games.load_image("titans_ng_h(wb).bmp")]
                self.standing_i2 = [games.load_image("titans_ng_h(wb).bmp")]
                self.running_i = [games.load_image("titans_ng_h(wb).bmp")]
                self.running_i2 = [games.load_image("titans_ng_h(wb).bmp")]
                self.tackled_i = [games.load_image("titans_ng_h_t1.bmp")]

        super(Noseguard, self).__init__(images = self.standing_i2, angle = 180,
                                        x = x, y = y,
                                        repeat_interval = 9, n_repeats = 0)

        self.game.players.append(self) # add self to list of all players
        self.game.d_players.append(self) # add self to list of defensive players
        self.game.can_not_catch.append(self)

        self.is_activated = False
        self.has_ball = False
        self.x_change = 0
        self.y_change = 0
        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = Noseguard.SPEED / 2
            self.speed_r = Noseguard.SPEED
        else:
            self.speed_w = Noseguard.SPEED2 / 2
            self.speed_r = Noseguard.SPEED2
        self.direction = "+"

    def update(self):
        if not self.game.is_paused:
            if not self.is_activated:
                if self.game.play_is_running:
                    if self.game.qb.has_ball:
                        self.speed = self.speed_r
                        
                        # turn sprite toward the quarterback
                        self.angle = 90 + math.degrees(math.atan2(self.game.qb.y - self.y, self.game.qb.x - self.x))    
        
                    else:
                        self.speed = 0
            
        # get Basic_defense's update method
        super(Noseguard, self).update()

class Safety(Basic_defense):
    SPEED = 5 + random.randrange(0, 3) / 10.0
    SPEED2 = 5 + random.randrange(0, 3) / 10.0

    def __init__(self, game, x, y):
        self.game = game
        if self.game.team1_offence:
            if self.game.team2 == "Titans":
                # animation lists
                self.standing_i = [games.load_image("titans_s_a_(wb).bmp")]
                self.standing_i2 = [games.load_image("titans_s_a_(wb).bmp")]
                self.running_i = [games.load_image("titans_s_a_(wb).bmp")]
                self.running_i2 = [games.load_image("titans_s_a_(wb).bmp")]
                self.tackled_i = [games.load_image("titans_s_a_t1.bmp")]
            elif self.game.team2 == "Colts":
                # animation lists
                self.standing_i = [games.load_image("colts_s_a_(wb).bmp")]
                self.standing_i2 = [games.load_image("colts_s_a_(wb).bmp")]
                self.running_i = [games.load_image("colts_s_a_(wb).bmp")]
                self.running_i2 = [games.load_image("colts_s_a_(wb).bmp")]
                self.tackled_i = [games.load_image("colts_s_a_t1.bmp")]
            elif self.game.team2 == "Patriots":
                # animation lists
                self.standing_i = []
                self.standing_i2 = []
                self.running_i = []
                self.running_i2 = []
                self.tackled_i = []

        else:
            if self.game.team1 == "Colts":
                # animation lists
                self.standing_i = [games.load_image("colts_s_h(wb).bmp")]
                self.standing_i2 = [games.load_image("colts_s_h(wb).bmp")]
                self.running_i = [games.load_image("colts_s_h(wb).bmp")]
                self.running_i2 = [games.load_image("colts_s_h(wb).bmp")]
                self.tackled_i = [games.load_image("colts_s_h_t1.bmp")]
            elif self.game.team1 == "Titans":
                # animation lists
                self.standing_i = [games.load_image("titans_s_h(wb).bmp")]
                self.standing_i2 = [games.load_image("titans_s_h(wb).bmp")]
                self.running_i = [games.load_image("titans_s_h(wb).bmp")]
                self.running_i2 = [games.load_image("titans_s_h(wb).bmp")]
                self.tackled_i = [games.load_image("titans_s_h_t1.bmp")]

        super(Safety, self).__init__(images = self.standing_i2, angle = 180,
                                        x = x, y = y,
                                        repeat_interval = 9, n_repeats = 0)

        self.game.players.append(self) # add self to list of all players
        self.game.d_players.append(self) # add self to list of defensive players

        self.is_activated = False
        self.has_ball = False
        self.x_change = 0
        self.y_change = 0
        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = Safety.SPEED / 2
            self.speed_r = Safety.SPEED
        else:
            self.speed_w = Safety.SPEED2 / 2
            self.speed_r = Safety.SPEED2
        self.direction = "+"

    def update(self):
        if not self.game.is_paused:
            if not self.is_activated:
                if self.game.play_is_running:
                    if self.has_ball:
                        pass
                    else:
                        if self.game.qb.has_ball:
                            if self.game.qb.y < self.game.field.bottom - self.game.line_of_scrimmage - 360:
                                self.angle = 90 + math.degrees(math.atan2(self.game.qb.y - self.y, self.game.qb.x - self.x))
                                self.speed = self.speed_r
                            else:
                                self.speed = 0
                                self.angle = 180
                                if 270 < self.game.qb.angle < 345 and self.x > self.game.field.left + 800:
                                    self.slide(-2)
                                elif 15 < self.game.qb.angle < 90 and self.x < self.game.field.right - 800:
                                    self.slide(2)
                                elif self.game.qb.angle >= 345 or self.game.qb.angle <= 15:
                                    if self.x > (self.game.field.right - self.game.field.left) / 2 + self.game.field.left + 1:
                                        self.slide(-2)
                                    elif self.x < (self.game.field.right - self.game.field.left) / 2 + self.game.field.left - 1:
                                        self.slide(2)

                        else:
                            for sprite in self.game.players:
                                if sprite.has_ball:
                                    self.angle = 90 + math.degrees(math.atan2(sprite.y - self.y, sprite.x - self.x))
                                    self.speed = self.speed_r
                else:
                    self.speed = 0

        # get Basic_defense's update method
        super(Safety, self).update()

class Game(object):
    """ The game """
    def __init__(self):
        """ Initializes game object """
        self.team1 = ""
        self.team2 = ""
        self.team1_score = 0
        self.team2_score = 0
        self.team1_offence = True
        self.down = 0
        self.clock_rate = 1
        self.quarter = 1
        self.non_activated_sprites = []
        self.is_paused = False
        self.can_pause = True
        self.players = []
        self.o_players = []
        self.d_players = []
        self.can_not_catch = []
        self.do_not_destroy = []
        self.play_num = 0
        self.play_is_running = False
        self.play_is_over = False
        self.ball_incomplete = False
        self.line_of_scrimmage = 1083
        self.for_first_down = 360
        self.winner_string = ""

    def pick_teams(self):
        """ Display text objects so that players can pick their teams """
        # clear the screen of other sprites
        games.screen.clear()

        # add text sprites to get the teams the players want to be
        self.set_text = ftxt.Settings_text(game = self)
        games.screen.add(self.set_text)        
        self.ask_text = ftxt.Ask_text(game = self, value = "Player 1, what team do you want?",
                    size = 30, color = ftxt.yellow, left = 10, top = 10)
        games.screen.add(self.ask_text)
        text = ftxt.Change_text(game = self, value = "Titans",
                    size = 25, left = 10, top = 40)
        games.screen.add(text)
        text = ftxt.Change_text(game = self, value = "Colts",
                    size = 25, left = 10, top = 70)
        games.screen.add(text)
        text = ftxt.Change_text(game = self, value = "Patriots",
                    size = 25, left = 10, top = 100)
        games.screen.add(text)

    def start(self):
        """ Puts the field on the screen """
        # clear the screen of other sprites
        games.screen.clear()
        
        # put the field on the screen
        self.field = Field(game = self)
        games.screen.add(self.field)

        # put the score on the screen
        self.score = ftxt.Score(game = self)
        games.screen.add(self.score)

        # put the number of downs on the screen
        self.downs_text = ftxt.Downs_text(game = self)
        games.screen.add(self.downs_text)

        # put the game clock on the screen
        self.game_clock = ftxt.Game_clock(game = self, rate = self.clock_rate)
        games.screen.add(self.game_clock)

        # put the quarter on the screen
        self.quarter_text = ftxt.Quarter_text(game = self)
        games.screen.add(self.quarter_text)

        self.bar = Bar(game = self)
        games.screen.add(self.bar)
        self.non_activated_sprites.append(self.bar)

        self.pick_play()

    def pick_play(self):
        for sprite in games.screen.all_objects:
            if sprite not in self.do_not_destroy:
                sprite.destroy()
        self.players = []
        self.o_players = []
        self.d_players = []
        self.can_not_catch = []

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

        self.downs_text.update_downs()

        # adjust the bar
        self.bar.right = 0

        # adjust the field on the screen
        self.field.x = games.screen.width / 2
        self.field.bottom = (games.screen.height * 3 / 4) + self.line_of_scrimmage + 360

        text = ftxt.Play_text(game = self)
        games.screen.add(text)

    def new_play(self):
        self.play_is_running = False
        self.play_is_over = False
        self.ball_incomplete = False

        # --- put the players on the screen ---

        # center
        self.center = Center(game = self, x = games.screen.width / 2,
                             y = games.screen.height * 3 / 4)
        games.screen.add(self.center)
        # quarterback
        self.qb = QB(game = self, x = games.screen.width / 2,
                y = games.screen.height * 3 / 4 + 50)
        games.screen.add(self.qb)
        # left wide recicver
        self.wr1 = WR(game = self, x = games.screen.width / 4,
                      y = games.screen.height * 3 / 4 + 50)
        games.screen.add(self.wr1)
        # right wide recicver
        self.wr2 = WR(game = self, x = games.screen.width * 3 / 4,
                      y = games.screen.height * 3 / 4 + 50)
        games.screen.add(self.wr2)

        # noseguard
        self.noseg = Noseguard(game = self, x = games.screen.width / 2,
                               y = games.screen.height * 3 / 4 - 20)
        games.screen.add(self.noseg)

        # safety
        self.safety = Safety(game = self, x = games.screen.width / 2,
                             y = games.screen.height * 3 / 4 - 275)
        games.screen.add(self.safety)

        # elevate bar sprite and score sprite above all other sprites
        self.bar.elevate()
        self.score.elevate()

    def change_offence(self):
        if self.team1_offence:
            self.team1_offence = False
        else:
            self.team1_offence = True

    def end_game(self):
        for sprite in games.screen.all_objects:
            if sprite not in self.do_not_destroy:
                sprite.destroy()

        # adjust the field on the screen
        self.field.x = games.screen.width / 2
        self.field.y = games.screen.height / 2

        if self.team1_score > self.team2_score:
            self.winner_string = "The " + self.team1 + " win!"
        elif self.team2_score > self.team1_score:
            self.winner_string = "The " + self.team2 + " win!"
        else:
            self.winner_string = "Tie!"

        text = ftxt.Text(game = self, value = self.winner_string, size = 100,
                    color = ftxt.red, x = games.screen.width / 2,
                    y = games.screen.height / 2)
        games.screen.add(text)

    def show_settings(self):
        games.screen.clear()

        self.c_settings = ftxt.Clock_settings(game = self)
        games.screen.add(self.c_settings)

        text = ftxt.Settings_exit(game = self)
        games.screen.add(text)

def main():
    football = Game()
    football.pick_teams()
    games.screen.mainloop()

# run program
main()
