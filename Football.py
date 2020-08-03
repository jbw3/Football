# Football
# Version 3.0
#
# A football game for two players. The player on offence controls the
# quarterback first, and then the player who catches the ball. The defence is
# controlled by the computer.
#
# To do:
# 1. make football players' arms
# 2. make center block noseguard better
# 3. add sounds

# import modules
from livewires import games
import math, random, football_text as ftxt
# football_text is a module specially designed for this game. It has all of the
# text and message objects needed for this game.

# initialize screen
games.init(screen_width = 1020, screen_height = 700, fps = 50)

# class definitions
class Arms(games.Animation):
    """ The arms of a football player """
    def __init__(self, player, images, command, xshift=0, angshift=0, is_collideable=False):
        """ Initializes object """
        self.player = player
        self.command = command
        self.xshift = xshift
        self.angshift = angshift
        if games.keyboard.is_pressed(games.K_RALT) or games.keyboard.is_pressed(games.K_LALT):
            interval = 9
        else:
            interval = 14

        super(Arms, self).__init__(images = images,
                                   x = self.player.x + self.xshift * math.sin(math.radians(self.player.angle + self.angshift + 90)),
                                   y = self.player.y + self.xshift * -math.cos(math.radians(self.player.angle + self.angshift + 90)),
                                   angle = self.player.angle + self.angshift,
                                   repeat_interval = interval,
                                   n_repeats = 0,
                                   is_collideable = is_collideable)
        games.screen.add(self)
        self.lower(self.player)

        self.player.game.non_activated_sprites.append(self) # 'Arms' object will move with the player it is attached to

    def update(self):
        self.x = self.player.x + self.xshift * math.sin(math.radians(self.player.angle + self.angshift + 90))
        self.y = self.player.y + self.xshift * -math.cos(math.radians(self.player.angle + self.angshift + 90))
        self.angle = self.player.angle + self.angshift
        if games.keyboard.is_pressed(games.K_RALT) or games.keyboard.is_pressed(games.K_LALT):
            self.set_interval(9)
        else:
            self.set_interval(14)

        if self.command == "hold ball":
            for sprite in self.overlapping_sprites:
                if sprite != self.player.game.qb and (sprite in self.player.game.d_players or (sprite in self.player.game.o_players and sprite not in self.player.game.can_not_catch)):
                    self.player.game.ball_carrier = sprite
                    self.player.game.qb.speed = 0

            if self.player.game.qb != self.player.game.ball_carrier or (not games.keyboard.is_pressed(games.K_PERIOD) and not games.keyboard.is_pressed(games.K_COMMA)):
                self.player.arm_side = 0
                self.destroy()

        if self.player.game.play_is_over:
            self.destroy()

    def destroy(self):
        self.player.arms = False
        try:
            self.player.game.non_activated_sprites.remove(self)
        except(ValueError):
            pass
        super(Arms, self).destroy()

class Legs(games.Animation):
    """ The legs of a football player """
    def __init__(self, player, images):
        """ Initializes object """
        self.player = player
        if games.keyboard.is_pressed(games.K_RALT) or games.keyboard.is_pressed(games.K_LALT):
            interval = 9
        else:
            interval = 14

        super(Legs, self).__init__(images = images,
                                   x = self.player.x, y = self.player.y,
                                   angle = self.player.angle,
                                   repeat_interval = interval,
                                   n_repeats = 0, is_collideable = False)
        games.screen.add(self)
        self.lower(self.player)

        self.player.game.non_activated_sprites.append(self) # 'Legs' object will move with the player it is attached to

    def update(self):
        self.x = self.player.x
        self.y = self.player.y
        self.angle = self.player.angle

        if self.player.speed == self.player.speed_r:
            self.set_interval(9)

        elif self.player.speed == self.player.speed_w:
            self.set_interval(14)

        elif self.player.speed == 0:
            self.destroy()

        if self.player.game.play_is_over:
            self.destroy()

    def destroy(self):
        self.player.legs = False
        try:
            self.player.game.non_activated_sprites.remove(self)
        except(ValueError):
            pass
        super(Legs, self).destroy()

