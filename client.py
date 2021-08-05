__author__ = 'amit stein'

import pygame
from math import atan2, cos, sin, degrees, hypot, pi
import socket
from sys import argv
# import classes
import time
import json

DEBUG = False
SIZE_HEADER_FORMAT = "000000|"
size_header_size = len(SIZE_HEADER_FORMAT)


def recv_by_size(sock):
    str_size = ""
    data_len = 0
    while len(str_size) < size_header_size:
        str_size += sock.recv(size_header_size - len(str_size))
        if str_size == "":
            break
    data = ""
    if str_size != "":
        data_len = int(str_size[:size_header_size - 1])
        while len(data) < data_len:
            data += sock.recv(data_len - len(data))
            if data == "":
                break
    if DEBUG and str_size != "" and len(data) < 100:
        print "\nReceived(%s)<<<%s" % (str_size, data)
    if data_len != len(data):
        data = ""
    return data


def send_with_size(sock, data):
    data = str(len(data)).zfill(size_header_size - 1) + "|" + data

    sock.send(data)

    if DEBUG and len(data) < 100:
        print "\nSent>>>" + data


############################################################
# graphic and game constants
# =======================================

# balls and table consts
MASS = 1
RADIUS = 10
MUE = 0.02
DRAG = 1 - MUE
ACCELARATION_CUE = 1.1
ELASTICITY_WALLS = 0.75
ELASTICITY_COLLISIONS = 0.3

# hole ranges - not good!!!! need circles and not squares!!:
# fuction who calc the distance between two points
LEFT_TOP_HOLE_X = 0
LEFT_TOP_HOLE_Y = 0

RIGHT_TOP_HOLE_X = 0
RIGHT_TOP_HOLE_Y = 0

LEFT_BOTTOM_HOLE_X = 0
LEFT_BOTTOM_HOLE_Y = 0

RIGHT_BOTTOM_HOLE_X = 0
RIGHT_BOTTOM_HOLE_Y = 0

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# screen sizes:
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1200

# table sizes:
TABLE_HEIGHT = 400
TABLE_WIDTH = 800

side_size = 40

# balls area:
BALLS_AREA_HEIGHT = TABLE_HEIGHT - side_size * 2
BALLS_AREA_WIDTH = TABLE_WIDTH - side_size * 2

table_place_X = TABLE_WIDTH / 4
table_place_Y = TABLE_HEIGHT / 4

# boundaries:
LEFT_BOUNDARY = table_place_X + side_size
TOP_BOUNDARY = table_place_Y + side_size
RIGHT_BOUNDARY = table_place_X + side_size + BALLS_AREA_WIDTH
BOTTOM_BOUNDARY = table_place_Y + side_size + BALLS_AREA_HEIGHT

# distance of x coordinate from first white ball place to the first ball of the balls triangle:
DISTANCE_BETWEEN_FIRST_WHITE_X_TO_FIRST_OTHERS_X = 500
DISTANCE_BETWEEN_LEFT_BOUNDARY_TO_FIRST_WHITE_X = 20

# middle white first place :
MIDDLE_WHITE_FIRST_PLACE_X = LEFT_BOUNDARY + DISTANCE_BETWEEN_LEFT_BOUNDARY_TO_FIRST_WHITE_X
MIDDLE_WHITE_FIRST_PLACE_Y = TOP_BOUNDARY + ((TABLE_HEIGHT - (2 * side_size)) / 2)

# middle other balls first place :
MIDDLE_OTHERS_FIRST_PLACE_X = MIDDLE_WHITE_FIRST_PLACE_X + DISTANCE_BETWEEN_FIRST_WHITE_X_TO_FIRST_OTHERS_X
MIDDLE_OTHERS_FIRST_PLACE_Y = MIDDLE_WHITE_FIRST_PLACE_Y

# other balls const places:
BALL_0_POS = (MIDDLE_WHITE_FIRST_PLACE_X, MIDDLE_WHITE_FIRST_PLACE_Y)  # white ball - defult place
BALL_1_POS = (MIDDLE_OTHERS_FIRST_PLACE_X, MIDDLE_WHITE_FIRST_PLACE_Y)  # LINE A
BALL_2_POS = (MIDDLE_OTHERS_FIRST_PLACE_X + (2 * RADIUS) - 2, MIDDLE_WHITE_FIRST_PLACE_Y - RADIUS)  # LINE B
BALL_3_POS = (MIDDLE_OTHERS_FIRST_PLACE_X + (2 * RADIUS) - 2, MIDDLE_WHITE_FIRST_PLACE_Y + RADIUS)  # LINE B
BALL_4_POS = (MIDDLE_OTHERS_FIRST_PLACE_X + (4 * RADIUS) - 4, MIDDLE_WHITE_FIRST_PLACE_Y - (2 * RADIUS))  # LINE C
BALL_8_POS = (MIDDLE_OTHERS_FIRST_PLACE_X + (4 * RADIUS) - 4,
              MIDDLE_WHITE_FIRST_PLACE_Y)  # LINE C # eight ball - this is the position of the 8 ball
BALL_5_POS = (MIDDLE_OTHERS_FIRST_PLACE_X + (4 * RADIUS) - 4, MIDDLE_WHITE_FIRST_PLACE_Y + (2 * RADIUS))  # LINE C
BALL_6_POS = (MIDDLE_OTHERS_FIRST_PLACE_X + (6 * RADIUS) - 6, MIDDLE_WHITE_FIRST_PLACE_Y - (3 * RADIUS))  # LINE D
BALL_7_POS = (MIDDLE_OTHERS_FIRST_PLACE_X + (6 * RADIUS) - 6, MIDDLE_WHITE_FIRST_PLACE_Y - RADIUS)  # LINE D
BALL_9_POS = (MIDDLE_OTHERS_FIRST_PLACE_X + (6 * RADIUS) - 6, MIDDLE_WHITE_FIRST_PLACE_Y + RADIUS)  # LINE D
BALL_10_POS = (MIDDLE_OTHERS_FIRST_PLACE_X + (6 * RADIUS) - 6, MIDDLE_WHITE_FIRST_PLACE_Y + (3 * RADIUS))  # LINE D
BALL_11_POS = (MIDDLE_OTHERS_FIRST_PLACE_X + (8 * RADIUS) - 8, MIDDLE_WHITE_FIRST_PLACE_Y - (4 * RADIUS))  # LINE E
BALL_12_POS = (MIDDLE_OTHERS_FIRST_PLACE_X + (8 * RADIUS) - 8, MIDDLE_WHITE_FIRST_PLACE_Y - (2 * RADIUS))  # LINE E
BALL_13_POS = (MIDDLE_OTHERS_FIRST_PLACE_X + (8 * RADIUS) - 8, MIDDLE_WHITE_FIRST_PLACE_Y)  # LINE E
BALL_14_POS = (MIDDLE_OTHERS_FIRST_PLACE_X + (8 * RADIUS) - 8, MIDDLE_WHITE_FIRST_PLACE_Y + (2 * RADIUS))  # LINE E
BALL_15_POS = (MIDDLE_OTHERS_FIRST_PLACE_X + (8 * RADIUS) - 8, MIDDLE_WHITE_FIRST_PLACE_Y + (4 * RADIUS))  # LINE E

