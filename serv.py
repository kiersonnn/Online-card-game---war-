import socket
import threading
import random

# Definicja kart
values = list(range(2, 11)) + ['J', 'Q', 'K', 'A']
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']

SERVER = '0.0.0.0'
PORT = 8080
ADDR = (SERVER, PORT)

# Funkcja do porównywania wartości kart
def card_value(card):
    if card[0] in ['J', 'Q', 'K', 'A']:
        return 11 + ['J', 'Q', 'K', 'A'].index(card[0])
    else:
        return int(card[0])

# Logika gry
def play_game(conn1, conn2):
    deck = [(value, suit) for value in values for suit in suits]
    random.shuffle(deck)

    player1_hand, player2_hand = deck[:26], deck[26:]
    player1_score, player2_score = 0, 0
    rounds_played = 0

    conn1.sendall("server>> Witaj graczu 1\n".encode())
    conn2.sendall("server>> Witaj graczu 2\n".encode())

    while rounds_played < 31 and player1_hand and player2_hand:
        round_cards = []

        for conn, hand in [(conn1, player1_hand), (conn2, player2_hand)]:
            conn.sendall("server>> Twoja tura, rzuc karte (r) lub poddaj się (p): ".encode())
            decision = conn.recv(1024).decode().strip().lower()

            if decision == 'p':
                conn.sendall("server>> Poddajesz się. Przegrałeś!\n".encode())
                (conn2 if conn == conn1 else conn1).sendall("Przeciwnik się poddał. Wygrałeś!\n".encode())
                return

            if decision == 'r':
                card = hand.pop(0)
                round_cards.append(card)
                conn.sendall(f"server>> Rzucasz kartę: {card}\n".encode())
                (conn2 if conn == conn1 else conn1).sendall(f"Przeciwnik rzucił kartę: {card}\n".encode())

        if len(round_cards) == 2:  # Pełna runda, obaj gracze rzucili kartę
            card1, card2 = round_cards
            if card_value(card1) > card_value(card2):
                player1_score += 1
                winner = "gracz 1"
            elif card_value(card1) < card_value(card2):
                player2_score += 1
                winner = "gracz 2"
            else:
                winner = "remis"

            summary = f"\nserver>> Runda {rounds_played + 1}: {winner} wygrywa.\n"
            conn1.sendall(summary.encode())
            conn2.sendall(summary.encode())

            rounds_played += 1  # Inkrementacja po pełnej rundzie

    result = f"\nserver>> Koniec gry. Twój wynik: {player1_score}, wynik przeciwnika: {player2_score}\n"
    conn1.sendall(result.encode())
    conn2.sendall(result.encode())
    conn1.close()
    conn2.close()

def handle_client(conn, addr, waiting_clients):
    print(f"[NEW CONNECTION] {addr} connected.")
    if waiting_clients:
        opponent_conn = waiting_clients.pop()
        threading.Thread(target=play_game, args=(conn, opponent_conn)).start()
    else:
        waiting_clients.append(conn)

# Start serwera
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")

    waiting_clients = []

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr, waiting_clients)).start()

start_server()