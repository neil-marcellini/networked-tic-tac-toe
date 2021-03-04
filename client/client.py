# client.py - a simple client

import argparse, socket, logging

# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)

def recv_until(sock, suffix):
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


def client(host,port):
    # connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host,port))
    sock.setblocking(True)
    logging.info('Connect to server: ' + host + ' on port: ' + str(port))

    msg = recv_until(sock, b"\n").decode('utf-8')
    logging.info('Message: ' + msg)

    # send Join command
    sock.send(b"Join")
    join_msg = sock.recv(len("Joined")).decode('utf-8')
    logging.info(f"Join message: {join_msg}")

    # quit
    sock.close()


if __name__ == '__main__':
    port = 9001

    parser = argparse.ArgumentParser(description='Client')
    parser.add_argument('host', help='IP address of the server.')
    args = parser.parse_args()

    client(args.host, port)