PICTURES = {0: r'balls\billiard_ball_0.png', 1: r'balls\billiard_ball_1.png', 2: r'balls\billiard_ball_2.png',
            3: r'balls\billiard_ball_3.png',
            4: r'balls\billiard_ball_4.png', 5: r'balls\billiard_ball_5.png', 6: r'balls\billiard_ball_6.png',
            7: r'balls\billiard_ball_7.png',
            8: r'balls\billiard_ball_8.png', 9: r'balls\billiard_ball_9.png', 10: r'balls\billiard_ball_10.png',
            11: r'balls\billiard_ball_11.png',
            12: r'balls\billiard_ball_12.png', 13: r'balls\billiard_ball_13.png', 14: r'balls\billiard_ball_14.png',
            15: r'balls\billiard_ball_15.png'}

# pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])#,pygame.mouse])
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Billiard')
table = pygame.image.load('my_pool_table_big_up_side_down.png')  # 800*400
# backgroung = pygame.image.load('background.png')  #1200*600
SCREEN_BACKGROUND = pygame.image.load('smoke_cue_background.jpg')  # CHANGE TO BACKGROUND
# make icon
clock = pygame.time.Clock()

CUE_LENGTH = 360
END_OF_CUE_DISTANCE_FROM_WHITE_BALL = 3
CUE_FIRST_DISTANCE_FROM_BALL = CUE_LENGTH / 2 + 2 * RADIUS + END_OF_CUE_DISTANCE_FROM_WHITE_BALL  # the distance from the middle of the cue so its head almost touches the whire ball

DISTANCE_BETWEEN_BALLS_LEFT_OR_IN_HOLE = 2
DISTANCE_BETWEEN_BALLS_LEFT_OR_HOLE_AND_TABLE = RADIUS + 2
DISTANCE_ON_Y_BETWEEN_NAMES_AND_BALLS = 40

Y_BALLS_IN_HOLE = table_place_Y + TABLE_HEIGHT + DISTANCE_BETWEEN_BALLS_LEFT_OR_HOLE_AND_TABLE
X_BALLS_IN_HOLE = table_place_X + (TABLE_WIDTH / 2) - RADIUS - DISTANCE_BETWEEN_BALLS_LEFT_OR_IN_HOLE - 7 * (
            2 * RADIUS + DISTANCE_BETWEEN_BALLS_LEFT_OR_IN_HOLE)

Y_PLAYERS_BALLS_LEFT = table_place_Y - DISTANCE_BETWEEN_BALLS_LEFT_OR_HOLE_AND_TABLE
X_THIS_PLAYER_BALLS_LEFT = table_place_X + side_size + ((TABLE_WIDTH - 2 * side_size) / 4) - 3 * (
            RADIUS * 2 + DISTANCE_BETWEEN_BALLS_LEFT_OR_IN_HOLE)
X_OTHER_PLAYER_BALLS_LEFT = table_place_X + side_size + ((TABLE_WIDTH - 2 * side_size) / 2) + (
            (TABLE_WIDTH - 2 * side_size) / 4) - 3 * (RADIUS * 2 + DISTANCE_BETWEEN_BALLS_LEFT_OR_IN_HOLE)

Y_PLAYERS_NAME = Y_PLAYERS_BALLS_LEFT - RADIUS - DISTANCE_ON_Y_BETWEEN_NAMES_AND_BALLS
X_THIS_PLAYER_NAME = table_place_X + side_size + ((TABLE_WIDTH - 2 * side_size) / 4)
X_OTHER_PLAYER_NAME = table_place_X + side_size + ((TABLE_WIDTH - 2 * side_size) / 2) + (
            (TABLE_WIDTH - 2 * side_size) / 4)

PLAY_BUTTON_HEIGHT = 100
PLAY_BUTTON_WIDTH = 200
PLAY_BUTTON_X = (SCREEN_WIDTH / 2) - (PLAY_BUTTON_WIDTH / 2)
PLAY_BUTTON_Y = (SCREEN_HEIGHT / 2) - (PLAY_BUTTON_HEIGHT / 2)
PLAY_BUTTON_COLOR = WHITE

WELCOME_MSG_TXT = 'Billiard Game'
WELCOME_MSG_FONT = pygame.font.SysFont("David", 80)
WELCOME_MSG_COLOR = BLUE
WELCOME_MSG_POS = (SCREEN_WIDTH / 2, PLAY_BUTTON_Y - PLAY_BUTTON_HEIGHT)  # 0+,0+
REGULAR_MSG_FONT = pygame.font.SysFont("David", 36)
REGULAR_MSG_POS = (table_place_X + (TABLE_WIDTH / 2), (table_place_Y + TABLE_HEIGHT / 4))
REGULAR_MSG_COLOR = WHITE
BYE_BYE_MSG_POS = (table_place_X + (TABLE_WIDTH / 2), (table_place_Y + TABLE_HEIGHT / 2))
BYE_BYE_MSG_COLOR = BLUE
BYE_BYE_MSG_FONT = pygame.font.SysFont("David", 60)
PLAYERS_NAME_FONT = pygame.font.SysFont("David", 36)
PLAYERS_NAME_COLOR = WHITE
PLAY_BUTTON_FONT = pygame.font.SysFont("David", 36)
WAITING_MSG_COLOR = WHITE
WAITING_MSG_POS = (table_place_X + (TABLE_WIDTH / 2), (table_place_Y + TABLE_HEIGHT / 4))
WIN_LOSE_MAG_FONT = pygame.font.SysFont("David", 60)
FPS = 1000

# BACKGROUND_MUSIC = pygame.mixer.music.load()
COLLIDE_SOUND = pygame.mixer.Sound('collide_sound.wav')


def draw_table():
    screen.blit(table, (table_place_X, table_place_Y))


def draw_background():
    screen.blit(SCREEN_BACKGROUND, (0, 0))


#########################


class Game_Mode_enum:
    start_game = 1
    balls_moving = 2
    choosing_ball = 3
    choosing_velocity = 4
    end_game = 5
    choosing_pocket_for_black_ball = 6


class Player_Type_enum:
    player1 = 1
    player2 = 2
    unknown = 3  # if we have not decided yet who is who


class Ball_Types_enum:
    white = 1
    black = 2
    stripe = 3
    solid = 4
    unknown = 5


def get_game_mode_str(enum):
    if enum == Game_Mode_enum.start_game:
        return 'start_game'
    elif enum == Game_Mode_enum.choosing_ball:
        return 'choosing_ball'
    elif enum == Game_Mode_enum.choosing_velocity:
        return 'choosing_velocity'
    elif enum == Game_Mode_enum.balls_moving:
        return 'balls_moving'
    elif enum == Game_Mode_enum.choosing_pocket_for_black_ball:
        return 'choosing_pocket_for_black_ball'
    elif enum == Game_Mode_enum.end_game:
        return 'end_game'


