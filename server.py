__author__ = 'amit stein'

import math

import pygame
from math import atan2, cos, sin, degrees, hypot, pi
import socket
import threading
from sys import argv
import random  # who will start the game
# import classes
import json

########################################################################
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


########################################################################
# errors:
EWOULDBLOCK = 10035
EINPROGRESS = 10036
EALREADY = 10037
Enew_clientRESET = 10054
ENOTnew_client = 10057
ESHUTDOWN = 10058
WSAEnew_clientABORTED = 10053

# globals and locks

# Shared information
######################################
dict_passwords_and_players = {}
dict_passwords_and_players_lock = threading.Lock()

father_going_to_close = False
father_going_to_close_lock = threading.Lock()

total_clients = 0
total_clients_lock = threading.Lock()
######################################

# player thread
######################################
dict_player_threads_tid = {}
dict_player_threads_tid_lock = threading.Lock()

player_threads_tid = 1
player_threads_tid_lock = threading.Lock()

total_player_threads = 0
total_player_threads_lock = threading.Lock()
######################################

# game thread
######################################
dict_game_threads_tid = {}
dict_game_threads_tid_lock = threading.Lock()

game_thread_tid = 1
game_thread_tid_lock = threading.Lock()

total_game_threads = 0
total_game_threads_lock = threading.Lock()

############################################################
# graphic and game constants
# =======================================

# balls and table consts
MASS = 1
RADIUS = 10
MUE = 0.1
DRAG = 1 - MUE
ELASTICITY_WALLS = 0.85
ELASTICITY_COLLISIONS = 0.85

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
DISTANCE_BETWEEN_LEFT_BOUNDARY_TO_FIRST_WHITE_X = 80  # TABLE_WIDTH / 4

# middle white first place :
MIDDLE_WHITE_FIRST_PLACE_X = LEFT_BOUNDARY + DISTANCE_BETWEEN_LEFT_BOUNDARY_TO_FIRST_WHITE_X + RADIUS + 2
MIDDLE_WHITE_FIRST_PLACE_Y = TOP_BOUNDARY + ((TABLE_HEIGHT - (2 * side_size)) / 2)

# middle other balls first place :
MIDDLE_OTHERS_FIRST_PLACE_X = MIDDLE_WHITE_FIRST_PLACE_X + DISTANCE_BETWEEN_FIRST_WHITE_X_TO_FIRST_OTHERS_X
MIDDLE_OTHERS_FIRST_PLACE_Y = MIDDLE_WHITE_FIRST_PLACE_Y

# other balls const places:
BALL_0_POS = (MIDDLE_WHITE_FIRST_PLACE_X, MIDDLE_WHITE_FIRST_PLACE_Y)  # white ball - default place
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


class Player_Fouls_enum:
    no_fouls = 1
    white_ball_insertef_to_pocket = 2
    white_ball_touched_other_player_ball_first = 3
    white_ball_did_not_touch_any_ball = 4
    turn_time_overed = 5


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


class Vector(object):
    def __init__(self, angle, size):
        self.angle = angle
        self.size = size

    def get_x(self):
        # print 'sin angle type:'+str(type(sin(5))) + ' * size type:'+str(type(self.size)) + ' = ' #+ type(str(cos(self.angle) * self.size))
        return sin(self.angle) * self.size

    def get_y(self):
        return cos(self.angle) * self.size

    def __repr__(self):
        return ('angle=' + str(degrees(self.angle)) + ' [deg], size=' + str(self.size) + ' [pixel/frame]')


class Hole(object):
    def __init__(self, x, y):  # for example: self.white_ball.picture =
        self.x = x
        self.y = y
        self.radius = 2 * RADIUS
        # self.TYPE = TYPE  ##enum class of two kinds


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

    def ball_move(self, with_friction):  # move the ball to the next place on the screen
        self.x += self.velocity.get_x()
        self.y -= self.velocity.get_y()
        if with_friction:
            self.velocity.size *= DRAG

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


class Player(object):
    def __init__(self, name, player_socket, ip, port):
        self.name = name
        self.sock = player_socket
        self.ip = ip
        self.port = port
        self.balls_type = Ball_Types_enum.unknown  # at open game mode we choose
        self.TYPE = Player_Type_enum.unknown  # at the beginning we choose
        self.was_quited = False
        # self.foul = Player_Fouls_enum.no_fouls
        # self.black_pocket_was_chose = False

    def change_name(self, new_name):
        self.name = new_name

    def __repr__(self):
        return 'name=' + str(self.name)


