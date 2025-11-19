import pygame
import sys

TOP = 0
LEFT = 1
BOTTOM = 2
RIGHT = 3

BLACK=1
WHITE=2

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
                neighbor_obj.neighbors[self.id].update(neighbor_obj.neighbors.pop(other.id))
        other.dead()
            
    def captured(self):
        print(f"Objeto {self.id} capturado")
        for (x, y) in self.stones:
            self.board.board[x][y] = None
            self.board.go_objects_matrix[x][y] = None
        for obj in self.neighbors:
            neighbor_obj=self.board.list_of_go_objects[obj]
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
        nbh=set(self.board.neighborhood(x,y))
        nbh.discard(False)
        if ((x,y) in self.liberties and len(self.liberties)==1) and None not in nbh:
            return False
        return True
        

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
    
    # TODO: Implement full legality checks
    def is_move_legal(self, x, y):
        if self.board[x][y] is not None:
            print(f"Ya hay una piedra ahi: {self.board[x][y]}")
            return False  
        nbh=set(self.neighborhood(x,y))
        nbh.discard(False)
        if None in nbh:
            return True
        if set([self.other_player()])==nbh:
            print("El suicidio no es la opción")
            return False
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
                go_object=self.list_of_go_objects[self.go_objects_matrix[n_x][n_y]]
                if go_object.id != object_near.id:
                    object_near.merge(go_object)
            if nbh[n_i]==piece_color:
                n_x,n_y=self.find_neighbor(x,y,n_i)
                obj_index=self.go_objects_matrix[n_x][n_y]
                object_near=self.list_of_go_objects[obj_index]
                if object_near.check_liberties(x,y):
                    object_near.add_stone(x,y)
                else:
                    return False
                
        if not object_near:
            new_object = GoObject(len(self.list_of_go_objects),piece_color, self)
            self.list_of_go_objects.append(new_object)
            new_object.add_stone(x,y)
        return True

    def place_stone(self, x, y):
        if self.is_move_legal(x,y) is False:
            return False  
        print((x,y))
        STEPS.append((x,y,self.current_player))
        if not self.update_objects(x,y):
            return False
        self.display_terminal()
        self.display_terminal_objects()
        self.current_player = self.other_player()
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
        # --- 1. Configuración de Colores ANSI ---
        PURPLE = '\033[95m' # Morado claro (Magenta)
        RESET = '\033[0m'   # Resetear color (MUY IMPORTANTE)
        
        # --- 2. Preparar conjunto de vecinos (Optimizado) ---
        # Usamos set() y tuple() para que la búsqueda sea rápida y correcta
        nei = {
            tuple(coord_tuple) 
            for n in self.list_of_go_objects # Asumo que es self, si es global usa 'g'
            for neighbor_set in n.neighbors.values()
            for coord_tuple in neighbor_set
        }

        lines = []
        
        # Cabecera de columnas (eje X)
        # Usamos :^3 para centrar los números en un espacio de 3 caracteres
        header_nums = " ".join([f"{x:^3}" for x in range(self.size)])
        lines.append(f"    {header_nums}")
        lines.append("   " + "_" * (self.size * 4 + 1)) 
        
        for y in range(self.size):
            # Cabecera de fila (eje Y)
            row_parts = [f"{y:>2} |"] 
            
            for x in range(self.size):
                cell = self.go_objects_matrix[x][y]
                
                # --- 3. Lógica de Contenido y Formato ---
                if cell is None:
                    # Espacio vacío de 3 caracteres
                    content = " . " 
                    row_parts.append(content)
                else:
                    # Convertimos el objeto a string
                    obj_str = str(cell) 
                    
                    # Forzamos que el texto ocupe 3 espacios y se centre (:^3)
                    # Esto asegura que la tabla no se mueva
                    formatted_cell = f"{obj_str:^3}"
                    
                    # --- 4. Aplicar Color si es vecino ---
                    if (x, y) in nei:
                        # Envolvemos SOLO el texto formateado con los códigos de color
                        row_parts.append(f"{PURPLE}{formatted_cell}{RESET}")
                    else:
                        row_parts.append(formatted_cell)
                        
            row_parts.append("|")
            lines.append("".join(row_parts))
        
        lines.append("   " + "‾" * (self.size * 4 + 1)) 
        
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
        for g_obj in g.list_of_go_objects:
            print(g_obj.id)
            print(g_obj.neighbors)
        for s in STEPS:
            print(f"g.place_stone({s[0]},{s[1]})")
        pygame.quit()
        sys.exit()
g=GoBoard(size=9)
g.place_stone(3,3)
g.place_stone(4,3)
g.place_stone(4,4)
g.place_stone(3,4)
g.place_stone(5,3)
g.place_stone(3,5)
g.place_stone(4,2)
g.place_stone(1,2)
g.place_stone(4,3)
g.place_stone(2,3)
g.place_stone(2,2)
g.place_stone(2,1)
g.place_stone(1,1)
g.place_stone(3,2)
g.place_stone(1,3)
g.place_stone(2,2)
g.place_stone(0,2)
g.place_stone(2,4)
g.place_stone(1,4)
g.place_stone(3,1)
g.place_stone(6,2)
g.place_stone(6,3)
g.place_stone(5,2)
g.place_stone(5,1)
g.place_stone(4,6)
g.place_stone(7,2)
g.place_stone(4,7)
g.place_stone(4,1)
g.place_stone(5,4)
g.place_stone(5,5)
g.place_stone(6,7)
g.place_stone(6,4)
g.place_stone(6,6)
g.place_stone(4,5)
g.place_stone(5,6)
g.place_stone(6,1)
g.place_stone(5,4)
g.place_stone(6,5)
g.place_stone(4,4)
g.place_stone(2,5)
g.place_stone(3,3)
g.place_stone(4,3)
g.place_stone(4,2)
g.place_stone(5,3)
g.place_stone(7,5)
g.place_stone(2,6)
g.place_stone(3,6)
g.place_stone(2,7)
g.place_stone(3,7)
g.place_stone(4,4)
g.place_stone(6,2)
g.place_stone(5,2)
g.place_stone(1,5)
g.place_stone(1,6)
g.place_stone(0,5)
g.place_stone(0,4)
g.place_stone(0,3)
g.place_stone(0,6)
g.place_stone(0,1)
g.place_stone(0,0)
g.place_stone(1,0)
g.place_stone(2,0)
g.place_stone(0,0)
g.place_stone(3,0)
g.place_stone(0,4)
g.place_stone(0,4)
g.place_stone(7,4)
g.place_stone(7,3)
g.place_stone(7,1)
try:
    g.run_gui()
except Exception as e:
    print(e)
    for g_obj in g.list_of_go_objects:
        print(g_obj.id)
        print(g_obj.neighbors)
    for s in STEPS:
        print(f"g.place_stone({s[0]},{s[1]})")