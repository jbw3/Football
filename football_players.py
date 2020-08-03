# Football Text
#
# This module contains all of the player objects needed for 'Football.py'

# imports
from livewires import games
import math, random, football_text as ftxt

class Football(games.Animation):
    """ The football """
    def __init__(self, play, game, x, y, angle, to_go=0):
        """ Initializes object """
        self.game = game
        self.play = play
        self.to_go = to_go
        self.loop = True
        self.game.ball_carrier = self
        if self.play == "pass":
            images = ["images\\football1.bmp",
                      "images\\football2.bmp",
                      "images\\football3.bmp",
                      "images\\football3.bmp",
                      "images\\football4.bmp"]
            self.to_go = self.game.bar.right * 3
            interval = 2
            self.speed = 7
            
        elif self.play == "hike":
            images = ["images\\football1.bmp"]
            self.game.play_status = 0
            self.game.sBoard.start_clock()
            interval = 10
            self.speed = 7

        elif self.play == "bounce":
            images = ["images\\football1.bmp",
                      "images\\football9.bmp",
                      "images\\football8.bmp",
                      "images\\football7.bmp",
                      "images\\football3.bmp",
                      "images\\football7.bmp",
                      "images\\football6.bmp",
                      "images\\football5.bmp"]
            self.to_go = 15 * random.randrange(2, 4)
            interval = 2
            self.speed = 4

        elif self.play == "punt":
            images = ["images\\football1.bmp",
                       "images\\football5.bmp",
                       "images\\football6.bmp",
                       "images\\football7.bmp",
                       "images\\football3.bmp",
                       "images\\football7.bmp",
                       "images\\football8.bmp",
                       "images\\football9.bmp"]
            interval = 1
            self.speed = 8

        self.x_change = self.speed * math.sin(math.radians(angle))
        self.y_change = self.speed * -math.cos(math.radians(angle))

        super(Football, self).__init__(images=images, x=x, y=y,
                                       angle=angle, repeat_interval=interval,
                                       n_repeats=0)

    def update(self):
        if self.loop:
            if self.play == "pass":
                self.to_go -= 7
                if self.to_go <= 0:
                    self.x_change = 0
                    self.y_change = 0
                    self.game.ball_incomplete = True
                    self.game.play_status = 1
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
                if self.to_go > 0:
                    for sprite in games.screen.get_all_objects():
                        if sprite != self and sprite not in self.game.non_activated_sprites:
                            sprite.x -= self.x_change
                            sprite.y -= self.y_change
                    for sprite in self.overlapping_sprites:
                        if sprite in self.game.players:
                            break
                    else:
                        self.to_go -= self.speed

                else:
                    self.images = [games.load_image("images\\football1.bmp")]

                for sprite in self.overlapping_sprites:
                    if sprite in self.game.players and not sprite.tackled:
                        self.game.ball_carrier = sprite
                        self.destroy()

            elif self.play == "punt":
                if self.to_go > 0:
                    for sprite in games.screen.get_all_objects():
                        if sprite != self and sprite not in self.game.non_activated_sprites:
                            sprite.x -= self.x_change
                            sprite.y -= self.y_change
                    self.to_go -= self.speed

                if self.top < self.game.field.top + 360 and self.game.play_status == 0:
                    self.game.sBoard.stop_clock()
                    self.game.for_first_down = 360
                    self.game.line_of_scrimmage = 720
                    self.game.play_status = 1
                    self.game.down = 0
                    self.game.change_offence()

                if (self.left < self.game.field.left or self.right > self.game.field.right) and self.game.play_status == 0:
                    self.game.sBoard.stop_clock()
                    self.game.for_first_down = 360
                    self.game.line_of_scrimmage = self.game.field.bottom - self.y - 360
                    self.game.play_status = 1
                    self.game.down = 0
                    self.game.change_offence()

                if self.to_go <= 0:
                    if self.speed == 8:
                        self.images = games.load_animation(
                                      ["images\\football1.bmp",
                                       "images\\football9.bmp",
                                       "images\\football8.bmp",
                                       "images\\football7.bmp",
                                       "images\\football3.bmp",
                                       "images\\football7.bmp",
                                       "images\\football6.bmp",
                                       "images\\football5.bmp"])
                        self.to_go = 15 * random.randrange(12, 48)
                        self.angle = random.randrange(360)
                        self.interval = 2
                        self.speed = 4
                        self.x_change = self.speed * math.sin(math.radians(self.angle))
                        self.y_change = self.speed * -math.cos(math.radians(self.angle))

                    elif self.speed == 4:
                        self.images = [games.load_image("images\\football1.bmp")]

                if self.speed < 8 or self.to_go <= 16:
                    for sprite in self.overlapping_sprites:
                        if not sprite.tackled:
                            if sprite in self.game.d_players:
                                self.game.ball_carrier = sprite
                            else:
                                self.game.for_first_down = 360
                                self.game.line_of_scrimmage = 3600 - (self.game.field.bottom - sprite.y - 360)
                                self.game.play_status = 1
                                self.game.down = 0
                                self.game.change_offence()
                            self.destroy()

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

        if self.player.game.play_status == 1:
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

        super(Legs, self).__init__(images=images,
                                   x=self.player.x, y=self.player.y,
                                   angle=self.player.angle,
                                   repeat_interval=interval,
                                   n_repeats=0, is_collideable=False)
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

        if self.player.game.play_status == 1:
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
    BASE_LEG_IMAGE = games.load_image("images\\feet.bmp")

    def update(self):
        if self.tackled > 0:
            self.tackled -= 1
            if self.tackled == 0:
                self.image = self.main_image
                del self.main_image

    def load_images(self, team, position, place):
        """ Loads all images necessary for object """
        team = team.lower()
        self.tackled_i = games.load_image("images\\" + team + position + place + "tackled.bmp")
        self.leg_i = [games.load_image("images\\" + team + "leg" + place + "1.bmp"),
                      games.load_image("images\\" + team + "leg" + place + "2.bmp")]
        return games.load_image("images\\" + team + position + place + ".bmp")

    def create_leg_list(self, add_list, every):
        insert = every
        while insert <= len(add_list):
            add_list[insert:insert] = [Basic_player.BASE_LEG_IMAGE]
            insert += every + 1

        return add_list

    def turn(self, sprite):
        """ Rotate sprite """
        angle = 90 + math.degrees(math.atan2(sprite.y - self.y, sprite.x - self.x))

    def adjust(self, speed):
        """ Calculate sprites x_change and y_change """
        x_move = True
        y_move = True
        for sprite in self.overlapping_sprites:
            if sprite in self.game.players:
                if speed > 0:
                    if sprite.y - 2 < self.top < sprite.bottom:
                        if 270 < self.angle < 360 or 0 <= self.angle < 90:
                            y_move = False
                    elif sprite.y + 2 > self.bottom > sprite.top:
                        if 90 < self.angle < 270:
                            y_move = False
                    elif sprite.x > self.right > sprite.left:
                        if 0 < self.angle < 180:
                            x_move = False
                    elif sprite.x < self.left < sprite.right:
                        if 180 < self.angle < 360:
                            x_move = False
                elif speed < 0:
                    if sprite.y - 2 < self.top < sprite.bottom:
                        if 90 < self.angle < 270:
                            y_move = False
                    elif sprite.y + 2 > self.bottom > sprite.top:
                        if 270 < self.angle < 360 or 0 <= self.angle < 90:
                            y_move = False
                    elif sprite.x > self.right > sprite.left:
                        if 180 < self.angle < 360:
                            x_move = False
                    elif sprite.x < self.left < sprite.right:
                        if 0 < self.angle < 180:
                            x_move = False

        if x_move:
            x_change = speed * math.sin(math.radians(self.angle))
        else:
            x_change = 0

        if y_move:
            y_change = speed * -math.cos(math.radians(self.angle))
        else:
            y_change = 0

        for sprite in games.screen.get_all_objects():
            if sprite != self and sprite not in self.game.non_activated_sprites:
                sprite.x -= x_change
                sprite.y -= y_change

        # set leg images
        if not self.legs and games.screen.all_objects:
            self.legs = Legs(player=self, images=self.leg_i)

    def move(self, speed, func=True):
        """ Moves sprite """
        x_move = True
        y_move = True
        if self.overlapping_sprites:
            for sprite in self.overlapping_sprites:
                if sprite in self.game.players:
                    if self.game.ball_carrier == sprite:
                        if self in self.game.o_players and sprite in self.game.d_players:
                            self.tackle(sprite)
                            x_move = False
                            y_move = False
                            break
                        elif self in self.game.d_players and sprite in self.game.o_players:
                            self.tackle(sprite)
                            x_move = False
                            y_move = False
                            break

                    if speed > 0:
                        if sprite.top < self.top < sprite.bottom:
                            if 270 < self.angle < 360 or 0 <= self.angle < 90:
                                y_move = False
                                self.top = sprite.bottom
                        elif sprite.bottom > self.bottom > sprite.top:
                            if 90 < self.angle < 270:
                                y_move = False
                                self.bottom = sprite.top
                        elif sprite.x > self.right > sprite.left:
                            if 0 < self.angle < 180:
                                x_move = False
                                self.right = sprite.left
                        elif sprite.x < self.left < sprite.right:
                            if 180 < self.angle < 360:
                                x_move = False
                                self.left = sprite.right
                    elif speed < 0:
                        if sprite.top < self.top < sprite.bottom:
                            if 90 < self.angle < 270:
                                y_move = False
                        elif sprite.bottom > self.bottom > sprite.top:
                            if 270 < self.angle < 360 or 0 <= self.angle < 90:
                                y_move = False
                        elif sprite.x > self.right > sprite.left:
                            if 180 < self.angle < 360:
                                x_move = False                        
                        elif sprite.x < self.left < sprite.right:
                            if 0 < self.angle < 180:
                                x_move = False
            if func and not self.tackled:
                self.overlap_func()

        if x_move:
            self.x += speed * math.sin(math.radians(self.angle))
        if y_move:
            self.y += speed * -math.cos(math.radians(self.angle))

        # set leg images
        if not self.legs and self in games.screen.all_objects:
            self.legs = Legs(player=self, images=self.leg_i)

    def slide(self, amount):
        """ Moves sprite to the left or right """
        x_move = True
        y_move = True
        for sprite in self.overlapping_sprites:
            if sprite in self.game.players:
                if amount < 0:
                    if sprite.top < self.top < sprite.bottom:
                        if 0 < self.angle < 180:
                            y_move = False
                    if sprite.bottom > self.bottom > sprite.top:
                        if 180 < self.angle < 360:
                            y_move = False
                    if sprite.left < self.left < sprite.right:
                        if 270 < self.angle <= 360 or 0 < self.angle < 90:
                            x_move = False
                    if sprite.right > self.right > sprite.left:
                        if 90 < self.angle < 270:
                            x_move = False

                elif amount > 0:
                    if sprite.top < self.top < sprite.bottom:
                        if 180 < self.angle < 360:
                            y_move = False
                    if sprite.bottom > self.bottom > sprite.top:
                        if 0 < self.angle < 180:
                            y_move = False
                    if sprite.left < self.left < sprite.right:
                        if 90 < self.angle < 270:
                            x_move = False
                    if sprite.right > self.right > sprite.left:
                        if 270 < self.angle <= 360 or 0 < self.angle < 90:
                            x_move = False

        if x_move:
            self.x -= amount * math.sin(math.radians(self.angle - 90))
        if y_move:
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
        if not self.tackled:
            if self.game.play_status == 0:                    
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
                        # sets sprite's speed based on keys pressed
                        if games.keyboard.is_pressed(games.K_RALT) or games.keyboard.is_pressed(games.K_LALT):
                            self.speed = self.speed_w
                        else:
                            self.speed = self.speed_r
                        self.adjust(self.speed)

                    # make sprite move in the opposite direction it is pointing
                    if games.keyboard.is_pressed(games.K_DOWN):
                        # sets sprite's speed based on keys pressed
                        if games.keyboard.is_pressed(games.K_RALT) or games.keyboard.is_pressed(games.K_LALT):
                            self.speed = self.speed_w
                        else:
                            self.speed = self.speed_r
                        self.adjust(-self.speed)

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
                        self.move(self.speed)

        super(Basic_offence, self).update()

    def tackle(self, player):
        """ Method to make self tackle 'player' """
        super(Basic_offence, self).tackle(player)
        if random.randrange(25) == 0:
            message = ftxt.Football_message(game = self.game, value = "Fumble!",
                                            x = games.screen.width / 2,
                                            y = games.screen.height / 2)
            games.screen.add(message)

            football = Football("bounce", self.game,
                                player.x + 25 * math.sin(math.radians(player.angle)),
                                player.y + 25 * -math.cos(math.radians(player.angle)),
                                player.angle)
            games.screen.add(football)
        else:
            self.game.play_status = 1
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
        if not self.tackled:
            if self.game.play_status == 0:
                if self.game.ball_carrier not in self.game.players and self.game.ball_carrier.play == "bounce":
                        self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                        self.speed = self.speed_r

                if self == self.game.ball_carrier:
                    self.speed = self.speed_r
                    self.adjust(self.speed)
                    if self.angle < 178:
                        self.angle += 3
                    elif self.angle > 182:
                        self.angle -= 3
                    else:
                        self.angle = 180

                else:
                    self.move(self.speed)

        super(Basic_defense, self).update()

    def tackle(self, player):
        super(Basic_defense, self).tackle(player)
        if random.randrange(25) == 0:
            message = ftxt.Football_message(game=self.game, value="Fumble!",
                                            x=games.screen.width / 2,
                                            y=games.screen.height / 2)
            games.screen.add(message)

            football = Football("bounce", self.game,
                                player.x + 25 * math.sin(math.radians(player.angle)),
                                player.y + 25 * -math.cos(math.radians(player.angle)),
                                player.angle)
            games.screen.add(football)
        else:
            self.game.play_status = 1
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
                if self.game.quarter == 5:
                    self.game.end_game()
                else:
                    message = ftxt.Football_message(game = self.game,
                                                    x = games.screen.width / 2,
                                                    y = games.screen.height / 2,
                                                    value = "Safety!")
                    games.screen.add(message)
            else:
                self.game.for_first_down -= self.game.field.bottom - self.game.line_of_scrimmage - 360 - player.y
                self.game.line_of_scrimmage = self.game.field.bottom - player.y - 360

