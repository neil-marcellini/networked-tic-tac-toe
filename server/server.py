# server.py - a simple threaded server

import argparse, socket, logging, threading
# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)

class ClientThread(threading.Thread):
    def __init__(self, address, socket, thread_cond):
        threading.Thread.__init__(self)
        self.csock = socket
        self.address = address
        self.thread_cond = thread_cond

        logging.info('New thread!')


    def run(self):
        # send a message
        self.csock.sendall(b'Hello client!\n')

        # get a message
        msg = self.recv_until(self.csock, b"\n").decode('utf-8')
        logging.info("Message: " + msg)

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


def server():
    # start serving (listening for clients)
    port = 9001
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost',port))

    # https://docs.python.org/3.8/library/threading.html#threading.Condition
    thread_cond = threading.Condition()

    while True:
        sock.listen(1)
        logging.info('Server is listening on port ' + str(port))

        # client has connected
        sc,sockname = sock.accept()
        logging.info('Accepted connection.')
        t = ClientThread(sockname, sc, thread_cond)
        t.start()

server()
