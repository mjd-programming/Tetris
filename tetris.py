import pygame
import random
import copy
from enum import Enum

font = pygame.font.init()

shapes = [
    [['....','oooo','....','....'],
     ['..o.','..o.','..o.','..o.'],
     ['....','....','oooo','....'],
     ['.o..','.o..','.o..','.o..']],
    [['o...','ooo.','....','....'],
     ['.oo.','.o..','.o..','....'],
     ['....','ooo.','..o.','....'],
     ['.o..','.o..','oo..','....']],
    [['..o.','ooo.','....','....'],
     ['.o..','.o..','.oo.','....'],
     ['....','ooo.','o...','....'],
     ['oo..','.o..','.o..','....']],
    [['.oo.','.oo.','....','....'],
     ['.oo.','.oo.','....','....'],
     ['.oo.','.oo.','....','....'],
     ['.oo.','.oo.','....','....']],
    [['.oo.','oo..','....','....'],
     ['.o..','.oo.','..o.','....'],
     ['....','.oo.','oo..','....'],
     ['o...','oo..','.o..','....']],
    [['.o..','ooo.','....','....'],
     ['.o..','.oo.','.o..','....'],
     ['....','ooo.','.o..','....'],
     ['.o..','oo..','.o..','....']],
    [['oo..','.oo.','....','....'],
     ['..o.','.oo.','.o..','....'],
     ['....','oo..','.oo.','....'],
     ['.o..','oo..','o...','....']]
]

shape_indecies = ['i','j','l','o','s','t','z']

colors = [(0,255,255),(0,0,255),(255,127,0),(255,255,0),(0,255,0),(255,0,255),(255,0,0)]
board_color = (220,220,220)
starting_positions = (3, -1)

FPS = 30

s_width = 540
s_height = 780
play_width = 300 
play_height = 600
block_size = 30

top_left_x = 120
top_left_y = 150

class Piece:
    def __init__(self, sx, sy, s):
        self.x = sx
        self.y = sy
        self.shape = s
        self.color = colors[s]
        self.spin = 0
        self.floored = False
        
    def move_left(self, n=1):
        for _ in range(n): self.x -= 1

    def move_right(self, n=1):
        for _ in range(n): self.x += 1

    def move_up(self, n=1):
        for _ in range(n): self.y -= 1

    def move_down(self, n=1):
        for _ in range(n): self.y += 1

    def spin_left(self):
        self.spin = self.spin - 1 % len(shapes[self.shape])

    def spin_right(self):
        self.spin = self.spin + 1 % len(shapes[self.shape])

def get_format(p):
    return shapes[p.shape][p.spin % len(shapes[p.shape])]

def get_grid(locked={}):
    g = [[board_color for _ in range(10)] for _ in range(20)]
    for i in range(20):
        for j in range(10):
            if (j, i) in locked:
                g[i][j] = locked[(j, i)]
    return g

def get_dist_to_true_bottum(p):
    f = get_format(p)
    b = 0
    for line in f[::-1]:
        if 'o' not in line:
            b += 1
        else:
            break
    return b

def get_dist_to_true_right(p):
    f = list(map(list,zip(*get_format(p)[::-1])))
    r = 0
    for row in f[::-1]:
        if 'o' not in row:
            r += 1
        else:
            break
    return - r + 3

def get_dist_to_true_left(p):
    f = list(map(list,zip(*get_format(p))))
    l = 0
    for row in f:
        if 'o' not in row:
            l += 1
        else:
            break
    return (2 * l)

def get_piece_positions(p):
    positions = []
    f = get_format(p)
    for i, l in enumerate(f):
        row = list(l)
        for j, c in enumerate(row):
            if c == 'o':
                positions.append((p.x + j, p.y + i))
    return positions

def is_valid(p, g, gh=None):
    if get_dist_to_true_right(p) + p.x > 9 or get_dist_to_true_left(p) + p.x < 0:
        return False
    if gh is not None:
        ap = [[(j, i) for j in range(10) if g[i][j] == board_color or (j, i) in get_piece_positions(gh)] for i in range(20)]
    else:
        ap = [[(j, i) for j in range(10) if g[i][j] == board_color] for i in range(20)]
    ap = [j for sub in ap for j in sub]
    f = get_piece_positions(p)
    for pos in f:
        if pos not in ap:
            if pos[1] > -1:
                return False
    return True

