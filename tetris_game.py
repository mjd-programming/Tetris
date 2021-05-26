import pygame
import random
import copy

pygame.font.init()

s_width = 540
s_height = 780
play_width = 300 
play_height = 600
block_size = 30

top_left_x = 120
top_left_y = 150


S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '.....',
      '..0..',
      '..00.',
      '...0.'],
      ['.....',
      '.....',
      '.....',
      '..00.',
      '.00..'],
      ['.....',
      '.....',
      '.0...',
      '.00..',
      '..0..']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '...0.',
      '..00.',
      '..0..'],
      ['.....',
      '.....',
      '.....',
      '.00..',
      '..00.'],
     ['.....',
      '.....',
      '..0..',
      '.00..',
      '.0...']]

I = [['.....',
      '.....',
      '0000.',
      '.....',
      '.....'],
     ['.0...',
      '.0...',
      '.0...',
      '.0...',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....'],
     ['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....'],
      ['.....',
      '.....',
      '.00..',
      '.00..',
      '.....'],
      ['.....',
      '.....',
      '.00..',
      '.00..',
      '.....'],
      ['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (0, 0, 255), (255, 165, 0), (128, 0, 128)]
board_color = (220, 220, 220)
starting_piece_position = (4, 2)


class Piece(object):
    rows = 20
    columns = 10

    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0
        self.floored = False
        self.left = False
        self.right = False
        self.down = False

    
    def move_left(self, n=1):
        for _ in range(n): self.x -= 1

    
    def move_right(self, n=1):
        for _ in range(n): self.x += 1


    def move_up(self, n=1):
        for _ in range(n): self.y -= 1


    def move_down(self, n=1):
        for _ in range(n): self.y += 1


    def spin_left(self, n=1):
        for _ in range(n): self.rotation = self.rotation - 1 % len(self.shape)

    
    def spin_right(self, n=1):
        for _ in range(n): self.rotation = self.rotation + 1 % len(self.shape)


def create_grid(locked_positions={}):
    grid = [[board_color for x in range(10)] for x in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j,i) in locked_positions:
                c = locked_positions[(j,i)]
                grid[i][j] = c
    return grid


def get_shape_positions(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)
    return positions


def get_distance_to_true_bottom(shape):
    format = shape.shape[shape.rotation % len(shape.shape)]
    b = 0
    for line in format[::-1]:
        if '0' not in line:
            b += 1
        else:
            break
    return b


def get_distance_to_true_right(shape):
    format = list(map(list,zip(*shape.shape[shape.rotation % len(shape.shape)][::-1])))
    r = 0
    for row in format[::-1]:
        if '0' not in row:
            r += 1
        else:
            break
    return - r + 2


def get_distance_to_true_left(shape):
    format = list(map(list,zip(*shape.shape[shape.rotation % len(shape.shape)])))
    l = 0
    for row in format:
        if '0' not in row:
            l += 1
        else:
            break
    return (2 * l) - 2


def valid_space(shape, grid, ghost=None):
    if get_distance_to_true_right(shape) + shape.x > 9 or get_distance_to_true_left(shape) + shape.x < 0:
        return False
    if ghost is not None:
        accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == board_color or (j, i) in get_shape_positions(ghost)] for i in range(20)]
    else:
        accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == board_color] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = get_shape_positions(shape)
    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 0 and x == 5:
            return True
    return False


def get_new_bag():
    o_bag = [Piece(starting_piece_position[0], starting_piece_position[1], s) for s in shapes]
    random.shuffle(o_bag)
    return o_bag


bag = get_new_bag() + get_new_bag()

def get_shape():
    global bag, shapes, shape_colors
    if len(bag) == 7:
        bag.extend(get_new_bag())
    return bag.pop(0)


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


def fix_locked_positions(l):
    m = [[board_color for _ in range(10)] for _ in range(20)]
    for p in l:
        m[p[1]][p[0]] = l[p]
    invalid_lines = []
    for i, row in enumerate(m):
        if board_color not in row:
            invalid_lines.append(i)
    invalid_keys = []
    for key in l:
        if key[1] in invalid_lines:
            invalid_keys.append(key)
    for key in invalid_keys:
        l.pop(key)
    return l


def clear_rows(grid, locked):
    fix_locked_positions(locked)
    inc = 0
    for i in range(len(grid)-1,-1,-1):
        row = grid[i]
        if board_color not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc


def remove_piece(grid, piece):
    format = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                grid[i][j] = board_color


