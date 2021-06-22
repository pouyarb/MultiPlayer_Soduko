import json
from os import name
from random import randint
from threading import Thread
from _thread import start_new_thread
from socket import socket, AF_INET, SOCK_STREAM
from Sudoku import Sudoku

class Server:
    
    def __init__(self, host, port) -> None:
        self.sock = socket(AF_INET, SOCK_STREAM)
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
            #Thread(target=self.handle_requests, args=(c_sock, addr)) 
            start_new_thread(self.handle_requests, (c_sock, addr))

        self.sock.close() 

    def handle_requests(self, c_sock, addr) -> None:
        game = None
        player_num = None
        while True:
            try:
                data = self.get_data(c_sock)
            except:
                if game != None:
                    if game.session in self._games:
                        self.quit(game, player_num, 'disconnect...', data['session'])
                print(f'client {addr[0]} : {addr[1]} disconnected badly')
                break
            #print(data['name'])
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
                    self.submit(game, player_num, c_sock, data['value'], data['pos_x'], data['pos_y'])
                elif 'quit' == com:
                    self.quit(game, player_num, 'quit the game...', data['session'])
                    continue
                elif 'disconnect' == com:
                    print(f'client {addr[0]} : {addr[1]} disconnected')
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
            'table' : table,
            'session' : session,
            'com_name' : name
        }
        c_sock.sendall(str(json.dumps(data)).encode('ascii'))

    def create_game(self, c_sock, name):
        game = Sudoku(name, c_sock)
        while True:
            session = str(randint(10 ** 4, 10 ** 5))
            if session not in self._games:
                self._games[session] = game
                game.session = session
                break
        self.send(c_sock, '200', 'game created', game.string_table, session, 'none')
        print(f'{name} create game. session : {session}')
        return game

    def join_game(self, c_sock, name, session):
        game = None
        if session in self._games:
            game = self._games[session]
            game.player_2_name = name
            game.player_2_sock = c_sock
            self.send(c_sock, '200', f'you join game {session}', game.string_table, session, game.player_1_name)
            self.send(game.player_1_sock, '200', f'{name} join the game', '-', session, name)
            print(f'{name} join game. session : {session}')
            return game
        self.send(c_sock, '300', 'session not found', 'none', 'none', 'none')
        return None

    def submit(self, game, player_num, c_sock, value, x, y) -> None:
        check = game.check_input(player_num, value, x, y)
        data1 = {
            'turn' : 'f',
            'update' : 'f'
        }
        data2 = {
            'turn' : 't',
            'update' : 'f'
        }
        if player_num == '1':
            data1['your_score'] = str(game.player_1_score)
            data1['com_score'] = str(game.player_2_score)
            data2['your_score'] = str(game.player_2_score)
            data2['com_score'] = str(game.player_1_score)
        else:
            data1['your_score'] = str(game.player_1_score)
            data1['com_score'] = str(game.player_2_score)
            data2['your_score'] = str(game.player_2_score)
            data2['com_score'] = str(game.player_1_score)
        if check == 1:
            data1['update'] = 't'
            data2['update'] = 't'
            data2['pos_x'] = x
            data2['pos_y'] = y
            data2['value'] = value
        elif check == 2:
            data1['update'] = 't'
            data2['update'] = 't'
            data1['turn'] = 'e'
            data2['turn'] = 'e'
            data2['pos_x'] = x
            data2['pos_y'] = y
            data2['value'] = value
            if data1['your_score'] > data1['com_score']:
                data1['message'] = 'congratulations you won!'
                data2['message'] = 'sorry you lose!'
            elif data1['your_score'] == data1['com_score']:
                data1['message'] = 'your score is same as your opponent...'
                data2['message'] = 'your score is same as your opponent...'
            else:
                data1['message'] = 'sorry you lose!'
                data2['message'] = 'congratulations you won!'
            session = game.session
            try:
                del self._games[session]
            except:
                print('session delete problem')
        c_sock.sendall(str(json.dumps(data1)).encode('ascii'))
        if player_num == '1':
            game.player_2_sock.sendall(str(json.dumps(data2)).encode('ascii'))   
        else:
            game.player_1_sock.sendall(str(json.dumps(data2)).encode('ascii'))


    def quit(self, game, player_num, message, session) -> None:
        data = {'turn' : 'd'}
        if player_num == '1':
            data['message'] = f'{game.player_1_name} {message}'
            game.player_2_sock.sendall(str(json.dumps(data)).encode('ascii'))
        else:
            data['message'] = f'{game.player_2_name} {message}'
            game.player_1_sock.sendall(str(json.dumps(data)).encode('ascii'))
        try:
            del self._games[session]
        except:
            print('session delete problem')


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 8080
    server = Server(host, port)
    server.run()