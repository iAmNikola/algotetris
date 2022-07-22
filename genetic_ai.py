import numpy as np
from copy import deepcopy
import random
 
# import pytris

NUM_FEATURES = 9
MUTATION = 0.2

# All possible moves for pieces
# key=piece_id value=[valid x axis start,end]
POSSIBLE_MOVES = {
    1: [[0,6+1],[-2,7+1]],                  # I
    2: [[0,7+1],[-1,7+1],[0,7+1],[0,8+1]],  # J
    3: [[0,7+1],[-1,7+1],[0,7+1],[0,8+1]],  # L
    4: [[-1,7+1]],                          # O
    5: [[0,7+1],[-1,7+1]],                  # S
    6: [[0,7+1],[-1,7+1],[0,7+1],[0,8+1]],  # T
    7: [[0,7+1],[-1,7+1]]                   # Z
}

class Genetic_AI:
    def __init__(self, genotype=None, mutate=False):
        if genotype is None:
            self.genotype = np.array([random.uniform(-1, 1) for _ in range(NUM_FEATURES)])
        else:
            self.genotype = genotype 
        if mutate:
            mutation = np.array([np.random.normal(1, MUTATION) for _ in range(NUM_FEATURES)])
            self.genotype = genotype * mutation
            
        self.fit_score = 0.0
        self.fit_rel = 0.0

    def __lt__(self, other: 'pytris.Genetic_AI'):
        return self.fit_score < other.fit_score      

    def evaluate_move(self, pytris: 'pytris.Pytris'):
        """
        """
        board: np.array = matrix_to_np_board(pytris.matrix)
        peaks = get_peaks(board)
        highest_peak = np.max(peaks)
        holes = get_holes(peaks, board)
        wells = get_wells(peaks)

        rating_funcs = {
            'aggregated_height': np.sum(peaks),
            'n_holes': np.sum(holes),
            'n_cols_with_holes': np.count_nonzero(np.array(holes) > 0),
            'bumpiness': get_bumpiness(peaks),
            'n_pits': np.count_nonzero(np.count_nonzero(board, axis=0) == 0),
            'deepest_well': np.max(wells),
            'row_transitions': get_row_transition(board, highest_peak), 
            'col_transitions': get_col_transition(board, peaks),
            'lines_cleared': count_lines_cleared(pytris.matrix) * 8
        } 

        ratings = np.array([*rating_funcs.values()], dtype=float)
        return np.dot(self.genotype, ratings)


    def get_best_move(self, pytris: 'pytris.Pytris'):
        """
        Gets the best for move an agents base on board, next piece, and genotype
        """
        current_board = deepcopy(pytris.matrix)
        max_value = -np.inf
        best_rotation = None
        best_x = None
        best_y = None

        for r in range(len(POSSIBLE_MOVES[pytris.mino])):
            pytris.rotation = r
            for x in range(*POSSIBLE_MOVES[pytris.mino][r]):
                pytris.dx, pytris.dy = x, 0
                if not pytris.is_stackable():   # check if move is possible
                    continue
                # move piece to bottom
                while not pytris.is_bottom(pytris.dx, pytris.dy):
                    pytris.dy += 1
                pytris.draw_mino()
                evaluation = self.evaluate_move(pytris)
                if evaluation > max_value:
                    max_value = evaluation
                    best_rotation = r
                    best_x = x
                    best_y = pytris.dy
                pytris.matrix = deepcopy(current_board)
        pytris.matrix = current_board   # reset board to state before generating moves
        return best_rotation, best_x, best_y

def count_lines_cleared(matrix):
    erase_count = 0
    for j in range(21):
        is_full = True
        for i in range(10):
            if matrix[i][j] == 0:
                is_full = False
        if is_full:
            erase_count += 1
    return erase_count


def matrix_to_np_board(matrix):
    board = np.array(matrix).T  # Transpose board
    board[ board > 0 ] = 1      # convert all nonzero values to 1
    return board


def get_peaks(area):
    peaks = np.array([])
    for col in range(area.shape[1]):
        if 1 in area[:, col]:
            p = area.shape[0] - np.argmax(area[:, col], axis=0)
            peaks = np.append(peaks, p)
        else:
            peaks = np.append(peaks, 0)
    return peaks


def get_row_transition(area, highest_peak):
    sum = 0
    # From highest peak to bottom
    for row in range(int(area.shape[0] - highest_peak), area.shape[0]):
        for col in range(1, area.shape[1]):
            if area[row, col] != area[row, col - 1]:
                sum += 1
    return sum


def get_col_transition(area, peaks):
    sum = 0
    for col in range(area.shape[1]):
        if peaks[col] <= 1:
            continue
        for row in range(int(area.shape[0] - peaks[col]), area.shape[0] - 1):
            if area[row, col] != area[row + 1, col]:
                sum += 1
    return sum


def get_bumpiness(peaks):
    s = 0
    for i in range(9):
        s += np.abs(peaks[i] - peaks[i + 1])
    return s


def get_holes(peaks, area):
    # Count from peaks to bottom
    holes = []
    for col in range(area.shape[1]):
        start = -peaks[col]
        # If there's no holes i.e. no blocks on that column
        if start == 0:
            holes.append(0)
        else:
            holes.append(np.count_nonzero(area[int(start) :, col] == 0))
    return holes


def get_wells(peaks):
    wells = []
    for i in range(len(peaks)):
        if i == 0:
            w = peaks[1] - peaks[0]
            w = w if w > 0 else 0
            wells.append(w)
        elif i == len(peaks) - 1:
            w = peaks[-2] - peaks[-1]
            w = w if w > 0 else 0
            wells.append(w)
        else:
            w1 = peaks[i - 1] - peaks[i]
            w2 = peaks[i + 1] - peaks[i]
            w1 = w1 if w1 > 0 else 0
            w2 = w2 if w2 > 0 else 0
            w = w1 if w1 >= w2 else w2
            wells.append(w)
    return wells