def has_lost(positions):
    for pos in positions:
        x, y = pos
        if y <= 0 and (x > starting_positions[0] - 2 and x < starting_positions[0] + 2):
            return True
        if y < 0:
            return True
    return False

def get_new_bag():
    o_bag = [Piece(starting_positions[0], starting_positions[1], s) for s in range(7)]
    random.shuffle(o_bag)
    return o_bag

def get_next_piece(b):
    if len(b) == 7:
        b.extend(get_new_bag())
    return b.pop(0)

def clear_rows(g, l):
    clear = []
    for i, row in enumerate(g):
        if board_color not in row:
            clear.append(i)
    if len(clear) > 0:
        c = False
        while not c:
            c = True
            for key in sorted(l, key=lambda x: x[1])[::-1]:
                y = key[1]
                if y in clear:
                    c = False
                    try:
                        del l[key]
                    except:
                        continue
        for i in clear:
            for key in sorted(l, key=lambda x: x[1])[::-1]:
                x, y = key
                if y < i:
                    newKey = (x, y + 1)
                    l[newKey] = l.pop(key)
    return len(clear)

def remove_piece(g, p):
    f = get_format(p)
    for i, line in enumerate(f):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                g[i][j] = board_color

def spin_right_handler(p, g):
    p.spin_right()
    if not is_valid(p, g):
        if p.shape == shape_indecies.index('t'):
            p.move_down(2)
            p.move_left()
            if not is_valid(p, g):
                p.move_up(2)
                p.move_right()
            else:
                return False
        if p.shape == shape_indecies.index('l'):
            p.move_down(2)
            p.move_left()
            if not is_valid(p, g):
                p.move_up(2)
                p.move_right()
            else:
                return False
        p.move_down()
    if not is_valid(p, g): p.move_left() 
    else: return False
    if not is_valid(p, g): p.move_right(2)
    else: return False
    if not is_valid(p, g): 
        p.move_up()
        p.move_left(2)
    else: return False    
    if not is_valid(p, g): p.move_right(2)
    else: return False
    if not is_valid(p, g):
        p.move_left()
        p.move_up()
    else: return False
    if not is_valid(p, g): p.move_left()
    else: return False
    if not is_valid(p, g): p.move_right(2)
    else: return False
    if not is_valid(p, g):
        p.move_down()
        p.move_left()
    else: return False
    p.spin_left()
    return True


def spin_left_handler(p, g):
    p.spin_left()
    if not is_valid(p, g):
        if p.shape == shape_indecies.index('t'):
            p.move_down(2)
            p.move_right()
            if not is_valid(p, g):
                p.move_up(2)
                p.move_left()
            else:
                return False
        if p.shape == shape_indecies.index('j'):
            p.move_down(2)
            p.move_right()
            if not is_valid(p, g):
                p.move_up(2)
                p.move_left()
            else:
                return False
        p.move_down()
    if not is_valid(p, g): p.move_right() 
    else: return False
    if not is_valid(p, g): p.move_left(2)
    else: return False
    if not is_valid(p, g): 
        p.move_up()
        p.move_right(2)
    else: return False    
    if not is_valid(p, g): p.move_left(2)
    else: return False
    if not is_valid(p, g):
        p.move_right()
        p.move_up()
    else: return False
    if not is_valid(p, g): p.move_right()
    else: return False
    if not is_valid(p, g): p.move_left(2)
    else: return False
    if not is_valid(p, g):
        p.move_down()
        p.move_right()
    else: return False
    p.spin_right()
    return True

def get_stack_height(l):
    return 19 - sorted(l, key=lambda x: x[1])[0][1]

def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    bg_label = font.render(text, 1, (0,0,0))
    label = font.render(text, 1, color)

    surface.blit(bg_label, (top_left_x + play_width/2 - (label.get_width() / 2) - 2, top_left_y + play_height/2 - label.get_height()/2))
    surface.blit(bg_label, (top_left_x + play_width/2 - (label.get_width() / 2) + 2, top_left_y + play_height/2 - label.get_height()/2))
    surface.blit(bg_label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y + play_height/2 - label.get_height()/2 - 2))
    surface.blit(bg_label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y + play_height/2 - label.get_height()/2 + 2))
    surface.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y + play_height/2 - label.get_height()/2))