class QB(Basic_offence):
    """ The quarterback """
    base_speed = None
    base_speed1 = None
    
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
        if self.game.team1_offence:
            self.speed_w = QB.base_speed / 2
            self.speed_r = QB.base_speed
        else:
            self.speed_w = QB.base_speed1 / 2
            self.speed_r = QB.base_speed1
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0
        self.arm_side = 0

    def update(self):
        if not self.tackled:
            if self == self.game.ball_carrier:
                if games.keyboard.is_pressed(games.K_SPACE) and self.game.bar.left < 0:
                    self.game.bar.x += 7

                if games.keyboard.is_pressed(games.K_PERIOD):
                    if self.arm_side != 1:
                        if self.arms:
                            self.arms.destroy()
                        if self.game.team1_offence:
                            self.arms = Arms(self, ["images\\" + self.game.team1 + "qbarm.bmp"], "hold ball", 18, is_collideable=True)
                        else:
                            self.arms = Arms(self, ["images\\" + self.game.team2 + "qbarm.bmp"], "hold ball", 18, is_collideable=True)
                        self.arm_side = 1

                elif games.keyboard.is_pressed(games.K_COMMA):
                    if self.arm_side != -1:
                        if self.arms:
                            self.arms.destroy()
                        if self.game.team1_offence:
                            self.arms = Arms(self, ["images\\" + self.game.team1 + "qbarm.bmp"], "hold ball", 18, 180, True)
                        else:
                            self.arms = Arms(self, ["images\\" + self.game.team2 + "qbarm.bmp"], "hold ball", 18, 180, True)
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
    base_speed = None
    base_speed1 = None
    
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
        if self.game.team1_offence:
            self.speed_w = WR.base_speed / 2
            self.speed_r = WR.base_speed
        else:
            self.speed_w = WR.base_speed1 / 2
            self.speed_r = WR.base_speed1
        self.timer = 0
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0

    def update(self):
        if not self.tackled:
            if not self == self.game.ball_carrier:
                if self.game.play_status == 0:
                    #-------------------- plays --------------------
                    if self.game.play_num == 1:
                        self.speed = self.speed_r

                    elif self.game.play_num == 2:
                        self.speed = self.speed_r
                        if self.side == "l":
                            self.angle = 70
                        else:
                            self.angle = 300

                    elif self.game.play_num == 3:
                        self.speed = self.speed_r
                        if self.side == "l":
                            self.angle = 315
                        elif self.side == "r":
                            if self.y < self.game.field.bottom - self.game.line_of_scrimmage - 410:
                                if self.angle > 270 or self.angle == 0:
                                    self.angle -= 3
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

                    elif self.game.play_num == 6:
                        self.speed = self.speed_r
                        if self.side == "l":
                            if self.y < self.game.field.bottom - self.game.line_of_scrimmage - 560 and self.x < self.game.field.left + 960:
                                self.angle = 105
                            elif self.x > self.game.field.left + 920:
                                self.angle = 75
                        elif self.side == "r":
                            if self.y < self.game.field.bottom - self.game.line_of_scrimmage - 660:
                                self.angle = 315
                    #-----------------------------------------------

        # get Basic_offence's update method
        super(WR, self).update()

    def overlap_func(self):
        self.slide(-self.speed_w)

