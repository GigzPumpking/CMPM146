from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice
from math import sqrt, log

num_nodes = 250
explore_faction = 2.

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    while node.untried_actions and len(node.child_nodes) == len(node.untried_actions):
        best = []
        best_ucb = 0
        is_opp = None
        player = board.current_player(state)
        if (player != bot_identity):
            is_opp = True
        else:
            is_opp = False

        for child in node.child_nodes:
            score = ucb(node.child_nodes[child], is_opp)
            if score == best_ucb:
                best.append(child)
            elif score > best_ucb:
                best = [child]
                best_ucb = score

        if not best:
            break
        random_best = choice(best)
        node = node.child_nodes[random_best]
        state = board.next_state(state, node.parent_action)
    return node, state

def expand_leaf(node: MCTSNode, board: Board, state):
    # Select an untried action and create a new child node
    untried = []
    for action in node.untried_actions:
        if action not in node.child_nodes:
            untried.append(action)

    if untried:
        tried_action = choice(untried)
        new_state = board.next_state(state, tried_action)
        new_node = MCTSNode(node, tried_action, board.legal_actions(new_state))
        node.child_nodes[tried_action] = new_node
        return new_node, new_state
    else:
        return node, state

def rollout(board: Board, state, bot_identity: int):
    while board.legal_actions(state):
        legal_actions = board.legal_actions(state)
            
        action = select_heuristic_move(board, state, legal_actions, bot_identity)

        state = board.next_state(state, action)
    return state

def select_heuristic_move(board: Board, state, legal_actions, bot_identity: int):
    # not picking a random best move
    max_heuristic_value = float('-inf')
    best_action_list = []
    best_action = None

    for action in legal_actions:
        # Calculate heuristic value for each action
        heuristic_value = calculate_heuristic(board, state, action, bot_identity)

        # Update best action if the current action has a higher heuristic value
        if heuristic_value > max_heuristic_value:
            max_heuristic_value = heuristic_value
            best_action_list = [action]
            best_action = action
        elif heuristic_value == max_heuristic_value:
            best_action_list.append(action)

    return choice(best_action_list)

