import socket
import os
import time
import sys

# Sprawdzenie, czy adres IP serwera został podany jako argument
if len(sys.argv) != 2:
    print("Użycie: python3 cli.py <adres_ip_serwera>")
    sys.exit(1)

SERVER = sys.argv[1]  # Pobranie adresu IP serwera z argumentów wiersza poleceń
PORT = 8080
ADDR = (SERVER, PORT)

def main():
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(ADDR)

	while True:
		response = client.recv(1024).decode()
        
        #if "Runda" in response:
        #	os.system("clear")

		print(response)
		if "Przeciwnik się poddał" in response:
			break
        
		if "Koniec gry" in response:
			break

		if "Twoja tura, rzuc karte (r) lub poddaj się (p): " in response:
			decision = input("Wybierz akcję: ").strip().lower()
			while decision not in ['r', 'p']:
				print("Niepoprawna komenda. Spróbuj ponownie.")
				decision = input("Wybierz akcję: ").strip().lower()
			client.send(decision.encode())
			if decision == 'p':
				break
	print("Kończenie działania programu...")
	time.sleep(2)
	return 0

main()


