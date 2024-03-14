from datetime import datetime
import os
import threading
import time
from queue import Queue

import pygame

import config
from agents import Human
from sprites import Tile, Checker, WinChecker
from state import State
from util import TimedFunction, Timeout


class EndGame(Exception):
    pass


class Quit(Exception):
    pass


class Game:

    def load_tiles(self):
        try:
            for i in range(config.M):
                for j in range(config.N):
                    tile = Tile((i, j))
                    self.tiles_list.append(tile)
                    tile.add(self.tiles_sprites)
        except Exception as e:
            raise e

    def load_checkers(self, actions_filename):
        if actions_filename is None:
            return
        try:
            with open(os.path.join(config.ACTIONS_FOLDER, actions_filename)) as file:
                for line in file:
                    self.generate_checker(int(line.strip()))
                    while self.checkers_list[-1].gravity():
                        pass
        except EndGame:
            self.endgame_handler()
        except Exception as e:
            raise e

    def __init__(self, agents_list, max_depth, max_think_time, actions_filename):
        pygame.display.set_caption('Pyveži4')
        pygame.font.init()
        config.INFO_FONT = pygame.font.Font(os.path.join(config.FONT_FOLDER, 'info_font.ttf'), 25)
        self.WIDTH = config.N * config.TILE_SIZE
        self.HEIGHT = config.M * config.TILE_SIZE
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT + config.INFO_HEIGHT))
        self.running = True
        self.playing = False
        self.falling = False
        self.status = None
        self.step_cnt = 0
        self.state = State()
        self.log = open(os.path.join(config.LOG_FOLDER, f'LOG_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.txt'), 'w')
        self.tiles_list = []
        self.tiles_sprites = pygame.sprite.Group()
        self.load_tiles()
        self.checkers_list = []
        self.checkers_sprites = pygame.sprite.Group()
        self.load_checkers(actions_filename)
        self.win_checkers_sprites = pygame.sprite.Group()
        self.agents_list = agents_list
        self.max_depth = max_depth
        self.max_think_time = max_think_time
        self.think_time = 0
        self.clock = pygame.time.Clock()

    def __del__(self):
        self.log.close()

    def endgame_handler(self):
        for pos in self.state.get_win_checkers_positions():
            win_checker = WinChecker(pos)
            win_checker.add(self.win_checkers_sprites)
        self.log.write(self.get_text_status())
        self.playing = False

    def get_text_status(self):
        return 'DRAW' if self.status == State.DRAW else f'WIN: {"RED" if self.status == State.RED else "YEL"}'

    def run(self):
        while self.running:
            try:
                try:
                    if self.playing:
                        if self.status is not None and not self.falling:
                            raise EndGame()
                        if (not self.falling and
                                type(self.agents_list[on_move := self.state.get_next_on_move()]) is not Human):
                            try:
                                tf_queue = Queue(1)
                                tf = TimedFunction(threading.current_thread().ident,
                                                   tf_queue, self.max_think_time,
                                                   self.agents_list[on_move].get_chosen_column,
                                                   self.state,
                                                   self.max_depth)
                                tf.daemon = True
                                tf.start()
                                start_time = time.time()
                                sleep_time = 0.001
                                while tf_queue.empty():
                                    time.sleep(sleep_time)
                                    self.think_time = time.time() - start_time
                                    self.draw_info_text()
                                    self.events()
                                action, elapsed = tf_queue.get(block=False)
                            except Timeout:
                                print(f'ERROR: Agent action took more than {self.max_think_time} seconds!')
                                raise Quit()
                            self.generate_checker(action)
                except EndGame:
                    self.endgame_handler()
                self.draw()
                self.events()
                self.clock.tick(config.FRAMES_PER_SEC)
            except Quit:
                self.playing = False
                self.running = False
            except Exception as e:
                raise e

    def generate_checker(self, column):
        self.falling = True
        self.step_cnt += 1
        self.log.write(f'=== STEP {self.step_cnt:03} ===\n')
        self.log.write(f'On move: {"RED" if self.state.get_next_on_move() == State.RED else "YEL"}\n')
        self.log.write(f'Chosen column: {column}\n')
        checker = Checker('yellow.png' if self.state.get_next_on_move() else 'red.png', (0, column),
                          (config.M - 1 - self.state.get_column_height(column), column))
        self.state = self.state.generate_successor_state(column)
        self.checkers_list.append(checker)
        checker.add(self.checkers_sprites)
        self.status = self.state.get_state_status()
        self.log.write(f'{self.state}\n')

    def draw_info_text(self):
        self.screen.fill(config.BLACK, [0, self.HEIGHT, self.WIDTH, config.INFO_HEIGHT])
        if self.status is not None:
            text_str = self.get_text_status()
        else:
            text_str = (f'{"" if self.playing else "PAUSED | "}'
                        f'On move: {"YEL" if self.state.get_next_on_move() else "RED"}')
        text_width, text_height = config.INFO_FONT.size(text_str)
        text = config.INFO_FONT.render(f'{text_str}', True, config.GREEN)
        self.screen.blit(text, (self.WIDTH - text_width - config.INFO_SIDE_OFFSET, self.HEIGHT))

        if self.playing and self.status is None and type(self.agents_list[self.state.get_next_on_move()]) is not Human:
            text_str = f'Time: {self.think_time:.2f}/{self.max_think_time:.2f}s'
            text = config.INFO_FONT.render(f'{text_str}', True, config.GREEN)
            self.screen.blit(text, (config.INFO_SIDE_OFFSET, self.HEIGHT))
        pygame.display.flip()

    def draw(self):
        self.screen.fill(config.WHITE)
        self.checkers_sprites.draw(self.screen)
        self.falling = self.checkers_list[-1].gravity() if self.checkers_list else False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        active_column = mouse_x // config.TILE_SIZE
        for i, tile in enumerate(self.tiles_list):
            if ((self.status is not None or not self.playing or self.falling or
                 not pygame.mouse.get_focused() or (i % config.N) != active_column)
                    or type(self.agents_list[self.state.get_next_on_move()]) is not Human):
                tile.draw_transparent(self.screen, False)
            else:
                tile.draw_transparent(self.screen, True)
        if not self.falling:
            self.win_checkers_sprites.draw(self.screen)
        self.draw_info_text()

    def events(self):
        # catch all events here
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.WINDOWCLOSE or \
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                raise Quit()
            if self.status is not None:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.playing = not self.playing
            if (event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.playing and not self.falling and
                    type(self.agents_list[self.state.get_next_on_move()]) is Human):
                mouse_x, mouse_y = pygame.mouse.get_pos()
                active_column = mouse_x // config.TILE_SIZE
                if active_column not in self.state.get_possible_columns():
                    return
                self.generate_checker(active_column)
