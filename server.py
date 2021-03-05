# server.py - a simple threaded server

import TTTEngine as ttt
from queue import Queue

import argparse, socket, logging, threading
# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)

class ClientThread(threading.Thread):
    def __init__(self, address, socket, thread_cond, q):
        threading.Thread.__init__(self)
        self.csock = socket
        self.address = address
        self.thread_cond = thread_cond
        self.q = q

        logging.info('New thread!')


    def run(self):
        # send a message
        self.csock.sendall(b'Hello client!\n')

        # get a message
        join_msg = self.recv_bytes(self.csock, len("Join")).decode('utf-8')
        logging.info("Message: " + join_msg)

        # check if game has started
        engine = self.q.get()
        started = engine.game_started
        logging.info(f"game_started = {started}")
        msg = b"Joined"
        if started:
            msg = b"ErrorS"
            # disconnect
            self.csock.close()
            logging.info('Disconnect client.')

        self.csock.sendall(msg)
        char_msg = self.recv_bytes(self.csock, len("X")).decode('utf-8')
        logging.info(f"Character chosen: {char_msg}")
        client_char = char_msg

        is_p1 = False
        # set player
        p1_char = engine.p1
        if p1_char is None:
            # your are p1 and you get your char choice
            is_p1 = True
            engine.p1 = char_msg
        else:
            # your are p2
            # you may or may not get your char choice
            if p1_char == "X":
                engine.p2 = "O"
                client_char = "O"
            else:
                engine.p2 = "X"
                client_char = "X"

        # set game state
        engine.game_started = engine.p1 is not None and engine.p2 is not None
        game_state = "W"
        if engine.game_started:
            game_state = "G"
        char_setup = client_char + game_state
        # update engine
        self.q.put(engine)
        # send back client_char
        self.csock.sendall(bytes(char_setup, 'utf-8'))

        if game_state != "G":
            # wait for updated engine from the other player
            self.thread_cond.acquire()
            self.thread_cond.wait()
            engine = self.q.get()
            # send the updated play to this client
            game_state = "".join(engine.board)
            self.csock.sendall(bytes(game_state, 'utf-8'))

        while engine.is_game_over() == "-":
            # get move from this client
            client_play = self.recv_bytes(self.csock, 9).decode('utf-8')
            # get the move based on board diff
            move = engine.get_move_from(client_play)
            valid_move = engine.make_move(move, client_char)
            if not valid_move:
                self.csock.sendall(b'ErrorI')
                game_state = "".join(engine.board)
                self.csock.sendall(bytes(game_state, 'utf-8'))
                continue
            # check for game over
            if engine.is_game_over() != "-":
                break
            # send to other client and notify them
            self.thread_cond.acquire()
            self.q.put(engine)
            print(f"thread {client_char} notifying opponent")
            self.thread_cond.notify()
            # wait for updated engine from the other player
            print(f"thread {client_char} waiting for move")
            self.thread_cond.wait()
            engine = self.q.get()
            print(f"thread {client_char} got new engine")
            # check for game over
            if engine.is_game_over() != "-":
                break
            # send to this client
            game_state = "".join(engine.board)
            self.csock.sendall(bytes(game_state, 'utf-8'))

        # find out who won
        winner = engine.is_game_over()
        # send End packet
        print(f"thread {client_char} sending end packet")
        end_packet = f"End{winner}"
        self.csock.sendall(bytes(end_packet, 'utf-8'))

        # send the end state to this client
        print(f"thread {client_char} sending end state")
        game_state = "".join(engine.board)
        self.csock.sendall(bytes(game_state, 'utf-8'))

        # send to other client and notify them
        self.thread_cond.acquire()
        self.q.put(engine)
        print(f"thread {client_char} notifying opponent")
        self.thread_cond.notify()
        print(f"thread {client_char} short wait ")
        self.thread_cond.wait(2)

        # disconnect
        self.csock.close()
        logging.info('Disconnect client.')


    def recv_until(self, sock, suffix):
        """Receive bytes over socket `sock` until we receive the `suffix`."""
        message = sock.recv(1024)
        if not message:
            raise EOFError('socket closed')
        while not message.endswith(suffix):
            data = sock.recv(1024)
            if not data:
                raise IOError('received {!r} then socket closed'.format(message))
            message += data
        return message

    def recv_bytes(self, sock, num_bytes):
        message = sock.recv(num_bytes)
        return message

def server():
    # start serving (listening for clients)
    port = 9001
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost',port))

    # https://docs.python.org/3.8/library/threading.html#threading.Condition
    thread_cond = threading.Condition()


    # game state
    engine = ttt.TicTacToeEngine()
    q = Queue()

    while True:
        sock.listen(1)
        logging.info('Server is listening on port ' + str(port))

        # client has connected
        sc,sockname = sock.accept()
        logging.info('Accepted connection.')
        # put engine on the q
        q.put(engine)
        t = ClientThread(sockname, sc, thread_cond, q)
        t.start()

server()
