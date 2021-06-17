import os
import json
from socket import socket

class Client:

    def __init__(self, host, port, name) -> None:
        self.sock = socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ser_host = host
        self.ser_port = port
        self.name = name
        self.com_name = None
        self.score = 0
        self.com_score = 0
        self.table = None

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
                self.send('create', '0')
                self.table = self.get_data()['table']
                self.play(False)
                os.system('cls')
            elif n == '2':
                s = input('Please enter game code: ')
                self.send('join', s)
                self.table = self.get_data()['table']
                self.play(True)
                os.system('cls')
            elif n == '3':
                break
            else :
                os.system('cls')
                print('invalid input!!! please try again')
        self.sock.close()

    def play(self, turn) -> None:
        while True:
            if turn:
                self.show_table()
                n = int(input('enter value in range 1-9 to submit or enter 0 to quit: '))
                if n == 0:
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
                    self.score = int(data['score'])
                    turn = bool(data['turn'])
                    if data['check'] == 't':
                        self.table[px][py] = n
            else:
                data = self.get_data()
                turn = data['turn']
                if data['update'] == 't':
                    self.table[data['pos_x']][data['pos_y']] = data['value']

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
        os.system('cls')
        print(f'{self.name} : {self.score}')
        print(f'{self.com_name} : {self.com_score}')
        for i in range(9):
            print(*self.table[i])

if __name__ == '__main__':
    server_host = 'localhost'
    server_port = 8080
    name = input('Enter your name: ')
    client = Client(server_host, server_port, name)
    client.run()