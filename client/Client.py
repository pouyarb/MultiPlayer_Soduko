import os
from time import sleep
import json
from socket import socket, AF_INET, SOCK_STREAM

class Client:

    def __init__(self, host, port, name) -> None:
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.ser_host = host
        self.ser_port = port
        self.name = name
        self.com_name = None
        self.score = '0'
        self.com_score = '0'
        self.table = []
        self.session = None

    def run(self) -> None:
        self.sock.connect((self.ser_host, self.ser_port))
        print(f'connected to server at {self.ser_host} on port {self.ser_port}')
        print('Menu:')
        while True:
            print('1-Create a new game')
            print('2-Join game')
            print('3-Exit')
            n = input('Enter a number: ')
            if n == '1':
                self.create_game()
            elif n == '2':
                self.join_game()
            elif n == '3':
                print('exit...')
                break
            else :
                os.system('cls')
                print('invalid input!!! please try again')
        self.sock.close()

    def play(self, turn) -> None:
        while True:
            if turn:
                os.system('cls')
                self.show_table()
                n = int(input('enter value in range 1-9 to submit or enter 0 to quit this game: '))
                if n == 0:
                    self.send('disconnect', '-')
                    break
                elif n < 10:
                    px = int(input('enter horizontal axis: '))
                    while px < 1 or px > 9:
                        print('not in range')
                        px = int(input('horizontal axis: '))
                    py = int(input('enter vertical axis: '))
                    while py < 1 or py > 9:
                        print('not in range')
                        px = int(input('vertical axis: '))
                    self.submit(n, px, py)
                    data = self.get_data()
                    if data['update'] == 't':
                        self.table[px][py] = n
                        self.score = data['your_score']
                        self.com_score = data['com_score']
                        turn = False
                        if data['turn'] == 'w':
                            print('\tfinal scores')
                            self.show_table()
                            print(data['message'])
                            break
            else:
                data = self.get_data()
                turn = True
                if data['update'] == 't':
                        self.table[data['pos_x']][data['pos_y']] = data['value']
                        self.score = data['your_score']
                        self.com_score = data['com_score']
                        if data['turn'] == 'w':
                            print('\tfinal scores')
                            self.show_table()
                            print(data['message'])
                            break
                if data['turn'] == 'd':
                    print(data['message'])
                    break


    def create_game(self) -> None:
        self.send('create', '0')
        data = self.get_data()
        print(data['message'])
        if data['status'] == '200':
            self.make_table(data['table'])
        else:
            return
        data = self.get_data()
        print(data['message'])
        if data['status'] == '200':
            self.com_name = data['com_name'] 
            self.session = data['session']
            sleep(2)
            self.play(True)

    def join_game(self) -> None:
        s = input('Please enter game code: ')
        self.send('join', s)
        data = self.get_data()
        print(data['message'])
        if data['status'] == '200':
            self.make_table(data['table'])
            self.session = s
            self.com_name = data['com_name']
            self.play(False)

    def submit(self, value, pos_x, pos_y) -> None:
        data = {
            'command' : 'submit',
            'value': str(value),
            'pos_x': str(pos_x),
            'pos_y' : str(pos_y)
        }
        self.sock.sendall(str(json.dumps(data)).encode('ascii'))

    def send(self, command, session) -> None:
        data = {
            'command': command,
            'name': self.name,
            'session' : session
        }
        self.sock.sendall(str(json.dumps(data)).encode('ascii'))

    def get_data(self):
        data = self.sock.recv(4096).decode('ascii')
        return json.loads(data)

    def show_table(self) -> None:
        print(f'{self.name} : {self.score}')
        print(f'{self.com_name} : {self.com_score}')
        for i in range(9):
            print(*self.table[i])

    def make_table(self, ls):
        i = 0
        for j in range(9):
            self.table.append(ls[i : i + 9])
            i = i + 9

if __name__ == '__main__':
    server_host = 'localhost'
    server_port = 8080
    name = input('Enter your name: ')
    client = Client(server_host, server_port, name)
    client.run()