class Basic_player(games.Sprite):
    """ Base class for all football players """
    BASE_LEG_IMAGE = games.load_image("feet.bmp")

    def update(self):
        if not self.game.is_paused:
            if self.tackled > 0:
                self.tackled -= 1
                if self.tackled == 0:
                    self.image = self.main_image
                    del self.main_image

    def load_images(self, team, position, place):
        """ Loads all images necessary for object """
        team = team.lower()
        self.tackled_i = games.load_image(team + position + place + "tackled.bmp")
        self.leg_i = [games.load_image(team + "leg" + place + "1.bmp"),
                      games.load_image(team + "leg" + place + "2.bmp")]
        return games.load_image(team + position + place + ".bmp")

    def create_leg_list(self, add_list, every):
        insert = every
        while insert <= len(add_list):
            add_list[insert:insert] = [Basic_player.BASE_LEG_IMAGE]
            insert += every + 1

        return add_list

    def turn(self, sprite):
        """ Rotate sprite """
        angle = 90 + math.degrees(math.atan2(sprite.y - self.y, sprite.x - self.x))

    def adjust(self):
        """ Calculate sprites x_change and y_change """
        self.x_move = True
        self.y_move = True
        for sprite in self.overlapping_sprites:
            if sprite in self.game.players:
                if self.direction == "+":
                    if sprite.y - 2 < self.top < sprite.bottom:
                        if 270 < self.angle < 360 or 0 <= self.angle < 90:
                            self.y_move = False
                    elif sprite.y + 2 > self.bottom > sprite.top:
                        if 90 < self.angle < 270:
                            self.y_move = False
                    elif sprite.x > self.right > sprite.left:
                        if 0 < self.angle < 180:
                            self.x_move = False
                    elif sprite.x < self.left < sprite.right:
                        if 180 < self.angle < 360:
                            self.x_move = False
                else:
                    if sprite.y - 2 < self.top < sprite.bottom:
                        if 90 < self.angle < 270:
                            self.y_move = False
                    elif sprite.y + 2 > self.bottom > sprite.top:
                        if 270 < self.angle < 360 or 0 <= self.angle < 90:
                            self.y_move = False
                    elif sprite.x > self.right > sprite.left:
                        if 180 < self.angle < 360:
                            self.x_move = False
                    elif sprite.x < self.left < sprite.right:
                        if 0 < self.angle < 180:
                            self.x_move = False

        if self.x_move:
            x_change = self.speed * math.sin(math.radians(self.angle))
        else:
            x_change = 0

        if self.y_move:
            y_change = self.speed * -math.cos(math.radians(self.angle))
        else:
            y_change = 0

        if self.direction == "-":
            x_change = -x_change
            y_change = -y_change

        for sprite in games.screen.get_all_objects():
            if sprite != self and sprite not in self.game.non_activated_sprites:
                sprite.x -= x_change
                sprite.y -= y_change

        # set leg images
        if not self.legs and games.screen.all_objects:
            self.legs = Legs(player=self, images=self.leg_i)

    def move(self, func=True):
        """ Moves sprite """
        self.x_move = True
        self.y_move = True
        if self.overlapping_sprites:
            for sprite in self.overlapping_sprites:
                if sprite in self.game.players:
                    if self.game.ball_carrier == sprite:
                        if self in self.game.o_players and sprite in self.game.d_players:
                            self.tackle(sprite)
                            self.x_move = False
                            self.y_move = False
                            break
                        elif self in self.game.d_players and sprite in self.game.o_players:
                            self.tackle(sprite)
                            self.x_move = False
                            self.y_move = False
                            break

                    if self.direction == "+":
                        if sprite.top < self.top < sprite.bottom:
                            if 270 < self.angle < 360 or 0 <= self.angle < 90:
                                self.y_move = False
                                self.top = sprite.bottom
                        elif sprite.bottom > self.bottom > sprite.top:
                            if 90 < self.angle < 270:
                                self.y_move = False
                                self.bottom = sprite.top
                        elif sprite.x > self.right > sprite.left:
                            if 0 < self.angle < 180:
                                self.x_move = False
                                self.right = sprite.left
                        elif sprite.x < self.left < sprite.right:
                            if 180 < self.angle < 360:
                                self.x_move = False
                                self.left = sprite.right
                    else:
                        if sprite.top < self.top < sprite.bottom:
                            if 90 < self.angle < 270:
                                self.y_move = False
                        elif sprite.bottom > self.bottom > sprite.top:
                            if 270 < self.angle < 360 or 0 <= self.angle < 90:
                                self.y_move = False
                        elif sprite.x > self.right > sprite.left:
                            if 180 < self.angle < 360:
                                self.x_move = False                        
                        elif sprite.x < self.left < sprite.right:
                            if 0 < self.angle < 180:
                                self.x_move = False
            if func and not self.tackled:
                self.overlap_func()

        if self.direction == "+":
            if self.x_move:
                self.x += self.speed * math.sin(math.radians(self.angle))
            if self.y_move:
                self.y += self.speed * -math.cos(math.radians(self.angle))
        else:
            if self.x_move:
                self.x -= self.speed * math.sin(math.radians(self.angle))
            if self.y_move:
                self.y -= self.speed * -math.cos(math.radians(self.angle))

        # set leg images
        if not self.legs and games.screen.all_objects:
            self.legs = Legs(player=self, images=self.leg_i)

    def slide(self, amount):
        """ Moves sprite to the left or right """
        self.x_move = True
        self.y_move = True
        for sprite in self.overlapping_sprites:
            if sprite in self.game.players:
                if amount < 0:
                    if sprite.top < self.top < sprite.bottom:
                        if 0 < self.angle < 180:
                            self.y_move = False
                    if sprite.bottom > self.bottom > sprite.top:
                        if 180 < self.angle < 360:
                            self.y_move = False
                    if sprite.left < self.left < sprite.right:
                        if 270 < self.angle <= 360 or 0 < self.angle < 90:
                            self.x_move = False
                    if sprite.right > self.right > sprite.left:
                        if 90 < self.angle < 270:
                            self.x_move = False

                elif amount > 0:
                    if sprite.top < self.top < sprite.bottom:
                        if 180 < self.angle < 360:
                            self.y_move = False
                    if sprite.bottom > self.bottom > sprite.top:
                        if 0 < self.angle < 180:
                            self.y_move = False
                    if sprite.left < self.left < sprite.right:
                        if 90 < self.angle < 270:
                            self.x_move = False
                    if sprite.right > self.right > sprite.left:
                        if 270 < self.angle <= 360 or 0 < self.angle < 90:
                            self.x_move = False

        if self.x_move:
            self.x -= amount * math.sin(math.radians(self.angle - 90))
        if self.y_move:
            self.y -= amount * -math.cos(math.radians(self.angle - 90))

    def tackle(self, player):
        self.elevate(player)
        self.tackled = 400
        player.tackled = 425
        self.main_image = self.image
        player.main_image = player.image
        player.image = player.tackled_i
        self.image = self.tackled_i
        player.speed = 0
        self.speed = 0

    def overlap_func(self):
        """ Method called when sprite overlaps another sprite """
        pass

    def destroy(self):
        if self.legs:
            self.legs.destroy()
        if self.arms:
            self.arms.destroy()
        super(Basic_player, self).destroy()

class Basic_offence(Basic_player):
    """ Base class for offincive players """
    def update(self):
        """
        If the player has control of the sprite, this class will allow the
        player to rotate the sprite, to move the sprite forward and backward,
        and to allow the player to set the speed at which the sprite moves.
        If the sprite is moving, it does not allow the sprite to overlap any
        other football player sprites.
        """
        if not self.game.is_paused:
            if not self.tackled:
                if self.game.play_is_running:                    
                    # --- allow sprite to move based on keys pressed if activated ---
                    
                    if self == self.game.ball_carrier:
                        # rotate sprite based on keys pressed
                        if games.keyboard.is_pressed(games.K_RIGHT):
                            self.angle += 3

                        if games.keyboard.is_pressed(games.K_LEFT):
                            self.angle -= 3

                        # --- make sprite move based on keys pressed ---

                        # make sprite move in the direction it is pointing
                        if games.keyboard.is_pressed(games.K_UP):
                            self.direction = "+"
                            # sets sprite's speed based on keys pressed
                            if games.keyboard.is_pressed(games.K_RALT) or games.keyboard.is_pressed(games.K_LALT):
                                self.speed = self.speed_w
                            else:
                                self.speed = self.speed_r
                            self.adjust()

                        # make sprite move in the opposite direction it is pointing
                        if games.keyboard.is_pressed(games.K_DOWN):
                            self.direction = "-"
                            # sets sprite's speed based on keys pressed
                            if games.keyboard.is_pressed(games.K_RALT) or games.keyboard.is_pressed(games.K_LALT):
                                self.speed = self.speed_w
                            else:
                                self.speed = self.speed_r
                            self.adjust()

                        # sets sprite's x_change and y_change to 0 if sprite is not moving
                        if not games.keyboard.is_pressed(games.K_UP) and not games.keyboard.is_pressed(games.K_DOWN) and not games.keyboard.is_pressed(games.K_m):
                            self.speed = 0

                    else:
                        if self.game.ball_carrier in self.game.d_players:
                            self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                            self.speed = self.speed_r

                        elif self.game.ball_carrier not in self.game.players and self.game.ball_carrier.play == "bounce":
                            self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                            self.speed = self.speed_r

                        if self.speed != 0:
                            # move sprite
                            self.direction = "+"
                            self.move()

        super(Basic_offence, self).update()

    def tackle(self, player):
        """ Method to make self tackle 'player' """
        super(Basic_offence, self).tackle(player)
        if random.randrange(20) == 0:
            message = ftxt.Football_message(game = self.game, value = "Fumble!",
                                            x = games.screen.width / 2,
                                            y = games.screen.height / 2)
            games.screen.add(message)

            football = Football("bounce", self.game, player.x, player.top - 23,
                                player.angle)
            games.screen.add(football)
        else:
            self.game.play_is_running = False
            self.game.play_is_over = True
            if player.bottom < self.game.field.top + 360:
                self.game.line_of_scrimmage = 720
            else:
                self.game.line_of_scrimmage = 3600 - (self.game.field.bottom - player.y - 360)
            self.game.for_first_down = 360
            self.game.down = 0
            self.game.change_offence()

