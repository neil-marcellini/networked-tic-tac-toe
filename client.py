# client.py - a simple client
import TTTEngine as ttt
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

    # send Join command
    sock.send(b"Join")
    join_msg = sock.recv(len("Joined")).decode('utf-8')
    print(join_msg)
    if join_msg == "ErrorS":
        print("Game already started. Try again later.")
        # quit
        sock.close()
    # ask user to enter their character
    character = input("Please type X or O\n")
    while character != "X" and character != "O":
        print("Invalid character choice")
        character = input("Please type X or O\n")
    # send character choice
    sock.send(bytes(character, 'utf-8'))
    # receive character setup packet
    char_setup = sock.recv(len("XS")).decode('utf-8')
    my_char = char_setup[0]
    if my_char == character:
        print(f"Your character is {my_char}")
    else:
        print(f"The other player is using {character}, your character is {my_char}")

    game_state = char_setup[1]
    engine = ttt.TicTacToeEngine()
    if game_state == "W" or game_state == "S":
        print("Waiting for the other player's move.")
        # wait for game state message
        state = sock.recv(9).decode('utf-8')
        # update board state
        new_board = [char for char in state]
        engine.board = new_board

    # make your first move
    engine.display_board()
    
    # main gameplay loop
    game_over = False
    winner = None
    final_move = False
    while not game_over:
        move_input = input("Enter the position between 0 and 8 where you want to play. Top left to bottom right.\n")
        move_is_valid = len(move_input) == 1 and move_input.isnumeric()
        while not move_is_valid:
            print("Invalid move")
            move_input = input("Enter the position between 0 and 8 where you want to play. Top left to bottom right.\n")
            move_is_valid = len(move_input) == 1 and move_input.isnumeric()
        move = int(move_input)
        engine.make_move(move, my_char)
        board_msg = "".join(engine.board)
        sock.send(bytes(board_msg, 'utf-8'))
        print("Your move:")
        engine.display_board()
        if engine.is_game_over() == "-":
            # game not over, get the next move
            print("Waiting for the other player's move.")
        else:
            # game will be over
            final_move = True
        state = sock.recv(9).decode('utf-8')
        if state.startswith("End"):
            game_over = True
            winner = state[3]
            if final_move:
                # go straight to results
                break
            else:
                # get end game state if you didn't make the last move
                state = sock.recv(9).decode('utf-8')
        # convert state into a list 
        new_board = [char for char in state]
        engine.board = new_board
        print("The other player's move is:")
        engine.display_board()

    if winner == my_char:
        print("You won!")
    elif winner == "T":
        print("It's a tie.")
    else:
        print("Sorry, you lost.")

    # quit
    sock.close()


if __name__ == '__main__':
    port = 9001

    parser = argparse.ArgumentParser(description='Client')
    parser.add_argument('host', help='IP address of the server.')
    args = parser.parse_args()

    client(args.host, port)
