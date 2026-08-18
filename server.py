from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import time

sock = socket(AF_INET, SOCK_STREAM)
sock.bind(('localhost', 8080))
sock.listen(5)
sock.setblocking(False)

players = {}
conn_ids = {}
id_counter = 0


def handle_data():
    global id_counter
    while True:
        time.sleep(0.01)
        to_remove = []

        # оновлюємо позиції тих, хто надіслав дані
        for conn in list(players):
            try:
                data = conn.recv(64).decode().strip()
                if ',' in data:
                    parts = data.split(',')
                    if len(parts) == 5:
                        pid, x, y, r = map(int, parts[:4])
                        name = parts[-1]
                        players[conn] = {'id': pid, 'x': x, 'y': y, 'r': r, 'name': name}
            except:
                pass

        # колізії по ВСІХ поточних гравцях (останні відомі позиції)
        eliminated = []
        conns = list(players.keys())
        for i, conn1 in enumerate(conns):
            if conn1 in eliminated:
                continue
            p1 = players[conn1]
            for conn2 in conns[i + 1:]:
                if conn2 in eliminated:
                    continue
                p2 = players[conn2]
                dx = p1['x'] - p2['x']
                dy = p1['y'] - p2['y']
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance < p1['r'] + p2['r']:
                    if p1['r'] > p2['r'] * 1.1:
                        p1['r'] += int(p2['r'] * 0.5)
                        players[conn1] = p1
                        eliminated.append(conn2)
                    elif p2['r'] > p1['r'] * 1.1:
                        p2['r'] += int(p1['r'] * 0.5)
                        players[conn2] = p2
                        eliminated.append(conn1)

        # розсилка + видалення
        for conn in list(players.keys()):
            if conn in eliminated:
                try:
                    conn.send("LOSE".encode())
                except:
                    pass
                to_remove.append(conn)
                continue

            try:
                # надсилаємо ВСІХ (включаючи себе), щоб клієнт міг оновити свій радіус
                packet = '|'.join(
                    f"{p['id']},{p['x']},{p['y']},{p['r']},{p['name']}"
                    for c, p in players.items() if c not in eliminated
                ) + '|'
                conn.send(packet.encode())
            except:
                to_remove.append(conn)

        for conn in to_remove:
            players.pop(conn, None)
            conn_ids.pop(conn, None)


Thread(target=handle_data, daemon=True).start()
print("SERVER running...")

while True:
    try:
        conn, addr = sock.accept()
        conn.setblocking(False)
        id_counter += 1
        players[conn] = {'id': id_counter, 'x': 0, 'y': 0, 'r': 20, 'name': ''}
        conn_ids[conn] = id_counter
        conn.send(f"{id_counter},0,0,20".encode())
    except:
        pass
