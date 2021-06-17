from random import randint

class Sudoku:

    def __init__(self, name, sock) -> None:
        self.real_table = self.initial_table()
        self.visible_table = self.create_visible_table()
        self.visible = 50
        self.player_1_name = name
        self.player_2_name = None
        self.player_1_score = 0
        self.player_2_score = 0
        self.player_1_sock = sock
        self.player_2_sock = None
        self.string_table = self.make_string

    def initial_table(self) -> list:
        base  = 3
        side  = base*base

        # pattern for a baseline valid solution
        def pattern(r,c): return (base*(r%base)+r//base+c)%side

        # randomize rows, columns and numbers (of valid base pattern)
        from random import sample
        def shuffle(s): return sample(s,len(s)) 
        rBase = range(base) 
        rows  = [ g*base + r for g in shuffle(rBase) for r in shuffle(rBase) ] 
        cols  = [ g*base + c for g in shuffle(rBase) for c in shuffle(rBase) ]
        nums  = shuffle(range(1,base*base+1))

        # produce board using randomized baseline pattern
        ret = [ [nums[pattern(r,c)] for c in cols] for r in rows ]
        # ret = [['0','0','0','0','0','0','0','0','0'] for x in range(9)]
        # for x in range(1, 9):
        #     check_col = ['0','0','0','0','0','0','0','0','0']
        #     for i in range(2):
        #         tmp_blk = randint(0, 2) * 3
        #         tmp_col = randint(0, 2)
        #         if check_col[tmp_blk + tmp_col] == 1:
        #             tmp_col = (tmp_col + 1) % 3
                
        #         check_col[tmp_blk + tmp_col] = 1
        #         if tmp_blk == 0:
        #             pass

        # for i in range(9):
        #     for j in range(9):
        #         if ret[i][j] == '0':
        #             ret[i][j] = '9'
        #             break

        return ret

    def create_visible_table(self) -> list:
        ret = self.real_table.copy()
        c = 81 - self.visible
        i = 0
        while i < c:
            v1 = randint(1, 9)
            v2 = randint(1, 9)
            if ret[v1][v2] != '-':
                ret[v1][v2] == '-'
                i += 1
        
        return ret

    def make_string(self) -> str:
        ret = ''
        for i in range(9):
            for j in range(9):
                ret += self.visible_table[i][j]

    def check_input(self, player, value, pos_x, pos_y) -> bool:
        pos_x = int(pos_x)
        pos_y = int(pos_y)
        if self.real_table[pos_x][pos_y] == value:
            self.visible_table[pos_x][pos_y] = value
            if player == 1:
                self.player_1_score += 1
                return True
            else:
                self.player_2_score += 1
                return True
        else:
            if player == 1:
                return False
            else:
                return False