def get_turn_str(enum):
    if enum == Player_Type_enum.player1:
        return 'player1 turn'
    else:
        return 'player2 turn'


def get_player_type_str(enum):
    if enum == Player_Type_enum.player1:
        return 'player1'
    else:
        return 'player2'


def get_balls_type_str(enum):
    if enum == Ball_Types_enum.unknown:
        return 'unknown'
    elif enum == Ball_Types_enum.stripe:
        return 'stripe'
    elif enum == Ball_Types_enum.solid:
        return 'solid'
    elif enum == Ball_Types_enum.white:
        return 'white'
    elif enum == Ball_Types_enum.black:
        return 'black'


'''
#TextBox class;
#Is used to get input in the graphics mode of pygame
class TextBox(object):
    def __init__(self):
        max_len = 10,
        x = -1,
        y = -1,
        surf = pygame.image.load("text_bar_surf.png")

        #Text font
        self.font = pygame.font.SysFont("David", 32)
        #Max length of the message
        self.max_len = max_len
        #Text of the message
        self.text = ""
        #The bg surface of the text box
        self.surf = surf
        #Text box location
        self.x = x
        self.y = y

    #Tick update of the text box. Returns true if player clicked enter
    def tick(self):
        for evt in pygame.event.get():
            if evt.type == pygame.KEYDOWN:
                if evt.unicode.isalnum() and len(self.text) < self.max_len:
                    self.text += evt.unicode
                    return False

                elif evt.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    return False

                elif evt.key == pygame.K_RETURN:
                    return True

    #Blits the text box to the given screen
    def blit(self, screen):
        screen.blit(self.surf, (self.x, self.y))
        screen.blit(self.font.render(self.text, True, (240, 240, 240)), (self.x + 15, self.y + 15))
'''


# x and y will be the center ot the text
def draw_massage_to_screen(msg, color, (x, y), font):
    screen_text = font.render(msg, True, color)
    screen_text_rect = screen_text.get_rect()
    screen_text_rect.center = (x, y)
    screen.blit(screen_text, screen_text_rect)


class Vector(object):
    def __init__(self, angle, size):
        self.angle = angle
        self.size = size

    def get_x(self):
        return sin(self.angle) * self.size

    def get_y(self):
        return cos(self.angle) * self.size

    def __repr__(self):
        return ('angle=' + str(degrees(self.angle)) + ',size=' + str(self.size))


class Hole(object):
    def __init__(self, TYPE, (x, y), velocity, picture):  # for example: self.white_ball.picture =
        self.x = x
        self.y = y
        self.radius = 2 * RADIUS
        self.TYPE = TYPE  ##enum class of six kinds


class Cue(object):
    def __init__(self, x, y, velocity, picture):
        self.x = x
        self.y = y
        self.velocity = velocity  # Vector velocity
        self.picture = picture  # for example: = pygame.image.load('ball_0.png')#20*20

    def rot_center(self, angle):
        """rotate an image while keeping its center and size"""
        orig_rect = self.picture.get_rect()
        rot_image = pygame.transform.rotate(self.picture, degrees(angle))
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        # rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    def draw(self, rot_image):
        center = (self.x - rot_image.get_rect().center[0], self.y - rot_image.get_rect().center[1])
        screen.blit(rot_image, (center))  # self.x,self.y))#center)

    def cue_move(self, with_accelaration):  # move back related to the distance between the mouse clicks
        self.x += self.velocity.get_x()
        self.y -= self.velocity.get_y()
        if with_accelaration:
            self.velocity.size *= ACCELARATION_CUE


class Ball(object):
    def __init__(self, number, mass, TYPE, (x, y), velocity, picture):  # for example: self.white_ball.picture =
        self.x = x
        self.y = y
        # self.color = BLUE
        # self.thickness = 0  #fully inside (no hole or holes)
        self.velocity = velocity  # Vector velocity
        self.picture = picture  # for example: = pygame.image.load('ball_0.png')#20*20
        self.radius = RADIUS  # const for all balls
        self.mass = mass  # const for all balls
        self.number = number
        self.TYPE = TYPE  ##constant - enum class of two kinds

    def __repr__(self):
        return 'ball - num:' + str(self.number) + ' , type:' + str(self.TYPE) + ' pos:' + str(
            (int(self.x), int(self.y))) + ' velocity:' + str(self.velocity)

    def handle_walls_collision(self):
        if self.x > (RIGHT_BOUNDARY - self.radius):
            self.x = 2 * (RIGHT_BOUNDARY - self.radius) - self.x
            self.velocity.angle = - self.velocity.angle
            self.velocity.size *= ELASTICITY_WALLS

        elif self.x < (LEFT_BOUNDARY + self.radius):
            self.x = 2 * (LEFT_BOUNDARY + self.radius) - self.x
            self.velocity.angle = - self.velocity.angle
            self.velocity.size *= ELASTICITY_WALLS

        if self.y > (BOTTOM_BOUNDARY - self.radius):
            self.y = 2 * (BOTTOM_BOUNDARY - self.radius) - self.y
            self.velocity.angle = pi - self.velocity.angle
            self.velocity.size *= ELASTICITY_WALLS

        elif self.y < (TOP_BOUNDARY + self.radius):
            self.y = 2 * (TOP_BOUNDARY + self.radius) - self.y
            self.velocity.angle = pi - self.velocity.angle
            self.velocity.size *= ELASTICITY_WALLS

    def is_in_hole(self):
        if (self.x < (LEFT_BOUNDARY + 26) and self.y < (TOP_BOUNDARY + 26)):
            return True  # if ball in a range of on of the holes
        return False

    def handle_in_a_hole(self):  # ball_1.IsInHole - property
        pass

    def draw(self):  # the client only draw the ball - does not do any calculations
        screen.blit(self.picture, (
            int(self.x) - self.radius,
            int(self.y) - self.radius))  # because it draws the picture from the left top edge

    def ball_move(self, with_friction):  # move the ball to the next place on the screen
        self.x += self.velocity.get_x()
        self.y -= self.velocity.get_y()
        if with_friction:
            self.velocity.size *= DRAG

    def is_collide_wall(self):
        if self.x > (RIGHT_BOUNDARY - self.radius) or self.x < (LEFT_BOUNDARY + self.radius) or self.y > (
                BOTTOM_BOUNDARY - self.radius) or self.y < (TOP_BOUNDARY + self.radius):
            return True

    def is_collide_ball(self, ball):
        dx = self.x - ball.x  # d for distanse - does not matter if the result is minus or plus - just need the length
        dy = self.y - ball.y
        distance = hypot(dx, dy)
        if distance < (self.radius + ball.radius):
            return True
        return False


