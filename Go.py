TOP = 0
LEFT = 1
BOTTOM = 2
RIGHT = 3

BLACK=1
WHITE=2

class GoObject:
    def __init__(self, color):
        self.color = color
        self.stones = []
    
    def add_stone(self, x, y):
        self.stones.append((x, y))
    
    def check_liberties(self, board):
        for (x, y) in self.stones:
            for direction in [TOP, LEFT, BOTTOM, RIGHT]:
                n_x, n_y = board.neighbor(x, y, direction)
                if n_x is not False and board.board[n_x][n_y] is None:
                    return True
        return False
    
    def dead(self):
        self.stones=[]
        

class GoBoard:
    def __init__(self, size=9):
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.objects_board=[[None for _ in range(size)] for _ in range(size)]
        self.objects = []
        self.current_player = BLACK
        self.captured_stones = {BLACK: 0, WHITE: 0}
    
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
            print(self.board[x][y])
            return False  
        return True
        # Additional rules like suicide and ko can be implemented here
        # Check if the game has ended

    def other_player(self):
        """
        Nim.other_player(player) returns the player that is not
        `player`. Assumes `player` is either 0 or 1.
        """
        return WHITE if self.current_player == BLACK else BLACK

    def neighbor(self, x, y, i):
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

    def neighbors(self, x, y):
        local_neighborhood = []
        for index in [-1,1]:
            if y+index>0:
                local_neighborhood.append(self.board[x][y+index])
            else:
                local_neighborhood.append(False)
            if x+index>0:
                local_neighborhood.append(self.board[x+index][y])
            else:
                local_neighborhood.append(False)
        return local_neighborhood

    def update_objects(self,x,y):
        piece_color= self.board[x][y]
        nbh = self.neighbors(x,y)
        fomo = True
        for n_i in range(len(nbh)):
            if nbh[n_i]==piece_color:
                fomo=False
                n_x,n_y=self.neighbor(x,y,n_i)
                obj_index=self.objects_board[n_x][n_y]
                self.objects[obj_index].add_stone(x,y)
                self.objects_board[x][y] = obj_index
        if fomo:
            new_object = GoObject(piece_color)
            new_object.add_stone(x,y)
            self.objects.append(new_object)
            self.objects_board[x][y] = len(self.objects) - 1

    def place_stone(self, x, y):
        if self.is_move_legal(x,y) is False:
            return False  
        
        self.board[x][y] = self.current_player
        self.update_objects(x,y)
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
        lines = []
        lines.append("   "+"  ".join(map(str, range(self.size))))
        lines.append("  "+"_" * (self.size * 3 + 1))  
        
        for y in range(self.size):
            row = [" " + str(y) +"|"]
            for x in range(self.size):
                cell = self.objects_board[x][y]
                if cell is None:
                    row.append("  ")
                else:
                    row.append(str(self.objects_board[x][y])+" ")
                row.append("|")
            lines.append("".join(row))
        
        lines.append("  "+"‾" * (self.size * 3 + 1)) 
        
        print("\n".join(lines))

    # TODO: Implement GUI display method
    def displa_gui(self):
        pass

g=GoBoard(size=9)

while True:
    x,y=map(int,input("Enter your move (x,y): ").split(","))
    g.place_stone(x,y)
    g.display_terminal()
    g.display_terminal_objects()
