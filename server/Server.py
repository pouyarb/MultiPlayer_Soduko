import json
from random import randint
from threading import Thread
#from _thread import start_new_thread
from socket import socket 
from Sudoku import Sudoku

class Server:
    
    def __init__(self, host, port) -> None:
        self.sock = socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        #self.lock = Lock()
        self._games = dict()
        
    def run(self) -> None:
        self.sock.bind((self.host, self.port)) 
        print('socket binded to port', self.port) 

        self.sock.listen(10)
        print('socket is listening...') 

        while True:
            c_sock, addr = self.sock.accept() 
            print(f'client {addr[0]} : {addr[1]} connected') 
            Thread(target=self.handle_requests, args=(c_sock, addr)) 
            #start_new_thread(self.handle_requests, (c_sock, addr))

        self.sock.close() 

    def handle_requests(self, c_sock, addr) -> None:
        game = None
        player_num = None
        while True:
            data = self.get_data(c_sock)
            if 'command' in data:
                com = data['command']
                if 'create' == com:
                    game = self.create_game(c_sock, data['name'])
                    player_num = '1'
                elif 'join' == com:
                    game = self.join_game(c_sock, data['name'], data['session'])
                    player_num = '2'
                elif 'submit' == com:
                    if game == None:
                        self.send(c_sock, '300', 'session not found', 'none', 'none', 'none')
                    self.submit(game, c_sock, player_num, data['value'], data['pos_x'], data['pos_y'])
                elif 'disconnect' == com:
                    break
                else:
                    self.send(c_sock, '300', 'request not found', 'none', 'none', 'none')

        c_sock.close()

    def get_data(self, c_sock) :
        data = c_sock.recv(4096).decode('ascii')
        return json.loads(data)

    def send(self, c_sock, status, message, table, session, name) -> None:
        data = {
            'status': status,
            'message': message,
            'table' : table
            'session' : session
            'name' : name
        }
        c_sock.sendall(str(json.dumps(data)).encode('ascii'))

    def create_game(self, c_sock, name):
        game = Sudoku(name, c_sock)
        session = str(randint(10 ** 4, 10 ** 5))
        self._games[session] = game
        self.send(c_sock, '200', 'game created', game.string_table, session, 'none')
        return game

    def join_game(self, c_sock, name, session):
        game = None
        if session in self._games:
            game = self._games[session]
            game.player_2_name = name
            game.player_2_sock = c_sock
            self.send(c_sock, '200', f'you join game {session}', game.string_table, session, game.player_1_name)
            return game
        self.send(c_sock, '300', 'session not found', 'none', 'none', 'none')
        return None

    def submit(self, game, player_num, c_sock, value, x, y) -> None:
        data = {
            'turn' : 'f',
            'update' : 'f'
        }
        if player_num == '1':
            if game.check_input(player_num, value, x, y):
                data['update'] = 't'
            data['your_score'] = str(game.player_1_score)
            data['com_score'] = str(game.player_2_score)
            c_sock.sendall(str(json.dumps(data)).encode('ascii'))
            data['turn'] = 't'
            if data['update'] == 't':
                data['pos_x'] = x
                data['pos_y'] = y
                data['value'] = value
            game.player_2_sock.sendall(str(json.dumps(data)).encode('ascii'))

        else:
            if game.check_input(player_num, value, x, y):
                data['update'] = 't'
            data['your_score'] = str(game.player_2_score)
            data['com_score'] = str(game.player_1_score)
            c_sock.sendall(str(json.dumps(data)).encode('ascii'))
            data['turn'] = 't'
            if data['update'] == 't':
                data['pos_x'] = x
                data['pos_y'] = y
                data['value'] = value
            game.player_1_sock.sendall(str(json.dumps(data)).encode('ascii'))


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 8080
    server = Server(host, port)
    server.run()