def get_balls_in_lists(balls_data):
    balls_on_table = []
    for num in balls_data[0].keys():
        number = int(num)
        mass = 1
        TYPE = balls_data[0][num][1]
        x = balls_data[0][num][2]
        y = balls_data[0][num][3]
        v_angle = balls_data[0][num][4]
        v_size = balls_data[0][num][5]
        velocity = Vector(v_angle, v_size)
        balls_on_table.append(Ball(number, mass, TYPE, (x, y), velocity, pygame.image.load(
            PICTURES[number])))  # dict of a picture name and the pygame.load(PICTURES[ball.number])

    stripes_balls_on_table = []
    for num in balls_data[1].keys():
        number = int(num)
        mass = 1
        TYPE = balls_data[1][num][1]
        x = balls_data[1][num][2]
        y = balls_data[1][num][3]
        v_angle = balls_data[1][num][4]
        v_size = balls_data[1][num][5]
        velocity = Vector(v_angle, v_size)
        stripes_balls_on_table.append(Ball(number, mass, TYPE, (x, y), velocity, pygame.image.load(
            PICTURES[number])))  # dict of a picture name and the pygame.load(PICTURES[ball.number])

    solids_balls_on_table = []
    for num in balls_data[2].keys():
        number = int(num)
        mass = 1
        TYPE = balls_data[2][num][1]
        x = balls_data[2][num][2]
        y = balls_data[2][num][3]
        v_angle = balls_data[2][num][4]
        v_size = balls_data[2][num][5]
        velocity = Vector(v_angle, v_size)
        solids_balls_on_table.append(Ball(number, mass, TYPE, (x, y), velocity, pygame.image.load(
            PICTURES[number])))  # dict of a picture name and the pygame.load(PICTURES[ball.number])

    balls_in_hole = []
    for num in balls_data[3].keys():
        number = int(num)
        mass = 1
        TYPE = balls_data[3][num][1]
        x = balls_data[3][num][2]
        y = balls_data[3][num][3]
        v_angle = balls_data[3][num][4]
        v_size = balls_data[3][num][5]
        velocity = Vector(v_angle, v_size)
        balls_in_hole.append(Ball(number, mass, TYPE, (x, y), velocity, pygame.image.load(
            PICTURES[number])))  # dict of a picture name and the pygame.load(PICTURES[ball.number])

    stripes_balls_in_hole = []
    for num in balls_data[4].keys():
        number = int(num)
        mass = 1
        TYPE = balls_data[4][num][1]
        x = balls_data[4][num][2]
        y = balls_data[4][num][3]
        v_angle = balls_data[4][num][4]
        v_size = balls_data[4][num][5]
        velocity = Vector(v_angle, v_size)
        stripes_balls_in_hole.append(Ball(number, mass, TYPE, (x, y), velocity, pygame.image.load(
            PICTURES[number])))  # dict of a ball num and the pygame.load(PICTURES[ball.number])

    solids_balls_in_hole = []
    for num in balls_data[5].keys():
        number = int(num)
        mass = 1
        TYPE = balls_data[5][num][1]
        x = balls_data[5][num][2]
        y = balls_data[5][num][3]
        v_angle = balls_data[5][num][4]
        v_size = balls_data[5][num][5]
        velocity = Vector(v_angle, v_size)
        solids_balls_in_hole.append(Ball(number, mass, TYPE, (x, y), velocity, pygame.image.load(
            PICTURES[number])))  # dict of a picture name and the pygame.load(PICTURES[ball.number])

    is_collision = balls_data[6]

    return (balls_on_table, stripes_balls_on_table, solids_balls_on_table, balls_in_hole, stripes_balls_in_hole,
            solids_balls_in_hole, is_collision)


class Player(object):
    def __init__(self, name, player_socket, ip, port):
        self.name = name
        self.sock = player_socket
        self.ip = ip
        self.port = port
        self.balls_type = Ball_Types_enum.unknown
        self.TYPE = Player_Type_enum.unknown
        self.was_quited = False
        # self.foul = Player_Fouls_enum.no_fouls
        # self.black_pocket_was_chose = False

    def change_name(self, new_name):
        self.name = new_name

    def __repr__(self):
        return 'name=' + str(self.name)


def draw_balls(balls_on_table):
    for ball in balls_on_table:
        ball.draw()


def findBalls(mouse_x, mouse_y, balls_on_table):
    for ball in balls_on_table:
        if hypot(ball.x - mouse_x, ball.y - mouse_y) <= ball.radius:
            return ball
    return None


def draw_circle_around_ball(x, y):
    pygame.draw.circle(screen, WHITE, (int(x), int(y)), RADIUS + 1, 1)


def get_index_of_white_ball(balls_list):
    for i in range(len(balls_list)):
        if balls_list[i].TYPE == Ball_Types_enum.white:
            return i
    return None


# get the position of the ball when it collide with somthing - before moving the ball - choosing_velocity mode
def get_pos_ball_when_collide(ball, balls):
    ret = ()
    ball.velocity.size = 1
    collide = False
    with_friction = False
    while not collide:
        ball.ball_move(with_friction)
        if (ball.is_collide_wall()):
            ret = (ball.x, ball.y)
            collide = True
        else:
            for ball2 in balls:
                if ball2.number != ball.number:
                    if ball.is_collide_ball(ball2):
                        ret = (ball.x, ball.y)
                        collide = True
                        break
    return ret


# get the position of the ball when it collide with somthing - before moving the ball - choosing_velocity mode
def get_pos_other_ball_when_collide(ball, balls):  # or None - not collide with a ball or not collide at all
    ret = ()
    ball.velocity.size = 1
    collide = False
    with_friction = False
    while not collide:
        ball.ball_move(with_friction)
        if (ball.is_collide_wall()):
            ret = None
            collide = True
        else:
            for ball2 in balls:
                if ball2.number != ball.number:
                    if ball.is_collide_ball(ball2):
                        ret = (ball2.x, ball2.y)  # the other ball position
                        collide = True
                        break
    return ret


def get_balls_on_table_not_original(balls_on_table):
    balls_not_original = []
    for ball in balls_on_table:
        # we must create a new object! because list is given to a method by reference and not by value.
        balls_not_original.append(
            Ball(ball.number, ball.mass, ball.TYPE, (ball.x, ball.y), ball.velocity, ball.picture))
    return balls_not_original


# data about the game mode,turn and which player is the client
def get_basic_data_from_server(player_sock):
    json_basic_data = recv_by_size(player_sock)
    if json_basic_data == '':
        print 'something went wrong in the code - can not play'
        print 'bye bye'
        return
    basic_data = json.loads(json_basic_data)
    ret = (basic_data[0], basic_data[1], basic_data[2], basic_data[3], basic_data[4], basic_data[5], basic_data[6],
           basic_data[7], basic_data[8], basic_data[
               9])  # (game_mode, turn, player.TYPE ,player.name ,player.balls_type,player.was_quited ,other_player_TYPE ,other_player_name ,other_player_balls_type, other_player_was_quited)
    return ret


