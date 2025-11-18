from neighbors_network import NeighborsGraph
import pygame
import sys

TOP = 0
LEFT = 1
BOTTOM = 2
RIGHT = 3

BLACK=1
WHITE=2

    # (obj_id, obj2_id): [(x1,y1), (x2,y2)...] posiciones que comparten
neighbors_graph=NeighborsGraph()

class GoObject:
    def __init__(self,id, color, board):
        self.color = color
        self.stones = []
        self.board=board
        self.state='alive'
        self.id=id
        self.liberties=set()

    def add_stone(self, x, y):
        self.board.go_objects_matrix[x][y] = self.id
        self.stones.append((x, y))
        self.update_liberties(x,y)

    def update_liberties(self, x,y):
        if self.board.current_player==self.color:
            nbh=self.board.neighborhood(x,y)
            if (x,y) in self.liberties:
                self.liberties.remove((x,y))
            for n_i in range(len(nbh)):
                n_x,n_y=self.board.find_neighbor(x,y,n_i)
                # Verificar que las coordenadas sean válidas
                if n_x is not False and n_y is not False:
                    if nbh[n_i] is None:
                        if (n_x,n_y) not in self.liberties:
                            self.liberties.add((n_x,n_y))
                    elif nbh[n_i]!=self.color and self.board.go_objects_matrix[n_x][n_y] is not None:
                        self.board.list_of_go_objects[self.board.go_objects_matrix[n_x][n_y]].update_liberties(x,y)
        else:
            if (x,y) in self.liberties:
                self.liberties.remove((x,y))
                # Verificar que hay un objeto en esa posición antes de acceder
            if self.board.go_objects_matrix[x][y] is not None:
                go_obj=self.board.list_of_go_objects[self.board.go_objects_matrix[x][y]]
                if not neighbors_graph.get(go_obj.id, self.id):
                    neighbors_graph[go_obj.id, self.id]=set()
                neighbors_graph[go_obj.id, self.id].add((x,y))
        
        if len(self.liberties)==0:
            self.captured()

    def merge(self, other):
        for (x, y) in other.stones:
            self.board.go_objects_matrix[x][y] = self.id
        self.stones.extend(other.stones)
        self.liberties.update(other.liberties)
        other.dead()
            
    def captured(self):
        print(f"Objeto {self.id} capturado")
        for (x, y) in self.stones:
            self.board.board[x][y] = None
            self.board.go_objects_matrix[x][y] = None
        keys_to_remove=[]
        for key,value in neighbors_graph.search(self.id):
            neighbor_obj=self.board.list_of_go_objects[key[0] if key[1]==self.id else key[1]]
            for (x,y) in value:
                neighbor_obj.liberties.add((x,y))
            keys_to_remove.append(key)
        for key in keys_to_remove:
            neighbors_graph.remove(key[0], key[1])            
        self.board.captured_stones[self.board.other_player()]+=len(self.stones)
        self.dead()

    def dead(self):
        self.stones=[]
        self.state='dead'
        