class RB(Basic_offence):
    """ The center """
    base_speed = None
    base_speed1 = None
    
    def __init__(self, game, x, y, num):
        """ Initializes object """
        self.game = game
        self.num = num
        if self.game.team1_offence:
            image = self.load_images(self.game.team1, "rb" + self.num, "h")

        else:
            image = self.load_images(self.game.team2, "rb" + self.num, "a")

        super(RB, self).__init__(image=image, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.o_players.append(self) # add self to list of offencive players

        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = RB.base_speed / 2
            self.speed_r = RB.base_speed
        else:
            self.speed_w = RB.base_speed1 / 2
            self.speed_r = RB.base_speed1
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0

    def update(self):
            if not self.tackled:
                if not self == self.game.ball_carrier:
                    if self.game.play_status == 0:
                        #-------------------- plays --------------------
                        if self.game.play_num == 1:
                            self.speed = self.speed_r
                            if self.y < self.game.field.bottom - self.game.line_of_scrimmage - 360 + 150:
                                if self.num == "1":
                                    if self.angle < 45:
                                        self.angle += 3
                                else:
                                    if self.angle == 0 or self.angle > 315:
                                        self.angle -= 3

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

                        elif self.game.play_num == 6:
                            self.speed = self.speed_r
                            if self.angle == 0 or self.angle > 315:
                                self.angle -= 3
                        #-----------------------------------------------

            # get Basic_offence's update method
            super(RB, self).update()

class Center(Basic_offence):
    """ The center """
    base_speed = None
    base_speed1 = None
    block = None
    block1 = None
    
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
        if self.game.team1_offence:
            self.speed_w = Center.base_speed / 2
            self.speed_r = Center.base_speed
            self.block = Center.block
        else:
            self.speed_w = Center.base_speed1 / 2
            self.speed_r = Center.base_speed1
            self.block = Center.block1
        self.timer = self.block
        self.can_snap = True
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0
        self.opponent = None

    def update(self):
        if not self.tackled:
            if not self == self.game.ball_carrier:
                if self.game.play_status == 0:
                    if self.opponent == None:
                        for player in self.game.d_players:
                            if not player.tackled and self.x - 40 < player.x < self.x + 40 and self.y - 20 < player.y < self.y + 20:
                                for ol in [self.game.llol, self.game.lol, self.game.rol, self.game.rrol]:
                                    if ol.opponent == player:
                                        break
                                else:
                                    self.opponent = player
                                if self.opponent != None:
                                    break
                    else:
                        if self.game.ball_carrier in self.game.o_players and self.opponent.speed != 0:
                            self.speed = self.speed_r
                            if self.x - 60 < self.opponent.x < self.x + 60 and self.y - 60 < self.opponent.y < self.y + 60:
                                self.speed = 0
                                self.angle = 180 + self.opponent.angle
                                if self.timer == 0:
                                    self.timer = self.block
                                else:
                                    if self.opponent.x < self.x:
                                        self.slide(-self.speed_r)
                                    elif self.opponent.x > self.x:
                                        self.slide(self.speed_r)
                                    self.timer -= 1
                            else:
                                self.angle = 90 + math.degrees(math.atan2(((self.opponent.y - self.game.ball_carrier.y) / 4 + self.game.ball_carrier.y) - self.y, ((self.opponent.x - self.game.ball_carrier.x) / 4 + self.game.ball_carrier.x) - self.x))
                                self.speed = self.speed_r
                        else:
                            self.speed = 0

            if self.can_snap:
                if games.keyboard.is_pressed(games.K_SPACE) and self.game.play_status != 0:
                    # initialize football sprite
                    football = Football(play = "hike", game = self.game,
                                        x = self.x, y = self.y + 10, angle = 180)
                    games.screen.add(football)
                    self.can_snap = False

        super(Center, self).update()

class OL(Basic_offence):
    base_speed = None
    base_speed1 = None
    block = None
    block1 = None

    def __init__(self, game, x, y, side):
        self.game = game
        self.side = side
        if self.game.team1_offence:
            image = self.load_images(self.game.team1, self.side + "ol", "h")

        else:
            image = self.load_images(self.game.team2, self.side + "ol", "a")

        super(OL, self).__init__(image=image, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.o_players.append(self) # add self to list of offencive players
        self.game.can_not_catch.append(self)

        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = OL.base_speed / 2
            self.speed_r = OL.base_speed
            self.block = OL.block
        else:
            self.speed_w = OL.base_speed1 / 2
            self.speed_r = OL.base_speed1
            self.block = OL.block1
        self.timer = self.block
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
        if not self.tackled:
            if not self == self.game.ball_carrier:
                if self.game.play_status == 0:
                    if self.game.ball_carrier in self.game.o_players and self.opponent.speed != 0:
                        self.speed = self.speed_r
                        if self.x - 60 < self.opponent.x < self.x + 60 and self.y - 60 < self.opponent.y < self.y + 60:
                            self.speed = 0
                            self.angle = 180 + self.opponent.angle
                            if self.timer == 0:
                                self.timer = self.block
                            else:
                                if self.opponent.x < self.x:
                                    self.slide(-self.speed_r)
                                elif self.opponent.x > self.x:
                                    self.slide(self.speed_r)
                                self.timer -= 1
                        else:
                            self.angle = 90 + math.degrees(math.atan2(((self.opponent.y - self.game.ball_carrier.y) / 4 + self.game.ball_carrier.y) - self.y, ((self.opponent.x - self.game.ball_carrier.x) / 4 + self.game.ball_carrier.x) - self.x))
                            self.speed = self.speed_r
                    else:
                        self.speed = 0

        super(OL, self).update()

class Punter(Basic_offence):
    """ The punter """
    base_speed = None
    base_speed1 = None
    
    def __init__(self, game, x, y):
        """ Initializes object """
        self.game = game
        # if team 1 is on offence
        if self.game.team1_offence:
            image = self.load_images(self.game.team1, "p", "h")

        # if team 2 is on offence
        else:
            image = self.load_images(self.game.team2, "p", "a")
        
        super(Punter, self).__init__(image=image, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.o_players.append(self) # add self to list of offencive players

        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = Punter.base_speed / 2
            self.speed_r = Punter.base_speed
        else:
            self.speed_w = Punter.base_speed1 / 2
            self.speed_r = Punter.base_speed1
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0

    def update(self):
        if not self.tackled:
            if self == self.game.ball_carrier:
                if games.keyboard.is_pressed(games.K_SPACE) and self.game.bar.left < 0:
                    self.game.bar.x += 10
                    if self.game.bar.left > 0:
                        self.game.bar.left = 0

                if games.keyboard.is_pressed(games.K_m):
                    self.speed = 0
                    football = Football("punt", self.game,
                        5 * math.sin((self.angle + 90) * math.pi / 180) + self.x,
                        5 * -math.cos((self.angle + 90) * math.pi / 180) + self.y,
                        self.angle, self.game.bar.right * 3)
                    games.screen.add(football)
                    self.game.bar.right = 0

        super(Punter, self).update()

class STCenter(Basic_offence):
    base_speed = None
    base_speed1 = None
    block = None
    block1 = None
    
    def __init__(self, game, x, y):
        """ Initializes object """
        self.game = game
        if self.game.team1_offence:
            image = self.load_images(self.game.team1, "stc", "h")

        else:
            image = self.load_images(self.game.team2, "stc", "a")

        super(STCenter, self).__init__(image=image, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.o_players.append(self) # add self to list of offencive players
        self.game.can_not_catch.append(self)
        self.game.ball_carrier = self

        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = STCenter.base_speed / 2
            self.speed_r = STCenter.base_speed
            self.block = STCenter.block
        else:
            self.speed_w = STCenter.base_speed1 / 2
            self.speed_r = STCenter.base_speed1
            self.block = STCenter.block1
        self.timer = self.block
        self.can_snap = True
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0
        self.opponent = self.game.ctackle

    def update(self):
        if not self.tackled:
            if not self == self.game.ball_carrier:
                if self.game.play_status == 0:
                    if self.game.ball_carrier not in self.game.players and self.game.ball_carrier.play == "punt":
                        self.speed = self.speed_r
                        self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                    elif self.game.ball_carrier in self.game.o_players:
                        if self.opponent.speed != 0:
                            self.speed = self.speed_r
                            if self.x - 60 < self.opponent.x < self.x + 60 and self.y - 60 < self.opponent.y < self.y + 60:
                                self.speed = 0
                                self.angle = 180 + self.opponent.angle
                                if self.timer == 0:
                                    self.timer = self.block
                                else:
                                    if self.opponent.x < self.x:
                                        self.slide(-self.speed_r)
                                    elif self.opponent.x > self.x:
                                        self.slide(self.speed_r)
                                    self.timer -= 1
                            else:
                                self.angle = 90 + math.degrees(math.atan2(((self.opponent.y - self.game.ball_carrier.y) / 4 + self.game.ball_carrier.y) - self.y, ((self.opponent.x - self.game.ball_carrier.x) / 4 + self.game.ball_carrier.x) - self.x))
                                self.speed = self.speed_r
                        else:
                            self.speed = 0

            if self.can_snap:
                if games.keyboard.is_pressed(games.K_SPACE) and self.game.play_status != 0:
                    # initialize football sprite
                    football = Football(play = "hike", game = self.game,
                                        x = self.x, y = self.y + 10, angle = 180)
                    games.screen.add(football)
                    self.can_snap = False

        super(STCenter, self).update()

class STOL(Basic_offence):
    base_speed = None
    base_speed1 = None
    block = None
    block1 = None

    def __init__(self, game, x, y, side):
        self.game = game
        self.side = side
        if self.game.team1_offence:
            image = self.load_images(self.game.team1, self.side + "stol", "h")

        else:
            image = self.load_images(self.game.team2, self.side + "stol", "a")

        super(STOL, self).__init__(image=image, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.o_players.append(self) # add self to list of offencive players
        self.game.can_not_catch.append(self)

        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = STOL.base_speed / 2
            self.speed_r = STOL.base_speed
            self.block = STOL.block
        else:
            self.speed_w = STOL.base_speed1 / 2
            self.speed_r = STOL.base_speed1
            self.block = STOL.block1
        self.timer = self.block
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
        if not self.tackled:
            if not self == self.game.ball_carrier:
                if self.game.play_status == 0:
                    if self.game.ball_carrier not in self.game.players and self.game.ball_carrier.play == "punt":
                        self.speed = self.speed_r
                        self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                    elif self.game.ball_carrier in self.game.o_players:
                        if self.opponent.speed != 0:
                            self.speed = self.speed_r
                            if self.x - 60 < self.opponent.x < self.x + 60 and self.y - 60 < self.opponent.y < self.y + 60:
                                self.speed = 0
                                self.angle = 180 + self.opponent.angle
                                if self.timer == 0:
                                    self.timer = self.block
                                else:
                                    if self.opponent.x < self.x:
                                        self.slide(-self.speed_r)
                                    elif self.opponent.x > self.x:
                                        self.slide(self.speed_r)
                                    self.timer -= 1
                            else:
                                self.angle = 90 + math.degrees(math.atan2(((self.opponent.y - self.game.ball_carrier.y) / 4 + self.game.ball_carrier.y) - self.y, ((self.opponent.x - self.game.ball_carrier.x) / 4 + self.game.ball_carrier.x) - self.x))
                                self.speed = self.speed_r
                        else:
                            self.speed = 0

        super(STOL, self).update()

class Noseguard(Basic_defense):
    base_speed = None
    base_speed1 = None
    
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
        if self.game.team1_offence:
            self.speed_w = Noseguard.base_speed / 2
            self.speed_r = Noseguard.base_speed
        else:
            self.speed_w = Noseguard.base_speed1 / 2
            self.speed_r = Noseguard.base_speed1
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0

    def update(self):
        if not self.tackled:
            if not self == self.game.ball_carrier:
                if self.game.play_status == 0:
                    if self.game.ball_carrier in self.game.o_players and (self.game.ball_carrier.y > self.y - 20 or self.game.ball_carrier.speed < self.speed_r):
                        self.speed = self.speed_r
                        self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                    else:
                        self.speed = 0
            
        # get Basic_defense's update method
        super(Noseguard, self).update()

    def overlap_func(self):
        self.move(-self.speed, False)
        self.slide(-self.speed_r)

class Tackle(Basic_defense):
    base_speed = None
    base_speed1 = None

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
        if self.game.team1_offence:
            self.speed_w = Tackle.base_speed / 2
            self.speed_r = Tackle.base_speed
        else:
            self.speed_w = Tackle.base_speed1 / 2
            self.speed_r = Tackle.base_speed1
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0

    def update(self):
        if not self.tackled:
            if not self == self.game.ball_carrier:
                if self.game.play_status == 0:
                    if self.game.ball_carrier in self.game.o_players and (self.game.ball_carrier.y > self.y - 20 or self.game.ball_carrier.speed < self.speed_r):
                        self.speed = self.speed_r
                        self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                    else:
                        self.speed = 0
            
        # get Basic_defense's update method
        super(Tackle, self).update()

    def overlap_func(self):
        self.move(-self.speed, False)
        if "l" in self.side:
            self.slide(-self.speed_r)
        else:
            self.slide(self.speed_r)

class LB(Basic_defense):
    base_speed = None
    base_speed1 = None

    def __init__(self, game, x, y, side):
        self.game = game
        self.side = side
        if self.game.team1_offence:
            image = self.load_images(self.game.team2, self.side + "lb", "a")

        else:
            image = self.load_images(self.game.team1, self.side + "lb", "h")

        super(LB, self).__init__(image=image, angle=180, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.d_players.append(self) # add self to list of defensive players
        self.game.can_not_catch.append(self)

        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = LB.base_speed / 2
            self.speed_r = LB.base_speed
        else:
            self.speed_w = LB.base_speed1 / 2
            self.speed_r = LB.base_speed1
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0

    def update(self):
        if not self.tackled:
            if not self == self.game.ball_carrier:
                if self.game.play_status == 0:
                    if self.game.blitz != 0:
                        self.speed = self.speed_r
                        self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                    elif self.game.ball_carrier in self.game.o_players:
                        if self.game.ball_carrier.y < self.game.field.bottom - self.game.line_of_scrimmage - 360:
                            self.speed = self.speed_r
                            self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                        elif self.side == "r":
                            if self.game.ball_carrier.x < self.game.field.left + 860:
                                if self.game.ball_carrier.y < self.game.field.bottom - self.game.line_of_scrimmage - 340:
                                    self.speed = self.speed_r
                                    self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                                else:
                                    if self.game.ball_carrier.x < self.x - 50 and self.x > self.game.field.left + 480:
                                        self.slide(self.speed_r)
                                    elif self.game.ball_carrier.x > self.x + 50 and self.x < self.game.field.left + 1020:
                                        self.slide(-self.speed_r)
                            else:
                                self.speed = 0
                        elif self.side == "c":
                            if self.game.field.left + 860 <= self.game.ball_carrier.x <= self.game.field.right - 860 and self.game.ball_carrier.y < self.game.field.bottom - self.game.line_of_scrimmage - 350:
                                self.speed = self.speed_r
                                self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                            else:
                                self.speed = 0
                        elif self.side == "l":
                            if self.game.ball_carrier.x > self.game.field.right - 860:
                                if self.game.ball_carrier.y < self.game.field.bottom - self.game.line_of_scrimmage - 340:
                                    self.speed = self.speed_r
                                    self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                                else:
                                    if self.game.ball_carrier.x > self.x + 50 and self.x < self.game.field.right - 480:
                                        self.slide(-self.speed_r)
                                    elif self.game.ball_carrier.x < self.x - 50 and self.x > self.game.field.right - 1020:
                                        self.slide(self.speed_r)
                            else:
                                self.speed = 0

        # get Basic_defense's update method
        super(LB, self).update()

class CB(Basic_defense):
    base_speed = None
    base_speed1 = None

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
        if self.game.team1_offence:
            self.speed_w = CB.base_speed / 2
            self.speed_r = CB.base_speed
        else:
            self.speed_w = CB.base_speed1 / 2
            self.speed_r = CB.base_speed1
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0
        self.timer = 5

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.timer = 5
        if not self.tackled:
            if self.game.play_status == 0:
                if not self == self.game.ball_carrier:
                    if self.game.ball_carrier == self.game.qb and self.game.qb.y < self.game.field.bottom - self.game.line_of_scrimmage - 360:
                        distance = abs((self.x - self.game.ball_carrier.x) / -math.cos(self.angle)) * 9/10
                        self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y + distance * -math.cos(math.radians(self.game.ball_carrier.angle)) - self.y,
                                                                  self.game.ball_carrier.x + distance * math.sin(math.radians(self.game.ball_carrier.angle)) - self.x))
                        self.speed = self.speed_r

                    else:
                        if self.game.ball_carrier in self.game.o_players and self.game.ball_carrier.y < self.game.field.bottom - self.game.line_of_scrimmage - 360:
                            distance = abs((self.x - self.game.ball_carrier.x) / -math.cos(self.angle)) * 9/10
                            self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y + distance * -math.cos(math.radians(self.game.ball_carrier.angle)) - self.y,
                                                                      self.game.ball_carrier.x + distance * math.sin(math.radians(self.game.ball_carrier.angle)) - self.x))
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

    def overlap_func(self):
        if self.side == "r":
            self.angle += 3
        elif self.side == "l":
            self.angle -= 3
        self.move(-self.speed, False)

class Safety(Basic_defense):
    base_speed = None
    base_speed1 = None
    base_speed2 = None
    base_speed3 = None

    def __init__(self, game, x, y, num):
        self.game = game
        self.num = num
        if self.game.team1_offence:
            image = self.load_images(self.game.team2, "s" + self.num, "a")
        else:
            image = self.load_images(self.game.team1, "s" + self.num, "h")

        super(Safety, self).__init__(image=image, angle=180, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.d_players.append(self) # add self to list of defensive players
        if (self.game.blitz == 2 and self.num == "1") or (self.game.blitz == 3 and self.num == "2") or self.game.blitz == 4:
            self.game.can_not_catch.append(self)

        self.speed = 0
        self.tracking = False
        if self.game.team1_offence:
            if self.num == "1":
                self.speed_w = Safety.base_speed / 2
                self.speed_r = Safety.base_speed
            else:
                self.speed_w = Safety.base_speed1 / 2
                self.speed_r = Safety.base_speed1
        else:
            if self.num == "1":
                self.speed_w = Safety.base_speed2 / 2
                self.speed_r = Safety.base_speed2
            else:
                self.speed_w = Safety.base_speed3 / 2
                self.speed_r = Safety.base_speed3
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0

    def update(self):
        if self.game.play_status == 0:
            if not self.tackled:
                if self != self.game.ball_carrier:
                    if self.game.ball_carrier in self.game.o_players and self.game.ball_carrier.y < self.game.field.bottom - self.game.line_of_scrimmage - 360:
                        distance = abs((self.x - self.game.ball_carrier.x) / -math.cos(self.angle)) * 9/10
                        self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y + distance * -math.cos(math.radians(self.game.ball_carrier.angle)) - self.y,
                                                                  self.game.ball_carrier.x + distance * math.sin(math.radians(self.game.ball_carrier.angle)) - self.x))
                        self.speed = self.speed_r
                    else:
                        if (self.game.blitz == 2 and self.num == "1") or (self.game.blitz == 3 and self.num == "2") or self.game.blitz == 4:
                            distance = abs((self.x - self.game.ball_carrier.x) / -math.cos(self.angle)) * 9/10
                            self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y + distance * -math.cos(math.radians(self.game.ball_carrier.angle)) - self.y,
                                                                      self.game.ball_carrier.x + distance * math.sin(math.radians(self.game.ball_carrier.angle)) - self.x))
                            self.speed = self.speed_r
                        elif self.game.ball_carrier not in self.game.players and self.game.ball_carrier.play != "hike":
                            self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                            self.speed = self.speed_r
                        else:
                            if self.num == "1":
                                if self.game.ball_carrier.x < self.x - 100 and self.x > self.game.field.left + 480:
                                    self.slide(self.speed_r)
                                elif self.game.ball_carrier.x > self.x + 100 and self.x < self.game.field.left + 768:
                                    self.slide(-self.speed_r)
                            elif self.num == "2":
                                if self.game.ball_carrier.x > self.x + 100 and self.x < self.game.field.right - 480:
                                    self.slide(-self.speed_r)
                                elif self.game.ball_carrier.x < self.x - 100 and self.x > self.game.field.right - 768:
                                    self.slide(self.speed_r)

        else:
            if ((self.game.blitz == 2 and self.num == "1") or (self.game.blitz == 3 and self.num == "2") or self.game.blitz == 4) and not self.game.play_status == 1:
                if self.y < self.game.field.bottom - self.game.line_of_scrimmage - 400:
                    self.speed = self.speed_r
                    self.move(self.speed)
                else:
                    self.speed = 0
                if self not in self.game.can_not_catch:
                    self.game.can_not_catch.append(self)

        # get Basic_defense's update method
        super(Safety, self).update()

    def overlap_func(self):
        self.slide(self.speed_w)