class Basic_defense(Basic_player):
    """ Base class for defensive players """
    def update(self):
        if not self.game.is_paused:
            if not self.tackled:
                if self.game.play_is_running:
                    if self.game.ball_carrier not in self.game.players and self.game.ball_carrier.play == "bounce":
                            self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                            self.speed = self.speed_r

                    if self == self.game.ball_carrier:
                        self.speed = self.speed_r
                        self.direction = "+"
                        self.adjust()
                        if self.angle < 178:
                            self.angle += 3
                        elif self.angle > 182:
                            self.angle -= 3
                        else:
                            self.angle = 180

                    else:
                        self.move()

        super(Basic_defense, self).update()

    def tackle(self, player):
        super(Basic_defense, self).tackle(player)
        if random.randrange(20) == 0:
            message = ftxt.Football_message(game = self.game, value = "Fumble!",
                                            x = games.screen.width / 2,
                                            y = games.screen.height / 2)
            games.screen.add(message)

            football = Football("bounce", self.game, player.x, player.top - 23,
                                player.angle)
            games.screen.add(football)
        else:
            self.game.play_is_running = False
            self.game.play_is_over = True
            if player.top > self.game.field.bottom - 360:
                self.game.for_first_down = 360
                self.game.line_of_scrimmage = 1083
                if self.game.team1_offence:
                    self.game.team2_score += 2
                else:
                    self.game.team1_score += 2
                self.game.sBoard.update_score()
                self.game.down = 0
                self.game.sBoard.stop_clock()
                message = ftxt.Football_message(game = self.game,
                                                x = games.screen.width / 2,
                                                y = games.screen.height / 2,
                                                value = "Safety!")
                games.screen.add(message)
            else:
                self.game.for_first_down -= self.game.field.bottom - self.game.line_of_scrimmage - 360 - player.y
                self.game.line_of_scrimmage = self.game.field.bottom - player.y - 360

class Bar(games.Sprite):
    def __init__(self, game):
        super(Bar, self).__init__(image = games.load_image("bar.bmp",
                                                           transparent = False),
                                  right = 0, y = games.screen.height - 30)
        self.game = game

        self.game.do_not_destroy.append(self) # add self to do_not_destroy list

class Field(games.Sprite):
    """ The football field """
    def __init__(self, game):
        """ Initializes object """
        self.game = game
        super(Field, self).__init__(image = games.load_image("football_field.bmp", transparent = False),
                                    x = games.screen.width/2,
                                    y = games.screen.height/2,
                                    is_collideable=False)

        self.timer = 150

        self.game.do_not_destroy.append(self) # add self to do_not_destroy list

    def update(self):
        if self.game.sBoard.game_is_over() and not self.game.play_is_running:
            self.game.play_is_over = True
            self.game.center.can_snap = False

        if self.game.play_is_over:
            self.timer -= 1
            if self.timer == 0:
                self.game.play_is_over = False
                self.game.play_is_running = False
                self.timer = 150
                if self.game.sBoard.game_is_over():
                    self.game.end_game()
                else:
                    self.game.pick_play()

        else:
            if self.game.ball_carrier in self.game.o_players and self.game.ball_carrier.top < self.top + 360:
                self.game.line_of_scrimmage = 1083
                self.for_first_down = 360
                self.game.play_is_over = True
                self.game.play_is_running = False
                self.game.ball_carrier.speed = 0
                if self.game.team1_offence:
                    self.game.team1_score += 6
                else:
                    self.game.team2_score += 6
                self.game.sBoard.update_score()
                self.game.down = 0
                self.game.sBoard.stop_clock()
                message = ftxt.Football_message(game = self.game,
                                                x = games.screen.width / 2,
                                                y = games.screen.height / 2,
                                                value = "Touchdown!")
                games.screen.add(message)
                self.game.change_offence()

            elif self.game.ball_carrier in self.game.d_players and self.game.ball_carrier.bottom > self.bottom - 360:
                self.game.line_of_scrimmage = 1083
                self.game.play_is_over = True
                self.game.play_is_running = False
                self.game.ball_carrier.speed = 0
                if self.game.team1_offence:
                    self.game.team2_score += 6
                else:
                    self.game.team1_score += 6
                self.game.sBoard.update_score()
                self.game.down = 0
                self.game.sBoard.stop_clock()
                message = ftxt.Football_message(game = self.game,
                                                x = games.screen.width / 2,
                                                y = games.screen.height / 2,
                                                value = "Touchdown!")
                games.screen.add(message)

            elif self.game.ball_carrier in self.game.players and (self.game.ball_carrier.x < self.left or self.game.ball_carrier.x > self.right):
                self.game.sBoard.stop_clock()
                self.game.for_first_down -= self.bottom - self.game.line_of_scrimmage - 360 - self.game.ball_carrier.y
                self.game.line_of_scrimmage = self.bottom - self.game.ball_carrier.y - 360
                self.game.play_is_running = False
                self.game.play_is_over = True
                self.game.ball_carrier.speed = 0
                self.game.ball_carrier.x_change = 0
                self.game.ball_carrier.y_change = 0
                if self.game.ball_carrier in self.game.d_players:
                    self.game.change_offence()

