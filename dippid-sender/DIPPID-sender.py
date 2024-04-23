import json
import numpy as np
import random
import socket
import time

# From simple-sender.py übernommen ----
IP = '127.0.0.1'
PORT = 5700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ----


def update_data(data: dict, key: str, value) -> dict:
    data['data'][key] = value
    return data


def random_btn_state() -> int:
    pressed = random.randint(0, 1)
    return pressed


def random_acc_data(x_origin: float) -> dict:
    acc_dic = {}
    acc_dic['x'] = np.cos(x_origin)
    acc_dic['y'] = np.cos(x_origin*2)
    acc_dic['z'] = np.cos(x_origin**2)
    return acc_dic


def main():
    x_origin = 0

    while True:
        print('sending data …')

        acc = random_acc_data(x_origin=x_origin)
        x_origin += 0.12

        # 'data' ist mein schlüsselwort, auf welches ich demo_heartbeat.py als callback genutzt habe
        # wird hier also erzeugt und ergäntzt durch meine funktion update_data
        data = {'data': {}}

        data = update_data(data, 'button_1', random_btn_state())
        data = update_data(data, 'button_2', random_btn_state())
        data = update_data(data, 'button_3', random_btn_state())
        data = update_data(data, 'accelerometer', acc)

        sock.sendto(json.dumps(data).encode(), (IP, PORT))
        time.sleep(1.5)


if __name__ == "__main__":
    main()
