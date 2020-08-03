# Football Players
#
# This module contains all of the player objects needed for 'Football.py'

# info list:
# [qb, rb1, rb2, rb3, wr1, wr2, wr3, wr4, wr5, lt, lg, c, rt, rg, te1, te2, p,
#  stwr1, stwr2, stol1, stol2, stol3, stc, stol4, stol5, stol6, stol7, dl1, dl2,
#  dl3, dl4, dl5, lb1, lb2, lb3, cb1, cb2, s1, s2, stdl1, stdl2, stdl3, stdl4,
#  stdl5, stlb1, stlb2, stlb3, stlb4, stcb1, stcb2, pr]
# len: 51

# imports
from livewires import games
import math, random, football_text as ftxt

class Shadow(games.Sprite):
    def __init__(self, sprite, xoffset=0, yoffset=0, halfarc=None,
                 midarcxoffset=None, midarcyoffset=None, txoffset=0,
                 tyoffset=0):
        super(Shadow, self).__init__(self.change_image(sprite.image),
                                     sprite.angle, sprite.x + xoffset,
                                     sprite.y + yoffset, is_collideable=False)

        self.sprite = sprite
        self.xoffset = xoffset
        self.yoffset = yoffset
        self.halfarc = halfarc
        self.midarcxoffset = midarcxoffset
        self.midarcyoffset = midarcyoffset
        self.has_traveled = 0
        self.past_half = False
        self.mxoffset = xoffset
        self.myoffset = yoffset
        self.txoffset = txoffset
        self.tyoffset = tyoffset

    def change_image(self, image):
        image = image.convert()
        for x in range(image.get_width()):
            for y in range(image.get_height()):
                if image.get_at((x, y)) != image.get_colorkey():
                    image.set_at((x, y), (0, 0, 0))
        image.set_alpha(150)
        return image

    def update_position(self):
        if self.halfarc != None and self.has_traveled >= 0:
            if self.past_half == False:
                self.has_traveled += math.sqrt(abs(self.x-self.sprite.x-self.xoffset)**2 + abs(self.y-self.sprite.y-self.yoffset)**2)
            else:
                self.has_traveled -= math.sqrt(abs(self.x-self.sprite.x-self.xoffset)**2 + abs(self.y-self.sprite.y-self.yoffset)**2)
            if self.has_traveled > self.halfarc:
                self.past_half = True
            if self.halfarc != None:
                self.xoffset = (self.has_traveled / self.halfarc) * self.midarcxoffset
                self.yoffset = (self.has_traveled / self.halfarc) * self.midarcyoffset

        self.x = self.sprite.x + self.xoffset
        self.y = self.sprite.y + self.yoffset
        self.angle = self.sprite.angle

    def tackle_data(self):
        self.image = self.change_image(self.sprite.image)
        self.xoffset = self.txoffset
        self.yoffset = self.tyoffset

    def main_data(self):
        self.image = self.change_image(self.sprite.image)
        self.xoffset = self.mxoffset
        self.yoffset = self.myoffset

