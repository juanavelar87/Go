from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import sys

TOP = 0
LEFT = 1
BOTTOM = 2
RIGHT = 3

BLACK=1
WHITE=2

PURPLE = '\033[95m' 
CYAN = '\033[96m'
RESET = '\033[0m'  

STEPS=[]
class GoObject:
    def __init__(self,id, color, board):
        self.color = color
        self.stones = set()
        self.board=board
        self.id=id
        self.liberties=set()
        self.neighbors={}
    
    def add_stone(self, x, y):
        self.board.board[x][y] = self.board.current_player
        self.board.go_objects_matrix[x][y] = self.id
        self.stones.add((x, y))
        self.update_liberties(x,y)
        

    def update_liberties(self, x,y):
        if self.board.current_player==self.color:
            nbh=self.board.neighborhood(x,y)
            if (x,y) in self.liberties:
                self.liberties.remove((x,y))
            for n_i in range(len(nbh)):
                n_x,n_y=self.board.find_neighbor(x,y,n_i)
                if n_x is not False and n_y is not False:
                    if nbh[n_i] is None:
                        if (n_x,n_y) not in self.liberties:
                            self.liberties.add((n_x,n_y))
                    elif nbh[n_i]!=self.color and self.board.go_objects_matrix[n_x][n_y] is not None:
                        go_obj=self.board.list_of_go_objects[self.board.go_objects_matrix[n_x][n_y]]
                        if go_obj.id not in self.neighbors:
                            self.neighbors[go_obj.id]=set()
                        self.neighbors[go_obj.id].add((n_x,n_y))
                        go_obj.update_liberties(x,y)
        else:
            if (x,y) in self.liberties:
                self.liberties.remove((x,y))
                # Verificar que hay un objeto en esa posición antes de acceder
                if self.board.go_objects_matrix[x][y] is not None:
                    go_obj=self.board.list_of_go_objects[self.board.go_objects_matrix[x][y]]
                    if go_obj.id not in self.neighbors:
                        self.neighbors[go_obj.id]=set()
                    self.neighbors[go_obj.id].add((x,y))
        
        if len(self.liberties)==0:
            self.captured()

    def merge(self, other):
        for (x, y) in other.stones:
            self.board.go_objects_matrix[x][y] = self.id
        self.stones.update(other.stones)
        self.liberties.update(other.liberties)
        for n_id in other.neighbors:
            if n_id != self.id:
                if n_id not in self.neighbors:
                    self.neighbors[n_id]=set()
                self.neighbors[n_id].update(other.neighbors[n_id])
                neighbor_obj=self.board.list_of_go_objects[n_id]
                if self.id not in neighbor_obj.neighbors:
                    neighbor_obj.neighbors[self.id]=set()
                
                if other.id in neighbor_obj.neighbors:
                    neighbor_obj.neighbors[self.id].update(neighbor_obj.neighbors.pop(other.id))
        other.dead()
            
    def captured(self):
        for (x, y) in self.stones:
            self.board.board[x][y] = None
            self.board.go_objects_matrix[x][y] = None
        for obj in self.neighbors:
            neighbor_obj=self.board.list_of_go_objects[obj]
            if self.id in neighbor_obj.neighbors:
                for (x,y) in neighbor_obj.neighbors[self.id]:
                    neighbor_obj.liberties.add((x,y))
                neighbor_obj.neighbors.pop(self.id,None)
            
        self.board.captured_stones[self.board.other_player()]+=len(self.stones)
        self.dead()

    def dead(self):
        self.stones=set()
        self.liberties=set()
        self.neighbors={}
    
    def check_liberties(self, x,y):
        nbh_array=self.board.neighborhood(x,y)
        nbh=set(nbh_array)
        nbh.discard(False)

        if (((x,y) in self.liberties and len(self.liberties)==1) or len(self.liberties)==0) and None not in nbh:
            # Matar y no suicidarse
            for n_i in range(4):
                n_x,n_y=self.board.find_neighbor(x,y,n_i)
                if n_x is not False and n_y is not False:
                    go_obj=self.board.list_of_go_objects[self.board.go_objects_matrix[n_x][n_y]]
                    if (x,y) in go_obj.liberties and len(go_obj.liberties)==1 and go_obj.color!=self.board.current_player:
                        return True
            
            return False

        if set([self.board.other_player()])==nbh:
            return False
        return True
        

