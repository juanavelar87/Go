import random
import Go
import pickle
import copy
import os
from tqdm import tqdm

class GoAI():
    def __init__(self, alpha=0.1, epsilon=0.3):
        """
        Initialize AI with an empty Q-learning dictionary,
        an alpha (learning) rate, and an epsilon rate.

        The Q-learning dictionary maps `(state, action)`
        pairs to a Q-value (a number).
         - `state` is a flattened tuple of the board state
         - `action` is a tuple `(x, y)` for placing a stone
        """
        self.q = dict()
        self.alpha = alpha
        self.epsilon = epsilon

    def board_to_state(self, board):
        """
        Convert a GoBoard to a hashable state representation.
        Includes current player to distinguish who's turn it is.
        """
        board_tuple = tuple(
            0 if cell is None else cell 
            for row in board.board 
            for cell in row
        )
        return (board.current_player,) + board_tuple

    def get_available_actions(self, board):
        """
        Get all legal moves for the current player.
        Returns a list of (x, y) coordinates where stones can be placed.
        """
        actions = []
        for x in range(board.size):
            for y in range(board.size):
                if board.board[x][y] is None and board.is_move_legal(x, y):
                    actions.append((x, y))
        return actions

    def copy_board(self, original_board):
        """
        Create a simple copy of the board for testing moves.
        """
        new_board = copy.deepcopy(original_board)
        return new_board

    def update(self, old_state, action, new_state, reward, board_after_move):
        """
        Update Q based on the state AFTER the move, not the previous player board.
        """
        old = self.get_q_value(old_state, action)
        
        best_future = self.best_future_reward(new_state, board_after_move)
        
        self.update_q_value(old_state, action, old, reward, best_future)
    def get_q_value(self, state, action):
        """
        Return the Q-value for the state `state` and the action `action`.
        If no Q-value exists yet in `self.q`, return 0.
        """
        if (state, action) in self.q:
            return self.q[(state, action)]
        else:
            return 0
        
    def update_q_value(self, state, action, old_q, reward, future_rewards):
        """
        Update the Q-value for the state `state` and the action `action`
        given the previous Q-value `old_q`, a current reward `reward`,
        and an estimate of future rewards `future_rewards`.

        Use the formula:

        Q(s, a) <- old value estimate
                   + alpha * (new value estimate - old value estimate)

        where `old value estimate` is the previous Q-value,
        `alpha` is the learning rate, and `new value estimate`
        is the sum of the current reward and estimated future rewards.
        """
        gamma = 0.9  
        self.q[(state, action)] = old_q + self.alpha * (reward + gamma * future_rewards - old_q)

    def best_future_reward(self, state, board):
        """
        Calculate best future reward using only legal actions.
        """
        actions = self.get_available_actions(board)
        if not actions:
            return 0
        return max(self.get_q_value(state, action) for action in actions)

    def choose_action(self, board, epsilon=True):
        """
        Given a board state, return an action `(x, y)` to take.

        If `epsilon` is `False`, then return the best action
        available in the state (the one with the highest Q-value,
        using 0 for pairs that have no Q-values).

        If `epsilon` is `True`, then with probability
        `self.epsilon` choose a random available action,
        otherwise choose the best action available.

        If multiple actions have the same Q-value, any of those
        options is an acceptable return value.
        """
        state = self.board_to_state(board)
        actions = self.get_available_actions(board)
        
        if not actions:
            return None
            
        if epsilon and random.random() < self.epsilon:
            return random.choice(actions)
        
        best_actions = []
        best_value = float('-inf')
        
        for action in actions:
            q_value = self.get_q_value(state, action)
            if q_value > best_value:
                best_value = q_value
                best_actions = [action]
            elif q_value == best_value:
                best_actions.append(action)
                
        return random.choice(best_actions)
    
    def save_model(self, filename):
        """Guarda el modelo Q-learning en un archivo"""
        try:
            with open(filename, 'wb') as f:
                pickle.dump({
                    'q': self.q,
                    'alpha': self.alpha,
                    'epsilon': self.epsilon
                }, f)
            print(f"Modelo guardado en {filename}")
            return True
        except Exception as e:
            print(f"Error al guardar modelo: {e}")
            return False
    
    def load_model(self, filename):
        """Carga el modelo Q-learning desde un archivo"""
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                self.q = data['q']
                self.alpha = data['alpha']
                self.epsilon = data['epsilon']
            print(f"Modelo cargado desde {filename}")
            print(f"Q-table tiene {len(self.q)} entradas")
            return True
        except FileNotFoundError:
            print(f"Archivo {filename} no encontrado")
            return False
        except Exception as e:
            print(f"Error al cargar modelo: {e}")
            return False

    def get_q_board(self, board):
        """
        Returns a 2D array showing Q-values for each position.
        Returns None for positions that already have stones.
        Shows the Q-value for the best action at each empty position.
        """
        state = self.board_to_state(board)
        q_board = []
        
        for x in range(board.size):
            row = []
            for y in range(board.size):
                if board.board[x][y] is not None:
                    row.append(None)
                else:
                    action = (x, y)
                    q_value = self.get_q_value(state, action)
                    row.append(round(q_value, 2))  
            q_board.append(row)
        
        return q_board
    