class Football(games.Animation):
    """ The football """
    def __init__(self, player, play, x, y, angle, to_go=0):
        """ Initializes object """
        self.player = player
        self.game = player.game
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
            self.to_go = self.game.bar.length * 2
            interval = 2
            self.speed = 8
            
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
            self.to_go = self.game.bar.length * 2
            interval = 1
            self.speed = 8

        self.x_change = self.speed * math.sin(math.radians(angle))
        self.y_change = self.speed * -math.cos(math.radians(angle))

        super(Football, self).__init__(images, angle, x, y,
                                       repeat_interval=interval, n_repeats=0)

    def update(self):
        if self.loop:
            if self.bottom < self.game.field.bottom - self.game.line_of_scrimmage - 360:
                self.game.passed_line = True

            if self.player and (not self.overlaps(self.player) or self.play == "bounce"):
                self.player = None

            if self.play == "pass":
                self.to_go -= self.speed
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
                        if sprite in self.game.players and sprite != self.game.qb:
                            sprite.ball_overlap(self)

            elif self.play == "hike":
                self.x += self.x_change
                self.y += self.y_change
                for sprite in self.overlapping_sprites:
                    if sprite in self.game.players and sprite != self.game.center:
                        sprite.ball_overlap(self)

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
                    if sprite in self.game.players:
                        sprite.ball_overlap(self)

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

                if self.speed < 8:
                    for sprite in self.overlapping_sprites:
                        if sprite in self.game.players:
                            sprite.ball_overlap(self)

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

        super(Arms, self).__init__(images=images,
                                   x=self.player.x + self.xshift * math.sin(math.radians(self.player.angle + self.angshift + 90)),
                                   y=self.player.y + self.xshift * -math.cos(math.radians(self.player.angle + self.angshift + 90)),
                                   angle=self.player.angle + self.angshift,
                                   repeat_interval=interval,
                                   n_repeats=0,
                                   is_collideable=is_collideable)
        games.screen.add(self)
        self.lower(self.player)

        if self.command == "hold ball":
            self.shadow = Shadow(self, 2, 3)
            games.screen.add(self.shadow)
            self.shadow.elevate(self.player.game.field)

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

            self.shadow.x = self.player.shadow.x + self.xshift * math.sin(math.radians(self.player.shadow.angle + self.angshift + 90))
            self.shadow.y = self.player.shadow.y + self.xshift * -math.cos(math.radians(self.player.shadow.angle + self.angshift + 90))
            self.shadow.angle = self.angle

        if self.player.game.play_status == 1:
            self.destroy()

    def destroy(self):
        self.player.arms = False
        self.shadow.destroy()
        try:
            self.player.game.non_activated_sprites.remove(self)
        except(ValueError):
            pass
        super(Arms, self).destroy()