class GameThread(threading.Thread):
    def __init__(self, player1, player2, port, game_thread_tid):  # constractor
        threading.Thread.__init__(self)

        # print "New thread started for "+ip+":"+str(port)
        # self.player1_sock = player1[0]
        # self.player1_ip = player1[1]
        # self.player2_sock = player2[0]
        # self.player2_ip = player2[1]
        self.player1 = player1
        self.player2 = player2
        self.port = port
        self.game_thread_tid = game_thread_tid  # another option	 : threading.current_thread().ident
        self.game_mode = Game_Mode_enum.start_game
        rnd = random.randint(1, 3)  # who starts
        if rnd == 1:  # 1/2 if 2, player 2 starts - we need to change the names of the variables of the players...
            # so every time player 1 will start (just in the variables)
            self.player1.name, self.player2.name = self.player2.name, self.player1.name
            self.player1, self.player2 = self.player2, self.player1
        self.turn = Player_Type_enum.player1  # for the server to know - not to send
        self.player1.TYPE = Player_Type_enum.player1
        self.player2.TYPE = Player_Type_enum.player2

        # 6 lists of balls:
        self.balls_on_table = []
        self.stripes_balls_on_table = []
        self.solids_balls_on_table = []
        self.balls_in_hole = []
        self.stripes_balls_in_hole = []
        self.solids_balls_in_hole = []
        self.is_collision = False
        self.set_balls_lists_to_start()

        # there is also a method:  - delete a ball that does not exist in balls_on_table_list
        self.white_in_a_hole = False  # at the end of the turn when all balls are not moving anymore, then white_in_a_hole = False again
        self.black_in_a_hole = False

        # at some modes we get data from one of the player and send it to the other player
        self.need_to_send_to_player1 = False
        self.need_to_send_to_player2 = False

        # 6 holes
        self.hole1 = Hole(LEFT_BOUNDARY + RADIUS, TOP_BOUNDARY + RADIUS)  # left_top
        self.hole2 = Hole(LEFT_BOUNDARY + ((TABLE_WIDTH - 2 * side_size) / 2),
                          TOP_BOUNDARY + RADIUS)  # top - here we do not need to raise the hole
        self.hole3 = Hole(RIGHT_BOUNDARY - RADIUS, TOP_BOUNDARY + RADIUS)  # right top
        self.hole4 = Hole(LEFT_BOUNDARY + RADIUS, BOTTOM_BOUNDARY - RADIUS)  # left bottom
        self.hole5 = Hole(LEFT_BOUNDARY + ((TABLE_WIDTH - 2 * side_size) / 2),
                          BOTTOM_BOUNDARY - RADIUS)  # bottom - here we do not need to raise the hole
        self.hole6 = Hole(RIGHT_BOUNDARY - RADIUS, BOTTOM_BOUNDARY - RADIUS)  # right bottom

        self.is_break_shot = True  # at the beginnig of the game it will change for the rest of the game
        self.is_table_open = True  # after the break shot the table is open-#at the beginnig of the game it will change for the rest of the game

        self.white_ball_collided = False
        self.white_ball_in_hole = False
        self.white_ball_first_collided_with_its_ball_type = False
        self.white_ball_first_collided_with_other_player_ball_type = False
        self.white_ball_first_collided_black_ball = False
        self.player_insert_his_balls_into_pocket = False
        self.player_insert_other_player_balls_into_pocket = False
        self.is_first_white_collision = True
        self.insert_balls_on_break_shot = False
        self.first_any_group_ball_inserted_into_a_pocket_type = Ball_Types_enum.unknown
        self.is_first_any_group_ball_inserted_into_a_pocket = False  # at the beginnig of the game it will change for the rest of the game

        self.winner = Player_Type_enum.unknown  # we do not know yet who won.

        self.game_running = True

    def set_balls_lists_to_start(self):
        white_ball = Ball(0, 1, Ball_Types_enum.white, BALL_0_POS, Vector(90, 0),
                          pygame.image.load(PICTURES[0]))  # default before player move it
        ball_1 = Ball(1, 1, Ball_Types_enum.stripe, BALL_1_POS, Vector(0, 0), pygame.image.load(PICTURES[1]))
        ball_2 = Ball(2, 1, Ball_Types_enum.stripe, BALL_2_POS, Vector(0, 0), pygame.image.load(PICTURES[2]))
        ball_3 = Ball(3, 1, Ball_Types_enum.stripe, BALL_3_POS, Vector(0, 0), pygame.image.load(PICTURES[3]))
        ball_4 = Ball(4, 1, Ball_Types_enum.stripe, BALL_4_POS, Vector(0, 0), pygame.image.load(PICTURES[4]))
        ball_5 = Ball(5, 1, Ball_Types_enum.stripe, BALL_5_POS, Vector(0, 0), pygame.image.load(PICTURES[5]))
        ball_6 = Ball(6, 1, Ball_Types_enum.stripe, BALL_6_POS, Vector(0, 0), pygame.image.load(PICTURES[6]))
        ball_7 = Ball(7, 1, Ball_Types_enum.stripe, BALL_7_POS, Vector(0, 0), pygame.image.load(PICTURES[7]))
        ball_8 = Ball(8, 1, Ball_Types_enum.black, BALL_8_POS, Vector(0, 0), pygame.image.load(PICTURES[8]))
        ball_9 = Ball(9, 1, Ball_Types_enum.solid, BALL_9_POS, Vector(0, 0), pygame.image.load(PICTURES[9]))
        ball_10 = Ball(10, 1, Ball_Types_enum.solid, BALL_10_POS, Vector(0, 0), pygame.image.load(PICTURES[10]))
        ball_11 = Ball(11, 1, Ball_Types_enum.solid, BALL_11_POS, Vector(0, 0), pygame.image.load(PICTURES[11]))
        ball_12 = Ball(12, 1, Ball_Types_enum.solid, BALL_12_POS, Vector(0, 0), pygame.image.load(PICTURES[12]))
        ball_13 = Ball(13, 1, Ball_Types_enum.solid, BALL_13_POS, Vector(0, 0), pygame.image.load(PICTURES[13]))
        ball_14 = Ball(14, 1, Ball_Types_enum.solid, BALL_14_POS, Vector(0, 0), pygame.image.load(PICTURES[14]))
        ball_15 = Ball(15, 1, Ball_Types_enum.solid, BALL_15_POS, Vector(0, 0), pygame.image.load(PICTURES[15]))

        # just to draw
        ball_1_tmp = Ball(1, 1, Ball_Types_enum.stripe, BALL_1_POS, Vector(0, 0), pygame.image.load(PICTURES[1]))
        ball_2_tmp = Ball(2, 1, Ball_Types_enum.stripe, BALL_2_POS, Vector(0, 0), pygame.image.load(PICTURES[2]))
        ball_3_tmp = Ball(3, 1, Ball_Types_enum.stripe, BALL_3_POS, Vector(0, 0), pygame.image.load(PICTURES[3]))
        ball_4_tmp = Ball(4, 1, Ball_Types_enum.stripe, BALL_4_POS, Vector(0, 0), pygame.image.load(PICTURES[4]))
        ball_5_tmp = Ball(5, 1, Ball_Types_enum.stripe, BALL_5_POS, Vector(0, 0), pygame.image.load(PICTURES[5]))
        ball_6_tmp = Ball(6, 1, Ball_Types_enum.stripe, BALL_6_POS, Vector(0, 0), pygame.image.load(PICTURES[6]))
        ball_7_tmp = Ball(7, 1, Ball_Types_enum.stripe, BALL_7_POS, Vector(0, 0), pygame.image.load(PICTURES[7]))
        ball_8_tmp = Ball(8, 1, Ball_Types_enum.black, BALL_8_POS, Vector(0, 0), pygame.image.load(PICTURES[8]))
        ball_9_tmp = Ball(9, 1, Ball_Types_enum.solid, BALL_9_POS, Vector(0, 0), pygame.image.load(PICTURES[9]))
        ball_10_tmp = Ball(10, 1, Ball_Types_enum.solid, BALL_10_POS, Vector(0, 0), pygame.image.load(PICTURES[10]))
        ball_11_tmp = Ball(11, 1, Ball_Types_enum.solid, BALL_11_POS, Vector(0, 0), pygame.image.load(PICTURES[11]))
        ball_12_tmp = Ball(12, 1, Ball_Types_enum.solid, BALL_12_POS, Vector(0, 0), pygame.image.load(PICTURES[12]))
        ball_13_tmp = Ball(13, 1, Ball_Types_enum.solid, BALL_13_POS, Vector(0, 0), pygame.image.load(PICTURES[13]))
        ball_14_tmp = Ball(14, 1, Ball_Types_enum.solid, BALL_14_POS, Vector(0, 0), pygame.image.load(PICTURES[14]))
        ball_15_tmp = Ball(15, 1, Ball_Types_enum.solid, BALL_15_POS, Vector(0, 0), pygame.image.load(PICTURES[15]))
        # placing the balls in the an lists

        self.balls_on_table = [white_ball, ball_1, ball_2, ball_3, ball_4, ball_5, ball_6, ball_7, ball_8, ball_9,
                               ball_10, ball_11, ball_12, ball_13, ball_14, ball_15]
        self.stripes_balls_on_table = [ball_1_tmp, ball_2_tmp, ball_3_tmp, ball_4_tmp, ball_5_tmp, ball_6_tmp,
                                       ball_7_tmp]
        self.solids_balls_on_table = [ball_9_tmp, ball_10_tmp, ball_11_tmp, ball_12_tmp, ball_13_tmp, ball_14_tmp,
                                      ball_15_tmp]
        self.balls_in_hole = []
        self.stripes_balls_in_hole = []
        self.solids_balls_in_hole = []

    def is_all_balls_rest(self):
        for ball in self.balls_on_table:
            if int(ball.velocity.size) > 0:  # at least one ball moves - not all of ball are rest
                return False
        return True

    def addVectors(self, vec1, vec2):
        x = sin(vec1.angle) * vec1.size + sin(vec2.angle) * vec2.size
        y = cos(vec1.angle) * vec1.size + cos(vec2.angle) * vec2.size

        angle = 0.5 * pi - atan2(y, x)
        size = hypot(x, y)  # length
        vec3 = Vector(angle, size)
        return vec3

    def findBalls(self, balls, mouse_x, mouse_y):
        for ball in balls:
            if hypot(ball.x - mouse_x, ball.y - mouse_y) <= ball.radius:
                return ball
        return None

    def is_it_a_ball(self, (x, y)):
        for ball in self.balls_on_table:
            if hypot(ball.x - x, ball.y - y) <= ball.radius:
                return True
        return False

    def handle_balls_collision(self, ball1, ball2, dx, dy, distance):
        # print ball1
        # print ball2
        # angle = atan2(dy, dx) + 0.5 * pi
        # ball1.velocity = self.addVectors(ball1.velocity, Vector(angle, 2 * ball2.velocity.size))
        # ball2.velocity = self.addVectors(ball2.velocity, Vector(angle + pi, 2 * ball1.velocity.size))

        # ball1.velocity.size *= ELASTICITY_COLLISIONS
        # ball2.velocity.size *= ELASTICITY_COLLISIONS

        # overlap = 0.5 * (ball1.radius + ball2.radius - distance + 1)
        # ball1.x += sin(angle) * overlap
        # ball1.y -= cos(angle) * overlap
        #  ball2.x -= sin(angle) * overlap
        #  ball2.y += cos(angle) * overlap
        print "BeforeCalc ball"+str(ball1.number) +"- " + str(ball2.velocity.size) + "|" + str(ball2.velocity.angle)
        vCollisionX = ball2.x - ball1.x
        vCollisionY = ball2.y - ball1.y
        distance = math.hypot((ball2.x - ball1.x), (ball2.y - ball1.y))

        vCollisionNormX = vCollisionX / distance
        vCollisionNormY = vCollisionY / distance
        B1Vx = ball1.velocity.size * math.cos(ball1.velocity.angle)
        B1Vy = ball1.velocity.size * math.sin(ball1.velocity.angle)
        B2Vx = ball2.velocity.size * math.cos(ball2.velocity.angle)
        B2Vy = ball2.velocity.size * math.sin(ball2.velocity.angle)
        vRelativeVelocityX = B1Vx - B2Vx
        vRelativeVelocityY = B1Vy - B2Vy

        speed = vRelativeVelocityX * vCollisionNormX + vRelativeVelocityY * vCollisionNormY
        if speed < 0:
            return

        impulse = 2 * speed / (1 + 1)
        B1Vx -= (impulse * 1 * vCollisionNormX)
        B1Vy -= (impulse * 1 * vCollisionNormY)
        B2Vx += (impulse * 1 * vCollisionNormX)
        B2Vy += (impulse * 1 * vCollisionNormY)

        ball1.velocity.size = math.hypot(ball1.x,ball1.y)
        ball1.velocity.angle = math.atan2(B1Vy, B1Vx)
        ball2.velocity.size = math.hypot(ball2.x,ball2.y)
        ball2.velocity.angle = math.atan2(B2Vy, B2Vx)
        print "AfterCalc ball"+str(ball1.number) +"- " + str(ball2.velocity.size) + "|" + str(ball2.velocity.angle)

        ball1.velocity.size *= ELASTICITY_COLLISIONS
        ball2.velocity.size *= ELASTICITY_COLLISIONS

    def is_in_hole(self, ball, hole):
        dx = ball.x - hole.x
        dy = ball.y - hole.y
        distance = hypot(dx, dy)  # distance between middle of the ball and middle of the hole
        if distance < 2 * ball.radius:
            return True
        return False

    def is_in_holes(self, ball):
        if self.is_in_hole(ball, self.hole1) or self.is_in_hole(ball, self.hole2) or self.is_in_hole(ball,
                                                                                                     self.hole3) or self.is_in_hole(
                ball, self.hole4) or self.is_in_hole(ball, self.hole5) or self.is_in_hole(ball, self.hole6):
            return True
        else:
            return False

    def remove_ball_by_list_and_num(self, list, ball_num):
        for ball in list:
            if ball.number == ball_num:
                list.remove(ball)
                break

    # for the next frame
    def update_balls_data(self):
        with_friction = True

        # all the fouls are fouls of the player whose is his!
        # MOVE ONE STEP ALL OF THE BALLS
        for ball in self.balls_on_table:
            ball.ball_move(with_friction)
            # print 'ball1 ' + str(i) + ': ' + str((int(ball1.x),int(ball1.y)))
        for i, ball1 in enumerate(self.balls_on_table):
            #self.balls_on_table[i].ball_move(with_friction)
            # print 'ball1 ' + str(i) + ': ' + str((int(ball1.x),int(ball1.y)))
            self.balls_on_table[i].handle_walls_collision()
            for ball2 in self.balls_on_table[i + 1:]:

                # this is not enough!!! must cheak a collision if not by distance by: if the ball will colllide a
                # ball in his diraction (like in the aiming method then if the velocity of the is bigger the the
                # distance then they also colliding and we will also get into the condition)
                dx = ball1.x - ball2.x
                dy = ball1.y - ball2.y
                distance = hypot(dx, dy)
                # if distance < (ball1.radius + ball2.radius) or the sum of velocities on the veticle line of the tangent line:
                if distance < (ball1.radius + ball2.radius):
                    # print 'collide!'
                    self.is_collision = True
                    # here make a send True in the last place where it says to_do_noise
                    # because this is the server... - we just send to the client what to do
                    # (velocity_was_chose,speed_angle, speed_size,cue_x,cue_y,cue_angle,to_do_noise)

                    # now update fouls
                    if ball1.TYPE == Ball_Types_enum.white and self.is_first_white_collision:
                        self.white_ball_collided = True
                        self.is_first_white_collision = False
                        if self.turn == self.player1.TYPE:
                            if ball2.TYPE == self.player1.balls_type and not self.is_table_open:
                                self.white_ball_first_collided_with_its_ball_type = True
                                # print 'white ball first collided with his balls'
                            elif ball2.TYPE == self.player2.balls_type and not self.is_table_open:
                                self.white_ball_first_collided_with_other_player_ball_type = True
                                # print 'white ball first collided with other player balls'
                            elif ball2.TYPE == Ball_Types_enum.black:
                                self.white_ball_first_collided_black_ball = True
                                # print 'white ball first collided with the black ball'
                            else:
                                pass
                                # print 'white ball first collided with legal balls - open table mode'
                                # it is open table mode so it is ok
                        else:
                            if ball2.TYPE == self.player2.balls_type and not self.is_table_open:
                                self.white_ball_first_collided_with_its_ball_type = True
                                # print 'white ball first collided with his balls'
                            elif ball2.TYPE == self.player1.balls_type and not self.is_table_open:
                                self.white_ball_first_collided_with_other_player_ball_type = True
                                # print 'white ball first collided with other player balls'
                            elif ball2.TYPE == Ball_Types_enum.black:
                                self.white_ball_first_collided_black_ball = True
                                # print 'white ball first collided with the black ball'
                            else:
                                pass
                                # print 'white ball first collided with legal balls - open table mode'
                                # it is open table mode so it is ok


                    elif ball2.TYPE == Ball_Types_enum.white and self.is_first_white_collision:
                        self.white_ball_collided = True
                        self.is_first_white_collision = False
                        print str(self.is_first_white_collision)
                        if self.turn == self.player1.TYPE:
                            if ball1.TYPE == self.player1.balls_type and not self.is_table_open:
                                self.white_ball_first_collided_with_its_ball_type = True
                                # print 'white ball first collided with his balls'
                            elif ball1.TYPE == self.player2.balls_type and not self.is_table_open:
                                self.white_ball_first_collided_with_other_player_ball_type = True
                                # print 'white ball first collided with other player balls'
                            elif ball1.TYPE == Ball_Types_enum.black:
                                self.white_ball_first_collided_black_ball = True
                                # print 'white ball first collided with the black ball'
                            else:
                                pass
                                # print 'white ball first collided with legal balls - open table mode'
                                # it is open table mode so it is ok
                        else:
                            if ball1.TYPE == self.player2.balls_type and not self.is_table_open:
                                self.white_ball_first_collided_with_its_ball_type = True
                                # print 'white ball first collided with his balls'
                            elif ball1.TYPE == self.player1.balls_type and not self.is_table_open:
                                self.white_ball_first_collided_with_other_player_ball_type = True
                                # print 'white ball first collided with other player balls'
                            elif ball1.TYPE == Ball_Types_enum.black:
                                self.white_ball_first_collided_black_ball = True
                                # print 'white ball first collided with the black ball'
                            else:
                                pass
                                # print 'white ball first collided with legal balls - open table mode'
                                # it is open table mode so it is ok

                    # collide the balls
                    self.handle_balls_collision(ball1, ball2, dx, dy,
                                                distance)  # dont change it actually good if two or three balls arecolliding at the same time - because then we will get the shakul vector of each one. - every compare we add to the main ball the velocities of the ball that collide with it

        for ball in self.balls_on_table:
            # check if the ball is in at least 1 hole of the 6
            if self.is_in_holes(ball):
                if self.is_break_shot:  # and self.is_table_open:
                    self.insert_balls_on_break_shot = True
                # update the fouls of the player whose turn is his
                elif self.is_table_open:  # also not break shot...
                    # only on the first group! ball inserted into pocket we will get here
                    if not self.is_first_any_group_ball_inserted_into_a_pocket and ball.TYPE != Ball_Types_enum.white and ball.TYPE != Ball_Types_enum.black:  # do not worry about what happens if white or black in hole - just tell the info
                        self.first_any_group_ball_inserted_into_a_pocket_type = ball.TYPE
                        self.is_first_any_group_ball_inserted_into_a_pocket = True
                        # print 'maybe!!! found the type of the first ball inserted after break'
                        # print 'we will cheak if it is a legal insert'
                        # happen once in a game
                        # at the end of the all balls rest if change it back to False
                    else:
                        pass
                        # print 'we are still on open table mode - you must put the white in also so it was not a legal insert...'
                else:  # regular mode - there are groups
                    print 'there are already groups'
                    if self.turn == self.player1.TYPE:  # and self.is_table_open:
                        if ball.TYPE == self.player1.balls_type:
                            self.player_insert_his_balls = True
                            # print get_player_type_str(self.player1.TYPE)+' inserted his balls type - another turn'
                        else:
                            self.player_insert_other_player_balls = True
                            # print get_player_type_str(self.player1.TYPE)+' inserted other ball type - turn changes'
                        print get_player_type_str(self.player1.TYPE) + ' inserted ball number ' + str(ball.number)
                    else:
                        if ball.TYPE == self.player2.balls_type:
                            self.player_insert_his_balls = True
                            # print get_player_type_str(self.player2.TYPE)+' inserted his balls type - another turn'
                        else:
                            self.player_insert_other_player_balls = True
                            # print get_player_type_str(self.player2.TYPE)+' inserted other player balls type - turn changes'
                        print get_player_type_str(self.player2.TYPE) + ' inserted ball number ' + str(ball.number)

                if ball.TYPE == Ball_Types_enum.stripe:
                    self.stripes_balls_in_hole.append(ball)
                    self.remove_ball_by_list_and_num(self.stripes_balls_on_table, ball.number)
                    # print 'ball number: ' + str(ball.number) + ' appended to: stripes_balls_in_hole'
                    # print 'ball number: ' + str(ball.number) + ' removed from: stripes_balls_on_table'
                    self.balls_in_hole.append(ball)
                    print 'ball number: ' + str(ball.number) + ' appended to: balls_in_hole'
                elif ball.TYPE == Ball_Types_enum.solid:
                    self.solids_balls_in_hole.append(ball)
                    self.remove_ball_by_list_and_num(self.solids_balls_on_table, ball.number)
                    # print 'ball number: ' + str(ball.number) + ' appended to: solids_balls_in_hole'
                    # print 'ball number: ' + str(ball.number) + ' removed from: solids_balls_on_table'
                    self.balls_in_hole.append(ball)
                    # print 'ball number: ' + str(ball.number) + ' appended to: balls_in_hole'
                elif ball.TYPE == Ball_Types_enum.white:
                    self.white_ball_in_hole = True  # to create and replace the white ball and foul
                elif ball.TYPE == Ball_Types_enum.black:  # also the last option
                    self.black_in_a_hole = True
                self.balls_on_table.remove(ball)
                print 'ball number: ' + str(ball.number) + ' removed from: balls_on_table'

    def put_balls_in_list(self):
        dict_balls_on_table = {}
        dict_stripes_balls_on_table = {}
        dict_solids_balls_on_table = {}

        dict_balls_in_hole = {}
        dict_stripes_balls_in_hole = {}
        dict_solids_balls_in_hole = {}

        # balls on the table
        for ball in self.balls_on_table:
            dict_balls_on_table[ball.number] = [ball.number, ball.TYPE, ball.x, ball.y, ball.velocity.angle,
                                                ball.velocity.size]
        for ball in self.stripes_balls_on_table:
            dict_stripes_balls_on_table[ball.number] = [ball.number, ball.TYPE, ball.x, ball.y, ball.velocity.angle,
                                                        ball.velocity.size]
        for ball in self.solids_balls_on_table:
            dict_solids_balls_on_table[ball.number] = [ball.number, ball.TYPE, ball.x, ball.y, ball.velocity.angle,
                                                       ball.velocity.size]

        # balls in holes
        for ball in self.balls_in_hole:
            dict_balls_in_hole[ball.number] = [ball.number, ball.TYPE, ball.x, ball.y, ball.velocity.angle,
                                               ball.velocity.size]
        for ball in self.stripes_balls_in_hole:
            dict_stripes_balls_in_hole[ball.number] = [ball.number, ball.TYPE, ball.x, ball.y, ball.velocity.angle,
                                                       ball.velocity.size]
        for ball in self.solids_balls_in_hole:
            dict_solids_balls_in_hole[ball.number] = [ball.number, ball.TYPE, ball.x, ball.y, ball.velocity.angle,
                                                      ball.velocity.size]

        return [dict_balls_on_table, dict_stripes_balls_on_table, dict_solids_balls_on_table, dict_balls_in_hole,
                dict_stripes_balls_in_hole, dict_solids_balls_in_hole, self.is_collision]

    def get_index_of_white_ball(self, balls_list):
        for i in range(len(balls_list)):
            if balls_list[i].TYPE == Ball_Types_enum.white:
                return i
        return None

    # send to both of the clients the balls data
    def get_balls_data(self):
        balls_to_send = self.put_balls_in_list()  # [dict_balls_on_table, dict_stripes_balls_on_table, dict_solids_balls_on_table,dict_balls_in_hole,dict_stripes_balls_in_hole, dict_solids_balls_in_hole]
        # json_balls_to_send = json.dumps(balls_to_send)
        to_send_player1 = balls_to_send
        to_send_player2 = balls_to_send
        return (to_send_player1, to_send_player2)

    # data about balls/cue/more
    # the clients will know how to relate to this data by the basic data
    def send_data_to_draw(self, to_send_player1, to_send_player2):
        # send almost together
        if DEBUG:
            print "---------------------sent---------------------"
            print 'game_thread_tid:' + str(self.game_thread_tid)
        if self.need_to_send_to_player1:
            json_to_send_player1 = json.dumps(to_send_player1)
            send_with_size(self.player1.sock, json_to_send_player1)
            if DEBUG:
                print 'Sent to player1: >>>' + str(to_send_player1)
            # print "-----------------------------------------------"
        if self.need_to_send_to_player2:
            json_to_send_player2 = json.dumps(to_send_player2)
            send_with_size(self.player2.sock, json_to_send_player2)
            if DEBUG:
                print 'Sent to player2: >>>' + str(to_send_player2)
        if DEBUG:
            print "---------------------sent---------------------"

    def get_quit_data_from_clients(self):
        # this is important
        json_was_quited_player1 = recv_by_size(self.player1.sock)
        if json_was_quited_player1 == "":
            print "Got empty data in Recv from player1 - Will close this client socket"
            return
        player1_was_quited = json.loads(json_was_quited_player1)
        if DEBUG:
            print 'recieved from + player1:' + str(player1_was_quited)

        json_was_quited_player2 = recv_by_size(self.player2.sock)
        if json_was_quited_player2 == "":
            print "Got empty data in Recv from player2 - Will close this client socket"
            return
        player2_was_quited = json.loads(json_was_quited_player2)
        if DEBUG:
            print 'recieved from + player2:' + str(player2_was_quited)

        return (player1_was_quited, player2_was_quited)

    # data about the game mode,turn and which player is the client
    # always send it to both of the clients
    def send_basic_data_to_both(self):
        basic_data_to_player1 = [self.game_mode, self.turn, self.player1.TYPE, self.player1.name,
                                 self.player1.balls_type, self.player1.was_quited, self.player2.TYPE, self.player2.name,
                                 self.player2.balls_type, self.player2.was_quited]
        basic_data_to_player2 = [self.game_mode, self.turn, self.player2.TYPE, self.player2.name,
                                 self.player2.balls_type, self.player2.was_quited, self.player1.TYPE, self.player1.name,
                                 self.player1.balls_type, self.player1.was_quited]
        json_basic_data_to_player1 = json.dumps(basic_data_to_player1)
        json_basic_data_to_player2 = json.dumps(basic_data_to_player2)

        to_send_player1 = json_basic_data_to_player1
        to_send_player2 = json_basic_data_to_player2
        send_with_size(self.player1.sock, to_send_player1)
        send_with_size(self.player2.sock, to_send_player2)
        if DEBUG:
            print '########################################################################'
            print 'sent basic data:'
            print 'game mode:' + get_game_mode_str(self.game_mode)
            print 'turn:' + get_turn_str(self.turn)
            print '########################################################################'

    # first time - not by the mouse place - if there not place for the white ball at the middle point we cheak all of the places until we find a place
    def replace_white_ball(self):  # replace_white_ball_first_time(self)
        if self.is_it_a_ball(
                BALL_0_POS):  # this place is caught by other ball - we need to find another place for the white ball
            for x in range(LEFT_BOUNDARY + RADIUS + RADIUS, RIGHT_BOUNDARY - RADIUS - RADIUS + 1):
                for y in range(TOP_BOUNDARY + RADIUS + RADIUS, BOTTOM_BOUNDARY - RADIUS - RADIUS):
                    if not self.is_it_a_ball((x, y)):
                        white_ball = Ball(0, 1, Ball_Types_enum.white, (x, y), Vector(90, 0),
                                          pygame.image.load(PICTURES[0]))

        else:
            white_ball = Ball(0, 1, Ball_Types_enum.white, BALL_0_POS, Vector(90, 0), pygame.image.load(PICTURES[0]))

        self.balls_on_table.append(white_ball)

    def get_players_name(self):
        json_player1_name = recv_by_size(self.player1.sock)
        if json_player1_name == '':
            print 'something went wrong in the code - can not play'
            print 'bye bye'
            return None
        self.player1.name = json.loads(json_player1_name)

        json_player2_name = recv_by_size(self.player2.sock)
        if json_player2_name == '':
            print 'something went wrong in the code - can not play'
            print 'bye bye'
            return None
        self.player2.name = json.loads(json_player2_name)

    def run(self):
        """
        the call thread_obj.start() will auto call to this method !!!!
        """
        global total_clients
        global father_going_to_close
        global dict_player_password

        global dict_player_threads_tid
        global player_threads_tid
        global total_player_threads

        global dict_game_threads_tid
        global game_thread_tid
        global total_game_threads

        # change_total_clients.acquire()  #lock
        # total_clients += 2
        # change_total_clients.release()  #release thr lock

        self.player1.sock.settimeout(None)  # 20)#20)  # Every some second will check whether Main want to kill

        self.player2.sock.settimeout(None)  # 20)  # Every some second will check whether Main want to kill
        if DEBUG:
            print "game_thread_tid: " + str(
                self.game_thread_tid) + " - New Game Thread after Accept from two clients:\n1: " + str(
                self.player1.ip) + '\n2: ' + str(self.player1.ip) + "port: " + str(self.port)

        self.game_mode = Game_Mode_enum.choosing_velocity  # server does not know the choosing_ball

        # to_send_does_everyone_ready=True
        # json_to_send_does_everyone_ready = json.dumps(to_send_does_everyone_ready)
        # to_send_player1, to_send_player2 = json_to_send_does_everyone_ready,json_to_send_does_everyone_ready
        # send_with_size(self.player1.sock,to_send_player1)
        # send_with_size(self.player2.sock,to_send_player2)

        self.send_basic_data_to_both()  # so both of the clients know the starct and the subject of the that the get
        if DEBUG:
            print '########################################################################'
            print 'sent basic data:'
            print 'game mode:' + get_game_mode_str(self.game_mode)
            print 'turn:' + get_turn_str(self.turn)
            print '########################################################################'

        self.need_to_send_to_player1 = True
        self.need_to_send_to_player2 = True
        (to_send_player1, to_send_player2) = self.get_balls_data()  # send to both of the clients
        self.send_data_to_draw(to_send_player1, to_send_player2)

        # now one of the players will chose the position and the velocity of the ball
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # main loop
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        print 'before main loop'
        to_close_clients_connection = False
        while self.game_running:
            try:
                self.need_to_send_to_player1 = False
                self.need_to_send_to_player2 = False

                if self.game_mode == Game_Mode_enum.end_game:
                    print 'game ended!'
                    # if one of the players pressed on exit we will get here after both of the players know that because basic data in the kast frame.
                    # we just need to sent the winner and kill the process without more sends or receives
                    to_close_clients_connection = True  # the only case that we close the sockets
                    to_send = self.winner
                    # json_to_send = json.dumps(to_send)
                    to_send_player1, to_send_player2 = to_send, to_send

                    # the players will get the data here and after that
                    self.need_to_send_to_player1 = True
                    self.need_to_send_to_player2 = True
                    self.game_running = False  # will not continue to the next frame - will be killed - that why we need to send the winner data now
                    # to_close_after_send=true
                    # send them both the winner (you just sent them the modw - end game - in the balls moving the mode has changed)
                    # close both of their sockets and kill process - let father know
                    # now tje client will close the connection - immidiatly after getting the winner message on end game mode and then the client will go backe to its main loop - to the options : welcome: name,password ,play button
                    # now the clients will have a window of you win! or you lost!
                    # then the client will go back to the menu
                elif self.game_mode == Game_Mode_enum.choosing_velocity:
                    # now get the info about the velocity by the mouse and the place and angle of cue
                    # check who needs to give it to you and to the other one you need to send because he do not know...
                    if self.turn == Player_Type_enum.player1:
                        # print 'waiting for player1 to send velocity'
                        json_data_choosing_velocity = recv_by_size(self.player1.sock)
                        if json_data_choosing_velocity == "":
                            print 'Got empty data in Recv from player1 - Will close this client socket 565'
                            break
                        if DEBUG:
                            print 'got player1 velocity data'
                            print 'game_thread_tid:' + str(
                                self.game_thread_tid) + ': Received<<< ' + json_data_choosing_velocity
                        self.need_to_send_to_player1 = False
                        self.need_to_send_to_player2 = True
                    else:
                        # print 'waiting for player2 to send velocity'
                        json_data_choosing_velocity = recv_by_size(self.player2.sock)
                        if json_data_choosing_velocity == "":
                            print "Got empty data in Recv from player2 - Will close this client socket"
                            break
                        if DEBUG:
                            print 'got player2 velocity data'
                            print "game_thread_tid:" + str(
                                self.game_thread_tid) + ": Received<<< " + json_data_choosing_velocity
                        self.need_to_send_to_player1 = True
                        self.need_to_send_to_player2 = False

                    list_choosing_velocity = json.loads(
                        json_data_choosing_velocity)  # need to import the vector class - velocity is size and angle so we have all the info we need
                    # get the information from the player whose turn is his
                    # (self.game_mode,velocity_was_chose,speed_angle, speed_size,cue_x,cue_y,cue_angle) = (list_before_balls_moving[0],list_before_balls_moving[1],list_before_balls_moving[2],list_before_balls_moving[3],list_before_balls_moving[4],list_before_balls_moving[5],list_before_balls_moving[6])
                    (velocity_was_chose, speed_angle, speed_size, cue_x, cue_y, cue_angle) = (
                        list_choosing_velocity[0], list_choosing_velocity[1], list_choosing_velocity[2],
                        list_choosing_velocity[3], list_choosing_velocity[4], list_choosing_velocity[5])
                    # now the server have the data from the one whose turn is his
                    # the server will send the data only to the other player - that why the variables:
                    # self.need_to_send__to_player1 and self.need_to_send__to_player2
                    if velocity_was_chose:
                        # print 'velocity chose!'
                        # change mode and send the data without balls
                        index_white_ball = self.get_index_of_white_ball(self.balls_on_table)
                        if index_white_ball == None:
                            print 'error - index white ball = None'
                            break
                        # update data
                        self.balls_on_table[index_white_ball].velocity.angle = float(speed_angle)
                        self.balls_on_table[index_white_ball].velocity.size = float(speed_size)
                        self.game_mode = Game_Mode_enum.balls_moving
                        # (to_close_clients_connection, to_send_player1,to_send_player2) = self.update_data_for_this_frame()#put data in list to send it
                        # else: #else we stay in the same mode - we do not send the balls lists here - only data about the cue speed level in the graph that will be in the future

                    # important!: send it to the client whose turn is not his!
                    to_send_to_the_player_that_it_is_not_his_turn = [speed_angle, speed_size, cue_x, cue_y,
                                                                     cue_angle]  # he does not need to know the velocity_was_chose - he just need to draw
                    # send the data to the other player
                    if self.need_to_send_to_player1:
                        to_send_player1 = to_send_to_the_player_that_it_is_not_his_turn
                        if DEBUG:
                            print 'sending only to player 1'
                    else:
                        to_send_player2 = to_send_to_the_player_that_it_is_not_his_turn
                        if DEBUG:
                            print 'sending only to player 2'


                elif self.game_mode == Game_Mode_enum.balls_moving:
                    self.update_balls_data()
                    if self.is_all_balls_rest():  # from the previous turn
                        print 'all_balls rest'
                        # check for win first

                        if self.black_in_a_hole:  # the game is over but who is the winner
                            if (self.turn == Player_Type_enum.player1 and ((
                                                                                   self.player1.balls_type == Ball_Types_enum.stripe and len(
                                                                               self.stripes_balls_on_table) == 0) or (
                                                                                   self.player1.balls_type == Ball_Types_enum.solid and len(
                                                                               self.solids_balls_on_table) == 0))) and not self.white_in_a_hole:
                                self.winner = Player_Type_enum.player1
                                print 1
                            # player1 insert black on the right time but also the white
                            elif (self.turn == Player_Type_enum.player1 and ((
                                                                                     self.player1.balls_type == Ball_Types_enum.stripe and len(
                                                                                 self.stripes_balls_on_table) == 0) or (
                                                                                     self.player1.balls_type == Ball_Types_enum.solid and len(
                                                                                 self.solids_balls_on_table) == 0))) and self.white_in_a_hole:
                                self.winner = Player_Type_enum.player2
                                print 2
                            # player2 insert black on the right time
                            elif (self.turn == Player_Type_enum.player2 and ((
                                                                                     self.player2.balls_type == Ball_Types_enum.stripe and len(
                                                                                 self.stripes_balls_on_table) == 0) or (
                                                                                     self.player2.balls_type == Ball_Types_enum.solid and len(
                                                                                 self.solids_balls_on_table) == 0))) and not self.white_in_a_hole:
                                self.winner = Player_Type_enum.player2
                                print 3
                            # player2 insert black on the right time but also the white
                            elif (self.turn == Player_Type_enum.player2 and ((
                                                                                     self.player2.balls_type == Ball_Types_enum.stripe and len(
                                                                                 self.stripes_balls_on_table) == 0) or (
                                                                                     self.player2.balls_type == Ball_Types_enum.solid and len(
                                                                                 self.solids_balls_on_table) == 0))) and self.white_in_a_hole:
                                self.winner = Player_Type_enum.player1
                                print 4
                            # player1 insert black ball not in time
                            elif (self.turn == Player_Type_enum.player1 and ((
                                                                                     self.player1.balls_type == Ball_Types_enum.stripe and len(
                                                                                 self.stripes_balls_on_table) != 0) or (
                                                                                     self.player1.balls_type == Ball_Types_enum.solid and len(
                                                                                 self.solids_balls_on_table) != 0))):
                                self.winner = Player_Type_enum.player2
                                print 5
                            # player2 insert black ball not in time
                            else:  # if (self.turn == Player_Type_enum.player2 and ((self.player2.balls_type==Ball_Types_enum.stripe and len(self.stripes_balls_on_table)!=0) or(self.player2.balls_type==Ball_Types_enum.solid and len(self.solids_balls_on_table)!=0))):
                                self.winner = Player_Type_enum.player1
                                print 6
                            print 'game end!'
                            self.game_mode = Game_Mode_enum.end_game

                        else:  # if no_one won - continue the game - check for fouls and change modes
                            if self.is_table_open:
                                # print 'table is open'
                                # check to change player.balls_type from
                                if self.is_break_shot:
                                    # print 'break shot'
                                    if (
                                            not self.white_ball_collided) or self.white_ball_in_hole:  # in any case of them we start again the break shot
                                        # print 'set the lists again'
                                        # print 'change turns1'
                                        # now we will change the turn and set the balls to let the other player play the break shot
                                        if self.turn == self.player1.TYPE:
                                            self.turn = self.player2.TYPE
                                        else:
                                            self.turn = self.player1.TYPE
                                        self.set_balls_lists_to_start()  # start over the game but the other player will have the opportunity to start

                                    else:  # legal shot on break shot and open table mode
                                        # in any case we do not know who is stripes and who is solids here rather then the player inserted legally a ball or more to the holes
                                        # but in this case we will give him another turn because he insert a ball into a pocket.
                                        # print 'legal shot'
                                        self.is_break_shot = False  # the most important thing here! - because we have a legal break shot we are moving on

                                        # for sure did not insert the black ball because we cheak it before every thing - the first thing we cheak!
                                        if not self.insert_balls_on_break_shot:  # only in break shot mode#player inserted a ball - have another turn
                                            # print 'change turns2'
                                            if self.turn == self.player1.TYPE:
                                                self.turn = self.player2.TYPE
                                            else:
                                                self.turn = self.player1.TYPE

                                        else:
                                            # white ball stay where it is
                                            # self.game_mode = Game_Mode_enum.choosing_velocity
                                            print 'another turn because insert balls (not black and not white)'
                                            # turn does not changes

                                else:  # not break shot - yed open table
                                    # print 'open table mode'
                                    # print 'not break shot'
                                    if self.white_ball_in_hole:
                                        self.choose_white_place = True
                                        self.replace_white_ball()
                                        # print 'replacing white ball'
                                        if self.turn == self.player1.TYPE:
                                            self.turn = self.player2.TYPE
                                        else:
                                            self.turn = self.player1.TYPE
                                    elif self.white_ball_first_collided_black_ball:
                                        # print 'little foul on open table mode - first collided black - other player will not choose  place! but the turns are changes'
                                        if self.turn == self.player1.TYPE:
                                            self.turn = self.player2.TYPE
                                        else:
                                            self.turn = self.player1.TYPE
                                    elif (
                                            not self.white_ball_collided):  # or self.white_ball_first_collided_with_other_ball_type :#if foul on open table and not on break shot
                                        # print 'foul on open table mode - other player can choose white place'
                                        if self.turn == self.player1.TYPE:
                                            self.turn = self.player2.TYPE
                                        else:
                                            self.turn = self.player1.TYPE

                                    else:  # legal shot
                                        # the player played a legal shot on open table mode but not on break shot
                                        if self.is_first_any_group_ball_inserted_into_a_pocket:
                                            # self.first_any_group_ball_inserted_into_a_pocket_type == Ball_Types_enum.unknown: #will be unknown only on open table mode and until one ball will be inserted to a pocket legally
                                            # unknown means we do not know yet what kind of ball went into a hole legally because no ball have been falling into a hole yet.
                                            # - turn does not changes
                                            # - now we can know who is the stripes and who is the solids because we have the type of the first legal ball that inserted to a pocket
                                            # print 'first ball in hole legally - on open table and not break shot'
                                            # print 'now we will split into groups'
                                            if self.turn == self.player1.TYPE:
                                                if self.first_any_group_ball_inserted_into_a_pocket_type == Ball_Types_enum.stripe:
                                                    self.player1.balls_type = Ball_Types_enum.stripe
                                                    self.player2.balls_type = Ball_Types_enum.solid
                                                else:
                                                    self.player1.balls_type = Ball_Types_enum.stripe
                                                    self.player2.balls_type = Ball_Types_enum.solid
                                            else:
                                                if self.first_any_group_ball_inserted_into_a_pocket_type == Ball_Types_enum.stripe:
                                                    self.player2.balls_type = Ball_Types_enum.stripe
                                                    self.player1.balls_type = Ball_Types_enum.solid
                                                else:
                                                    self.player2.balls_type = Ball_Types_enum.stripe
                                                    self.player1.balls_type = Ball_Types_enum.solid
                                            self.is_table_open = False  # important! - will not get in those if of open table anymore!
                                        # print 'open table mode will be changed on the next turn (not frame)'

                                        else:
                                            # print 'did not insert any ball (solids or stripes)'
                                            # print 'turn changes'
                                            if self.turn == self.player1.TYPE:
                                                self.turn = self.player2.TYPE
                                            else:
                                                self.turn = self.player1.TYPE

                                            # we are not changing the turns
                            else:  # not open table - regular rules
                                # print 'regular table'
                                if self.white_ball_in_hole:
                                    self.choose_white_place = True
                                    self.replace_white_ball()  # only when the white ball is out of the table - we need to find it a place until the player will
                                    # print 'replacing white ball'
                                    if self.turn == self.player1.TYPE:
                                        self.turn = self.player2.TYPE
                                    else:
                                        self.turn = self.player1.TYPE
                                elif (
                                        not self.white_ball_collided) or self.white_ball_first_collided_with_other_player_ball_type or self.white_ball_first_collided_black_ball:  # if foul on regular mode
                                    # print 'white_ball_collided='+ str(self.white_ball_collided)
                                    # print 'white_ball_first_collided_with_other_player_ball_type='+str(self.white_ball_first_collided_with_other_player_ball_type)
                                    # print 'white_ball_first_collided_black_ball='+str(self.white_ball_first_collided_black_ball)
                                    if self.turn == self.player1.TYPE:
                                        self.turn = self.player2.TYPE
                                    else:
                                        self.turn = self.player1.TYPE
                                    self.choose_white_place = True

                                else:  # legal shot on regular table mode
                                    if not (
                                            self.player_insert_his_balls and not self.player_insert_other_player_balls):  # insert only balls from his groupe
                                        if self.turn == self.player1.TYPE:
                                            self.turn = self.player2.TYPE
                                        else:
                                            self.turn = self.player1.TYPE
                                    else:
                                        print 'nice - put your balls in and did not touched other irst and did not put black in-have another turn :)'
                                        # if the player did not do that - he will get another turn

                            # else:#player2 did not win
                            # cheak for fouls
                            # if the white ball got into hole we need to create it again because it was earased from the balls_on_table_list

                            # if it was a legal shot and the player did not insert to holes both of the ball types and it is not self.is_it_break_shot

                            # self.turn = Player_Type_enum.player1
                            # if (self.player1.balls_type==Ball_Types_enum.stripe and len(self.stripes_balls_on_table)==0) or\
                            # (self.player1.balls_type==Ball_Types_enum.solid and len(self.solids_balls_on_table)==0):
                            # self.game_mode=Game_Mode_enum.choosing_pocket_for_black_ball
                            # else:
                            #  self.game_mode = Game_Mode_enum.choosing_velocity

                        # do not need to cheak pocket for black ball
                        # if (self.player2.balls_type==Ball_Types_enum.stripe and len(self.stripes_balls_on_table)==0) or (self.player2.balls_type==Ball_Types_enum.solid and len(self.solids_balls_on_table)==0) or (self.player1.balls_type==Ball_Types_enum.stripe and len(self.stripes_balls_on_table)==0) or (self.player1.balls_type==Ball_Types_enum.solid and len(self.solids_balls_on_table)==0):
                        # self.game_mode=Game_Mode_enum.choosing_pocket_for_black_ball

                        # for next turn! - not frame - we cheak for fouls and victory only after the balls stop moving

                        self.white_ball_collided = False
                        self.white_ball_in_hole = False
                        self.player_insert_other_player_balls = False
                        self.player_insert_his_balls = False
                        self.white_ball_first_collided_with_other_player_ball_type = False
                        self.is_first_white_collision = True
                        self.insert_balls_on_break_shot = False
                        self.white_ball_first_collided_black_ball = False
                        self.is_first_any_group_ball_inserted_into_a_pocket = False
                        if self.game_mode != Game_Mode_enum.end_game:
                            self.game_mode = Game_Mode_enum.choosing_velocity  # most important

                        # print 'player1 balls type = '+get_balls_type_str(self.player1.balls_type)
                        # print 'player2 balls type = '+get_balls_type_str(self.player2.balls_type)

                        # can not print here the white ball because if it inserted into a pocket with the black, then we do not insert back the white ball...
                        # print str(self.balls_on_table[self.get_index_of_white_ball(self.balls_on_table)])

                    # here the white can be deleted only on choosing moving balls mode - then whet we are going back to cgoosing vekocity the server is responsible to replace the white ball in the balls on table list so the client can use it in the graphics
                    self.need_to_send_to_player1 = True
                    self.need_to_send_to_player2 = True
                    (to_send_player1, to_send_player2) = self.get_balls_data()
                    self.is_collision = False  # set to next frame

                # done to update the data!
                ######################################################

                # now we will semd the data to the players

                self.send_data_to_draw(to_send_player1, to_send_player2)  # so the clients know what to draw

                if (
                        self.player1.was_quited or self.player2.was_quited) and not self.game_mode == Game_Mode_enum.end_game:  # so it gets in only on the first time - when the game mode is not end_game
                    print 'one of the players quited'
                    self.game_mode = Game_Mode_enum.end_game
                    # if one of the players quited - on the next frame to_close_clients_connection will be true and the players will not get basic data.
                    # that because they will get the data now (to_close_clients_connection = False) so they willknow what kind of data they will get on the next turn (winner data)

                if not to_close_clients_connection:
                    # now we will send the data to the clients
                    self.player1.was_quited, self.player2.was_quited = self.get_quit_data_from_clients()  # so we know if one of them pressed on exit during the game
                    self.send_basic_data_to_both()
                    # send the clients the basic data #so the clients know what is going to happen on the next frame
                    # (in which mode the need to be - what kind of data they will get, are they need to close their window or come back to main)
                else:
                    # we will not send to the clients data for the next frame because there is no next frame - we are closing the connection with them
                    print 'to_close_clients_connection = true'
                    break

            except socket.error as e:
                if e.errno == Enew_clientRESET:  # 'new_clientection reset by peer'
                    print "Error %s - Seems Client Disconnected. try Accept new Client " % e.errno
                    break
                elif e.errno == EWOULDBLOCK or str(e) == "timed out":  # (time out) Client didnt send any data yet
                    if father_going_to_close:
                        print "Father Going To Die"
                        self.player1.sock.close()
                        self.player2.sock.close()
                        break
                    print ".",
                    continue

                else:
                    print "Unhandled Socket error at recv. Server will exit %s " % e
                    break

        # below there are things we do when both clients have closed the connection

        # print "Clients disconnected..."
        print "Before  close 1 son thread of 2 sockets - total threads = %d (%d)" % (
            how_many_threads("Child"), total_clients)
        self.player1.sock.close()
        self.player2.sock.close()
        print 'two sockets closed'

        dict_game_threads_tid_lock.acquire()
        dict_game_threads_tid.pop(self.game_thread_tid)
        dict_game_threads_tid_lock.release()
        print 'removed game thread from dict'

        total_game_threads_lock.acquire()
        total_game_threads -= 1
        total_game_threads_lock.release()
        print 'decreased total_player_threads to' + str(total_game_threads)

        print 'end of game thread'


