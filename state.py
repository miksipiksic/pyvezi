"""
STATE REPRESENTATION
For instance, for (6 x 7) dimension
state is represented with 2 values of 42 (6 x 7) bits
representing checkers positions for each player.
5 11  17  23  29  35  41
4 10  16  22  28  34  40
3  9  15  21  27  33  39
2  8  14  20  26  32  38
1  7  13  19  25  31  37
0  6  12  18  24  30  36

For instance:
STATE            STATE_binary_    X (RED) state    O (YEL) state
_ _ _ _ _ _ _    0 0 0 0 0 0 0    0 0 0 0 0 0 0    0 0 0 0 0 0 0
_ _ _ _ _ _ _    0 0 0 0 0 0 0    0 0 0 0 0 0 0    0 0 0 0 0 0 0
_ _ _ O _ _ _    0 0 0 1 0 0 0    0 0 0 0 0 0 0    0 0 0 1 0 0 0
_ _ _ X _ _ _    0 0 0 1 0 0 0    0 0 0 1 0 0 0    0 0 0 0 0 0 0
_ _ _ O _ X _    0 0 0 1 0 1 0    0 0 0 0 0 1 0    0 0 0 1 0 0 0
X 0 _ X _ O _    1 1 0 1 0 1 0    1 0 0 1 0 0 0    0 1 0 0 0 1 0
"""
import config


class State:
    @staticmethod
    def get_all_win_states():
        win_indexes = []

        # column wins
        indexes = filter(lambda sub_l: len(set(s // config.M for s in sub_l if s < config.M * config.N)) == 1,
                         [[i + j for j in range(config.WIN_CNT)]
                          for i in range(config.M * config.N - config.WIN_CNT + 1)])
        win_indexes.extend(indexes)

        # row wins
        indexes = filter(lambda sub_l: len(sub_l) == len([s for s in sub_l if s < config.M * config.N]),
                         [[j * config.M + i for j in range(config.WIN_CNT)]
                          for i in range(config.M * config.N - config.WIN_CNT + 1)])
        win_indexes.extend(indexes)

        # main diagonal wins
        indexes = filter(lambda sub_l: (length := len(sub_l)) == len(
            ind := set(s // config.M for s in sub_l if s < config.M * config.N)) and length == len(
            range(min(ind), max(ind) + 1)),
                         [[j * (config.M - 1) + i for j in range(config.WIN_CNT)]
                          for i in range(config.M * config.N - config.WIN_CNT + 1)])
        win_indexes.extend(indexes)

        # anti diagonal wins
        indexes = filter(lambda sub_l: (length := len(sub_l)) == len(
            ind := set(s // config.M for s in sub_l if s < config.M * config.N)) and length == len(
            range(min(ind), max(ind) + 1)),
                         [[j * (config.M + 1) + i for j in range(config.WIN_CNT)]
                          for i in range(config.M * config.N - config.WIN_CNT + 1)])
        win_indexes.extend(indexes)

        win_masks_set = set()
        for sub_list in win_indexes:
            win_mask = 0
            for sub in sub_list:
                win_mask |= 1 << sub
            win_masks_set.add(win_mask)
        return win_masks_set

    DRAW_MASK = (1 << (config.M * config.N)) - 1
    win_masks = get_all_win_states()
    RED = 0
    YEL = 1
    DRAW = 2

    def __init__(self):
        self.checkers_red = 0 & State.DRAW_MASK
        self.checkers_yellow = 0 & State.DRAW_MASK
        self.next_on_move = 0

    def __str__(self):
        return '\n'.join([' '.join(['X' if ((mask := 1 << (i + j * config.M)) & self.checkers_red) == mask else
                                    'O' if (mask & self.checkers_yellow) == mask else '_' for j in range(config.N)])
                          for i in range(config.M - 1, -1, -1)])

    def get_checkers(self, ident):
        if ident == State.RED:
            return self.checkers_red
        elif ident == State.YEL:
            return self.checkers_yellow
        else:
            return None

    def get_int_state(self):
        return self.checkers_red | self.checkers_yellow

    def get_next_on_move(self):
        return self.next_on_move

    def get_state_status(self):
        if self.get_int_state() == State.DRAW_MASK:
            return State.DRAW
        for mask in self.win_masks:
            if (self.checkers_red & mask) == mask:
                return State.RED
            if (self.checkers_yellow & mask) == mask:
                return State.YEL
        return None

    def get_win_checkers_positions(self):
        positions = []
        if self.get_state_status() is not None:
            for mask in self.win_masks:
                if (self.checkers_red & mask) == mask or (self.checkers_yellow & mask) == mask:
                    while mask:
                        temp = mask & -mask
                        pos = temp.bit_length() - 1
                        positions.append((config.M - 1 - pos % config.M, pos // config.M))
                        mask ^= temp
                    break
        return positions

    def get_possible_columns(self):
        state_int = self.get_int_state()
        mask = 1 << (config.M - 1)
        possible_columns = []
        for col in range(config.N):
            if not (state_int & mask):
                possible_columns.append(col)
            mask <<= config.M
        return possible_columns

    def generate_successor_state(self, column):
        if self.get_state_status() is not None:
            raise Exception(f'State is finite!\n{self}')
        if column is None or column < 0 or column >= config.N:
            raise Exception(f'Column {column} out of bounds [0 - {config.N - 1}]!')
        copy_state = State()
        copy_state.checkers_red = self.checkers_red
        copy_state.checkers_yellow = self.checkers_yellow
        state_int = self.get_int_state()
        mask = 1 << (column * config.M)
        for _ in range(config.M):
            if not (state_int & mask):
                if self.next_on_move == State.RED:
                    copy_state.checkers_red |= mask
                else:
                    copy_state.checkers_yellow |= mask
                copy_state.next_on_move = State.YEL if self.next_on_move == State.RED else State.RED
                return copy_state
            mask <<= 1
        raise Exception(f'Column {column} is full!\n{self}')

    def get_column_height(self, column):
        if column is None or column < 0 or column >= config.N:
            raise Exception(f'Column {column} out of bounds [0 - {config.N - 1}]!')
        state = self.get_int_state()
        mask = 1 << (column * config.M)
        height = 0
        for _ in range(config.M):
            if state & mask:
                height += 1
            else:
                break
            mask <<= 1
        return height