def get_balls_data_from_server(player_sock):
    json_balls_data = recv_by_size(player_sock)
    if json_balls_data == '':
        print 'something went wrong in the code - can not play'
        print 'bye bye'
        return
    balls_data = json.loads(json_balls_data)
    ret = get_balls_in_lists(
        balls_data)  # (balls_on_table,stripes_balls_on_table,solids_balls_on_table,balls_in_hole, stripes_balls_in_hole, solids_balls_in_hole)
    return ret


def is_it_a_ball(list_balls, (x, y)):
    for ball in list_balls:
        if hypot(ball.x - x, ball.y - y) <= ball.radius:
            return True


def did_pressed_white_ball(list_balls, (mouse_x, mouse_y)):
    for ball in list_balls:
        if hypot(ball.x - mouse_x, ball.y - mouse_y) <= ball.radius and ball.TYPE == Ball_Types_enum.white:
            return True
    return False


def replace_white_ball(balls_on_table):  # replace_white_ball_first_time(self)
    if is_it_a_ball(balls_on_table,
                    BALL_0_POS):  # this place is caught by other ball - we need to find another place for the white ball
        for x in range(LEFT_BOUNDARY + RADIUS + RADIUS, RIGHT_BOUNDARY - RADIUS - RADIUS + 1):
            for y in range(TOP_BOUNDARY + RADIUS + RADIUS, BOTTOM_BOUNDARY - RADIUS - RADIUS):
                if not is_it_a_ball(balls_on_table, (x, y)):
                    white_ball = Ball(0, 1, Ball_Types_enum.white, (x, y), Vector(90, 0),
                                      pygame.image.load(PICTURES[0]))

    else:
        white_ball = Ball(0, 1, Ball_Types_enum.white, BALL_0_POS, Vector(90, 0), pygame.image.load(PICTURES[0]))

    balls_on_table.append(white_ball)


# not from the server - from the client whose turn is his
def get_velocity_data_by_client(first_click_down_X, first_click_down_Y, last_mouse_X, last_mouse_Y, angle_was_chose,
                                speed_angle, white_ball):  # ,is_choosing_white_place,balls_on_table):
    # if did_pressed_white_ball(balls_on_table,(first_click_down_X,first_click_down_Y)) and is_choosing_white_place:
    #   print 5
    #    white_ball.x = last_mouse_X
    #   white_ball.y = last_mouse_Y
    dx_clicks = last_mouse_X - first_click_down_X
    dy_clicks = last_mouse_Y - first_click_down_Y
    distance = hypot(dx_clicks, dy_clicks)
    dx_ball_and_last_mouse = first_click_down_X - last_mouse_X
    dy_ball_and_last_mouse = first_click_down_Y - last_mouse_Y
    # print 'dx_ball_and_last_mouse1' + str(dx_ball_and_last_mouse)
    mouse_angle_with_screen = atan2(dy_ball_and_last_mouse, dx_ball_and_last_mouse)  # + 0.5 * pi
    if not angle_was_chose:  # if the angle was chose we do not want to change it!
        dx_ball_and_last_mouse = last_mouse_X - white_ball.x
        dy_ball_and_last_mouse = last_mouse_Y - white_ball.y
        speed_angle = 0.5 * pi + atan2(dy_ball_and_last_mouse, dx_ball_and_last_mouse)
    mouse_angle_with_speed_angle = speed_angle + pi - mouse_angle_with_screen
    # we can multiply it buy 0.7 if it is too fast!!!!!!!!!!!!!!!!!!!!!!!!!!!
    distance_on_white_line = (-1) * distance * sin(
        mouse_angle_with_speed_angle)  # *0.7 #if the distance is 0 - the speed_size will be 0 because the mul by 0...(distance)
    if distance_on_white_line < 0:
        distance_on_white_line = 0  # it can not be minus (-)
    if distance_on_white_line > 80:
        distance_on_white_line = 80
    speed_size = distance_on_white_line
    cue_angle = 1.5 * pi - speed_angle  # pi + 0.5 * pi-speed_angle
    cue_move_angle = pi - speed_angle
    cue_x, cue_y = white_ball.x - (CUE_FIRST_DISTANCE_FROM_BALL + speed_size) * sin(cue_move_angle), white_ball.y - (
                CUE_FIRST_DISTANCE_FROM_BALL + speed_size) * cos(cue_move_angle)

    return (speed_angle, speed_size, cue_x, cue_y, cue_angle)


def draw_players_names(this_player_name, other_player_name):
    draw_massage_to_screen(this_player_name, PLAYERS_NAME_COLOR, (X_THIS_PLAYER_NAME, Y_PLAYERS_NAME),
                           PLAYERS_NAME_FONT)
    draw_massage_to_screen(other_player_name, PLAYERS_NAME_COLOR, (X_OTHER_PLAYER_NAME, Y_PLAYERS_NAME),
                           PLAYERS_NAME_FONT)


def draw_players_balls_left(this_player_balls, other_player_balls):
    x_this_player = X_THIS_PLAYER_BALLS_LEFT
    print str(this_player_balls)
    for i, ball in enumerate(this_player_balls):
        ball.x = x_this_player + i * (2 * RADIUS + DISTANCE_BETWEEN_BALLS_LEFT_OR_IN_HOLE)
        ball.y = Y_PLAYERS_BALLS_LEFT
        ball.draw()

    x_other_player = X_OTHER_PLAYER_BALLS_LEFT
    for i, ball in enumerate(other_player_balls):
        ball.x = x_other_player + i * (2 * RADIUS + DISTANCE_BETWEEN_BALLS_LEFT_OR_IN_HOLE)
        ball.y = Y_PLAYERS_BALLS_LEFT
        ball.draw()


def draw_players_balls_in_hole(balls_in_hole):
    x_balls_in_hole = X_BALLS_IN_HOLE
    for i, ball in enumerate(balls_in_hole):
        ball.x = x_balls_in_hole + i * (2 * RADIUS + DISTANCE_BETWEEN_BALLS_LEFT_OR_IN_HOLE)
        ball.y = Y_BALLS_IN_HOLE
        ball.draw()


'''
def send_name(player,name):
    json_name = json.dumps(name)
    send_with_size(player,json_name)'''


def send_name_and_password_to_server(player_sock, player_name, password):
    to_send = [player_name, password]
    json_to_send = json.dumps(to_send)
    send_with_size(player_sock, json_to_send)


def draw_play_button(rect_color):
    pygame.draw.rect(screen, rect_color, [PLAY_BUTTON_X, PLAY_BUTTON_Y, PLAY_BUTTON_WIDTH, PLAY_BUTTON_HEIGHT])

    draw_massage_to_screen('PLAY', PLAY_BUTTON_COLOR,
                           ((PLAY_BUTTON_X + PLAY_BUTTON_WIDTH / 2), (PLAY_BUTTON_Y + PLAY_BUTTON_HEIGHT / 2)),
                           PLAY_BUTTON_FONT)
    # screen_text = Font.render('PLAY',True,BLACK)
    # screen_text_rect=screen_text.get_rect()
    # screen_text_rect.center =((PLAY_BUTTON_X + PLAY_BUTTON_WIDTH/2),(PLAY_BUTTON_Y + PLAY_BUTTON_HEIGHT/2))
    # screen.blit(screen_text,screen_text_rect)