class STTackle(Basic_defense):
    base_speed = None
    base_speed1 = None

    def __init__(self, game, x, y, side):
        self.game = game
        self.side = side
        if self.game.team1_offence:
            image = self.load_images(self.game.team2, self.side + "stt", "a")

        else:
            image = self.load_images(self.game.team1, self.side + "stt", "h")

        super(STTackle, self).__init__(image=image, angle=180, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.d_players.append(self) # add self to list of defensive players
        self.game.can_not_catch.append(self)

        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = STTackle.base_speed / 2
            self.speed_r = STTackle.base_speed
        else:
            self.speed_w = STTackle.base_speed1 / 2
            self.speed_r = STTackle.base_speed1
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0

    def update(self):
        if not self.tackled:
            if not self == self.game.ball_carrier:
                if self.game.play_status == 0:
                    if self.game.ball_carrier not in self.game.players and self.game.ball_carrier.play == "punt":
                        self.speed = self.speed_r
                        self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                    elif self.game.ball_carrier in self.game.o_players and (self.game.ball_carrier.y > self.y - 20 or self.game.ball_carrier.speed < self.speed_r):
                        self.speed = self.speed_r
                        self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                    else:
                        self.speed = 0
            
        # get Basic_defense's update method
        super(STTackle, self).update()

    def overlap_func(self):
        self.move(-self.speed, False)
        if "l" in self.side:
            self.slide(-self.speed_r)
        else:
            self.slide(self.speed_r)

class PR(Basic_defense):
    base_speed = None
    base_speed1 = None

    def __init__(self, game, x, y):
        self.game = game
        if self.game.team1_offence:
            image = self.load_images(self.game.team2, "pr", "a")

        else:
            image = self.load_images(self.game.team1, "pr", "h")

        super(PR, self).__init__(image=image, angle=180, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.d_players.append(self) # add self to list of defensive players

        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = PR.base_speed / 2
            self.speed_r = PR.base_speed
        else:
            self.speed_w = PR.base_speed1 / 2
            self.speed_r = PR.base_speed1
        self.legs = False
        self.arms = False
        self.leg_i = self.create_leg_list(self.leg_i, 1)
        self.tackled = 0

    def update(self):
        if not self.tackled:
            if not self == self.game.ball_carrier:
                if self.game.play_status == 0:
                    if self.game.ball_carrier not in self.game.players and self.game.ball_carrier.play == "punt":
                        if self.game.ball_carrier.to_go <= 720:
                            self.speed = self.speed_r
                            self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y,
                                                                      self.game.ball_carrier.x - self.x))
                        else:
                            if self.game.ball_carrier.x > self.x + 4:
                                self.slide(-self.speed_r)
                            elif self.game.ball_carrier.x < self.x - 4:
                                self.slide(self.speed_r)
                    elif self.game.ball_carrier in self.game.o_players and self.game.ball_carrier.y < self.game.field.bottom - self.game.line_of_scrimmage - 360:
                        distance = abs((self.x - self.game.ball_carrier.x) / -math.cos(self.angle)) * 9/10
                        self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y + distance * -math.cos(math.radians(self.game.ball_carrier.angle)) - self.y,
                                                                  self.game.ball_carrier.x + distance * math.sin(math.radians(self.game.ball_carrier.angle)) - self.x))
                        self.speed = self.speed_r

        # get Basic_defense's update method
        super(PR, self).update()
