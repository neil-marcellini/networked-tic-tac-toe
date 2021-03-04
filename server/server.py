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