def how_many_threads(caller):
    if caller == "main":
        return threading.activeCount() - 1
    else:
        return threading.activeCount() - 1


def get_name_and_password_from_client(player_sock):
    json_player_name_and_password = recv_by_size(player_sock)
    if json_player_name_and_password == '':
        print 'did not get player name - got empty data - something wrong in my code'
        print 'bye bye'
        return None
    print 'goy player name - got empty data - something wrong in my code'
    player_name_and_password = json.loads(json_player_name_and_password)
    return (player_name_and_password[0], player_name_and_password[1])


def handle_first_player_before_game_starts_Thread(password, first_player, tid):
    global total_clients
    global father_going_to_close
    global dict_player_password

    global dict_player_threads_tid
    global player_threads_tid
    global total_player_threads

    global dict_game_threads_tid
    global game_thread_tid
    global total_game_threads

    print first_player.name + 'got into player thread'
    first_player.sock.settimeout(0.01)
    was_first_player_quited = False
    while len(dict_passwords_and_players[password]) != 2 and not was_first_player_quited:
        # here the server will send both of the players if the other player is ready and only then will do the game thread and append the thread to the thread list using aquire and...
        # this is the second player
        try:
            json_was_first_player_quited = recv_by_size(first_player.sock)
            if json_was_first_player_quited == '':
                print 'got empty data from new player sock - something wrong'
                return None  # there will be error in the rest of the code because basic_data equals to empty list: []
            else:
                was_first_player_quited = json.loads(json_was_first_player_quited)

        except socket.timeout as e:
            print str(e.errno)
            continue
            # print 'client thread still did not send any QUIT data'

    # the main server got new player with the same password
    # now we will send both of the players 'READY'
    # call game_thread and delete them from the dict

    if was_first_player_quited:  # the other player must of not being in the list yet - so we make him the first one in the list by deleting this player
        if len(dict_passwords_and_players[password]) == 1:  # must - the first player
            first_player.sock.close()  # close first player's socket - dict_passwords_and_players[password][0]
            dict_passwords_and_players_lock.acquire()
            deleted_password = dict_passwords_and_players.pop(password)
            dict_passwords_and_players_lock.release()
            print 'first player to connect with server quited'
            print 'password of %s has deleted from the dictionary' % (deleted_password)

            total_clients_lock.acquire()
            total_clients -= 1
            total_clients_lock.release()
            print 'decreased total_clients'


        elif len(dict_passwords_and_players[password]) == 2:  # can not happen but if will happen...
            # thar means the first player quited just after another player joined to the same password so the server did not have time to delete the first player from the list so the next player to connect with this password will be the first
            # we will send false on other player is ready and the client will close
            print 'strange!!!!!'
            second_player = dict_passwords_and_players[1]
            to_send_second_player = was_first_player_quited  # 'QUIT'
            json_to_send_second_player = to_send_second_player
            send_with_size(second_player.sock, json_to_send_second_player)  # send only to first player

            dict_passwords_and_players_lock.acquire()
            deleted_password = dict_passwords_and_players.pop(password)
            dict_passwords_and_players_lock.release()
            print 'password of %s has deleted from the dictionary' % (deleted_password)
            total_clients_lock.acquire()
            total_clients -= 2
            total_clients_lock.release()
            print 'decreased total_clients'
            print 'decreased total_clients'



    else:  # must that the list of the password length equals 2!
        # first player did not quit (was still false) but another player connected with the main server and appended to the list
        # the main server got new player with the same password
        # now we will send both of the players 'READY'
        # call game_thread and delete them from the dict
        print 'there are two players with the same password'
        second_player = dict_passwords_and_players[password][1]

        # fron now they will be on blocking mode
        first_player.sock.settimeout(None)
        second_player.sock.settimeout(None)

        to_send = True  # 'READY'
        json_to_send_both = json.dumps(to_send)
        send_with_size(first_player.sock, json_to_send_both)  # send to first player
        send_with_size(second_player.sock, json_to_send_both)  # send to second player
        print 'sent both of the client true - the other player is ready'

        # new game thread
        new_game_thread = GameThread(first_player, second_player, port,
                                     game_thread_tid)  # this line call to the __init__ of the  new_thread
        new_game_thread.start()  # this call to run method of new_thread

        print 'new game thread started'
        # print "number of threads:%d\number of clients:%d " % (
        # how_many_threads("main"), total_clients)  # just to know how many threads i have totally
        dict_game_threads_tid_lock.acquire()
        dict_game_threads_tid[game_thread_tid] = new_game_thread
        dict_game_threads_tid_lock.release()
        print 'add player thread to dict'
        game_thread_tid_lock.acquire()
        game_thread_tid += 1
        game_thread_tid_lock.release()

        total_game_threads_lock.acquire()
        total_game_threads += 1
        total_game_threads_lock.release()
        print 'increased total_game_threads'

        # most important so the main server will not get into the else - so there are no passwords with more the two clients.
        dict_passwords_and_players_lock.acquire()
        deleted_password = dict_passwords_and_players.pop(password)
        dict_passwords_and_players_lock.release()
        print 'password of %s has deleted from the dictionary' % (deleted_password)

        total_clients_lock.acquire()
        total_clients -= 2
        total_clients_lock.release()
        print 'decreased total_clients'
        print 'decreased total_clients'

    dict_player_threads_tid_lock.acquire()
    dict_player_threads_tid.pop(tid)
    dict_player_threads_tid_lock.release()
    print 'remove player_thread from dict'

    total_player_threads_lock.acquire()
    total_player_threads -= 1
    total_player_threads_lock.release()
    print 'decreased total_player_threads'

    print 'end of player thread'