def calculate_heuristic(board: Board, state, action, bot_identity: int):

    enemy_identity = 1 if bot_identity == 2 else 2

    heuristic_value = 0

    GridR, GridC, SquareX, SquareY = action

    rowBotCount = 0
    colBotCount = 0
    rowEnemyCount = 0
    colEnemyCount = 0

    owned_dict = board.owned_boxes(state)
    print(owned_dict)

    for row in range(0, 3):
        if owned_dict[(row, SquareY)] == bot_identity:
            rowBotCount += 1
        elif owned_dict[(row, SquareY)] == enemy_identity:
            rowEnemyCount += 1

    for col in range(0, 3):
        if owned_dict[(SquareX, col)] == bot_identity:
            colBotCount += 1
        elif owned_dict[(SquareX, col)] == enemy_identity:
            colEnemyCount += 1

    diagonalBotCount = 0
    diagonalEnemyCount = 0
    # hard code diagonal checks 
    
    if (SquareX, SquareY) == (0, 0):
        if owned_dict[(1, 1)] == bot_identity:
            diagonalBotCount += 1
        elif owned_dict[(1, 1)] == enemy_identity:
            diagonalEnemyCount += 1
        if owned_dict[(2, 2)] == bot_identity:
            diagonalBotCount += 1
        elif owned_dict[(2, 2)] == enemy_identity:
            diagonalEnemyCount += 1

    if (SquareX, SquareY) == (0, 2):
        if owned_dict[(1, 1)] == bot_identity:
            diagonalBotCount += 1
        elif owned_dict[(1, 1)] == enemy_identity:
            diagonalEnemyCount += 1
        if owned_dict[(2, 0)] == bot_identity:
            diagonalBotCount += 1
        elif owned_dict[(2, 0)] == enemy_identity:
            diagonalEnemyCount += 1
    
    if (SquareX, SquareY) == (2, 0):
        if owned_dict[(1, 1)] == bot_identity:
            diagonalBotCount += 1
        elif owned_dict[(1, 1)] == enemy_identity:
            diagonalEnemyCount += 1
        if owned_dict[(0, 2)] == bot_identity:
            diagonalBotCount += 1
        elif owned_dict[(0, 2)] == enemy_identity:
            diagonalEnemyCount += 1

    if (SquareX, SquareY) == (2, 2):
        if owned_dict[(1, 1)] == bot_identity:
            diagonalBotCount += 1
        elif owned_dict[(1, 1)] == enemy_identity:
            diagonalEnemyCount += 1
        if owned_dict[(0, 0)] == bot_identity:
            diagonalBotCount += 1
        elif owned_dict[(0, 0)] == enemy_identity:
            diagonalEnemyCount += 1
    

    if (SquareX, SquareY) == (1, 1):
        if owned_dict[(0, 0)] == bot_identity:
            diagonalBotCount += 1
        elif owned_dict[(0, 0)] == enemy_identity:
            diagonalEnemyCount += 1
        if owned_dict[(0, 2)] == bot_identity:
            diagonalBotCount += 1
        elif owned_dict[(0, 2)] == enemy_identity:
            diagonalEnemyCount += 1
        if owned_dict[(2, 0)] == bot_identity:
            diagonalBotCount += 1
        elif owned_dict[(2, 0)] == enemy_identity:
            diagonalEnemyCount += 1
        if owned_dict[(2, 2)] == bot_identity:
            diagonalBotCount += 1
        elif owned_dict[(2, 2)] == enemy_identity:
            diagonalEnemyCount += 1

    if rowBotCount == 2 or colBotCount == 2 or diagonalBotCount == 2:
        heuristic_value += 100
    if (diagonalEnemyCount == 1 or rowEnemyCount == 1 or colEnemyCount == 1) and (rowBotCount == 1 or colBotCount == 1 or diagonalBotCount == 1):
        heuristic_value -= 150
    if diagonalEnemyCount == 2 or rowEnemyCount == 2 or colEnemyCount == 2:
        heuristic_value += 100
    return heuristic_value

def backpropagate(node: MCTSNode|None, won: bool):
    # backpropagate from the expanded node and work back to the root node
    if (node is None):
        return
    node.visits += 1
    if won:
        node.wins += 1
    backpropagate(node.parent, won)

def ucb(node: MCTSNode, is_opponent: bool):
    if not is_opponent:
        first = node.wins / node.visits
        c = explore_faction
        second = sqrt((log(node.parent.visits) / node.visits))

        final = first + (c * second)

        return final
    else:
        return 1 - (node.wins / node.visits)

def get_best_action(root_node: MCTSNode):
    root = root_node
    child_scores = {}
    
    for child in root.child_nodes:
        score = root.child_nodes[child].wins / root.child_nodes[child].visits
        child_scores[child] = score
    max_key = max(child_scores, key=lambda k: child_scores[k])
    return max_key

def is_win(board: Board, state, identity_of_bot: int):
    # checks if state is a win state for identity_of_bot
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        current_state:  The current state of the game.

    Returns:    The action to be taken from the current state

    """
    bot_identity = board.current_player(current_state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(current_state))

    for _ in range(num_nodes):
        state = current_state
        node = root_node

        # Do MCTS - This is all you!
        node, state = traverse_nodes(node, board, state, bot_identity)
        node, state = expand_leaf(node, board, state)

        # Simulate rollout and backpropagate results
        rollout_state = rollout(board, state, bot_identity)
        won = is_win(board, rollout_state, bot_identity)
        backpropagate(node, won)

    # Return the action with the highest visit count from the root node
    best_action = get_best_action(root_node)
    # print(f"Action chosen: {best_action}")
    return best_action