def draw_next_shapes(shapes, surface):
    font = pygame.font.SysFont('comicsans', 40)
    label = font.render('Next', 1, (0,0,0))
    for yh, shape in enumerate(shapes):
        format = shape.shape[0]
        pygame.draw.rect(surface, board_color, (450, 60 + yh * 90, 60, 60))
        draw_grid(surface, 4, 4, 450, 60 + yh * 90, 60, 60, block_size / 2)
        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    pygame.draw.rect(surface, shape.color, (450 + j*block_size/2, 60 + i*block_size/2 + yh * 90, block_size / 2, block_size / 2), 0)
                    pygame.draw.rect(surface, (0,0,0), (450 + j*block_size/2, 60 + i*block_size/2 + yh * 90, block_size / 2, block_size / 2), 2)
            pygame.draw.rect(surface, (0,0,0), (450, 60 + yh * 90, 60, 60), 3)

    surface.blit(label, (450, 30))

def draw_hold_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 40)
    label = font.render('Hold', 1, (0,0,0))
    pygame.draw.rect(surface, board_color, (30, 60, 60, 60))
    draw_grid(surface, 4, 4, 30, 60 , 60, 60, block_size / 2)
    if shape != None:
        format = shape.shape[0]
        pygame.draw.rect(surface, board_color, (30, 60, 60, 60), 3)
        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    pygame.draw.rect(surface, shape.color, (30 + j*block_size/2, 60 + i*block_size/2, block_size / 2, block_size / 2), 0)
                    pygame.draw.rect(surface, (0,0,0), (30 + j*block_size/2, 60 + i*block_size/2, block_size / 2, block_size / 2), 2)

    surface.blit(label, (30, 30))
    pygame.draw.rect(surface, (0,0,0), (30, 60, 60, 60), 3)


def draw_ghost(piece, grid, surface):
    ghost = copy.deepcopy(piece)
    while valid_space(ghost, grid, piece):
        ghost.y += 1
    ghost.y -= 1
    format = ghost.shape[ghost.rotation % len(ghost.shape)]
    for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    pygame.draw.rect(surface, (0,0,0), (top_left_x + j * 30 + ghost.x * 30 - 60, top_left_y + i * 30 + ghost.y * 30 - 120, 30, 30), 3)