class GoBoard:
    def __init__(self, size=9, ai_player=None, human_color=BLACK):
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.go_objects_matrix=[[None for _ in range(size)] for _ in range(size)]
        self.list_of_go_objects = []
        self.current_player = BLACK
        self.captured_stones = {BLACK: 0, WHITE: 0}
        self.stones={}
        
        # AI attributes
        self.ai_player = ai_player
        self.human_color = human_color
        self.ai_color = WHITE if human_color == BLACK else BLACK
        self.game_over = False
        self.winner = None

        # Pygame attributes
        self.cell_size = 50
        self.margin = 40
        self.window_size = self.size * self.cell_size + 2 * self.margin
        self.screen = None
        self.clock = None
        self.running = False
    
    def available_moves(self):
        objects_of_current_player = [obj for obj in self.list_of_go_objects if obj.color == self.current_player]
        moves = set()
        for obj in objects_of_current_player:
            for (x,y) in obj.liberties:
                if self.is_move_legal(x,y) and obj.check_liberties(x,y):
                    moves.add((x,y))
        return moves
    
    def is_move_legal(self, x, y):
        if self.board[x][y] is not None:
            return False  
        nbh=set(self.neighborhood(x,y))
        nbh.discard(False)
        if None in nbh:
            return True
        return True

    def other_player(self):
        """
        Nim.other_player(player) returns the player that is not
        `player`. Assumes `player` is either 0 or 1.
        """
        return WHITE if self.current_player == BLACK else BLACK

    def find_neighbor(self, x, y, i):
        match i:
            #Por cosas de python no se puede poner TOP, RIGHT...
            case 0: #TOP
                new_x, new_y = x, y - 1
            case 1: #LEFT
                new_x, new_y = x - 1, y
            case 2: #BOTTOM
                new_x, new_y = x, y + 1
            case 3: #RIGHT
                new_x, new_y = x + 1, y
            case _:
                return False,False
    
        if 0 <= new_x < self.size and 0 <= new_y < self.size:
            return new_x, new_y
        else:
            return False, False  

    def neighborhood(self, x, y):
        local_neighborhood = []
        for index in [-1,1]:
            if y+index>=0 and y+index<self.size:
                local_neighborhood.append(self.board[x][y+index])
            else:
                local_neighborhood.append(False)
            if x+index>=0 and x+index<self.size:
                local_neighborhood.append(self.board[x+index][y])
            else:
                local_neighborhood.append(False)
        return local_neighborhood

    def update_objects(self,x,y):
        piece_color= self.current_player
        nbh = self.neighborhood(x,y)
        object_near = False
        for n_i in range(len(nbh)):
            if object_near is not False and nbh[n_i]==piece_color:
                n_x,n_y=self.find_neighbor(x,y,n_i)
                obj_index = self.go_objects_matrix[n_x][n_y]
                if obj_index is not None:
                    go_object=self.list_of_go_objects[obj_index]
                    if go_object.id != object_near.id:
                        object_near.merge(go_object)
            if nbh[n_i]==piece_color:
                n_x,n_y=self.find_neighbor(x,y,n_i)
                obj_index=self.go_objects_matrix[n_x][n_y]
                if obj_index is not None:
                    object_near=self.list_of_go_objects[obj_index]
                    if object_near.check_liberties(x,y):
                        object_near.add_stone(x,y)
                    else:
                        return False
                
        if not object_near:
            new_object = GoObject(len(self.list_of_go_objects),piece_color, self)
            self.list_of_go_objects.append(new_object)
            if new_object.check_liberties(x,y):
                new_object.add_stone(x,y)
            else:
                return False
        return True

    def place_stone(self, x, y):
        if self.is_move_legal(x,y) is False:
            return False  
        STEPS.append((x,y,self.current_player))
        if not self.update_objects(x,y):
            return False
        # No cambiar de jugador automáticamente si hay AI
        if self.ai_player is None:
            self.current_player = self.other_player()
        return True
    
    def make_ai_move(self):
        """Hace que la AI juegue su turno"""
        if self.ai_player and self.current_player == self.ai_color and not self.game_over:
            # Mostrar heatmap antes de decidir
            print("\n🤖 Turno de AI (Negro) - Analizando opciones:")
            self.display_terminal_objects()
            
            action = self.ai_player.choose_action(self, epsilon=False)
            if action:
                x, y = action
                print(f"🤖 AI elige: ({x}, {y})")
                success = self.place_stone(x, y)
                if success:
                    self.current_player = self.other_player()
                    return True
        return False
    
    def end_game(self, winner=None):
        """Termina el juego manualmente"""
        self.game_over = True
        self.winner = winner
        if winner:
            print(f"¡Juego terminado! Ganador: {'Humano' if winner == self.human_color else 'AI'}")
        else:
            print("¡Juego terminado!")

    def display_terminal(self):
        lines = []
        lines.append("   "+"  ".join(map(str, range(self.size))))
        lines.append("  "+"_" * (self.size * 3 + 1))  
        
        for y in range(self.size):
            row = [" " + str(y) +"|"]
            for x in range(self.size):
                cell = self.board[x][y]
                if cell is None:
                    row.append("  ")
                elif cell == BLACK:
                    row.append("⚫️")
                else:
                    row.append("⚪️")
                row.append("|")
            lines.append("".join(row))
        
        lines.append("  "+"‾" * (self.size * 3 + 1)) 
        
        print("\n".join(lines))

    def display_terminal_objects(self):        
        nei = {
            tuple(coord_tuple) 
            for n in self.list_of_go_objects
            for neighbor_set in n.neighbors.values()
            for coord_tuple in neighbor_set
        }

        lines = []
        
        q_lines=None
        if self.ai_player:
            q_lines=self.ai_player.get_q_board(self)
        
        # Determine cell width based on content
        cell_width = 8 if q_lines else 3
        
        # Header with fixed width columns
        header_nums = "".join([f"{x:^{cell_width}}" for x in range(self.size)])
        lines.append(f"    {header_nums}")
        lines.append("   " + "_" * (len(header_nums) + 2)) 
        
        for y in range(self.size):
            row_parts = [f"{y:>2} |"] 
            
            for x in range(self.size):
                cell = self.go_objects_matrix[x][y]
                if cell is None:
                    if q_lines and q_lines[x][y] is not None:
                        content = f"{q_lines[x][y]:^{cell_width}.2f}"
                    else:
                        content = ".".center(cell_width)
                    row_parts.append(f"{CYAN}{content}{RESET}")
                else:
                    obj_str = str(cell) 
                    formatted_cell = f"{obj_str:^{cell_width}}"
                    
                    if (x, y) in nei:
                        row_parts.append(f"{PURPLE}{formatted_cell}{RESET}")
                    else:
                        row_parts.append(formatted_cell)
                        
            row_parts.append("|")
            lines.append("".join(row_parts))
        
        lines.append("   " + "‾" * (len(header_nums) + 2)) 
        
        print("\n".join(lines))
    def init_pygame(self):
        """Inicializa pygame y crea la ventana"""
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_size, self.window_size + 100))
        pygame.display.set_caption("Go Game")
        self.clock = pygame.time.Clock()
        self.running = True

    def display_gui(self):
        """Muestra el tablero usando pygame"""
        if not self.screen:
            self.init_pygame()
        
        if not self.screen or not self.clock:
            return
        
        # Colores
        BLACK_COLOR = (0, 0, 0)
        WHITE_COLOR = (255, 255, 255)
        GRID_COLOR = (0, 0, 0)
        BACKGROUND = (222, 184, 135)
        
        self.screen.fill(BACKGROUND)
        
        start_x = self.margin
        start_y = self.margin
        
        for i in range(self.size):
            pygame.draw.line(self.screen, GRID_COLOR,
                        (start_x + i * self.cell_size, start_y),
                        (start_x + i * self.cell_size, start_y + (self.size - 1) * self.cell_size), 2)
            pygame.draw.line(self.screen, GRID_COLOR,
                        (start_x, start_y + i * self.cell_size),
                        (start_x + (self.size - 1) * self.cell_size, start_y + i * self.cell_size), 2)
        
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] is not None:
                    center_x = start_x + x * self.cell_size
                    center_y = start_y + y * self.cell_size
                    radius = self.cell_size // 2 - 3
                    
                    if self.board[x][y] == BLACK:
                        pygame.draw.circle(self.screen, BLACK_COLOR, (center_x, center_y), radius)
                        pygame.draw.circle(self.screen, WHITE_COLOR, (center_x, center_y), radius, 2)
                    else:  
                        pygame.draw.circle(self.screen, WHITE_COLOR, (center_x, center_y), radius)
                        pygame.draw.circle(self.screen, BLACK_COLOR, (center_x, center_y), radius, 2)
        
        font = pygame.font.Font(None, 32)
        
        if not self.game_over:
            if self.ai_player:
                if self.current_player == self.human_color:
                    turn_text = f"Tu turno ({'Negro' if self.human_color == BLACK else 'Blanco'})"
                else:
                    turn_text = f"Turno de AI ({'Negro' if self.ai_color == BLACK else 'Blanco'})"
            else:
                current_player_text = "Negro" if self.current_player == BLACK else "Blanco"
                turn_text = f"Turno: {current_player_text}"
        else:
            if self.winner:
                winner_text = "Humano" if self.winner == self.human_color else "AI"
                turn_text = f"¡Juego terminado! Ganador: {winner_text}"
            else:
                turn_text = "¡Juego terminado!"
        
        text = font.render(turn_text, True, BLACK_COLOR)
        self.screen.blit(text, (10, self.window_size + 10))
        
        captures_text = font.render(f"Capturadas - Negro: {self.captured_stones[BLACK]}, Blanco: {self.captured_stones[WHITE]}", True, BLACK_COLOR)
        self.screen.blit(captures_text, (10, self.window_size + 40))
        
        if not self.game_over:
            end_button_text = font.render("Presiona 'E' para terminar juego", True, BLACK_COLOR)
            self.screen.blit(end_button_text, (10, self.window_size + 70))
        
        pygame.display.flip()
        
    def handle_click(self, pos):
        """Maneja los clicks del mouse para colocar piedras"""
        if self.game_over:
            return False
            
        mouse_x, mouse_y = pos
        
        # Calcular la posición en el tablero
        grid_x = round((mouse_x - self.margin) / self.cell_size)
        grid_y = round((mouse_y - self.margin) / self.cell_size)
        
        # Verificar que está dentro del tablero
        if 0 <= grid_x < self.size and 0 <= grid_y < self.size:
            # Solo permitir movimiento si es turno del humano (o no hay AI)
            if self.ai_player is None or self.current_player == self.human_color:
                success = self.place_stone(grid_x, grid_y)
                if success:
                    self.display_terminal_objects()
                    
                    if self.ai_player:
                        self.current_player = self.other_player()
                    self.display_gui()
                return success
        return False
    
    def run_gui(self):
        """Ejecuta el juego con interfaz gráfica"""
        self.init_pygame()
        ai_move_delay = 0
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Click izquierdo
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_e:  # Terminar juego
                        if not self.game_over:
                            if self.captured_stones[BLACK] > self.captured_stones[WHITE]:
                                winner = WHITE
                            elif self.captured_stones[WHITE] > self.captured_stones[BLACK]:
                                winner = BLACK
                            else:
                                winner = None  
                            self.end_game(winner)
                    elif event.key == pygame.K_r and self.game_over: 
                        self.__init__(self.size, self.ai_player, self.human_color)
            
            if (self.ai_player and self.current_player == self.ai_color and 
                not self.game_over and ai_move_delay <= 0):
                self.make_ai_move()
                ai_move_delay = 30  
            
            if ai_move_delay > 0:
                ai_move_delay -= 1
            
            self.display_gui()
            if self.clock:
                self.clock.tick(60)
            
        pygame.quit()
        sys.exit()