def draw_grid(surface, row, col, x=top_left_x, y=top_left_y, w=play_width, h=play_height, size=block_size):
    sx = x
    sy = y
    for i in range(row):
        pygame.draw.line(surface, (200,200,200), (sx, sy+ i*size), (sx + w, sy + i * size))
        for j in range(col):
            pygame.draw.line(surface, (200,200,200), (sx + j * size, sy), (sx + j * size, sy + h))

def draw_next_shapes(shapes, surface):
    font = pygame.font.SysFont('comicsans', 40)
    label = font.render('Next', 1, (0,0,0))
    for yh, piece in enumerate(shapes):
        format = get_format(piece)
        pygame.draw.rect(surface, board_color, (450, 60 + yh * 90, 60, 60))
        draw_grid(surface, 4, 4, 450, 60 + yh * 90, 60, 60, block_size / 2)
        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == 'o':
                    pygame.draw.rect(surface, piece.color, (450 + j*block_size/2, 60 + i*block_size/2 + yh * 90, block_size / 2, block_size / 2), 0)
                    pygame.draw.rect(surface, (0,0,0), (450 + j*block_size/2, 60 + i*block_size/2 + yh * 90, block_size / 2, block_size / 2), 2)
            pygame.draw.rect(surface, (0,0,0), (450, 60 + yh * 90, 60, 60), 3)

    surface.blit(label, (450, 30))

def draw_hold_shape(piece, surface):
    font = pygame.font.SysFont('comicsans', 40)
    label = font.render('Hold', 1, (0,0,0))
    pygame.draw.rect(surface, board_color, (30, 60, 60, 60))
    draw_grid(surface, 4, 4, 30, 60 , 60, 60, block_size / 2)
    if piece != None:
        format = get_format(piece)
        pygame.draw.rect(surface, board_color, (30, 60, 60, 60), 3)
        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == 'o':
                    pygame.draw.rect(surface, piece.color, (30 + j*block_size/2, 60 + i*block_size/2, block_size / 2, block_size / 2), 0)
                    pygame.draw.rect(surface, (0,0,0), (30 + j*block_size/2, 60 + i*block_size/2, block_size / 2, block_size / 2), 2)

    surface.blit(label, (30, 30))
    pygame.draw.rect(surface, (0,0,0), (30, 60, 60, 60), 3)

def draw_ghost(piece, grid, surface):
    ghost = copy.deepcopy(piece)
    while is_valid(ghost, grid, piece):
        ghost.y += 1
    ghost.y -= 1
    format = get_format(ghost)
    for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == 'o':
                    pygame.draw.rect(surface, (0,0,0), (top_left_x + j * 30 + ghost.x * 30, top_left_y + i * 30 + ghost.y * 30, 30, 30), 3)

