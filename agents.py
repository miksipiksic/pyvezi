import math
import random
import time

import config

import state as st


class Agent:
    ident = 0

    def __init__(self):
        self.id = Agent.ident
        Agent.ident += 1

    def get_chosen_column(self, state, max_depth):
        pass



class Human(Agent):
    pass


class ExampleAgent(Agent):
    def get_chosen_column(self, state, max_depth):
        time.sleep(random.random())
        columns = state.get_possible_columns()
        number = 0
        for mask in state.win_masks:
            number+=1
            print(mask)
        print(number)
        return columns[random.randint(0, len(columns) - 1)]


class MinimaxABAgent(Agent):

    def count_ones(self, n):
        count = 0
        while n > 0:
            count = count + 1
            n = n & (n - 1)
        return count

    def is_terminal_state(self, state):
        if state.get_state_status() != None:
            return True
        return False

    def totalNumberOfWinMasks(self):
        mask = 0
        for m in st.win_masks:
            mask += 1
        return mask

    def countPoints(self, state, player):
        numberOfMasks = 0

        for mask in state.get_all_win_states():
            if (mask & state.get_checkers(1 - player)) == 0:
                numberOfMasks += 1
                if (self.count_ones(mask & state.get_checkers(player) ) == 4):
                    return 10000 - self.count_ones(state.get_checkers(player))
        print("number of masks: " +  str(numberOfMasks) + " for player: " + str(player))
        return numberOfMasks

    def state_eval(self, state, player):
        if self.is_terminal_state(state):
            if state.get_state_status() == st.State.RED:
                return 10000
            if state.get_state_status() == st.State.YEL:
                return -10000
            if state.get_state_status() == st.State.DRAW:
                return 0
        playerOnMove = self.countPoints(state, player)
        print("player on move: " + str(playerOnMove))
        opponent = self.countPoints(state, 1 - player)
        print("opponent: " + str(opponent))
        if(player):
            # min
            print(opponent - playerOnMove)
            return opponent - playerOnMove
        else:
            # max
            print(playerOnMove - opponent)
            return playerOnMove - opponent



    def minimaxAB(self, state, depth,  alpha, beta,  player):

        if depth == 0 or self.is_terminal_state(state):
            return self.state_eval(state, self.id)

        score = -math.inf if player == 1 else math.inf
        best_column = None


        possible_columns = state.get_possible_columns()
        columnOrder = [3, 2, 4, 1, 5, 0, 6]

        def sorting_key(state, column):
            columnPriority = columnOrder.index(column)

            return (columnPriority, column)

        sorted_columns = sorted(possible_columns, key=lambda col: sorting_key(state, col), reverse=False)

        val = True if player else False
        for col in sorted_columns:
            successor = state.generate_successor_state(col)
            child_score, _ = self.minimaxAB(successor, depth - 1, alpha, beta,val)

            if (player == 1 and child_score > score) or (player == 0 and child_score < score):
                score = child_score
                best_column = col

            if player == 1:
                alpha = max(alpha, score)
            else:
                beta = min(beta, score)

            if alpha >= beta:
                break

        return score, best_column



    def get_chosen_column(self, state, max_depth):
        columns = state.get_possible_columns()
        columnOrder = [3, 2, 4, 1, 5, 0, 6]

        def sorting_key(state, column):
            columnPriority = columnOrder.index(column)

            return (columnPriority, column)

        columns = sorted(columns, key=lambda col: sorting_key(state, col), reverse=False)

        best_value = float('-inf')
        best_column = None
        alpha = float('-inf')
        beta = float('inf')

        for column in columns:
            successor_state = state.generate_successor_state(column)
            value = self.minimaxAB(successor_state, max_depth - 1, alpha, beta, False)

            if value > best_value:
                best_value = value
                best_column = column

            alpha = max(alpha, best_value)

        return best_column