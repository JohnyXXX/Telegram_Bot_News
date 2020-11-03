import time
from multiprocessing import Process

from main import Main

TIMEOUT = 600


def core():
    main = Main()
    main.run()


if __name__ == '__main__':
    while True:
        p = Process(target=core, name='Process-Bot')
        p.start()
        time.sleep(TIMEOUT)
        if p.is_alive():
            p.terminate()