class Legs(games.Animation):
    """ The legs of a football player """
    WALK_INTERVAL = 4
    RUN_INTERVAL = 2
    def __init__(self, player, images):
        """ Initializes object """
        self.player = player
        if self.player.speed == self.player.speed_r:
            interval = Legs.RUN_INTERVAL

        elif self.player.speed == self.player.speed_w:
            interval = Legs.WALK_INTERVAL

        super(Legs, self).__init__(images=images,
                                   x=self.player.x, y=self.player.y,
                                   angle=self.player.angle,
                                   repeat_interval=interval,
                                   n_repeats=0, is_collideable=False)
        games.screen.add(self)
        self.lower(self.player.shadow)

        self.player.game.non_activated_sprites.append(self) # 'Legs' object will move with the player it is attached to

    def update_position(self):
        self.x = self.player.x
        self.y = self.player.y
        self.angle = self.player.angle

        if self.player.speed == self.player.speed_r:
            self.interval = Legs.RUN_INTERVAL

        elif self.player.speed == self.player.speed_w:
            self.interval = Legs.WALK_INTERVAL

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
    BASE_LEG_IMAGE = games.load_image("images\\dot.bmp")
    hit = games.load_sound("sounds\\hit.wav")

    def __init__(self, image, angle=0, x=0, y=0):
        super(Basic_player, self).__init__(image, angle, x, y)
        self.shadow = Shadow(self, 2, 3, txoffset=1, tyoffset=1)
        games.screen.add(self.shadow)
        self.shadow.elevate(self.game.field)

    def update(self):
        if self.tackled > 0:
            self.tackled -= 1
            if self.tackled == 0:
                self.image = self.main_image
                del self.main_image
                self.shadow.main_data()

        self.shadow.update_position()
        if self.legs and games.screen.all_objects:
            self.legs.update_position()

    def load_images(self, team, position, place):
        """ Loads all images necessary for object """
        team = team.lower()
        self.tackled_i = games.load_image("images\\" + team + position + place + "tackled.bmp")
        self.leg_i = games.load_animation(
                     ["images\\" + team + "leg" + place + "1.bmp",
                      "images\\" + team + "leg" + place + "2.bmp",
                      "images\\" + team + "leg" + place + "3.bmp",
                      "images\\" + team + "leg" + place + "2.bmp",
                      "images\\" + team + "leg" + place + "1.bmp",
                      "images\\dot.bmp",
                      "images\\" + team + "leg" + place + "4.bmp",
                      "images\\" + team + "leg" + place + "5.bmp",
                      "images\\" + team + "leg" + place + "6.bmp",
                      "images\\" + team + "leg" + place + "5.bmp",
                      "images\\" + team + "leg" + place + "4.bmp",
                      "images\\dot.bmp"])
        return games.load_image("images\\" + team + position + place + ".bmp")

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
        if not self.legs and self.speed != 0 and games.screen.all_objects:
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
        if not self.legs and self.speed != 0 and self in games.screen.all_objects:
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
        self.game.play_sound(Basic_player.hit)
        self.elevate(player)
        self.tackled = 350
        player.tackled = 375
        self.main_image = self.image
        player.main_image = player.image
        angle1 = (player.angle - 90) % 360
        angle2 = (player.angle + 90) % 360
        if (angle1 < self.angle < angle2) or ((angle1 < self.angle < 360 or 0 <= self.angle < angle2) and angle2 < 180):
            player.image = player.tackled_i
        else:
            player.image = player.tackled_i1
        self.image = self.tackled_i
        player.speed = 0
        self.speed = 0
        self.shadow.tackle_data()
        player.shadow.tackle_data()

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
                    if self.bottom < self.game.field.bottom - self.game.line_of_scrimmage - 360:
                        self.game.passed_line = True
                    # rotate sprite based on keys pressed
                    if games.keyboard.is_pressed(games.K_RIGHT):
                        self.angle += 4

                    if games.keyboard.is_pressed(games.K_LEFT):
                        self.angle -= 4

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
            message = ftxt.Football_message(self.game, "Fumble!",
                                            x=games.screen.width / 2,
                                            y=games.screen.height / 2)
            games.screen.add(message)

            football = Football(self, "bounce",
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

    def ball_overlap(self, ball):
        if (self not in self.game.can_not_catch or ball.play != "pass") and not self.tackled and ball.player != self:
            self.game.ball_carrier = self
            ball.destroy()
            if ball.play == "punt":
                self.game.for_first_down = 360
                self.game.line_of_scrimmage = 3600 - (self.game.field.bottom - self.y - 360)
                self.game.play_status = 1
                self.game.down = 0
                self.game.change_offence()

class Basic_defense(Basic_player):
    """ Base class for defensive players """
    intercept = None

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

                elif self.speed != 0:
                    self.move(self.speed)

        super(Basic_defense, self).update()

    def tackle(self, player):
        super(Basic_defense, self).tackle(player)
        if random.randrange(25) == 0:
            message = ftxt.Football_message(self.game, "Fumble!",
                                            x=games.screen.width / 2,
                                            y=games.screen.height / 2)
            games.screen.add(message)

            football = Football(self, "bounce",
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
                message = ftxt.Football_message(self.game, "Safety!",
                                                x=games.screen.width / 2,
                                                y=games.screen.height / 2)
                games.screen.add(message)
            else:
                self.game.for_first_down -= self.game.field.bottom - self.game.line_of_scrimmage - 360 - player.y
                self.game.line_of_scrimmage = self.game.field.bottom - player.y - 360

    def ball_overlap(self, ball):
        if not self.tackled and ball.player != self:
            if ball.play == "pass":
                if self not in self.game.can_not_catch:
                    if Basic_defense.intercept == 0:
                        self.game.ball_carrier = self
                        ball.destroy()
                        message = ftxt.Football_message(self.game, "Interception!",
                                                        x=games.screen.width / 2,
                                                        y=games.screen.height / 2)
                        games.screen.add(message)
                        self.reset_intercept()
                    else:
                        Basic_defense.intercept -= 1
                        print Basic_defense.intercept
            else:
                self.game.ball_carrier = self
                ball.destroy()
        ###########
        #if (self not in self.game.can_not_catch or ball.play != "pass") and not self.tackled and ball.player != self:
        #    self.game.ball_carrier = self
        #    ball.destroy()
        #    if ball.play == "pass":
        #        message = ftxt.Football_message(self.game, "Interception!",
        #                                        x=games.screen.width / 2,
        #                                        y=games.screen.height / 2)
        #        games.screen.add(message)

    def reset_intercept():
        Basic_defense.intercept = 50 + random.randrange(150)
    reset_intercept = staticmethod(reset_intercept)

class QB(Basic_offence):
    """ The quarterback """
    base_speed = None
    base_speed1 = None
    
    def __init__(self, game, x, y):
        """ Initializes object """
        self.game = game
        # if team 1 is on offence
        if self.game.team1_offence:
            image, self.tackled_i, self.tackled_i1 = self.game.team1_images[0]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        # if team 2 is on offence
        else:
            image, self.tackled_i, self.tackled_i1 = self.game.team2_images[0]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])
        
        super(QB, self).__init__(image, x=x, y=y)

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
        self.tackled = 0
        self.arm_side = 0

    def update(self):
        if not self.tackled:
            if self == self.game.ball_carrier:
                if games.keyboard.is_pressed(games.K_SPACE):
                    self.game.bar.advance()

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
                    football = Football(self, "pass",
                         10 * math.sin(math.radians(self.angle + 90)) + self.x,
                         10 * -math.cos(math.radians(self.angle + 90)) + self.y,
                        self.angle)
                    games.screen.add(football)
                    self.game.bar.reset()

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
            if self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[4]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[5]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        else:
            if self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[4]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[5]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])

        super(WR, self).__init__(image, x=x, y=y)

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
        self.tackled = 0

        if self.game.play_num == 1:
            self.markers = [(1245, 10), (1245, 600)]
        elif self.game.play_num == 2:
            if self.side == "l":
                self.markers = [(1305, 675)]
            elif self.side == "r":
                self.markers = [(615, 525)]
        elif self.game.play_num == 3:
            if self.side == "l":
                self.markers = [(705, 600)]
            elif self.side == "r":
                self.markers = [(615, 525)]
        elif self.game.play_num == 4:
            if self.side == "l":
                self.markers = [(1305, 675)]
            elif self.side == "r":
                self.markers = [(1215, 50), (1515, 50)]
        elif self.game.play_num == 5:
            if self.side == "l":
                self.markers = [(705, 350), (1305, 350)]
            elif self.side == "r":
                self.markers = [(1215, 125), (615, 125)]
        elif self.game.play_num == 6:
            if self.side == "l":
                self.markers = [(705, 200), (960, 125), (1600, 200)]
            elif self.side == "r":
                self.markers = [(1215, 350), (815, 650)]

    def update(self):
        if not self.tackled:
            if not self == self.game.ball_carrier:
                if self.game.play_status == 0:
                    if self.markers == []:
                        self.speed = 0
                    else:
                        if self.game.field.left + self.markers[0][0] - 3 < self.x < self.game.field.left + self.markers[0][0] + 3 and self.game.field.bottom - self.game.line_of_scrimmage - 360 - self.markers[0][1] - 3 < self.y < self.game.field.bottom - self.game.line_of_scrimmage - 360 - self.markers[0][1] + 3:
                            del self.markers[0]
                        if self.markers != []:
                            self.speed = self.speed_r
                            self.angle = 90 + math.degrees(math.atan2((self.game.field.bottom - self.game.line_of_scrimmage - 360 - self.markers[0][1]) - self.y,
                                                                       self.game.field.left + self.markers[0][0] - self.x))

        # get Basic_offence's update method
        super(WR, self).update()

    def overlap_func(self):
        self.slide(-self.speed_w)