def load_or_train_ai(n=2000, model_filename="go_ai_model4x4.pkl"):
    """
    Carga un modelo existente o entrena uno nuevo si no existe.
    """
    player = GoAI()
    
    if os.path.exists(model_filename):
        print(f"Modelo encontrado: {model_filename}")
        if player.load_model(model_filename):
            print("¿Quieres entrenar más o usar el modelo existente?")
            print("1. Usar modelo existente")
            print("2. Entrenar más (se guardará automáticamente)")
            choice = input("Elige 1 o 2: ").strip()
            if choice == "2":
                print(f"Entrenamiento adicional con {n} juegos...")
                player = train_ai(player, n)
            else:
                print("Usando modelo existente")
        else:
            print("Error cargando modelo, entrenando uno nuevo...")
            player = train_ai(player, n)
    else:
        print("🆕 No se encontró modelo previo, entrenando uno nuevo...")
        player = train_ai(player, n)
    
    return player

def train_ai(player, n, max_moves_per_game=20):
    """
    Train the AI to play as BLACK (First Player) against a Random Opponent.
    This treats the opponent's moves as part of the environment dynamics.
    """
    
    with tqdm(range(n), desc="Training Black AI", unit="games") as pbar:
        for i in pbar:
            game = Go.GoBoard(size=3)  # 3x3 board
            
            move_count = 0
            game_ended = False
            failed_move_count = 0
            max_failed_moves = 10
            
            while move_count < max_moves_per_game and not game_ended and failed_move_count < max_failed_moves:
                if game.current_player != Go.BLACK:
                    game.current_player = Go.BLACK
                
                state = player.board_to_state(game)
                
                available_actions = player.get_available_actions(game)
                if not available_actions:
                    break
                
                action = player.choose_action(game)
                if action is None:
                    break
                
                prev_captured = {
                    Go.BLACK: game.captured_stones[Go.BLACK],
                    Go.WHITE: game.captured_stones[Go.WHITE]
                }
                
                success = game.place_stone(action[0], action[1])
                if not success:
                    failed_move_count += 1
                    continue
                failed_move_count = 0
                
                if game.game_over:
                    reward = calculate_move_reward(game, Go.BLACK, prev_captured)
                    player.update(state, action, player.board_to_state(game), reward, game)
                    game_ended = True
                    break

                # Random 
                white_actions = []
                for x in range(game.size):
                    for y in range(game.size):
                        if game.board[x][y] is None and game.is_move_legal(x, y):
                            white_actions.append((x, y))
                
                if white_actions:
                    white_action = random.choice(white_actions)
                    game.place_stone(white_action[0], white_action[1])
                else:
                    pass
                
                if game.game_over:
                    reward = calculate_move_reward(game, Go.BLACK, prev_captured)
                    player.update(state, action, player.board_to_state(game), reward, game)
                    game_ended = True
                    break
                
                new_state = player.board_to_state(game)
                
                reward = calculate_move_reward(game, Go.BLACK, prev_captured)
                
                # Q(s, a) += alpha * (r + gamma * max Q(s'', a') - Q(s, a))
                player.update(state, action, new_state, reward, game)
                
                move_count += 1
                
                # Update progress bar stats
                if i % 50 == 0:
                    pbar.set_postfix({
                        'Q-table': len(player.q),
                        'Reward': f'{reward:.2f}'
                    })

    print(f"\n✅ Training completed! Q-table has {len(player.q)} entries")
    
    # Guardar el modelo automáticamente
    model_filename = "go_ai_model.pkl"
    player.save_model(model_filename)
    
    return player

def calculate_move_reward(game, player_color, prev_captured):
    """
    Calculate reward for the player based on the change in game state.
    """
    current_captured = {
        Go.BLACK: game.captured_stones[Go.BLACK],
        Go.WHITE: game.captured_stones[Go.WHITE]
    }
    
    opponent = Go.WHITE if player_color == Go.BLACK else Go.BLACK
    
    reward = 0.0
    
    my_captures = current_captured[opponent] - prev_captured[opponent]
    opponent_captures = current_captured[player_color] - prev_captured[player_color]
    
    if my_captures > 0:
        reward += my_captures * 10.0
    if opponent_captures > 0:
        reward -= opponent_captures * 15.0 
        
    my_stones = sum(1 for x in range(game.size) for y in range(game.size) if game.board[x][y] == player_color)
    opp_stones = sum(1 for x in range(game.size) for y in range(game.size) if game.board[x][y] == opponent)
    
    reward += (my_stones - opp_stones) * 0.5
    
    return reward