class Football(games.Animation):
    """ The football """
    def __init__(self, play, game, x, y, angle):
        """ Initializes object """
        self.game = game
        self.play = play
        self.loop = True
        self.game.ball_carrier = self
        if self.play == "pass":
            images = ["football1.bmp",
                      "football2.bmp",
                      "football3.bmp",
                      "football3.bmp",
                      "football4.bmp"]
            self.to_go = self.game.bar.right * 3
            interval = 2
            self.speed = 7
            
        elif self.play == "hike":
            images = ["football1.bmp"]
            self.game.play_is_running = True
            self.game.sBoard.start_clock()
            interval = 10
            self.speed = 7

        elif self.play == "bounce":
            images = ["football1.bmp",
                      "football9.bmp",
                      "football8.bmp",
                      "football7.bmp",
                      "football3.bmp",
                      "football7.bmp",
                      "football6.bmp",
                      "football5.bmp"]
            interval = 2
            self.speed = 4

        self.x_change = self.speed * math.sin(math.radians(angle))
        self.y_change = self.speed * -math.cos(math.radians(angle))
            
        super(Football, self).__init__(images = images, x = x, y = y,
                                       angle = angle, repeat_interval = interval,
                                       n_repeats = 0)

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
                        self.images = [self.image]
                        self.game.sBoard.stop_clock()

                    else:
                        for sprite in games.screen.get_all_objects():
                            if sprite != self and sprite not in self.game.non_activated_sprites:
                                sprite.x -= self.x_change
                                sprite.y -= self.y_change

                    # check to see if self overlaps a football player
                    if not self.game.ball_incomplete:
                        for sprite in self.overlapping_sprites:
                            if sprite in self.game.players and sprite != self.game.qb and sprite not in self.game.can_not_catch:
                                self.game.ball_carrier = sprite
                                if sprite in self.game.d_players:
                                    message = ftxt.Football_message(game = self.game,
                                                    x = games.screen.width / 2,
                                                    y = games.screen.height / 2,
                                                    value = "Interception!")
                                    games.screen.add(message)
                                self.destroy()

                elif self.play == "hike":
                    self.x += self.x_change
                    self.y += self.y_change
                    for sprite in self.overlapping_sprites:
                        if sprite in self.game.players and sprite != self.game.center:
                            self.game.ball_carrier = sprite
                            self.destroy()

                elif self.play == "bounce":
                    if self.speed > .5:
                        if random.randrange(25) == 0:
                            self.angle += random.randrange(-5, 6)
                        for sprite in self.overlapping_sprites:
                            if sprite in self.game.players:
                                break
                        else:
                            self.speed *= .75 + random.randrange(5, 21) / 100.0
                        self.x_change = self.speed * math.sin(math.radians(self.angle))
                        self.y_change = self.speed * -math.cos(math.radians(self.angle))

                        for sprite in games.screen.get_all_objects():
                            if sprite != self and sprite not in self.game.non_activated_sprites:
                                sprite.x -= self.x_change
                                sprite.y -= self.y_change

                    else:
                        self.images = [games.load_image("football1.bmp")]

                    for sprite in self.overlapping_sprites:
                        if sprite in self.game.players and not sprite.tackled:
                            self.game.ball_carrier = sprite
                            self.destroy()

