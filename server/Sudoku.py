from random import randint, sample

class Sudoku:

    def __init__(self, name, sock) -> None:
        self.real_table = self.initial_table()
        self.visible = 80
        self.visible_table = self.create_visible_table()
        self.player_1_name = name
        self.player_2_name = None
        self.player_1_score = 0
        self.player_2_score = 0
        self.player_1_sock = sock
        self.player_2_sock = None
        self.string_table = self.make_string()
        self.session = None

    def initial_table(self) :
        base  = 3
        side  = base*base

        # pattern for a baseline valid solution
        def pattern(r,c): 
            return (base*(r%base)+r//base+c)%side

        # randomize rows, columns and numbers (of valid base pattern)
        def shuffle(s): 
            return sample(s,len(s)) 

        rBase = range(base) 
        rows  = [ g*base + r for g in shuffle(rBase) for r in shuffle(rBase) ] 
        cols  = [ g*base + c for g in shuffle(rBase) for c in shuffle(rBase) ]
        nums  = shuffle(range(1,base*base+1))

        # produce board using randomized baseline pattern
        ret = [ [nums[pattern(r,c)] for c in cols] for r in rows ]
        
        for i in range(9):
            for j in range(9):
                ret[i][j] = str(ret[i][j])
        return ret

    def create_visible_table(self) -> list:
        ret = []
        for i in range(9):
            ret.append(self.real_table[i].copy())
        #ret = self.real_table.copy()
        c = 81 - self.visible
        i = 0
        while i < c:
            v1 = randint(0, 8)
            v2 = randint(0, 8)
            if ret[v1][v2] != '-':
                ret[v1][v2] = '-'
                i += 1
        
        return ret

    def make_string(self) -> str:
        ret = ''
        for i in range(9):
            for j in range(9):
                ret += self.visible_table[i][j]
        return ret

    def check_input(self, player, value, pos_x, pos_y) -> int:
        result = 0
        x = int(pos_x) - 1
        y = int(pos_y) - 1
        if self.real_table[x][y] == value and self.visible_table[x][y] == '-':
            self.visible_table[x][y] = value
            self.visible += 1
            if self.visible == 81:
                result = 2
            else:
                result = 1
            if player == '1':
                self.player_1_score += 1
            else:
                self.player_2_score += 1

        return result