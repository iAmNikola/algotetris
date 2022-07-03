import pygame
from pygame.locals import *
import operator
import random
from pathlib import Path
import numpy as np

from genetic_ai import Genetic_AI     
from ui_variables import UI_variables
from mino import *
from genetic_ai import Genetic_AI

class Pytris:
    block_size = 17 # Height, width of single block
    width = 10      # Board width
    height = 20     # Board height
    clock = None
    screen = None
    headless = False

    def default_values(self):
        self.score_multiplier = [0, 50, 150, 350, 1000]
        self.score = 0      # Total score during one game
        self.level = 1      # Current level
        self.goal = 10      # Lines per level
        self.lines = 0      # Total lines done during one game
        self.bottom_count = 0   # Counter for block to stay in place
        self.hard_drop = False
        
        self.fall_time = 100  # Bigger -> Slower

        # Initial values
        self.blink = False      # Used for blinking effect
        self.start = False      # True when game is being played
        self.pause = False      # True when game is paused
        self.done = False       # True when user quits game
        self.game_over = False  # True when game over
        
        self.dx, self.dy = 3, 0     # Minos location status
        self.rotation = 0           # Minos rotation status
        self.bag = [1, 2, 3, 4, 5, 6, 7]            # Bag with minos
        self.mino = self.get_mino_from_bag()        # Current mino
        self.next_mino = self.get_mino_from_bag()   # Next mino
        
        self.hold = False        # Hold status
        self.hold_mino = None    # Holded mino

        self.ai: Genetic_AI = None  # Agent playing (None = human player)

        self.name_location = 0
        self.name = [65, 65, 65]
        
        self.matrix = [[0 for y in range(self.height + 1)] for x in range(self.width)] # Board matrix

        self.leaders = {'AAA': 0, 'BBB': 0, 'CCC': 0}
        for i in [line.rstrip('\n') for line in open(Path(Path(__file__).parent.absolute(), "leaderboard.txt"))]:
            self.leaders[i.split(' ')[0]] = int(i.split(' ')[1])
        self.leaders = sorted(self.leaders.items(), key=operator.itemgetter(1), reverse=True)

    def __init__(self, ai:Genetic_AI=None, headless=False):
        self.default_values()
        if ai:
            self.ai = ai
            self.start = True
        if headless:
            self.headless = True
        else:
            pygame.init()
            self.ui_vars = UI_variables()

    def run_headless(self):
        if self.ai is None:
            return "Can't run instance with no AI!"
        for pieces_dropped in range(500):    # Do N pieces maximum
            self.rotation, self.dx, self.dy = self.ai.get_best_move(self)
            self.draw_mino()
            erase_count = 0
            for j in range(21):
                is_full = True
                for i in range(10):
                    if self.matrix[i][j] == 0:
                        is_full = False
                if is_full:
                    erase_count += 1
                    k = j
                    while k > 0:
                        for i in range(10):
                            self.matrix[i][k] = self.matrix[i][k - 1]
                        k -= 1
            self.score += self.score_multiplier[erase_count] * self.level
            self.lines += erase_count
            self.mino, self.next_mino = self.next_mino, self.get_mino_from_bag()
            self.dx, self.dy = 3, 0
            self.rotation = 0
            if not self.is_stackable():
                break
        return self.score

    def run(self):
        if self.headless:
            return "Can't run instance with of option 'headless' ON!"

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((300, 374))
        pygame.display.set_caption("PYTRIS™")
        
        self.ai: Genetic_AI = self.ai
        if self.ai:
            pygame.time.set_timer(pygame.USEREVENT, 100)
        else:
            pygame.time.set_timer(pygame.USEREVENT, self.fall_time * 10)
        ###########################################################
        # Loop Start
        ###########################################################

        while not self.done:
            # Pause screen
            if self.pause:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.done = True
                    elif event.type == USEREVENT:
                        pygame.time.set_timer(pygame.USEREVENT, 300)
                        self.draw_board()

                        pause_text = self.ui_vars.h2_b.render("PAUSED", 1, self.ui_vars.white)
                        pause_start = self.ui_vars.h5.render("Press esc to continue", 1, self.ui_vars.white)

                        self.screen.blit(pause_text, (43, 100))
                        if self.blink:
                            self.screen.blit(pause_start, (40, 160))
                            self.blink = False
                        else:
                            self.blink = True
                        pygame.display.update()
                    elif event.type == KEYDOWN:
                        self.erase_mino()
                        if event.key == K_ESCAPE:
                            self.pause = False
                            self.ui_vars.click_sound.play()
                            pygame.time.set_timer(pygame.USEREVENT, 1)

            # Game screen
            elif self.start:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.done = True
                    elif event.type == USEREVENT:
                        # Set speed
                        if not self.game_over:
                            keys_pressed = pygame.key.get_pressed()
                            if self.ai:
                                pygame.time.set_timer(pygame.USEREVENT, 100)
                            else:
                                if keys_pressed[K_DOWN]:
                                    pygame.time.set_timer(pygame.USEREVENT, self.fall_time * 1)
                                else:
                                    pygame.time.set_timer(pygame.USEREVENT, self.fall_time * 10)

                        # Draw a mino
                        self.draw_mino()
                        self.draw_board()

                        # Erase a mino
                        if not self.game_over:
                            self.erase_mino()

                        # Move mino down
                        if not self.is_bottom(self.dx, self.dy):
                            self.dy += 1

                        # Create new mino
                        else:
                            if self.hard_drop or self.bottom_count == 6 or self.ai:
                                self.hard_drop = False
                                self.bottom_count = 0
                                self.score += 10 * self.level
                                self.draw_mino()
                                self.draw_board()
                                self.dx, self.dy = 3, 0
                                self.rotation = 0
                                if self.is_stackable():
                                    self.mino, self.next_mino = self.next_mino, self.get_mino_from_bag()
                                    self.hold = False
                                    if self.ai:
                                        self.rotation, self.dx, _ = self.ai.get_best_move(self)
                                else:
                                    self.start = False
                                    self.game_over = True
                                    self.print_stats()
                                    pygame.time.set_timer(pygame.USEREVENT, 1)
                                    if self.ai:
                                        outfile = open(Path(Path(__file__).parent.absolute(),"leaderboard.txt"),'a')
                                        outfile.write("AlgoBot " + str(self.score) + '\n')
                                        outfile.close()
                            else:
                                self.bottom_count += 1

                        # Erase line
                        erase_count = 0
                        for j in range(21):
                            is_full = True
                            for i in range(10):
                                if self.matrix[i][j] == 0:
                                    is_full = False
                            if is_full:
                                erase_count += 1
                                k = j
                                while k > 0:
                                    for i in range(10):
                                        self.matrix[i][k] = self.matrix[i][k - 1]
                                    k -= 1
                        self.score += self.score_multiplier[erase_count] * self.level
                        if erase_count == 1:
                            self.ui_vars.single_sound.play()
                        elif erase_count == 2:
                            self.ui_vars.double_sound.play()
                        elif erase_count == 3:
                            self.ui_vars.triple_sound.play()
                        elif erase_count == 4:
                            self.ui_vars.tetris_sound.play()

                        # Increase level
                        self.goal -= erase_count
                        self.lines += erase_count
                        if self.goal < 1:
                            self.level += 1
                            self.goal = 10
                            if self.level < 21:
                                self.fall_time = int(self.fall_time * 0.9)

                    elif event.type == KEYDOWN:
                        self.erase_mino()
                        if event.key == K_ESCAPE:
                            self.ui_vars.click_sound.play()
                            self.pause = True
                        # Hard drop
                        elif event.key == K_SPACE:
                            self.ui_vars.drop_sound.play()
                            while not self.is_bottom(self.dx, self.dy):
                                self.dy += 1
                            self.hard_drop = True
                            pygame.time.set_timer(pygame.USEREVENT, 1)
                            self.draw_mino()
                            self.draw_board()
                        # Hold
                        elif event.key == K_LSHIFT or event.key == K_c:
                            if self.hold == False:
                                self.ui_vars.move_sound.play()
                                if self.hold_mino is None:
                                    self.hold_mino, self.mino = self.mino, self.next_mino
                                    self.next_mino = self.get_mino_from_bag()
                                else:
                                    self.hold_mino, self.mino = self.mino, self.hold_mino
                                self.dx, self.dy = 3, 0
                                self.rotation = 0
                                self.hold = True
                            self.draw_mino()
                            self.draw_board()
                        # Turn right
                        elif event.key == K_UP or event.key == K_x:
                            if self.is_turnable_r(self.dx, self.dy):
                                self.ui_vars.move_sound.play()
                                self.rotation += 1
                            # Kick
                            elif self.is_turnable_r(self.dx, self.dy - 1):
                                self.ui_vars.move_sound.play()
                                self.dy -= 1
                                self.rotation += 1
                            elif self.is_turnable_r(self.dx + 1, self.dy):
                                self.ui_vars.move_sound.play()
                                self.dx += 1
                                self.rotation += 1
                            elif self.is_turnable_r(self.dx - 1, self.dy):
                                self.ui_vars.move_sound.play()
                                self.dx -= 1
                                self.rotation += 1
                            elif self.is_turnable_r(self.dx, self.dy - 2):
                                self.ui_vars.move_sound.play()
                                self.dy -= 2
                                self.rotation += 1
                            elif self.is_turnable_r(self.dx + 2, self.dy):
                                self.ui_vars.move_sound.play()
                                self.dx += 2
                                self.rotation += 1
                            elif self.is_turnable_r(self.dx - 2, self.dy):
                                self.ui_vars.move_sound.play()
                                self.dx -= 2
                                self.rotation += 1
                            if self.rotation == 4:
                                self.rotation = 0
                            self.draw_mino()
                            self.draw_board()
                        # Turn left
                        elif event.key == K_z or event.key == K_LCTRL:
                            if self.is_turnable_l(self.dx, self.dy):
                                self.ui_vars.move_sound.play()
                                self.rotation -= 1
                            # Kick
                            elif self.is_turnable_l(self.dx, self.dy - 1):
                                self.ui_vars.move_sound.play()
                                self.dy -= 1
                                self.rotation -= 1
                            elif self.is_turnable_l(self.dx + 1, self.dy):
                                self.ui_vars.move_sound.play()
                                self.dx += 1
                                self.rotation -= 1
                            elif self.is_turnable_l(self.dx - 1, self.dy):
                                self.ui_vars.move_sound.play()
                                self.dx -= 1
                                self.rotation -= 1
                            elif self.is_turnable_l(self.dx, self.dy - 2):
                                self.ui_vars.move_sound.play()
                                self.dy -= 2
                                self.rotation += 1
                            elif self.is_turnable_l(self.dx + 2, self.dy):
                                self.ui_vars.move_sound.play()
                                self.dx += 2
                                self.rotation += 1
                            elif self.is_turnable_l(self.dx - 2, self.dy):
                                self.ui_vars.move_sound.play()
                                self.dx -= 2
                            if self.rotation == -1:
                                self.rotation = 3
                            self.draw_mino()
                            self.draw_board()
                        # Move left
                        elif event.key == K_LEFT:
                            if not self.is_leftedge():
                                self.ui_vars.move_sound.play()
                                self.dx -= 1
                            self.draw_mino()
                            self.draw_board()
                        # Move right
                        elif event.key == K_RIGHT:
                            if not self.is_rightedge():
                                self.ui_vars.move_sound.play()
                                self.dx += 1
                            self.draw_mino()
                            self.draw_board()

                pygame.display.update()

            # Game over screen
            elif self.game_over:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.done = True
                    elif event.type == USEREVENT:
                        pygame.time.set_timer(pygame.USEREVENT, 300)
                        over_text_1 = self.ui_vars.h2_b.render("GAME", 1, self.ui_vars.white)
                        over_text_2 = self.ui_vars.h2_b.render("OVER", 1, self.ui_vars.white)
                        over_start = self.ui_vars.h5.render("Press return to continue", 1, self.ui_vars.white)

                        self.draw_board()
                        self.screen.blit(over_text_1, (58, 75))
                        self.screen.blit(over_text_2, (62, 105))

                        name_1 = self.ui_vars.h2_i.render(chr(self.name[0]), 1, self.ui_vars.white)
                        name_2 = self.ui_vars.h2_i.render(chr(self.name[1]), 1, self.ui_vars.white)
                        name_3 = self.ui_vars.h2_i.render(chr(self.name[2]), 1, self.ui_vars.white)

                        underbar_1 = self.ui_vars.h2.render("_", 1, self.ui_vars.white)
                        underbar_2 = self.ui_vars.h2.render("_", 1, self.ui_vars.white)
                        underbar_3 = self.ui_vars.h2.render("_", 1, self.ui_vars.white)

                        self.screen.blit(name_1, (65, 147))
                        self.screen.blit(name_2, (95, 147))
                        self.screen.blit(name_3, (125, 147))

                        if self.blink:
                            self.screen.blit(over_start, (32, 195))
                            self.blink = False
                        else:
                            if self.name_location == 0:
                                self.screen.blit(underbar_1, (65, 145))
                            elif self.name_location == 1:
                                self.screen.blit(underbar_2, (95, 145))
                            elif self.name_location == 2:
                                self.screen.blit(underbar_3, (125, 145))
                            self.blink = True

                        pygame.display.update()
                    elif event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            self.ui_vars.click_sound.play()

                            outfile = open(Path(Path(__file__).parent.absolute(),"leaderboard.txt"),'a')
                            outfile.write(chr(self.name[0]) + chr(self.name[1]) + chr(self.name[2]) + ' ' + str(self.score) + '\n')
                            outfile.close()

                            self.default_values()

                            pygame.time.set_timer(pygame.USEREVENT, 1)
                        elif event.key == K_RIGHT:
                            if self.name_location != 2:
                                self.name_location += 1
                            else:
                                self.name_location = 0
                            pygame.time.set_timer(pygame.USEREVENT, 1)
                        elif event.key == K_LEFT:
                            if self.name_location != 0:
                                self.name_location -= 1
                            else:
                                self.name_location = 2
                            pygame.time.set_timer(pygame.USEREVENT, 1)
                        elif event.key == K_UP:
                            self.ui_vars.click_sound.play()
                            if self.name[self.name_location] != 90:
                                self.name[self.name_location] += 1
                            else:
                                self.name[self.name_location] = 65
                            pygame.time.set_timer(pygame.USEREVENT, 1)
                        elif event.key == K_DOWN:
                            self.ui_vars.click_sound.play()
                            if self.name[self.name_location] != 65:
                                self.name[self.name_location] -= 1
                            else:
                                self.name[self.name_location] = 90
                            pygame.time.set_timer(pygame.USEREVENT, 1)

            # Start screen
            else:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.done = True
                    elif event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            self.ui_vars.click_sound.play()
                            self.start = True
                pygame.time.set_timer(pygame.USEREVENT, 300)
                self.screen.fill(self.ui_vars.white)
                pygame.draw.rect(
                    self.screen,
                    self.ui_vars.grey_1,
                    Rect(0, 187, 300, 187)
                )

                title = self.ui_vars.h1.render("PYTRIS™", 1, self.ui_vars.grey_1)
                title_start = self.ui_vars.h5.render("Press space to start", 1, self.ui_vars.white)
                title_info = self.ui_vars.h6.render("Copyright (c) 2017 Jason Kim All Rights Reserved.", 1, self.ui_vars.white)

                leader_1 = self.ui_vars.h5_i.render('1st ' + self.leaders[0][0] + ' ' + str(self.leaders[0][1]), 1, self.ui_vars.grey_1)
                leader_2 = self.ui_vars.h5_i.render('2nd ' + self.leaders[1][0] + ' ' + str(self.leaders[1][1]), 1, self.ui_vars.grey_1)
                leader_3 = self.ui_vars.h5_i.render('3rd ' + self.leaders[2][0] + ' ' + str(self.leaders[2][1]), 1, self.ui_vars.grey_1)

                if self.blink:
                    self.screen.blit(title_start, (92, 195))
                    self.blink = False
                else:
                    self.blink = True

                self.screen.blit(title, (65, 120))
                self.screen.blit(title_info, (40, 335))

                self.screen.blit(leader_1, (10, 10))
                self.screen.blit(leader_2, (10, 23))
                self.screen.blit(leader_3, (10, 36))

                if not self.start:
                    pygame.display.update()
                    self.clock.tick(3)
        pygame.quit()


    # Draw block
    def draw_block(self, x, y, color):
        pygame.draw.rect(
            self.screen,
            color,
            Rect(x, y, self.block_size, self.block_size)
        )
        pygame.draw.rect(
            self.screen,
            self.ui_vars.grey_1,
            Rect(x, y, self.block_size, self.block_size),
            1
        )

    # Draw game screen
    def draw_board(self):
        self.screen.fill(self.ui_vars.grey_1)

        # Draw sidebar
        pygame.draw.rect(
            self.screen,
            self.ui_vars.white,
            Rect(204, 0, 96, 374)
        )

        # Draw next mino
        grid_n = tetrimino.mino_map[self.next_mino - 1][0]

        for i in range(4):
            for j in range(4):
                dx = 220 + self.block_size * j
                dy = 140 + self.block_size * i
                if grid_n[i][j] != 0:
                    pygame.draw.rect(
                        self.screen,
                        self.ui_vars.t_color[grid_n[i][j]],
                        Rect(dx, dy, self.block_size, self.block_size)
                    )

        # Draw hold mino

        if self.hold_mino is not None:
            grid_h = tetrimino.mino_map[self.hold_mino - 1][0]
            for i in range(4):
                for j in range(4):
                    dx = 220 + self.block_size * j
                    dy = 50 + self.block_size * i
                    if grid_h[i][j] != 0:
                        pygame.draw.rect(
                            self.screen,
                            self.ui_vars.t_color[grid_h[i][j]],
                            Rect(dx, dy, self.block_size, self.block_size)
                        )

        # Draw texts
        text_hold = self.ui_vars.h5.render("HOLD", 1, self.ui_vars.black)
        text_next = self.ui_vars.h5.render("NEXT", 1, self.ui_vars.black)
        text_score = self.ui_vars.h5.render("SCORE", 1, self.ui_vars.black)
        score_value = self.ui_vars.h4.render(str(self.score), 1, self.ui_vars.black)
        text_level = self.ui_vars.h5.render("LEVEL", 1, self.ui_vars.black)
        level_value = self.ui_vars.h4.render(str(self.level), 1, self.ui_vars.black)
        text_lines = self.ui_vars.h5.render("LINES", 1, self.ui_vars.black)
        lines_value = self.ui_vars.h4.render(str(self.lines), 1, self.ui_vars.black)

        # Place texts
        self.screen.blit(text_hold, (215, 14))
        self.screen.blit(text_next, (215, 104))
        self.screen.blit(text_score, (215, 194))
        self.screen.blit(score_value, (220, 210))
        self.screen.blit(text_level, (215, 254))
        self.screen.blit(level_value, (220, 270))
        self.screen.blit(text_lines, (215, 314))
        self.screen.blit(lines_value, (220, 330))

        # Draw board
        for x in range(self.width):
            for y in range(self.height):
                dx = 17 + self.block_size * x
                dy = 17 + self.block_size * y
                self.draw_block(dx, dy, self.ui_vars.t_color[self.matrix[x][y + 1]])

    # Draw a tetrimino
    def draw_mino(self):
        grid = tetrimino.mino_map[self.mino - 1][self.rotation]
        tx, ty = self.dx, self.dy
        while not self.is_bottom(tx, ty):
            ty += 1

        if not self.ai:
            # Draw ghost
            for i in range(4):
                for j in range(4):
                    if grid[i][j] != 0:
                        self.matrix[tx + j][ty + i] = 8

        # Draw mino
        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    self.matrix[self.dx + j][self.dy + i] = grid[i][j]

    # Erase a tetrimino
    def erase_mino(self):
        grid = tetrimino.mino_map[self.mino - 1][self.rotation]

        if not self.ai:
            # Erase ghost
            for j in range(21):
                for i in range(10):
                    if self.matrix[i][j] == 8:
                        self.matrix[i][j] = 0

        # Erase mino
        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    self.matrix[self.dx + j][self.dy + i] = 0

    # Returns true if mino is at bottom
    def is_bottom(self, x, y):
        grid = tetrimino.mino_map[self.mino - 1][self.rotation]

        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    if (y + i + 1) == 21:
                        return True
                    elif self.matrix[x + j][y + i + 1] != 0\
                        and self.matrix[x + j][y + i + 1] != 8:
                        return True
        return False

    # Returns true if new block is drawable
    def is_stackable(self):
        grid = tetrimino.mino_map[self.next_mino - 1][self.rotation]
        for i in range(4):
            for j in range(4):
                if (self.dx + j) < 0 or (self.dx + j) > 9:
                    continue
                if grid[i][j] != 0 and self.matrix[self.dx + j][self.dy + i] != 0:
                    return False
        return True

    # Returns true if mino is at the left edge
    def is_leftedge(self):
        grid = tetrimino.mino_map[self.mino - 1][self.rotation]

        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    if (self.dx + j - 1) < 0:
                        continue
                    elif self.matrix[self.dx + j - 1][self.dy + i] != 0:
                        return True

        return False

    # Returns true if mino is at the right edge
    def is_rightedge(self):
        grid = tetrimino.mino_map[self.mino - 1][self.rotation]

        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    if (self.dx + j + 1) > 9:
                        continue
                    elif self.matrix[self.dx + j + 1][self.dy + i] != 0:
                        return True

        return False

    # Returns true if turning right is possible
    def is_turnable_r(self, x, y):
        if self.rotation != 3:
            grid = tetrimino.mino_map[self.mino - 1][self.rotation + 1]
        else:
            grid = tetrimino.mino_map[self.mino - 1][0]

        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    if (x + j) < 0 or (x + j) > 9 or (y + i) < 0 or (y + i) > 20:
                        continue
                    elif self.matrix[x + j][y + i] != 0:
                        return False
        return True

    # Returns true if turning left is possible
    def is_turnable_l(self, x, y):
        if self.rotation != 3:
            grid = tetrimino.mino_map[self.mino - 1][self.rotation + 1]
        else:
            grid = tetrimino.mino_map[self.mino - 1][0]

        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    if (x + j) < 0 or (x + j) > 9 or (y + i) < 0 or (y + i) > 20:
                        continue
                    elif self.matrix[x + j][y + i] != 0:
                        return False
        return True

    # Returns 1 of the minos from the bag and ensures that each element will be spawned 
    def get_mino_from_bag(self):
        if self.bag == []:
            self.bag = [1, 2, 3, 4, 5, 6, 7]
        i = random.randrange(len(self.bag))      # get random index
        self.bag[i], self.bag[-1] = self.bag[-1], self.bag[i]   # swap with the last element
        return self.bag.pop()                    # pop last element O(1)

    def print_stats(self):
        print(f"{'='*20}")
        print("{:^20s}".format("Game stats"))
        print(f"{'-'*20}")
        print(f"Score: {self.score}")
        print(f"Lines: {self.lines}")
        print(f"{'='*20}")


if __name__ == "__main__":
    AI_RUN = True
    top_gene_weights = [
            -0.7255216469812669,    # aggregated_height
            -0.734674596688063,     # n_holes
            -0.44155695690797003,   # n_cols_with_holes
            -0.012949057576052692,  # bumpiness
            -0.6886875589233459,    # n_pits
            0.8379280068158563,     # deepest_well
            -0.8355259931400796,    # row_transitions
            0.3028779001998809,     # col_transitions
            0.22814520433580232     # lines_cleared
        ]
    top_gene_weights = [0.5501233868775208, -0.45474448395384504, -0.032619056589323896, -0.4054268211077717, -0.42503073375086964, -0.12941049261789878, 0.15512310177762675, -1.4142555391926974, 0.8136523639225275]
    if AI_RUN:
        game = Pytris(ai=Genetic_AI(genotype=np.array(top_gene_weights)))
    else:
        game = Pytris()
    game.run()