def is_on_play_button((mouse_x, mouse_y)):
    if mouse_x >= PLAY_BUTTON_X and mouse_y >= PLAY_BUTTON_Y and mouse_x <= (
            PLAY_BUTTON_X + PLAY_BUTTON_WIDTH) and mouse_y <= (PLAY_BUTTON_Y + PLAY_BUTTON_HEIGHT):
        return True
    return False


def send_was_player_quited_to_server(player):
    to_send_was_player_quited = player.was_quited
    json_to_send_was_player_quited = json.dumps(to_send_was_player_quited)
    send_with_size(player.sock, json_to_send_was_player_quited)


# main loop of client for beginnig - options:
#                   1. if the user wants to play - he will need to tell his name and the password and only then the client will connect to the server
def main(ip, port, player_name, password):
    # pygame.init()
    to_quit = False
    draw_background()
    draw_massage_to_screen('Billiard Game', WELCOME_MSG_COLOR, WELCOME_MSG_POS, WELCOME_MSG_FONT)
    while not to_quit:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    to_quit = True
                else:
                    # draw_background()
                    mouse_pos = pygame.mouse.get_pos()
                    if is_on_play_button(mouse_pos):
                        draw_play_button(GREEN)
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            was_click_down = True
                        elif event.type == pygame.MOUSEBUTTONUP and was_click_down:
                            was_click_down = False
                            (to_quit, does_other_player_ready, player) = wait_for_other_client_to_get_ready_page(ip,
                                                                                                                 port,
                                                                                                                 player_name,
                                                                                                                 password)  # only the first player will wait - so if he quit the server update the dictionary
                            if not to_quit and does_other_player_ready:
                                print 'calling game main!'
                                to_quit = game_main(player)  # ip,port,name,password)
                                print 'game ended'
                            elif to_quit:
                                pass
                                print 'player quited'
                            elif not does_other_player_ready:  # the player that the other player quited on waiting mode
                                print 'other player quited on waiting mode'
                                # the player variable does not have any influence - the socket is closed
                            else:
                                print 'OMG!!!!!!!!!!! NO!!!!!!!!!!!!!!!!!!!'
                            print 'bye bye'
                    else:
                        draw_play_button(RED)
            pygame.display.flip()
        except ValueError as e:
            print "ValueError: number %s" % str(e)
            break
        except OSError as err:
            print("OS error: {0}".format(err))
        except socket.error as e:
            print "socket.error number: %s" % str(e)
            break
        except IOError as e:
            print "I\O error number: %s " % str(e)
            break
        except Exception as e:
            print "Client Disconnected general error %s" % str(e)
            break

    draw_background()
    draw_massage_to_screen('Bye Bye...', BYE_BYE_MSG_COLOR, (BYE_BYE_MSG_POS), REGULAR_MSG_FONT)
    pygame.display.flip()
    time.sleep(2)  # in seconds


def get_to_wait_data_from_server(player):
    json_to_wait_data = recv_by_size(player.sock)
    if json_to_wait_data == "":
        print "Got empty data in Recv from server - Will close this client socket"
        return None
    to_wait_data = json.loads(json_to_wait_data)
    return to_wait_data


def wait_for_other_client_to_get_ready_page(ip, port, player_name, password):
    # the player pressed on play button
    player_sock = socket.socket()  # object

    player_sock.settimeout(0.01)  # must get out of the block quickly so pygame will not stack

    print 'before connect'
    player_sock.connect((ip, port))
    print 'after connect with server'
    send_name_and_password_to_server(player_sock, player_name, password)
    print 'player\'s name sent to the server'
    # print "waiting server to get ready to play..."
    player = Player(player_name, player_sock, ip, port)
    pygame.display.set_caption(password + ' - ' + player.name)
    # getting the first time data from server - it will be basic data
    to_wait = get_to_wait_data_from_server(
        player)  # the main server will send it immediately after connecting - in the if statements
    to_quit = False  # defult - if the player do not need to wait - he can not have time to quit... - the game will start immediately
    does_other_player_ready = False  # for the second player
    if to_wait:
        # you are the first to enter - wait for the other player and send to the server thread if you quited #only the server thread will tell if the other player is ready
        while not to_quit and not does_other_player_ready:  #
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        to_quit = True
                draw_background()
                draw_table()
                draw_massage_to_screen('waiting other player to connect...', WAITING_MSG_COLOR, WAITING_MSG_POS,
                                       REGULAR_MSG_FONT)
                pygame.display.flip()  # need to flip here because we might not get to the lasr line in the while because timeout exeption
                json_does_other_player_ready = recv_by_size(player.sock)
                if json_does_other_player_ready == '':
                    print 'got empty data from server thread - something wrong'
                    return  # there will be error in the rest of the code because basic_data equals to empty list: []
                else:
                    does_other_player_ready = json.loads(json_does_other_player_ready)
                    # the server thread will send it wen he see len password key = 2 - means the other player entered
            except socket.timeout as e:
                print str(e)
                print 'server thread still did not send READY data'
                continue
        # now the other player is ready - in the dictionary
        if to_quit:  # send to the server  True on does_first_player_ready variable there (with the player in the dict the thread will ask)
            # do not forget to lock - aquire.. and write global - ask gal
            # the thread will also call the game_main - the main server will add a player to the password key and because the thread always check if the length of the password key values list equals 2 he will call the game main and pop the password key
            print player.name + ' pressed on quit button'
            # server will send the other player - the player in the second place-False  - other player not ready - the first player that was waiting has quitted
            to_send = to_quit
            json_to_send = json.dumps(to_send)
            send_with_size(player.sock, json_to_send)  # sent that he quited
            print player.name + ' sent that he quited'
        # not else because does_other_player_ready must be true - there is no other option that the server sends - change it to: "READY - it is not a boolian
    else:
        # without waiting
        json_does_other_player_ready = recv_by_size(player.sock)
        if json_does_other_player_ready == '':
            print 'got empty data from server thread - something wrong'
            return  # there will be error in the rest of the code because basic_data equals to empty list: []
        else:
            does_other_player_ready = json.loads(json_does_other_player_ready)
            print 'got ready data:' + str(does_other_player_ready)
            # if the other player
            # the server thread will send it when he see len password key = 2 - means the other player entered
            # finally the server will send both of the clients in the same time that their other player client is ready to play
    if to_quit or not does_other_player_ready:
        print 'closing player sock - ' + player.name
        player.sock.close()  # also the server delete the player from
        player = None  # have no reference any more but we still need to return him
    else:
        player_sock.settimeout(
            None)  # blocking mode - change it so the client will get the 'True' msg for sure - unless he will not be able to continue in any case
    print 'to_quit=' + str(to_quit)
    return (to_quit, does_other_player_ready, player)
    # if to_quit is true - the main client method will deal with it - close the socket - the server is already know!!!!!!!!!!!!