class RB(Basic_offence):
    """ A running back """
    base_speed = None
    base_speed1 = None
    
    def __init__(self, game, x, y, num):
        """ Initializes object """
        self.game = game
        self.num = num
        if self.game.team1_offence:
            if self.num == "1":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[1]
            elif self.num == "2":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[2]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        else:
            if self.num == "1":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[1]
            elif self.num == "2":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[2]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])

        super(RB, self).__init__(image, x=x, y=y)

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

    sound = games.load_sound("sounds\\hut.wav")
    
    def __init__(self, game, x, y):
        """ Initializes object """
        self.game = game
        if self.game.team1_offence:
            image, self.tackled_i, self.tackled_i1 = self.game.team1_images[11]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        else:
            image, self.tackled_i, self.tackled_i1 = self.game.team2_images[11]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])

        super(Center, self).__init__(image, x=x, y=y)

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
        self.tackled = 0
        self.opponent = None

    def update(self):
        if not self.tackled:
            if not self == self.game.ball_carrier:
                if self.game.play_status == 0:
                    if self.opponent == None:
                        for player in self.game.d_players:
                            if not player.tackled and self.x - 40 < player.x < self.x + 40 and self.y - 20 < player.y < self.y + 20:
                                for ol in (self.game.llol, self.game.lol, self.game.rol, self.game.rrol, self.game.te1):
                                    if ol != None and ol.opponent == player:
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
                    self.game.play_sound(Center.sound)
                    # initialize football sprite
                    football = Football(self, "hike", self.x, self.y + 10, 180)
                    games.screen.add(football)
                    self.can_snap = False

        super(Center, self).update()

