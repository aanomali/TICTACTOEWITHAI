import copy
import sys
import pygame
import numpy as np

# --- PYGAME SETUP ---
WIDTH = 1000  # Genişletilmiş genişlik
HEIGHT = 1000  # Genişletilmiş yükseklik

ROWS = 3
COLS = 3
SQSIZE = WIDTH // COLS

LINE_WIDTH = 15

OFFSET = 50

# --- COLORS ---
LINE_COLOR = (173, 216, 230)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('TIC TAC TOE AI')

# --- LOAD IMAGES ---
# Resimleri ve arka planı uygun dizine ekleyin
tridents_img = pygame.image.load('Şeytan mızrağı karakteri.png')
halo_img = pygame.image.load('Melek halkası karakteri.png')
background_img = pygame.image.load('arkaplan.webp')
angel_wins_img = pygame.image.load('yapay zekanın kazandığı durumun resmi.webp')
draw_img = pygame.image.load('Beraberlik ekranı.webp')

tridents_img = pygame.transform.scale(tridents_img, (SQSIZE, SQSIZE))
halo_img = pygame.transform.scale(halo_img, (SQSIZE, SQSIZE))
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
angel_wins_img = pygame.transform.scale(angel_wins_img, (WIDTH, HEIGHT))
draw_img = pygame.transform.scale(draw_img, (WIDTH, HEIGHT))