def game_main(player):
    (game_mode, turn, player.TYPE, player.name, player.balls_type, player.was_quited, other_player_TYPE,
     other_player_name, other_player_balls_type, other_player_was_quited) = get_basic_data_from_server(
        player.sock)  # (game_mode, turn, player.TYPE ,player.name ,player.balls_type, player.was_quited ,other_player_TYPE ,other_player_name ,other_player_balls_type, other_player_was_quited)
    print '########################################################################'
    print 'got basic data:'
    print '--------------'
    print 'game mode:' + get_game_mode_str(game_mode)
    print 'turn:' + get_turn_str(turn)
    print 'player:' + get_player_type_str(player.TYPE)
    print '########################################################################'

    # getting the first time balls data
    (balls_on_table, stripes_balls_on_table, solids_balls_on_table, balls_in_hole, stripes_balls_in_hole,
     solids_balls_in_hole, is_collision) = get_balls_data_from_server(player.sock)
    print '************************************************************************'
    print 'got balls data:'
    print '--------------'
    print 'balls_on_table: ' + str(balls_on_table)
    print 'stripes_balls_in_hole: ' + str(stripes_balls_in_hole)
    print 'solids_balls_in_hole: ' + str(solids_balls_in_hole)
    print '************************************************************************'

    ############################

    velocity_was_chose = False
    # white_ball_chose = False #not for the server - for the client to know if it need to print a circle around the ball
    # was_mouse_click_down=False

    # all of them will be changed immidiatlly
    first_click_down_X = 0
    first_click_down_Y = 0
    last_mouse_X = 0
    last_mouse_Y = 0
    speed_angle = 0  # it will be change on the first frame to the angle with the mouse
    speed_size = 0
    cue_x = 0
    cue_y = 0
    cue_angle = 0
    angle_was_chose = False  # if there was first click down - we are not changing the angle - only the size - angle was chose
    CUE_PICTURE = 'cue.png'
    cue = Cue(0, 0, Vector(0, 0), pygame.image.load(CUE_PICTURE))
    rot = cue.picture
    groups_chose = False
    # is_choosing_white_place = True
    print 'before main loop of game - not of program!'
    to_close_client_after_game = False
    game_running = True
    player.was_quited = False
    while game_running:
        try:
            # the white ball can fall and not be in this list...
            # #every frame the index can be change because balls falls to pockets
            if game_mode == Game_Mode_enum.choosing_velocity:
                white_ball = balls_on_table[get_index_of_white_ball(
                    balls_on_table)]  # the server must send the balls on table list with the white ball only on choosing velocity mode
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print 'player quited by pressing X on pygame screen'
                    player.was_quited = True
                    # game_mode = Game_Mode_enum.end_game
                    # break #we do not need to check for more events
                    # the only case where the client change the mode!!!!
                    # because the server can't predict it.
                    # that why the client send to the server every frame if he quited

                    # to_close_client_after_game = True
                elif turn == player.TYPE and Game_Mode_enum.choosing_velocity:
                    (speed_angle, speed_size, cue_x, cue_y, cue_angle) = get_velocity_data_by_client(first_click_down_X,
                                                                                                     first_click_down_Y,
                                                                                                     last_mouse_X,
                                                                                                     last_mouse_Y,
                                                                                                     angle_was_chose,
                                                                                                     speed_angle,
                                                                                                     white_ball)  # ,is_choosing_white_place,balls_on_table)
                    # now we can change the data about mouse positions because we already used the previous data and we do not need it anymore
                    if event.type == pygame.MOUSEBUTTONDOWN and not angle_was_chose:
                        (first_click_down_X, first_click_down_Y) = pygame.mouse.get_pos()
                        (last_mouse_X, last_mouse_Y) = (first_click_down_X, first_click_down_Y)
                        angle_was_chose = True
                        # print 'first click down!!!!!!!!!!!!!!!!!'
                    elif pygame.mouse.get_pressed()[
                        0] and angle_was_chose:  # means the player keep pressing down (after first click)
                        (last_mouse_X, last_mouse_Y) = pygame.mouse.get_pos()
                        # print 'choosing size'
                    elif event.type == pygame.MOUSEBUTTONUP:  # and not is_choosing_white_place:
                        if angle_was_chose:
                            if speed_size > 0:
                                velocity_was_chose = True
                                (last_mouse_X, last_mouse_Y) = pygame.mouse.get_pos()
                                # print 'velocity chose!'
                            else:
                                (first_click_down_X, first_click_down_Y) = pygame.mouse.get_pos()
                                (last_mouse_X, last_mouse_Y) = (first_click_down_X, first_click_down_Y)
                                angle_was_chose = False
                                # print 'pressed up and down on the same place... v=0'
                        else:  # may not get here ever
                            (first_click_down_X, first_click_down_Y) = pygame.mouse.get_pos()
                            (last_mouse_X, last_mouse_Y) = (first_click_down_X, first_click_down_Y)
                            # print 'maybe pressed out of the screen down and then came to the screen and pressed up first'

                    else:
                        (first_click_down_X, first_click_down_Y) = pygame.mouse.get_pos()
                        (last_mouse_X, last_mouse_Y) = (first_click_down_X, first_click_down_Y)
                        # print 'choosing angle'
                else:
                    print 'not choosing_velocity'

            if game_mode == Game_Mode_enum.choosing_velocity:  # for sure the white ball was selected
                # no if for velocity_was_chose because the server decide
                # white_ball_index = get_index_of_white_ball(balls_on_table)
                if turn == player.TYPE:
                    # here you have the responsibility to calculate he velocity data and send it to the
                    # server so it can send to the other player because he also needs to use this data
                    # the one whose turn is his already calculated the velocity data
                    to_send_choosing_velocity = [velocity_was_chose, speed_angle, speed_size, cue_x, cue_y, cue_angle]
                    json_to_send_choosing_velocity = json.dumps(to_send_choosing_velocity)
                    send_with_size(player.sock, json_to_send_choosing_velocity)

                else:
                    # the turn is not yours - you do not know what the other player did - you need to recieve it from the server
                    json_choosing_velocity_data = recv_by_size(player.sock)
                    if json_choosing_velocity_data == "":
                        print "Got empty data in Recv from server - Will close this client socket"
                        break
                    list_choosing_velocity_data = json.loads(
                        json_choosing_velocity_data)  # need to import the vector class - velocity is size and angle so we have all the info we need
                    # do not need to send the other client if velocity was chose or not - he will get the new mode (balls_moving) after that...
                    (speed_angle, speed_size, cue_x, cue_y, cue_angle) = (
                    list_choosing_velocity_data[0], list_choosing_velocity_data[1], list_choosing_velocity_data[2],
                    list_choosing_velocity_data[3], list_choosing_velocity_data[4])

                # here the two players have the data!!!!
                # update here the data here:
                white_ball.velocity.size = speed_size
                white_ball.velocity.angle = speed_angle

                # draw the data to the screen:
                draw_background()
                draw_table()
                draw_balls(balls_on_table)

                balls_on_table_not_original = get_balls_on_table_not_original(balls_on_table)
                white_ball_not_original = balls_on_table_not_original[
                    get_index_of_white_ball(balls_on_table_not_original)]
                (x_collide_ball, y_collide_ball) = get_pos_ball_when_collide(white_ball_not_original,
                                                                             balls_on_table_not_original)
                if (x_collide_ball, y_collide_ball) != (white_ball.x, white_ball.y):
                    pygame.draw.line(screen, WHITE, [white_ball.x, white_ball.y], [x_collide_ball, y_collide_ball], 1)
                draw_circle_around_ball(x_collide_ball, y_collide_ball)

                if not angle_was_chose:
                    rot = cue.rot_center(cue_angle)
                (cue.x, cue.y) = (cue_x, cue_y)

                cue.draw(rot)

                # draw the line of velocity
                # pygame.draw.line(screen, BLUE, [first_click_down_X - distance_on_white_line*sin(pi-speed_angle), first_click_down_Y - distance_on_white_line*cos(pi-speed_angle)],[first_click_down_X, first_click_down_Y], 1)

                if velocity_was_chose:  # it means that also angle_was_chose
                    # next time when the mode will be again 'choosing_velocity' the velocity_was_chose variable
                    # at the beginning, will be False - because the player has not chose yet the velocity of the ball
                    velocity_was_chose = False
                    angle_was_chose = False

            elif game_mode == Game_Mode_enum.balls_moving:
                (balls_on_table, stripes_balls_on_table, solids_balls_on_table, balls_in_hole, stripes_balls_in_hole,
                 solids_balls_in_hole, is_collision) = get_balls_data_from_server(player.sock)

                # draw_background() # only because the cue can get out of the table
                draw_table()
                draw_balls(balls_on_table)
                if is_collision:
                    pygame.mixer.Sound.play(COLLIDE_SOUND)

            elif game_mode == Game_Mode_enum.end_game:
                print 'waiting the server to send the winner'
                json_winner = recv_by_size(player.sock)
                if json_winner == "":
                    print "Got empty data in Recv from server - Will close this client socket"
                    break
                winner = json.loads(json_winner)
                # winner = int(winner)
                # print 'received <<< ' + str(winner)
                if winner == player.TYPE:
                    draw_massage_to_screen('you won (:', GREEN, REGULAR_MSG_POS, WIN_LOSE_MAG_FONT)
                    time.sleep(2)  # seconds
                elif winner == other_player_TYPE:
                    draw_massage_to_screen('you lost :(', RED, REGULAR_MSG_POS, WIN_LOSE_MAG_FONT)
                    pygame.display.flip()
                    time.sleep(2)  # seconds
                elif winner == Player_Type_enum.unknown:
                    if player.was_quited:
                        # we don't have a reason to pring on pygame screen that this player has quited because he know that...
                        print 'this player - ' + get_player_type_str(player.TYPE) + ' quited'
                        to_close_client_after_game = True
                    elif other_player_was_quited:
                        print 'other player - ' + get_player_type_str(other_player_TYPE) + ' quited'
                        draw_massage_to_screen('other player quited', REGULAR_MSG_COLOR, REGULAR_MSG_POS,
                                               WIN_LOSE_MAG_FONT)
                        pygame.display.flip()
                        time.sleep(2)  # seconds



                else:
                    print 'OMG! BAD!'
                # in any case - the game ended
                game_running = False  # so we get out of the loop

            else:
                print 'NO WAYY!!!!!!!!!!!'
                print 'game mode variable has bad information!'

            # will be printed also when game is over - it will be actually
            draw_players_names(player.name, other_player_name)  # always
            draw_players_balls_in_hole(balls_in_hole)
            if player.balls_type != Ball_Types_enum.unknown and other_player_balls_type != Ball_Types_enum.unknown:
                if player.balls_type == Ball_Types_enum.stripe and other_player_balls_type == Ball_Types_enum.solid:
                    draw_players_balls_left(stripes_balls_on_table, solids_balls_on_table)
                elif player.balls_type == Ball_Types_enum.solid and other_player_balls_type == Ball_Types_enum.stripe:
                    draw_players_balls_left(solids_balls_on_table,
                                            stripes_balls_on_table)  # first parameter is this balls type

                if not groups_chose:  # will happen only on the first time  - when the groups have just declared
                    groups_chose = True
                    draw_massage_to_screen('You Are ' + get_balls_type_str(player.balls_type), REGULAR_MSG_COLOR,
                                           (REGULAR_MSG_POS), REGULAR_MSG_FONT)
                    time.sleep(2)

            # if game_running:#if not we already did a flip in end game uf atatement
            pygame.display.flip()
            clock.tick(FPS)  # frame per second

            # preparation for next frame

            if game_mode != Game_Mode_enum.end_game:  # the client does not changes the game mode so when the game mode in the server is end game -
                # for the first time - it will get in here and change the game mode also in the client
                # send if this player has quited or not
                send_was_player_quited_to_server(player)

                # update basic data for the next frame
                (game_mode, turn, player.TYPE, player.name, player.balls_type, player.was_quited, other_player_TYPE,
                 other_player_name, other_player_balls_type, other_player_was_quited) = get_basic_data_from_server(
                    player.sock)
                # if DEBUG:
                #         print 'got basic data:'
                print '########################################################################'
                print '--------------'
                print 'game mode:' + get_game_mode_str(game_mode)
                print 'turn:' + get_turn_str(turn)
                print '--------------'
                print 'player type:' + get_player_type_str(player.TYPE)
                print 'player name:' + str(player.name)
                print 'player balls type:' + get_balls_type_str(player.balls_type)
                print 'this player quited:' + str(player.was_quited)
                print '--------------'
                print 'other type:' + get_player_type_str(other_player_TYPE)
                print 'other name:' + str(other_player_name)
                print 'other balls type:' + get_balls_type_str(other_player_balls_type)
                print 'other player quited:' + str(other_player_was_quited)
                print '########################################################################'
            # print 'stripes on table'+str(stripes_balls_on_table)
            # print 'solids on table'+str(solids_balls_on_table)
        except ValueError as e:
            print "ValueError: number %s" % str(e)
            break
        except OSError as err:
            print("OS error: {0}".format(err))
        except socket.error as e:
            print "socket.error number: %s" % str(e)
            break
        except IOError as e:
            print "I\O error number: %s " % str(e)
            break
        except Exception as e:
            print "Client Disconnected general error %s" % (str(e))
            break
    print 'closing this client\'s socket'
    player.sock.close()
    return to_close_client_after_game  # so the client will close the whole game if the player clicket on exit


if __name__ == '__main__':
    try:
        if len(argv) != 5:
            print "Usage: <ip> <port_number> <name> <password>"
            exit()
        else:
            ip = argv[1]
            port = int(argv[2])
            name = argv[3]
            password = argv[4]
            main(ip, port, name, password)
    except KeyboardInterrupt:
        print "\nGot ^C Main\n"

        father_going_to_close = True