class OL(Basic_offence):
    """ An offencive line player """
    base_speed = None
    base_speed1 = None
    block = None
    block1 = None

    def __init__(self, game, x, y, side):
        self.game = game
        self.side = side
        if self.game.team1_offence:
            if self.side == "ll":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[9]
            elif self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[10]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[12]
            elif self.side == "rr":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[13]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        else:
            if self.side == "ll":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[9]
            elif self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[10]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[12]
            elif self.side == "rr":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[13]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])

        super(OL, self).__init__(image, x=x, y=y)

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

class TE(Basic_offence):
    """ A tight end """
    base_speed = None
    base_speed1 = None
    block = None
    block1 = None
    
    def __init__(self, game, x, y, num):
        """ Initializes object """
        self.game = game
        self.num = num
        if self.game.team1_offence:
            if self.num == "1":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[14]
            elif self.num == "2":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[15]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        else:
            if self.num == "1":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[14]
            elif self.num == "2":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[15]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])

        super(TE, self).__init__(image, x=x, y=y)

        self.game.players.append(self) # add self to list of all players
        self.game.o_players.append(self) # add self to list of offencive players

        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = TE.base_speed / 2
            self.speed_r = TE.base_speed
            self.block = TE.block
        else:
            self.speed_w = TE.base_speed1 / 2
            self.speed_r = TE.base_speed1
            self.block = TE.block1
        self.timer = self.block
        self.legs = False
        self.arms = False
        self.tackled = 0
        self.opponent = None
        if self.game.play_num == 6:
            self.markers = [(1080, 20), (1680, 620)]

    def update(self):
        if not self.tackled:
            if not self == self.game.ball_carrier:
                if self.game.play_status == 0:
                    if self.game.play_num in (1, 3):
                        if self.opponent == None:
                            for player in self.game.d_players:
                                if not player.tackled and self.x - 50 < player.x < self.x + 40 and self.y - 50 < player.y < self.y + 40:
                                    for ol in (self.game.llol, self.game.lol, self.game.rol, self.game.rrol, self.game.center):
                                        if ol != None and ol.opponent == player:
                                            break
                                    else:
                                        self.opponent = player
                                        if self not in self.game.can_not_catch:
                                            self.game.can_not_catch.append(self)
                                    if self.opponent != None:
                                        break

                    if self.opponent != None:
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

                    elif self.game.play_num == 3:
                        if self.game.rb1 == self.game.ball_carrier and self.game.rb1.x > self.game.field.left + 1080:
                            self.speed = self.speed_r
                            self.angle = self.game.rb1.angle

                    elif self.game.play_num == 6:
                        if self.markers == []:
                            self.speed = 0
                        else:
                            if self.game.field.left + self.markers[0][0] - 3 < self.x < self.game.field.left + self.markers[0][0] + 3 and self.game.field.bottom - self.game.line_of_scrimmage - 360 - self.markers[0][1] - 3 < self.y < self.game.field.bottom - self.game.line_of_scrimmage - 360 - self.markers[0][1] + 3:
                                del self.markers[0]
                            if self.markers != []:
                                self.speed = self.speed_w
                                self.angle = 90 + math.degrees(math.atan2((self.game.field.bottom - self.game.line_of_scrimmage - 360 - self.markers[0][1]) - self.y,
                                                                           self.game.field.left + self.markers[0][0] - self.x))

        super(TE, self).update()

class Punter(Basic_offence):
    """ The punter """
    base_speed = None
    base_speed1 = None
    
    def __init__(self, game, x, y):
        """ Initializes object """
        self.game = game
        if self.game.team1_offence:
            image, self.tackled_i, self.tackled_i1 = self.game.team1_images[16]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        else:
            image, self.tackled_i, self.tackled_i1 = self.game.team2_images[16]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])
        
        super(Punter, self).__init__(image, x=x, y=y)

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
        self.tackled = 0

    def update(self):
        if not self.tackled:
            if self == self.game.ball_carrier:
                if games.keyboard.is_pressed(games.K_SPACE):
                    self.game.bar.advance()

                if games.keyboard.is_pressed(games.K_m):
                    self.speed = 0
                    football = Football(self, "punt",
                        5 * math.sin(math.radians(self.angle + 90)) + self.x,
                        5 * -math.cos(math.radians(self.angle + 90)) + self.y,
                        self.angle)
                    games.screen.add(football)
                    self.game.bar.reset()

        super(Punter, self).update()