def draw_window(surface):
    surface.fill((200,200,200))
    font = pygame.font.SysFont('comicsans', 48)
    label = font.render('TETRIS', 1, (0,0,0))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 20))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j* 30, top_left_y + i * 30, 30, 30))

    draw_grid(surface, 20, 10)
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] != board_color:
                pygame.draw.rect(surface, (0,0,0), (top_left_x + j* 30, top_left_y + i * 30, 30, 30), 3)
    pygame.draw.rect(surface, (0, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)


def redraw(w, n, h):
    draw_window(win)
    draw_next_shapes(n, win)
    draw_hold_shape(h, win)


def countdown(surface, pieces, hold):
    redraw(surface, pieces, hold)
    draw_text_middle('3', 100, (255,0,0), surface)
    pygame.display.update()
    pygame.time.wait(1000)
    redraw(surface, pieces, hold)
    draw_text_middle('2', 100, (255,0,0), surface)
    pygame.display.update()
    pygame.time.wait(1000)
    redraw(surface, pieces, hold)
    draw_text_middle('1', 100, (255,0,0), surface)
    pygame.display.update()
    pygame.time.wait(1000)


def spin_right_handler(piece, grid):
    piece.spin_right()
    if not valid_space(piece, grid):
        if piece.shape == T:
            piece.move_down(2)
            piece.move_left()
            if not valid_space(piece, grid):
                piece.move_up(2)
                piece.move_right()
            else:
                return False
        if piece.shape == L:
            piece.move_down(2)
            piece.move_left()
            if not valid_space(piece, grid):
                piece.move_up(2)
                piece.move_right()
            else:
                return False
        piece.move_down()
    if not valid_space(piece, grid): piece.move_left() 
    else: return False
    if not valid_space(piece, grid): piece.move_right(2)
    else: return False
    if not valid_space(piece, grid): 
        piece.move_up()
        piece.move_left(2)
    else: return False    
    if not valid_space(piece, grid): piece.move_right(2)
    else: return False
    if not valid_space(piece, grid):
        piece.move_left()
        piece.move_up()
    else: return False
    if not valid_space(piece, grid): piece.move_left()
    else: return False
    if not valid_space(piece, grid): piece.move_right(2)
    else: return False
    if not valid_space(piece, grid):
        piece.move_down()
        piece.move_left()
    else: return False
    piece.spin_left()
    return True


def spin_left_handler(piece, grid):
    piece.spin_left()
    if not valid_space(piece, grid):
        if piece.shape == T:
            piece.move_down(2)
            piece.move_right()
            if not valid_space(piece, grid):
                piece.move_up(2)
                piece.move_left()
            else:
                return False
        if piece.shape == J:
            piece.move_down(2)
            piece.move_right()
            if not valid_space(piece, grid):
                piece.move_up(2)
                piece.move_left()
            else:
                return False
        piece.move_down()
    if not valid_space(piece, grid): piece.move_right() 
    else: return False
    if not valid_space(piece, grid): piece.move_left(2)
    else: return False
    if not valid_space(piece, grid): 
        piece.move_up()
        piece.move_right(2)
    else: return False    
    if not valid_space(piece, grid): piece.move_left(2)
    else: return False
    if not valid_space(piece, grid):
        piece.move_right()
        piece.move_up()
    else: return False
    if not valid_space(piece, grid): piece.move_right()
    else: return False
    if not valid_space(piece, grid): piece.move_left(2)
    else: return False
    if not valid_space(piece, grid):
        piece.move_down()
        piece.move_right()
    else: return False
    piece.spin_right()
    return True


def main():
    global grid, bag

    bag = get_new_bag() + get_new_bag()

    hold_piece = None
    hold_valid = True

    up_locked = False

    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()

    update_time = 0
    FPS = 30
    total_clear_lines = 0

    grid = create_grid(locked_positions)
    clock.tick(FPS)
        
    pygame.display.update()
    countdown(win, [current_piece, next_piece] + bag[:3], hold_piece)
    while run:
        grid = create_grid(locked_positions)
        clock.tick(FPS)
        update_time += 1

        game_speed = 2 + int(total_clear_lines / 8)
        if game_speed > FPS:
            game_speed = FPS

        if update_time % int(FPS / 10) == 0:
            print('fps')
            if not up_locked:
                if current_piece.left:
                    current_piece.move_left()
                    if not valid_space(current_piece, grid):
                        current_piece.move_right()
                    else:
                        current_piece.floored = False
                elif current_piece.right:
                    current_piece.move_right()
                    if not valid_space(current_piece, grid):
                        current_piece.move_left()
                    else:
                        current_piece.floored = False
                if current_piece.down:
                    current_piece.move_down()
                    if not valid_space(current_piece, grid):
                        current_piece.move_up()
        if update_time % int(FPS / game_speed) == 0:
            print('game speed')
            current_piece.move_down()
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.move_up()
                if current_piece.floored:
                    change_piece = True
                else:
                    current_piece.floored = True
            else:
                current_piece.floored = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and not up_locked:
            current_piece.left = True
        else:
            current_piece.left = False
        if keys[pygame.K_RIGHT] and not up_locked:
            current_piece.right = True
        else:
            current_piece.right = False
        if keys[pygame.K_DOWN] and not up_locked:
            current_piece.down = True
        else:
            current_piece.down = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()
            if event.type == pygame.KEYDOWN and not up_locked:
                if event.key == pygame.K_r:
                    main()
                if event.key == pygame.K_x:
                    current_piece.floored = spin_right_handler(current_piece, grid)                 
                if event.key == pygame.K_z:
                    current_piece.floored = spin_left_handler(current_piece, grid)   
                if event.key == pygame.K_UP:
                    up_locked = True
                    while valid_space(current_piece, grid):
                        current_piece.move_down()
                    current_piece.move_up()
                if event.key == pygame.K_c:
                    if hold_valid and not change_piece:
                        remove_piece(grid, current_piece)
                        hold_valid = False
                        if hold_piece == None:
                            hold_piece = current_piece
                            hold_piece.x = starting_piece_position[0]
                            hold_piece.y = starting_piece_position[1]
                            current_piece = next_piece
                            next_piece = get_shape()
                        else:
                            temp_piece = hold_piece
                            hold_piece = current_piece
                            current_piece = temp_piece
                            current_piece.x = starting_piece_position[0]
                            current_piece.y = starting_piece_position[1]

        shape_pos = get_shape_positions(current_piece)
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            temp_piece = current_piece
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            hold_valid = True
            up_locked = False

            total_clear_lines += clear_rows(grid, locked_positions)
            print(total_clear_lines)

        redraw(win, [next_piece] + bag[:4], hold_piece)
        draw_ghost(current_piece, grid, win)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False
            draw_text_middle("Game Over", 100, (255,0,0), win)
            pygame.display.update()
            pygame.time.wait(1000)
            main()


win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')

if __name__ == '__main__':
    main()