class GoBoard:
    def __init__(self, size=9):
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.go_objects_matrix=[[None for _ in range(size)] for _ in range(size)]
        self.list_of_go_objects = []
        self.current_player = BLACK
        self.captured_stones = {BLACK: 0, WHITE: 0}
        self.stones={}
        
        # Pygame attributes
        self.cell_size = 50
        self.margin = 40
        self.window_size = self.size * self.cell_size + 2 * self.margin
        self.screen = None
        self.clock = None
        self.running = False
    
    def available_moves(self):
        moves = []
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] is None and self.is_move_legal(x, y):
                    moves.append((x, y))
        return moves
    
    def is_move_legal(self, x, y):
        # Casilla ocupada
        if self.board[x][y] is not None:
            return False

        # Simular poner piedra temporalmente
        self.board[x][y] = self.current_player

        enemy_color = self.other_player()
        captures_enemy = False

        # Ver si algún grupo enemigo quedaría sin libertades
        nbh = self.neighborhood(x, y)
        for i, val in enumerate(nbh):
            if val == enemy_color:
                nx, ny = self.find_neighbor(x, y, i)
                stones, liberties = self.group_liberties(nx, ny)
                if len(liberties) == 0:
                    captures_enemy = True
                    break

        # Ver libertades propias
        stones, my_liberties = self.group_liberties(x, y)

        # Quitar piedra temporal
        self.board[x][y] = None

        # Si captura, SIEMPRE es legal
        if captures_enemy:
            return True

        # Si no captura pero tiene libertades → legal
        if len(my_liberties) > 0:
            return True

        # Si no captura y no tiene libertades → suicidio
        return False

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

    def group_liberties(self, x, y):
        color = self.board[x][y]
        visited = set()
        to_check = [(x, y)]
        stones = set()
        liberties = set()

        while to_check:
            cx, cy = to_check.pop()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            stones.add((cx, cy))

            nbh = self.neighborhood(cx, cy)
            for i, val in enumerate(nbh):
                nx, ny = self.find_neighbor(cx, cy, i)
                if nx is False:
                    continue
                if val is None:
                    liberties.add((nx, ny))
                elif val == color and (nx, ny) not in visited:
                    to_check.append((nx, ny))

        return stones, liberties

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

    def update_objects(self, x, y):
        color = self.board[x][y]
        neighbors_same_color = []
        
        # Buscar grupos vecinos del mismo color
        nbh = self.neighborhood(x, y)
        for i, val in enumerate(nbh):
            if val == color:
                nx, ny = self.find_neighbor(x, y, i)
                obj_id = self.go_objects_matrix[nx][ny]
                if obj_id is not None:
                    neighbors_same_color.append(self.list_of_go_objects[obj_id])
        
        # Quitar duplicados
        neighbors_same_color = list(set(neighbors_same_color))

        # Si ningún vecino → crear grupo nuevo
        if len(neighbors_same_color) == 0:
            new_object = GoObject(len(self.list_of_go_objects), color, self)
            self.list_of_go_objects.append(new_object)
            new_object.add_stone(x, y)
            return
        
        # Si hay un solo vecino → añadir piedra a ese grupo
        main_obj = neighbors_same_color[0]
        main_obj.add_stone(x, y)
        
        # Si hay más vecinos → unirlos al grupo principal
        for other_obj in neighbors_same_color[1:]:
            main_obj.merge(other_obj)   
    def place_stone(self, x, y):
        if self.is_move_legal(x,y) is False:
            return False  
        
        self.board[x][y] = self.current_player
        self.update_objects(x,y)
        self.current_player = self.other_player()
        self.display_terminal_objects()
        return True

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
        lines = []
        lines.append("   "+"  ".join(map(str, range(self.size))))
        lines.append("  "+"_" * (self.size * 3 + 1))  
        
        for y in range(self.size):
            row = [" " + str(y) +"|"]
            for x in range(self.size):
                cell = self.go_objects_matrix[x][y]
                if cell is None:
                    row.append("  ")
                else:
                    row.append(str(self.go_objects_matrix[x][y])+" ")
                row.append("|")
            lines.append("".join(row))
        
        lines.append("  "+"‾" * (self.size * 3 + 1)) 
        
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
        
        # Colores
        BLACK_COLOR = (0, 0, 0)
        WHITE_COLOR = (255, 255, 255)
        GRID_COLOR = (0, 0, 0)
        BACKGROUND = (222, 184, 135)
        
        # Limpiar pantalla
        self.screen.fill(BACKGROUND)
        
        # Dibujar el tablero
        start_x = self.margin
        start_y = self.margin
        
        # Dibujar las líneas del tablero
        for i in range(self.size):
            # Líneas verticales
            pygame.draw.line(self.screen, GRID_COLOR,
                           (start_x + i * self.cell_size, start_y),
                           (start_x + i * self.cell_size, start_y + (self.size - 1) * self.cell_size), 2)
            # Líneas horizontales
            pygame.draw.line(self.screen, GRID_COLOR,
                           (start_x, start_y + i * self.cell_size),
                           (start_x + (self.size - 1) * self.cell_size, start_y + i * self.cell_size), 2)
        
        # Dibujar las piedras
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] is not None:
                    center_x = start_x + x * self.cell_size
                    center_y = start_y + y * self.cell_size
                    radius = self.cell_size // 2 - 3
                    
                    if self.board[x][y] == BLACK:
                        pygame.draw.circle(self.screen, BLACK_COLOR, (center_x, center_y), radius)
                        pygame.draw.circle(self.screen, WHITE_COLOR, (center_x, center_y), radius, 2)
                    else:  # WHITE
                        pygame.draw.circle(self.screen, WHITE_COLOR, (center_x, center_y), radius)
                        pygame.draw.circle(self.screen, BLACK_COLOR, (center_x, center_y), radius, 2)
        
        # Mostrar información del juego
        font = pygame.font.Font(None, 36)
        current_player_text = "Negro" if self.current_player == BLACK else "Blanco"
        text = font.render(f"Turno: {current_player_text}", True, BLACK_COLOR)
        self.screen.blit(text, (10, self.window_size + 10))
        
        # Mostrar capturas
        captures_text = font.render(f"Capturas - Negro: {self.captured_stones[BLACK]}, Blanco: {self.captured_stones[WHITE]}", True, BLACK_COLOR)
        self.screen.blit(captures_text, (10, self.window_size + 50))
        
        pygame.display.flip()
        
    def handle_click(self, pos):
        """Maneja los clicks del mouse para colocar piedras"""
        mouse_x, mouse_y = pos
        
        # Calcular la posición en el tablero
        grid_x = round((mouse_x - self.margin) / self.cell_size)
        grid_y = round((mouse_y - self.margin) / self.cell_size)
        
        # Verificar que está dentro del tablero
        if 0 <= grid_x < self.size and 0 <= grid_y < self.size:
            success = self.place_stone(grid_x, grid_y)
            if success:
                self.display_gui()
            return success
        return False
    
    def run_gui(self):
        """Ejecuta el juego con interfaz gráfica"""
        self.init_pygame()
        
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
            
            self.display_gui()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

g=GoBoard(size=9)
g.run_gui()