class STCenter(Basic_offence):
    base_speed = None
    base_speed1 = None
    block = None
    block1 = None

    sound = games.load_sound("sounds\\hut.wav")
    
    def __init__(self, game, x, y):
        """ Initializes object """
        self.game = game
        if self.game.team1_offence:
            image, self.tackled_i, self.tackled_i1 = self.game.team1_images[22]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        else:
            image, self.tackled_i, self.tackled_i1 = self.game.team2_images[22]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])

        super(STCenter, self).__init__(image, x=x, y=y)

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
                    self.game.play_sound(STCenter.sound)
                    # initialize football sprite
                    football = Football(self, "hike", self.x, self.y + 10, 180)
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
            if self.side == "ll":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[20]
            elif self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[21]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[23]
            elif self.side == "rr":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[24]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        else:
            if self.side == "ll":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[20]
            elif self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[21]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[23]
            elif self.side == "rr":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[24]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])

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

class DL(Basic_defense):
    base_speed = None
    base_speed1 = None

    def __init__(self, game, x, y, side):
        self.game = game
        self.side = side
        if self.game.team1_offence:
            if self.side == "ll":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[27]
            elif self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[28]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[29]
            elif self.side == "rr":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[30]
            elif self.side == "rrr":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[31]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])

        else:
            if self.side == "ll":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[27]
            elif self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[28]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[29]
            elif self.side == "rr":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[30]
            elif self.side == "rrr":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[31]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        super(DL, self).__init__(image, 180, x, y)

        self.game.players.append(self) # add self to list of all players
        self.game.d_players.append(self) # add self to list of defensive players
        self.game.can_not_catch.append(self)

        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = DL.base_speed / 2
            self.speed_r = DL.base_speed
        else:
            self.speed_w = DL.base_speed1 / 2
            self.speed_r = DL.base_speed1
        self.legs = False
        self.arms = False
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
        super(DL, self).update()

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
            if self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[32]
            elif self.side == "c":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[33]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[34]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])

        else:
            if self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[32]
            elif self.side == "c":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[33]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[34]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        super(LB, self).__init__(image, 180, x, y)

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
        self.tackled = 0

    def update(self):
        if not self.tackled:
            if not self == self.game.ball_carrier:
                if self.game.play_status == 0:
                    if self.game.blitz != 0:
                        self.speed = self.speed_r
                        self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                    elif self.game.ball_carrier in self.game.o_players:
                        if self.game.passed_line:
                            distance = abs((self.x - self.game.ball_carrier.x) / -math.cos(self.angle)) * 9/10
                            self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y + distance * -math.cos(math.radians(self.game.ball_carrier.angle)) - self.y,
                                                                      self.game.ball_carrier.x + distance * math.sin(math.radians(self.game.ball_carrier.angle)) - self.x))
                            self.speed = self.speed_r
                        elif self.side == "r":
                            if self.game.ball_carrier.x < self.game.field.left + 860:
                                if self.game.ball_carrier.y < self.game.field.bottom - self.game.line_of_scrimmage - 340:
                                    distance = abs((self.x - self.game.ball_carrier.x) / -math.cos(self.angle)) * 9/10
                                    self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y + distance * -math.cos(math.radians(self.game.ball_carrier.angle)) - self.y,
                                                                              self.game.ball_carrier.x + distance * math.sin(math.radians(self.game.ball_carrier.angle)) - self.x))
                                    self.speed = self.speed_r
                                else:
                                    if self.game.ball_carrier.x < self.x - 50 and self.x > self.game.field.left + 200:
                                        self.slide(self.speed_r)
                                    elif self.game.ball_carrier.x > self.x + 50 and self.x < self.game.field.left + 1020:
                                        self.slide(-self.speed_r)
                            else:
                                self.speed = 0
                        elif self.side == "c":
                            if self.game.field.left + 860 <= self.game.ball_carrier.x <= self.game.field.right - 860 and self.game.ball_carrier.y < self.game.field.bottom - self.game.line_of_scrimmage - 350:
                                distance = abs((self.x - self.game.ball_carrier.x) / -math.cos(self.angle)) * 9/10
                                self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y + distance * -math.cos(math.radians(self.game.ball_carrier.angle)) - self.y,
                                                                          self.game.ball_carrier.x + distance * math.sin(math.radians(self.game.ball_carrier.angle)) - self.x))
                                self.speed = self.speed_r
                            else:
                                self.speed = 0
                        elif self.side == "l":
                            if self.game.ball_carrier.x > self.game.field.right - 860:
                                if self.game.ball_carrier.y < self.game.field.bottom - self.game.line_of_scrimmage - 340:
                                    distance = abs((self.x - self.game.ball_carrier.x) / -math.cos(self.angle)) * 9/10
                                    self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y + distance * -math.cos(math.radians(self.game.ball_carrier.angle)) - self.y,
                                                                              self.game.ball_carrier.x + distance * math.sin(math.radians(self.game.ball_carrier.angle)) - self.x))
                                    self.speed = self.speed_r
                                else:
                                    if self.game.ball_carrier.x > self.x + 50 and self.x < self.game.field.right - 200:
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
            if self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[35]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[36]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])

        else:
            if self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[35]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[36]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        super(CB, self).__init__(image, 180, x, y)

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
            if self.num == "1":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[37]
            elif self.num == "2":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[38]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])

        else:
            if self.num == "1":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[37]
            elif self.num == "2":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[38]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        super(Safety, self).__init__(image, 180, x, y)

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
                            if self.game.ball_carrier.y < self.y + 50:
                                self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                                self.speed = self.speed_r
                            else:
                                if self.num == "1":
                                    if self.game.ball_carrier.x > self.x:
                                        if self.x < self.game.field.x - 40:
                                            self.slide(-self.speed_r)
                                    else:
                                        if self.x > self.game.field.left + 200:
                                            self.slide(self.speed_r)
                                elif self.num == "2":
                                    if self.game.ball_carrier.x < self.x:
                                        if self.x > self.game.field.x + 40:
                                            self.slide(self.speed_r)
                                    else:
                                        if self.x < self.game.field.right - 200:
                                            self.slide(-self.speed_r)
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