def draw_window(surface, g):
    surface.fill((200,200,200))
    font = pygame.font.SysFont('comicsans', 48)
    label = font.render('TETRIS', 1, (0,0,0))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 20))

    for i in range(20):
        for j in range(10):
            pygame.draw.rect(surface, g[i][j], (top_left_x + j* 30, top_left_y + i * 30, 30, 30))

    draw_grid(surface, 20, 10)
    for i in range(len(g)):
        for j in range(len(g[i])):
            if g[i][j] != board_color:
                pygame.draw.rect(surface, (0,0,0), (top_left_x + j* 30, top_left_y + i * 30, 30, 30), 3)
    pygame.draw.rect(surface, (0, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

def redraw(w, n, h, g):
    draw_window(w, g)
    draw_next_shapes(n, w)
    draw_hold_shape(h, w)

def countdown(surface, pieces, hold, grid):
    redraw(surface, pieces, hold, grid)
    draw_text_middle('3', 100, (255,0,0), surface)
    pygame.display.update()
    pygame.time.wait(500)
    redraw(surface, pieces, hold, grid)
    draw_text_middle('2', 100, (255,0,0), surface)
    pygame.display.update()
    pygame.time.wait(500)
    redraw(surface, pieces, hold, grid)
    draw_text_middle('1', 100, (255,0,0), surface)
    pygame.display.update()
    pygame.time.wait(500)
    redraw(surface, pieces, hold, grid)
    draw_text_middle('GO', 100, (255,0,0), surface)
    pygame.display.update()
    pygame.time.wait(500)

class Tetris:
    def __init__(self):
        self.pygame = pygame
        self.window = pygame.display.set_mode((s_width, s_height))
        pygame.display.set_caption('Tetris')
        self.clock = self.pygame.time.Clock()
        self.reset()

    def reset(self):
        self.grid = get_grid()
        self.locked_positions = {}
        self.game_speed = 10
        self.bag = get_new_bag()
        self.c_piece = get_next_piece(self.bag)
        self.n_piece = get_next_piece(self.bag)
        self.h_piece = None
        self.lines_clear = 0
        self.lost = False
        self.change = False
        self.hold_valid = True
        self.up_locked = False
        self.update_time = 0
        self.stack_height = 19
        self.run = True
        pygame.display.update()
        countdown(self.window, [self.c_piece, self.n_piece] + self.bag[:3], self.h_piece, self.grid)
        self.start()
    
    def move_left(self):
        if self.up_locked or self.change: return
        self.c_piece.move_left()
        if not is_valid(self.c_piece, self.grid):
            self.c_piece.move_right()

    def move_right(self):
        if self.up_locked or self.change: return
        self.c_piece.move_right()
        if not is_valid(self.c_piece, self.grid):
            self.c_piece.move_left()

    def soft_drop(self):
        if self.up_locked or self.change: return
        self.c_piece.move_down()
        if not is_valid(self.c_piece, self.grid):
            self.c_piece.move_up()
            self.change = True

    def hard_drop(self):
        self.up_locked = True
        while is_valid(self.c_piece, self.grid):
            self.c_piece.move_down()
        self.c_piece.move_up()
        self.change = True

    def spin_left(self):
        if self.up_locked or self.change: return
        self.c_piece.floored = spin_left_handler(self.c_piece, self.grid)

    def spin_right(self):
        if self.up_locked or self.change: return
        self.c_piece.floored = spin_right_handler(self.c_piece, self.grid)

    def hold(self):
        if self.hold_valid and not self.up_locked and not self.change:
            remove_piece(self.grid, self.c_piece)
            self.hold_valid = False
            if self.h_piece == None:
                self.h_piece = self.c_piece
                self.h_piece.x = starting_positions[0]
                self.h_piece.y = starting_positions[1]
                self.c_piece = self.n_piece
                self.n_piece = get_next_piece(self.bag)
            else:
                temp_piece = self.h_piece
                self.h_piece = self.c_piece
                self.c_piece = temp_piece
                self.c_piece.x = starting_positions[0]
                self.c_piece.y = starting_positions[1]

    def start(self):
        while self.run:
            self.grid = get_grid(self.locked_positions)
            self.clock.tick(FPS)
            self.update_time += 1

            self.game_speed = 2 + int(self.lines_clear / 8)
            if self.game_speed > 10:
                self.game_speed = 10
            if self.update_time % (FPS / self.game_speed) == 0:
                self.soft_drop()
            if self.update_time % (FPS / 10) == 0:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    self.move_left()
                if keys[pygame.K_RIGHT]:
                    self.move_right()
                if keys[pygame.K_DOWN]:
                    self.soft_drop()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.run = False
                        pygame.display.quit()
                        quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.reset()
                        if event.key == pygame.K_x:
                            self.spin_right()                 
                        if event.key == pygame.K_z:
                            self.spin_left()   
                        if event.key == pygame.K_UP:
                            self.hard_drop()
                        if event.key == pygame.K_c:
                            self.hold()

            shape_pos = get_piece_positions(self.c_piece)
            for i in range(len(shape_pos)):
                x, y = shape_pos[i]
                if y > -1:
                    self.grid[y][x] = self.c_piece.color

            if self.change:
                for pos in shape_pos:
                    p = (pos[0], pos[1])
                    self.locked_positions[p] = self.c_piece.color
                self.c_piece = self.n_piece
                self.n_piece = get_next_piece(self.bag)
                self.change = False
                self.hold_valid = True
                self.up_locked = False

                self.lines_clear += clear_rows(self.grid, self.locked_positions)

            redraw(self.window, [self.n_piece] + self.bag[:4], self.h_piece, self.grid)
            draw_ghost(self.c_piece, self.grid, self.window)
            pygame.display.update()

            if has_lost(self.locked_positions):
                self.run = False
                draw_text_middle("Game Over", 100, (255,0,0), self.window)
                pygame.display.update()
                pygame.time.wait(1000)
                self.reset()

if __name__ == '__main__':
    Tetris()