# --- CLASSES ---
class Board:
    def __init__(self):
        self.squares = np.zeros((ROWS, COLS))
        self.marked_sqrs = 0

    def final_state(self, show=False):
        '''
            @return 0 if there is no win yet
            @return 1 if player 1 wins
            @return 2 if player 2 wins
        '''
        # vertical wins
        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    color = (239, 231, 200) if self.squares[0][col] == 2 else (66, 66, 66)
                    iPos = (col * SQSIZE + SQSIZE // 2, 20)
                    fPos = (col * SQSIZE + SQSIZE // 2, HEIGHT - 20)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[0][col]

        # horizontal wins
        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    color = (239, 231, 200) if self.squares[row][0] == 2 else (66, 66, 66)
                    iPos = (20, row * SQSIZE + SQSIZE // 2)
                    fPos = (WIDTH - 20, row * SQSIZE + SQSIZE // 2)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[row][0]

        # desc diagonal
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                color = (239, 231, 200) if self.squares[1][1] == 2 else (66, 66, 66)
                iPos = (20, 20)
                fPos = (WIDTH - 20, HEIGHT - 20)
                pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
            return self.squares[1][1]

        # asc diagonal
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                color = (239, 231, 200) if self.squares[1][1] == 2 else (66, 66, 66)
                iPos = (20, HEIGHT - 20)
                fPos = (WIDTH - 20, 20)
                pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
            return self.squares[1][1]

        # no win yet
        return 0

    def mark_sqr(self, row, col, player):
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def unmark_sqr(self, row, col):
        self.squares[row][col] = 0
        self.marked_sqrs -= 1

    def empty_sqr(self, row, col):
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        empty_sqrs = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.empty_sqr(row, col):
                    empty_sqrs.append((row, col))

        return empty_sqrs

    def isfull(self):
        return self.marked_sqrs == 9

    def isempty(self):
        return self.marked_sqrs == 0


class AI:
    def __init__(self, level=1, player=2):
        self.level = level
        self.player = player

    def rnd(self, board):
        empty_sqrs = board.get_empty_sqrs()
        idx = np.random.choice(len(empty_sqrs))
        return empty_sqrs[idx]  # (row, col)

    def minimax(self, board, depth, maximizing):
        case = board.final_state()

        # terminal case
        if case == 1:
            return 1, None
        elif case == 2:
            return -1, None
        elif board.isfull():
            return 0, None

        if depth == 0:
            return 0, None

        best_move = None

        if maximizing:
            max_eval = -float('inf')
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval = self.minimax(temp_board, depth - 1, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)

            return max_eval, best_move

        else:
            min_eval = float('inf')
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval = self.minimax(temp_board, depth - 1, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)

            return min_eval, best_move

    def eval(self, main_board):
        if self.level == 0:
            move = self.rnd(main_board)
        else:
            eval, move = self.minimax(main_board, 6, False)
            if move is None:
                move = self.rnd(main_board)

        print(f'AI has chosen to mark the square in pos {move}')
        return move  # row, col


class Game:
    def __init__(self):
        self.board = Board()
        self.ai = AI()
        self.player = 1  # 1-cross (tridents)  #2-circles (halo)
        self.gamemode = 'ai'  # pvp or ai
        self.running = True
        self.move_history = []  # Move history to keep track of moves
        self.total_moves = 0  # Total move counter
        self.show_background()
        self.show_lines()

    def show_background(self):
        screen.blit(background_img, (0, 0))

    def show_lines(self):
        # vertical lines
        for col in range(1, COLS):
            pygame.draw.line(screen, LINE_COLOR, (col * SQSIZE, 0), (col * SQSIZE, HEIGHT), LINE_WIDTH)

        # horizontal lines
        for row in range(1, ROWS):
            pygame.draw.line(screen, LINE_COLOR, (0, row * SQSIZE), (WIDTH, row * SQSIZE), LINE_WIDTH)

    def draw_fig(self, row, col):
        if self.board.squares[row][col] == 1:
            screen.blit(tridents_img, (col * SQSIZE, row * SQSIZE))
        elif self.board.squares[row][col] == 2:
            screen.blit(halo_img, (col * SQSIZE, row * SQSIZE))

    def clear_fig(self, row, col):
        rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
        screen.blit(background_img, rect, rect)
        self.show_lines()

    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.move_history.append((row, col, self.player))
        self.draw_fig(row, col)
        self.total_moves += 1

        if len(self.move_history) > 7:
            self.undo_move(self.move_history[0])
            self.move_history.pop(0)

        if not self.isover():
            self.next_turn()
        else:
            self.running = False
            winner = self.board.final_state(show=True)
            pygame.display.update()
            pygame.time.wait(1000)
            if winner == 2:
                self.show_victory_image()
            elif winner == 0 and self.total_moves >= 25:
                self.show_draw_image()

    def undo_move(self, move):
        row, col, _ = move
        self.board.unmark_sqr(row, col)
        self.clear_fig(row, col)
        self.show_lines()
        for move in self.move_history:
            self.draw_fig(move[0], move[1])

    def next_turn(self):
        self.player = self.player % 2 + 1

    def change_gamemode(self):
        self.gamemode = 'ai' if self.gamemode == 'pvp' else 'pvp'

    def isover(self):
        return self.board.final_state(show=True) != 0 or self.total_moves >= 25

    def reset(self):
        self.__init__()

    def show_victory_image(self):
        screen.blit(angel_wins_img, (0, 0))
        pygame.display.flip()

    def show_draw_image(self):
        screen.blit(draw_img, (0, 0))
        pygame.display.flip()

    def draw_text(self, text):
        font = pygame.font.Font(None, 80)
        text_surface = font.render(text, True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()


def main():
    game = Game()
    board = game.board
    ai = game.ai

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    game.change_gamemode()

                if event.key == pygame.K_r:
                    game.reset()
                    board = game.board
                    ai = game.ai

                if event.key == pygame.K_0:
                    ai.level = 0

                if event.key == pygame.K_1:
                    ai.level = 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                row = pos[1] // SQSIZE
                col = pos[0] // SQSIZE

                if board.empty_sqr(row, col) and game.running and game.player == 1:
                    game.make_move(row, col)
                    if game.isover():
                        game.running = False
                        winner = board.final_state()
                        if winner == 1:
                            game.show_victory_image()
                        elif winner == 2:
                            game.show_victory_image()
                        elif game.total_moves >= 25 and winner == 0:
                            game.show_draw_image()

        if game.gamemode == 'ai' and game.player == ai.player and game.running:
            row, col = ai.eval(board)
            game.make_move(row, col)
            if game.isover():
                game.running = False
                winner = board.final_state()
                pygame.display.update()
                pygame.time.wait(1)
                if winner == 1:
                    game.show_victory_image()
                elif winner == 2:
                    game.show_victory_image()
                elif game.total_moves >= 25 and winner == 0:
                    game.show_draw_image()

        pygame.display.update()


main()
