import socket
import threading
import pickle

HOST = 'localhost'
PORT = 12345

class GameManager:
    def __init__(self):
        self.board = [[0] * 7 for _ in range(6)]  # 6x7 board
        self.current_player = 1
        self.game_over = False

    def make_move(self, col):
        for row in range(5, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = self.current_player
                if self.check_win(row, col):
                    self.game_over = True
                self.current_player = (self.current_player % 4) + 1  # Switch to next player
                return True
        return False

    def check_win(self, row, col):
        piece = self.board[row][col]
        for c in range(COLUMN_COUNT - 3):
            for r in range(ROW_COUNT):
                if self.board[r][c] == piece and self.board[r][c + 1] == piece and self.board[r][c + 2] == piece and self.board[r][c + 3] == piece:
                    return True
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT - 3):
                if self.board[r][c] == piece and self.board[r + 1][c] == piece and self.board[r + 2][c] == piece and self.board[r + 3][c] == piece:
                    return True
        for c in range(COLUMN_COUNT - 3):
            for r in range(ROW_COUNT - 3):
                if self.board[r][c] == piece and self.board[r + 1][c + 1] == piece and self.board[r + 2][c + 2] == piece and self.board[r + 3][c + 3] == piece:
                    return True
        for c in range(COLUMN_COUNT - 3):
            for r in range(3, ROW_COUNT):
                if self.board[r][c] == piece and self.board[r - 1][c + 1] == piece and self.board[r - 2][c + 2] == piece and self.board[r - 3][c + 3] == piece:
                    return True
        return False

def client_handler(conn, addr, game_manager):
    print(f"Connected by {addr}")
    try:
        while True:
            data = pickle.loads(conn.recv(4096))
            if data['action'] == 'request_board':
                conn.sendall(pickle.dumps({'action': 'update_board', 'board': game_manager.board}))

            elif data['action'] == 'move':
                col = data['column']
                if game_manager.make_move(col):
                    response = {
                        'action': 'update_board',
                        'board': game_manager.board,
                        'game_over': game_manager.game_over,
                        'winner': game_manager.current_player if game_manager.game_over else None
                    }
                    conn.sendall(pickle.dumps(response))
            elif data['action'] == 'quit':
                print(f"Player {addr} quit.")
                break

    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(4)  # Listen for 4 players
    print(f"Server started on {HOST}:{PORT}")

    game_manager = GameManager()

    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=client_handler, args=(conn, addr, game_manager)).start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