def main(port):  # responsable of giving every two clients a thread server that will manage their game

    print 'in main'

    global total_clients
    global father_going_to_close
    global dict_player_password

    global dict_player_threads_tid
    global player_threads_tid
    global total_player_threads

    global dict_game_threads_tid
    global game_thread_tid
    global total_game_threads

    srv = socket.socket()
    ip = '0.0.0.0'  # socket.gethostname()  #"127.0.0.1"	 ??????????????????????? not supposed to be "0.0.0.0" ?????????????????????????

    #  SO_REUSEADDR means : reopen	socket even if its in wait state from last execution without waiting
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((ip, port))
    print "After bind to " + str(ip) + " port: " + str(port)

    srv.listen(20)  # 20 clients - 10 games together - 10 threads
    print "After listen"

    # player_threads = []
    # game_threads = []

    # game_thread_tid = 1  #trunsuction id - the first game_thread_tid will be 1

    srv.settimeout(10)
    cnt = 0

    # lst_2_players = []  #list of the players
    # dict_passwords_and_players = {} #{password:player}
    while True:
        try:
            # because of the time out i must do accept only to 1 client!!!!!!!!!!!!!!!!!!!!!!1111
            # like i wanted - dictionary of users and password
            (new_client, (ip, port)) = srv.accept()  # new_client means new_sock
            new_client.settimeout(None)  # 20)
            print "\n new client\n"

            total_clients_lock.acquire()
            total_clients += 1
            total_clients_lock.release()

            # becarful - there can timeout exeption here also - maybe make a variable that tells if this clien already
            # connected but did not send his name and password - so the server can not go for the next client to accept...
            (player_name, player_password) = get_name_and_password_from_client(new_client)
            player_name = str(player_name)
            player_password = str(player_password)
            new_player = Player(player_name, new_client, ip, port)

            # if player_password not in dict_passwords_and_players.keys(): #{password:player}
            if player_password not in dict_passwords_and_players:
                # this is first player to enter
                dict_passwords_and_players_lock.acquire()
                dict_passwords_and_players[player_password] = [new_player]
                dict_passwords_and_players_lock.release()
                print 'added player to dict_passwords_and_players'

                player_thread = threading.Thread(target=handle_first_player_before_game_starts_Thread,
                                                 args=(player_password, new_player, player_threads_tid))
                player_thread.start()

                dict_player_threads_tid_lock.acquire()
                dict_player_threads_tid[player_threads_tid] = player_thread
                dict_player_threads_tid_lock.release()
                print 'add player thread to dict'

                player_threads_tid_lock.acquire()
                player_threads_tid += 1
                player_threads_tid_lock.release()
                print 'increased player_threads_tid to' + str(player_threads_tid)

                total_player_threads_lock.acquire()
                total_player_threads -= 1
                total_player_threads_lock.release()
                print 'decreased total_player_threads to ' + str(total_player_threads)

                print 'new password and new player in dict: %s - %s' % (str(player_password), str(player_name))
                to_wait = True
                to_send = to_wait
                json_to_send = json.dumps(to_send)
                send_with_size(new_player.sock, json_to_send)
                # this player will wait. the server player thread will wait for a receive that this player had quitted,
                #  if another player got in the list (by the main server) then the thread will get out of the while and send to both of the players 'READY' or true.
                # after sending them both that the other player is ready - then the thread will call the game thread, then delete the players from the list and then the thred kills himself.
            elif len(dict_passwords_and_players[player_password]) == 1:
                dict_passwords_and_players_lock.acquire()
                dict_passwords_and_players[player_password].append(new_player)
                dict_passwords_and_players_lock.release()
                print 'add player thread to dict'

                to_wait = False
                to_send = to_wait
                json_to_send = json.dumps(to_send)
                send_with_size(new_player.sock, json_to_send)
            else:
                print 'let the player_thread do the work'
                print 'dictionary passwords and players = ' + str(dict_passwords_and_players)

        except socket.timeout:
            cnt += 1  # when got 10 , we will go to the next line - to show that the server work
            print "#\n" if cnt % 10 == 0 else ',',
            print 'dictionary passwords and players = ' + str(dict_passwords_and_players)

        except KeyboardInterrupt:
            print "\nGot ^C Main\n"
            father_going_to_close = True

    srv.close()
    print "Server Says: Bye Bye ...."
    for t in dict_game_threads_tid.keys():
        t.join()
    for t in dict_player_threads_tid.keys():
        t.join()
    return


# End main

# global father_going_to_close
if __name__ == '__main__':
    try:
        if len(argv) < 2:
            print "Usage: <port_number>"
            exit()
        else:
            port = int(argv[1])
            main(port)
    except KeyboardInterrupt:
        print "\nGot ^C Main\n"
        father_going_to_close = True