class QB(Basic_offence):
    """ The quarterback """
    SPEED = 5 + random.randrange(0, 1) / 10.0
    SPEED2 = 5 + random.randrange(0, 1) / 10.0
    
    def __init__(self, game, x, y):
        """ Initializes object """
        self.game = game
        # if team 1 is on offence
        if self.game.team1_offence:
            image = self.load_images(self.game.team1, "qb", "h")

        # if team 2 is on offence
        else:
            image = self.load_images(self.game.team2, "qb", "a")
        
        super(QB, self).__init__(image=image, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.o_players.append(self) # add self to list of offencive players

        self.speed = 0
        self.x_move = True
        self.y_move = True
        if self.game.team1_offence:
            self.speed_w = QB.SPEED / 2
            self.speed_r = QB.SPEED
        else:
            self.speed_w = QB.SPEED2 / 2
            self.speed_r = QB.SPEED2
        self.direction = "+"
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0
        self.arm_side = 0

    def update(self):
        if not self.game.is_paused:
            if not self.tackled:
                if self == self.game.ball_carrier:
                    if games.keyboard.is_pressed(games.K_SPACE) and self.game.bar.left < 0:
                        self.game.bar.x += 7

                    if games.keyboard.is_pressed(games.K_PERIOD):
                        if self.arm_side != 1:
                            if self.arms:
                                self.arms.destroy()
                            if self.game.team1_offence:
                                self.arms = Arms(self, [self.game.team1 + "qbarm.bmp"], "hold ball", 18, is_collideable=True)
                            else:
                                self.arms = Arms(self, [self.game.team2 + "qbarm.bmp"], "hold ball", 18, is_collideable=True)
                            self.arm_side = 1

                    elif games.keyboard.is_pressed(games.K_COMMA):
                        if self.arm_side != -1:
                            if self.arms:
                                self.arms.destroy()
                            if self.game.team1_offence:
                                self.arms = Arms(self, [self.game.team1 + "qbarm.bmp"], "hold ball", 18, 180, True)
                            else:
                                self.arms = Arms(self, [self.game.team2 + "qbarm.bmp"], "hold ball", 18, 180, True)
                            self.arm_side = -1

                    # makes quarterback throw the football
                    if games.keyboard.is_pressed(games.K_m):
                        self.speed = 0
                        football = Football(game = self.game, play = "pass",
                            x = 10 * math.sin((self.angle + 90) * math.pi / 180) + self.x,
                            y = 10 * -math.cos((self.angle + 90) * math.pi / 180) + self.y,
                            angle = self.angle)
                        games.screen.add(football)
                        self.game.bar.right = 0

        super(QB, self).update()

class WR(Basic_offence):
    """ A wide receiver """
    SPEED = 5 + random.randrange(0, 3) / 10.0
    SPEED2 = 5 + random.randrange(0, 3) / 10.0
    
    def __init__(self, game, x, y, side):
        """ Initializes object """
        self.game = game
        self.side = side
        if self.game.team1_offence:
            image = self.load_images(self.game.team1, self.side + "wr", "h")

        else:
            image = self.load_images(self.game.team2, self.side + "wr", "a")

        super(WR, self).__init__(image=image, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.o_players.append(self) # add self to list of offencive players

        self.speed = 0
        self.x_move = True
        self.y_move = True
        if self.game.team1_offence:
            self.speed_w = WR.SPEED / 2
            self.speed_r = WR.SPEED
        else:
            self.speed_w = WR.SPEED2 / 2
            self.speed_r = WR.SPEED2
        self.direction = "+"
        self.timer = 0
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0

    def update(self):        
        if not self.game.is_paused:
            if not self.tackled:
                if not self == self.game.ball_carrier:
                    if self.game.play_is_running:
                        #-------------------- plays --------------------
                        if self.game.play_num == 1:
                            self.speed = self.speed_r
                            if self.side == "l":
                                self.angle = 70
                            else:
                                self.angle = 300

                        elif self.game.play_num == 2:
                            self.speed = self.speed_r
                            if self.side == "l":
                                if self.angle < 90:
                                    self.angle += 3
                                else:
                                    self.angle = 90
                            else:
                                if self.angle > 270 or self.angle == 0:
                                    self.angle -= 3
                                else:
                                    self.angle = 270

                        elif self.game.play_num == 3:
                            self.speed = self.speed_r
                            self.timer += 1
                            if self.side == "l":
                                self.angle = 315
                            elif self.side == "r":
                                if self.angle > 270 or self.angle == 0:
                                    self.angle -= 4
                                else:
                                    self.angle = 270

                        elif self.game.play_num == 4:
                            self.speed = self.speed_r
                            if self.side == "l":
                                self.angle = 50

                        elif self.game.play_num == 5:
                            self.speed = self.speed_r
                            if self.side == "r":
                                if self.angle > 270 or self.angle == 0:
                                    self.angle -= 3
                                else:
                                    self.angle = 270
                            elif self.side == "l":
                                self.timer += 1
                                if self.timer >= 40:
                                    if self.angle < 90:
                                        self.angle += 2
                                    else:
                                        self.angle = 90
                        #-----------------------------------------------

        # get Basic_offence's update method
        super(WR, self).update()

    def overlap_func(self):
        self.slide(-self.speed_w)

class RB(Basic_offence):
    """ The center """
    SPEED = 5.1 + random.randrange(0, 2) / 10.0
    SPEED2 = 5.1 + random.randrange(0, 2) / 10.0
    
    def __init__(self, game, x, y):
        """ Initializes object """
        self.game = game
        if self.game.team1_offence:
            image = self.load_images(self.game.team1, "rb", "h")

        else:
            image = self.load_images(self.game.team2, "rb", "a")

        super(RB, self).__init__(image=image, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.o_players.append(self) # add self to list of offencive players

        self.speed = 0
        self.x_move = True
        self.y_move = True
        if self.game.team1_offence:
            self.speed_w = RB.SPEED / 2
            self.speed_r = RB.SPEED
        else:
            self.speed_w = RB.SPEED2 / 2
            self.speed_r = RB.SPEED2
        self.direction = "+"
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0

    def update(self):        
            if not self.game.is_paused:
                if not self.tackled:
                    if not self == self.game.ball_carrier:
                        if self.game.play_is_running:
                            #-------------------- plays --------------------
                            if self.game.play_num == 1:
                                self.speed = self.speed_r
                                if self.angle < 45:
                                    self.angle += 3

                            elif self.game.play_num == 2:
                                self.speed = self.speed_r
                                if self.angle < 45:
                                    self.angle += 3

                            elif self.game.play_num == 3:
                                self.speed = self.speed_r
                                if self.angle < 45:
                                    self.angle += 3

                            elif self.game.play_num == 4:
                                self.speed = self.speed_r
                                if self.angle == 0 or self.angle > 315:
                                    self.angle -= 3

                            elif self.game.play_num == 5:
                                self.speed = self.speed_r
                                if self.angle < 45:
                                    self.angle += 3
                            #-----------------------------------------------

            # get Basic_offence's update method
            super(RB, self).update()

class Center(Basic_offence):
    """ The center """
    SPEED = 5 + random.randrange(-3, 1) / 10.0
    SPEED2 = 5 + random.randrange(-3, 1) / 10.0
    
    def __init__(self, game, x, y):
        """ Initializes object """
        self.game = game
        if self.game.team1_offence:
            image = self.load_images(self.game.team1, "c", "h")

        else:
            image = self.load_images(self.game.team2, "c", "a")

        super(Center, self).__init__(image=image, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.o_players.append(self) # add self to list of offencive players
        self.game.can_not_catch.append(self)
        self.game.ball_carrier = self

        self.speed = 0
        self.x_move = True
        self.y_move = True
        if self.game.team1_offence:
            self.speed_w = Center.SPEED / 2
            self.speed_r = Center.SPEED
        else:
            self.speed_w = Center.SPEED2 / 2
            self.speed_r = Center.SPEED2
        self.direction = "+"
        self.can_snap = True
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0

    def update(self):
        if not self.game.is_paused:
            if not self.tackled:
                if not self == self.game.ball_carrier:
                    if self.game.play_is_running:
                        if self.x - 50 < self.game.noseg.x < self.x + 50 and self.y - 50 < self.game.noseg.y < self.y + 50:
                            self.speed = 0
                            self.angle = 180 + self.game.noseg.angle
                            if random.randrange(3) != 0:
                                if self.game.noseg.x < self.x:
                                    self.slide(-self.speed_w)
                                elif self.game.noseg.x > self.x:
                                    self.slide(self.speed_w)                
                        else:
                            self.angle = 90 + math.degrees(math.atan2(((self.game.noseg.y - self.game.qb.y) / 4 + self.game.qb.y) - self.y, ((self.game.noseg.x - self.game.qb.x) / 4 + self.game.qb.x) - self.x))
                            self.speed = self.speed_r
                            #self.angle = 90 + math.degrees(math.atan2(self.game.noseg.y - self.y, self.game.noseg.x - self.x))

                        #self.angle = math.degrees(math.atan2(self.game.noseg.y - self.y - 15 * -math.cos(math.radians(self.game.noseg.angle)), self.x - self.game.noseg.x - 15 * math.sin(math.radians(self.game.noseg.angle))))
                        #self.slide(self.speed_w)

                if self.can_snap:
                    if games.keyboard.is_pressed(games.K_SPACE) and not self.game.play_is_running:
                        # initialize football sprite
                        football = Football(play = "hike", game = self.game,
                                            x = self.x, y = self.y + 10, angle = 180)
                        games.screen.add(football)
                        self.can_snap = False

        super(Center, self).update()

class Guard(Basic_offence):
    SPEED = 5 + random.randrange(-3, 1) / 10.0
    SPEED2 = 5 + random.randrange(-3, 1) / 10.0

    def __init__(self, game, x, y, side):
        self.game = game
        self.side = side
        if self.game.team1_offence:
            image = self.load_images(self.game.team1, self.side + "g", "h")

        else:
            image = self.load_images(self.game.team2, self.side + "g", "a")

        super(Guard, self).__init__(image=image, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.o_players.append(self) # add self to list of offencive players
        self.game.can_not_catch.append(self)

        self.speed = 0
        self.x_move = True
        self.y_move = True
        if self.game.team1_offence:
            self.speed_w = Guard.SPEED / 2
            self.speed_r = Guard.SPEED
        else:
            self.speed_w = Guard.SPEED2 / 2
            self.speed_r = Guard.SPEED2
        self.direction = "+"
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0
        if self.side == "r":
            self.opponent = self.game.ltackle
        elif self.side == "rr":
            self.opponent = self.game.lltackle
        elif self.side == "l":
            self.opponent = self.game.rtackle
        elif self.side == "ll":
            self.opponent = self.game.rrtackle

    def update(self):
        if not self.game.is_paused:
            if not self.tackled:
                if not self == self.game.ball_carrier:
                    if self.game.play_is_running:
                        if self.x - 60 < self.opponent.x < self.x + 60 and self.y - 60 < self.opponent.y < self.y + 60:
                            self.speed = 0
                            self.angle = 180 + self.opponent.angle
                            if random.randrange(3) != 0:
                                if self.opponent.x < self.x:
                                    self.slide(-self.speed_w)
                                elif self.opponent.x > self.x:
                                    self.slide(self.speed_w)                
                        else:
                            self.angle = 90 + math.degrees(math.atan2(((self.opponent.y - self.game.qb.y) / 4 + self.game.qb.y) - self.y, ((self.opponent.x - self.game.qb.x) / 4 + self.game.qb.x) - self.x))
                            self.speed = self.speed_r

        super(Guard, self).update()

class Noseguard(Basic_defense):
    SPEED = 5 + random.randrange(-3, 1) / 10.0
    SPEED2 = 5 + random.randrange(-3, 1) / 10.0
    
    def __init__(self, game, x, y):
        """ Initializes sprite """
        self.game = game
        if self.game.team1_offence:
            image = self.load_images(self.game.team2, "ng", "a")

        else:
            image = self.load_images(self.game.team1, "ng", "h")

        super(Noseguard, self).__init__(image=image, angle=180, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.d_players.append(self) # add self to list of defensive players
        self.game.can_not_catch.append(self)

        self.speed = 0
        self.x_move = True
        self.y_move = True
        if self.game.team1_offence:
            self.speed_w = Noseguard.SPEED / 2
            self.speed_r = Noseguard.SPEED
        else:
            self.speed_w = Noseguard.SPEED2 / 2
            self.speed_r = Noseguard.SPEED2
        self.direction = "+"
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0

    def update(self):
        if not self.game.is_paused:
            if not self.tackled:
                if not self == self.game.ball_carrier:
                    if self.game.play_is_running:
                        if self.game.ball_carrier == self.game.qb:
                            self.speed = self.speed_r
                            
                            # turn sprite toward the quarterback
                            self.angle = 90 + math.degrees(math.atan2(self.game.qb.y - self.y, self.game.qb.x - self.x))
            
                        else:
                            self.speed = 0
            
        # get Basic_defense's update method
        super(Noseguard, self).update()

    def overlap_func(self):
        self.slide(-self.speed_w)

class Tackle(Basic_defense):
    SPEED = 5 + random.randrange(-3, 1) / 10.0
    SPEED2 = 5 + random.randrange(-3, 1) / 10.0

    def __init__(self, game, x, y, side):
        self.game = game
        self.side = side
        if self.game.team1_offence:
            image = self.load_images(self.game.team2, self.side + "t", "a")

        else:
            image = self.load_images(self.game.team1, self.side + "t", "h")

        super(Tackle, self).__init__(image=image, angle=180, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.d_players.append(self) # add self to list of defensive players
        self.game.can_not_catch.append(self)

        self.speed = 0
        self.x_move = True
        self.y_move = True
        if self.game.team1_offence:
            self.speed_w = Tackle.SPEED / 2
            self.speed_r = Tackle.SPEED
        else:
            self.speed_w = Tackle.SPEED2 / 2
            self.speed_r = Tackle.SPEED2
        self.direction = "+"
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0

    def update(self):
        if not self.game.is_paused:
            if not self.tackled:
                if not self == self.game.ball_carrier:
                    if self.game.play_is_running:
                        if self.game.ball_carrier == self.game.qb:
                            self.speed = self.speed_r
                            # turn sprite toward the quarterback
                            self.angle = 90 + math.degrees(math.atan2(self.game.qb.y - self.y, self.game.qb.x - self.x))
            
                        else:
                            self.speed = 0
            
        # get Basic_defense's update method
        super(Tackle, self).update()

    def overlap_func(self):
        self.direction = "-"
        self.move(False)
        if "l" in self.side:
            self.slide(-self.speed_w)
        else:
            self.slide(self.speed_w)
        self.direction = "+"

class CB(Basic_defense):
    SPEED = 5 + random.randrange(0, 3) / 10.0
    SPEED2 = 5 + random.randrange(0, 3) / 10.0

    def __init__(self, game, x, y, side):
        self.game = game
        self.side = side
        if self.game.team1_offence:
            image = self.load_images(self.game.team2, self.side + "cb", "a")

        else:
            image = self.load_images(self.game.team1, self.side + "cb", "h")

        super(CB, self).__init__(image=image, angle=180, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.d_players.append(self) # add self to list of defensive players

        self.speed = 0
        self.x_move = True
        self.y_move = True
        if self.game.team1_offence:
            self.speed_w = CB.SPEED / 2
            self.speed_r = CB.SPEED
        else:
            self.speed_w = CB.SPEED2 / 2
            self.speed_r = CB.SPEED2
        self.direction = "+"
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0
        self.timer = 5

    def update(self):
        if not self.game.is_paused:
            if self.timer > 0:
                self.timer -= 1
            else:
                self.timer = 5
            if not self.tackled:
                if self.game.play_is_running:
                    if not self == self.game.ball_carrier:
                        if self.game.ball_carrier == self.game.qb and self.game.qb.y < self.game.field.bottom - self.game.line_of_scrimmage - 360:
                            self.angle = 90 + math.degrees(math.atan2(self.game.qb.y - self.y, self.game.qb.x - self.x))
                            self.speed = self.speed_r

                        else:
                            if self.game.ball_carrier in self.game.o_players and self.game.ball_carrier.y < self.game.field.bottom - self.game.line_of_scrimmage - 360:
                                    self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                                    self.speed = self.speed_r

                            else:
                                if self.side == "l":
                                    if self.timer == 0:
                                        self.angle = 90 + math.degrees(math.atan2(self.game.wr2.y - self.y, self.game.wr2.x - self.x))
                                    if self.game.wr2.right + 30 > self.x > self.game.wr2.left - 30 and self.game.wr2.bottom + 30 > self.y > self.game.wr2.top - 30:
                                        self.speed = self.speed_w
                                    else:
                                        self.speed = self.speed_r

                                elif self.side == "r":
                                    if self.timer == 0:
                                        self.angle = 90 + math.degrees(math.atan2(self.game.wr1.y - self.y, self.game.wr1.x - self.x))
                                    if self.game.wr1.right + 30 > self.x > self.game.wr1.left - 30 and self.game.wr1.bottom + 30 > self.y > self.game.wr1.top - 30:
                                        self.speed = self.speed_w
                                    else:
                                        self.speed = self.speed_r

        # get Basic_defense's update method
        super(CB, self).update()

class Safety(Basic_defense):
    SPEED = 5 + random.randrange(0, 3) / 10.0
    SPEED2 = 5 + random.randrange(0, 3) / 10.0

    def __init__(self, game, x, y):
        self.game = game
        if self.game.team1_offence:
            image = self.load_images(self.game.team2, "s", "a")

        else:
            image = self.load_images(self.game.team1, "s", "h")

        super(Safety, self).__init__(image=image, angle=180, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.d_players.append(self) # add self to list of defensive players
        if self.game.blitz:
            self.game.can_not_catch.append(self)

        self.speed = 0
        self.x_move = True
        self.y_move = True
        self.tracking = False
        if self.game.team1_offence:
            self.speed_w = Safety.SPEED / 2
            self.speed_r = Safety.SPEED
        else:
            self.speed_w = Safety.SPEED2 / 2
            self.speed_r = Safety.SPEED2
        self.direction = "+"
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0

    def update(self):
        if not self.game.is_paused:
            if not self.tackled:
                if self.game.play_is_running:
                    if not self == self.game.ball_carrier:
                        if self.game.ball_carrier == self.game.qb:
                            if self.game.blitz:
                                self.angle = 90 + math.degrees(math.atan2(self.game.qb.y - self.y, self.game.qb.x - self.x))
                                self.speed = self.speed_r
                            else:
                                if self.game.qb.y < self.game.field.bottom - self.game.line_of_scrimmage - 360:
                                    self.angle = 90 + math.degrees(math.atan2(self.game.qb.y - self.y, self.game.qb.x - self.x))
                                    self.speed = self.speed_r
                                else:
                                    self.speed = 0
                                    self.angle = 180
                                    if 270 < self.game.qb.angle < 345 and self.x > self.game.qb.x - 200:
                                        self.slide(self.speed_w)
                                    elif 15 < self.game.qb.angle < 90 and self.x < self.game.qb.x + 200:
                                        self.slide(-self.speed_w)
                                    elif self.game.qb.angle >= 345 or self.game.qb.angle <= 15:
                                        if self.x > self.game.qb.x + 1:
                                            self.slide(self.speed_w)
                                        elif self.x < self.game.qb.x - 1:
                                            self.slide(-self.speed_w)
                                    else:
                                        if self.game.qb.x > self.x and self.x < self.game.field.right - 600:
                                            self.slide(-self.speed_w)
                                        elif self.game.qb.x < self.x and self.x > self.game.field.left + 600:
                                            self.slide(self.speed_w)

                        else:
                            if self.game.ball_carrier in self.game.o_players:
                                if self.game.ball_carrier.y < self.game.field.bottom - self.game.line_of_scrimmage - 360:
                                    self.tracking = True
                                if self.tracking:
                                    self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                                    self.speed = self.speed_r

                            elif self.game.ball_carrier not in self.game.d_players and self.game.ball_carrier.play != "hike":
                                self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                                self.speed = self.speed_r

                else:
                    if games.keyboard.is_pressed(games.K_q):
                        self.game.blitz = True
                        self.game.can_not_catch.append(self)
                    if self.game.blitz and not self.game.play_is_over:
                        if self.y < self.game.field.bottom - self.game.line_of_scrimmage - 400:
                            self.speed = self.speed_r
                            self.move()
                        else:
                            self.speed = 0

        # get Basic_defense's update method
        super(Safety, self).update()

    def overlap_func(self):
        self.slide(self.speed_w)

class Scoreboard(object):
    """ The scoreboard """
    def __init__(self, game):
        """ Put all of the scoreboard items on the screen """
        self.game = game

        # put the background on the screen
        self.background = games.Sprite(
            image=games.load_image("scoreboard_background.bmp", transparent=False),
            left=0, top=0)
        games.screen.add(self.background)

        self.game.non_activated_sprites.append(self.background)
        self.game.do_not_destroy.append(self.background)

        # put the score on the screen
        self.score = ftxt.Score(game = self.game)
        games.screen.add(self.score)

        # put the number of downs on the screen
        self.downs_text = ftxt.Downs_text(game = self.game)
        games.screen.add(self.downs_text)

        # put the game clock on the screen
        self.game_clock = ftxt.Game_clock(game = self.game,
                                          rate = self.game.get_clock_rate())
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

    def show_play_clock(self):
        """ Put play clock on screen """
        text = ftxt.Play_clock(game=self.game, top=self.game_clock.bottom + 10)
        games.screen.add(text)

    def game_is_over(self):
        """ Returns True or False based on whether or not the game is over """
        return self.game_clock.minutes == 0 and self.game_clock.seconds == 0 and self.quarter_text > 4

    def update_downs(self):
        self.downs_text.update_downs()

    def update_score(self):
        self.score.update_score()

    def update_quarter(self):
        self.quarter_text.update_value()

class Game(object):
    """ The game """
    def __init__(self):
        self.clock_rate = 1
        self.sound_set = True
        self.teams = ("Colts", "Titans")

    def set_variables(self):
        self.team1 = ""
        self.team2 = ""
        self.team1_score = 0
        self.team2_score = 0
        self.team1_offence = True
        self.down = 0
        self.quarter = 1
        self.non_activated_sprites = []
        self.is_paused = False
        self.can_pause = True
        self.ball_carrier = None
        self.players = []
        self.o_players = []
        self.d_players = []
        self.can_not_catch = []
        self.do_not_destroy = []
        self.blitz = False
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
        self.set_text = ftxt.Settings_text(game = self, value = "Settings",
                                           size = 30, color1 = ftxt.white,
                                           color2 = ftxt.gray,
                                           right = games.screen.width - 10,
                                           top = 10)
        games.screen.add(self.set_text)

        self.ask_text = ftxt.Ask_text(game = self, value = "Player 1, what team do you want?",
                    size = 30, color = ftxt.yellow, left = 10, top = 10)
        games.screen.add(self.ask_text)

        top = 40
        for value in self.teams:
            text = ftxt.Change_text(game = self, value = value,
                                    size = 25, color1 = ftxt.white,
                                    color2 = self.ask_text.get_color(),
                                    color_func2 = self.ask_text.get_color,
                                    left = 10, top = top)
            games.screen.add(text)

            top = 10 + text.bottom

        self.exit_text = ftxt.Game_exit(game = self)
        games.screen.add(self.exit_text)

    def start(self):
        """ Puts the field on the screen """        
        # clear the screen of other sprites
        games.screen.clear()
        
        # put the field on the screen
        self.field = Field(game = self)
        games.screen.add(self.field)

        self.sBoard = Scoreboard(game = self)

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
        self.blitz = False

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
        self.play_is_running = False
        self.play_is_over = False
        self.ball_incomplete = False

        # --- put the players on the screen ---

        # noseguard
        self.noseg = Noseguard(game = self, x = games.screen.width / 2,
                               y = games.screen.height * 3 / 4 - 20)
        games.screen.add(self.noseg)
        # left tackle 1
        self.ltackle = Tackle(game = self, x = games.screen.width / 2 + 40,
                              y = games.screen.height * 3 / 4 - 20, side = "l")
        games.screen.add(self.ltackle)
        # left tackle 2
        self.lltackle = Tackle(game = self, x = games.screen.width / 2 + 80,
                              y = games.screen.height * 3 / 4 - 20, side = "ll")
        games.screen.add(self.lltackle)
        # right tackle 1
        self.rtackle = Tackle(game = self, x = games.screen.width / 2 - 40,
                              y = games.screen.height * 3 / 4 - 20, side = "r")
        games.screen.add(self.rtackle)
        # right tackle 2
        self.rrtackle = Tackle(game = self, x = games.screen.width / 2 - 80,
                              y = games.screen.height * 3 / 4 - 20, side = "rr")
        games.screen.add(self.rrtackle)
        # left cornerback
        self.cbl = CB(game = self, x = games.screen.width * 3 / 4,
                      y = games.screen.height * 3 / 4 - 70, side="l")
        games.screen.add(self.cbl)
        # right cornerback
        self.cbr = CB(game = self, x = games.screen.width / 4,
                      y = games.screen.height * 3 / 4 - 70, side="r")
        games.screen.add(self.cbr)
        # safety
        self.safety = Safety(game = self, x = games.screen.width / 2,
                             y = games.screen.height * 3 / 4 - 275)
        games.screen.add(self.safety)

        # center
        self.center = Center(game = self, x = games.screen.width / 2,
                             y = games.screen.height * 3 / 4)
        games.screen.add(self.center)
        # right guard 1
        self.rguard = Guard(game = self, x = games.screen.width / 2 + 40,
                            y = games.screen.height * 3 / 4, side = "r")
        games.screen.add(self.rguard)
        # right guard 2
        self.rrguard = Guard(game = self, x = games.screen.width / 2 + 80,
                             y = games.screen.height * 3 / 4, side = "rr")
        games.screen.add(self.rrguard)
        # left guard 1
        self.lguard = Guard(game = self, x = games.screen.width / 2 - 40,
                            y = games.screen.height * 3 / 4, side = "l")
        games.screen.add(self.lguard)
        # left guard 2
        self.llguard = Guard(game = self, x = games.screen.width / 2 - 80,
                             y = games.screen.height * 3 / 4, side = "ll")
        games.screen.add(self.llguard)
        # quarterback
        self.qb = QB(game = self, x = games.screen.width / 2,
                y = games.screen.height * 3 / 4 + 50)
        games.screen.add(self.qb)
        self.rb = RB(game = self, x = games.screen.width / 2,
                     y = games.screen.height - 6)
        games.screen.add(self.rb)
        # left wide recicver
        self.wr1 = WR(game = self, x = games.screen.width / 4,
                      y = games.screen.height * 3 / 4, side="l")
        games.screen.add(self.wr1)
        # right wide recicver
        self.wr2 = WR(game = self, x = games.screen.width * 3 / 4,
                      y = games.screen.height * 3 / 4, side="r")
        games.screen.add(self.wr2)

        # elevate bar sprite and scoreboard sprites above all other sprites
        self.bar.elevate()
        self.sBoard.elevate()

    def change_offence(self):
        """ Changes the team that is on offence """
        if self.team1_offence:
            self.team1_offence = False
        else:
            self.team1_offence = True

    def penalize(self, yards, string):
        """ Moves penalized team 'yards' back and displays a message object
        with the value of 'string' """
        self.remove_players()
        self.sBoard.stop_clock()
        self.play_is_over = True
        self.line_of_scrimmage -= 36 * yards
        message = ftxt.Football_message(game = self, value = string,
                                        x = games.screen.width / 2,
                                        y = games.screen.height / 2)
        games.screen.add(message)

    def end_game(self):
        """ Method evoked at the end of the game """
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

        text = ftxt.Play_again_text(game = self, x = games.screen.width / 2,
                                    bottom = games.screen.height - 10)
        games.screen.add(text)

    def show_settings(self):
        games.screen.clear()

        self.c_settings = ftxt.Clock_settings(game = self)
        games.screen.add(self.c_settings)

        self.s_settings = ftxt.Sound_settings(game = self)
        games.screen.add(self.s_settings)

        text = ftxt.Settings_exit(game = self)
        games.screen.add(text)

    def play_sound(self, sound, loop = 0):
        """ Plays 'sound' if sound setting is on """
        if self.sound_set:
            sound.play(loop)

    def remove_players(self):
        """ Removes all football players from the screen """
        for sprite in games.screen.all_objects:
            if sprite not in self.do_not_destroy:
                sprite.destroy()

    def get_clock_rate(self):
        return self.clock_rate

    def get_sound_set(self):
        return self.sound_set

def main():
    football = Game()
    football.set_variables()
    football.pick_teams()
    games.screen.mainloop()

# run program
main()