class STDL(Basic_defense):
    base_speed = None
    base_speed1 = None

    def __init__(self, game, x, y, side):
        self.game = game
        self.side = side
        if self.game.team1_offence:
            if self.side == "ll":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[39]
            elif self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[40]
            elif self.side == "c":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[41]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[42]
            elif self.side == "rr":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[43]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])

        else:
            if self.side == "ll":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[39]
            elif self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[40]
            elif self.side == "c":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[41]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[42]
            elif self.side == "rr":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[43]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        super(STDL, self).__init__(image, 180, x, y)

        self.game.players.append(self) # add self to list of all players
        self.game.d_players.append(self) # add self to list of defensive players
        self.game.can_not_catch.append(self)

        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = STDL.base_speed / 2
            self.speed_r = STDL.base_speed
        else:
            self.speed_w = STDL.base_speed1 / 2
            self.speed_r = STDL.base_speed1
        self.legs = False
        self.arms = False
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
        super(STDL, self).update()

    def overlap_func(self):
        self.move(-self.speed, False)
        if "l" in self.side:
            self.slide(-self.speed_r)
        else:
            self.slide(self.speed_r)

class STLB(Basic_defense):
    base_speed = None
    base_speed1 = None

    def __init__(self, game, x, y, side):
        self.game = game
        self.side = side
        if self.game.team1_offence:
            if self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[44]
            elif self.side == "c":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[45]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team2_images[46]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])

        else:
            if self.side == "l":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[44]
            elif self.side == "c":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[45]
            elif self.side == "r":
                image, self.tackled_i, self.tackled_i1 = self.game.team1_images[46]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        super(STLB, self).__init__(image, 180, x, y)

        self.game.players.append(self) # add self to list of all players
        self.game.d_players.append(self) # add self to list of defensive players
        self.game.can_not_catch.append(self)

        self.speed = 0
        if self.game.team1_offence:
            self.speed_w = STLB.base_speed / 2
            self.speed_r = STLB.base_speed
        else:
            self.speed_w = STLB.base_speed1 / 2
            self.speed_r = STLB.base_speed1
        self.legs = False
        self.arms = False
        self.tackled = 0

    def update(self):
        if not self.tackled:
            if not self == self.game.ball_carrier:
                if self.game.play_status == 0:
                    if self.game.ball_carrier not in self.game.players and self.game.ball_carrier.play == "punt":
                        self.speed = self.speed_r
                        self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                    elif self.game.ball_carrier in self.game.o_players:
                        if self.game.passed_line:
                            self.speed = self.speed_r
                            self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y - self.y, self.game.ball_carrier.x - self.x))
                        elif self.side == "r":
                            if self.game.ball_carrier.x < self.game.field.left + 860:
                                if self.game.ball_carrier.y < self.game.field.bottom - self.game.line_of_scrimmage - 340:
                                    distance = abs((self.x - self.game.ball_carrier.x) / -math.cos(self.angle)) * 9/10
                                    self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y + distance * -math.cos(math.radians(self.game.ball_carrier.angle)) - self.y,
                                                                              self.game.ball_carrier.x + distance * math.sin(math.radians(self.game.ball_carrier.angle)) - self.x))
                                    self.speed = self.speed_r
                                else:
                                    if self.game.ball_carrier.x < self.x - 50 and self.x > self.game.field.left + 200:
                                        self.slide(self.speed_r)
                                    elif self.game.ball_carrier.x > self.x + 50 and self.x < self.game.field.left + 1020:
                                        self.slide(-self.speed_r)
                            else:
                                self.speed = 0
                        elif self.side == "c":
                            if self.game.field.left + 860 <= self.game.ball_carrier.x <= self.game.field.right - 860 and self.game.ball_carrier.y < self.game.field.bottom - self.game.line_of_scrimmage - 350:
                                distance = abs((self.x - self.game.ball_carrier.x) / -math.cos(self.angle)) * 9/10
                                self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y + distance * -math.cos(math.radians(self.game.ball_carrier.angle)) - self.y,
                                                                          self.game.ball_carrier.x + distance * math.sin(math.radians(self.game.ball_carrier.angle)) - self.x))
                                self.speed = self.speed_r
                            else:
                                self.speed = 0
                        elif self.side == "l":
                            if self.game.ball_carrier.x > self.game.field.right - 860:
                                if self.game.ball_carrier.y < self.game.field.bottom - self.game.line_of_scrimmage - 340:
                                    distance = abs((self.x - self.game.ball_carrier.x) / -math.cos(self.angle)) * 9/10
                                    self.angle = 90 + math.degrees(math.atan2(self.game.ball_carrier.y + distance * -math.cos(math.radians(self.game.ball_carrier.angle)) - self.y,
                                                                              self.game.ball_carrier.x + distance * math.sin(math.radians(self.game.ball_carrier.angle)) - self.x))
                                    self.speed = self.speed_r
                                else:
                                    if self.game.ball_carrier.x > self.x + 50 and self.x < self.game.field.right - 200:
                                        self.slide(-self.speed_r)
                                    elif self.game.ball_carrier.x < self.x - 50 and self.x > self.game.field.right - 1020:
                                        self.slide(self.speed_r)
                            else:
                                self.speed = 0
                    else:
                        self.speed = 0
            
        # get Basic_defense's update method
        super(STLB, self).update()

class PR(Basic_defense):
    base_speed = None
    base_speed1 = None

    def __init__(self, game, x, y):
        self.game = game
        if self.game.team1_offence:
            image, self.tackled_i, self.tackled_i1 = self.game.team2_images[50]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team2 + "lega1.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega3.bmp",
                      "images\\" + self.game.team2 + "lega2.bmp",
                      "images\\" + self.game.team2 + "lega1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega6.bmp",
                      "images\\" + self.game.team2 + "lega5.bmp",
                      "images\\" + self.game.team2 + "lega4.bmp",
                      "images\\dot.bmp"])

        else:
            image, self.tackled_i, self.tackled_i1 = self.game.team1_images[50]
            self.leg_i = games.load_animation(
                     ["images\\" + self.game.team1 + "legh1.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh3.bmp",
                      "images\\" + self.game.team1 + "legh2.bmp",
                      "images\\" + self.game.team1 + "legh1.bmp",
                      "images\\dot.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh6.bmp",
                      "images\\" + self.game.team1 + "legh5.bmp",
                      "images\\" + self.game.team1 + "legh4.bmp",
                      "images\\dot.bmp"])

        super(PR, self).__init__(image, 180, x, y)

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
