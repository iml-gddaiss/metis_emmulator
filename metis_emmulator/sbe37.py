"""
Author: jerome.guay@protonmail.com
Date: August 2023


Notes
-----
From Controller Firmware:
    Start:
      SerialOut(SerialSBE37,CHR(13),"S>",1,50)
      SerialOut(SerialSBE37,"ts"&CHR(13)," ",1,400)
      SerialIn(RawSBE37_SalinityTest,SerialSBE37,300,CHR(83),40)
    Collect:
      SerialOut(SerialSBE37,CHR(13),"S>",1,50)

      If X = 1 Then
        SerialOut(SerialSBE37,"tss"&CHR(13)," ",1,400)
      Else
        SerialOut(SerialSBE37,"sl"&CHR(13)," ",1,400)
      EndIf

      SerialIn(RawSBE37,SerialSBE37,400,83,60)

"""

import socket
import threading
import time
import logging

SBE37_BEAUDERATE = 9600

class SBE37Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.is_running = False

        self._socket = None

        self.conns = {}

        self.thread = None

        logging.info(f'Test server host: {host}')

    def start_comm_port(self, number_of_connections=5):
        logging.info('Starting Test')

        self.is_running = True
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while self.is_running:
            try:
                self._socket.bind((self.host, self.port))
                break
            except OSError:
                logging.debug(f'Error, download port {self.port} unavailable. (Retrying in 2 seconds)')
                time.sleep(2)
                #self.port += 1

        self._socket.listen(number_of_connections)
        self.thread = threading.Thread(target=self.run_comm_port, daemon=True)
        self.thread.start()

    def run_comm_port(self):
        logging.info(f"Test server listening on port {self.port}")
        while self.is_running:
            try:
                conn, addr = self._socket.accept()
                logging.info(f"Test server accepted connection from {addr}")
                threading.Thread(target=self.handle_connection, args=(conn, addr[1])).start()
            except Exception as e:
                logging.debug(f"Error accepting connection: {e}")
                time.sleep(1)

    def handle_connection(self, conn, name):
        self.conns[name] = conn
        try:
            while True:
                message = self.generate_message()
                conn.sendall(message.encode())
                logging.debug(f"sent: {message}")
                time.sleep(.2)
        except Exception as e:
            logging.debug(f"Error handling connection: {e}")
        finally:
            conn.close()
            self.conns.pop(name)

    def close_all(self):
        self.is_running = False
        for k, v in self.conns.items():
            v.detach()

        if self._socket:
            self._socket.close()
            self._socket = None

    @staticmethod
    def generate_message():
        return "%w,1.000kg#\n"

    def send_to(self, name, msg):
        self.conns[name].sendall(msg.encode())


def start_server(host, port):
    server = SBE37Server(host, port)
    server.start_comm_port()
    return server

if __name__ == '__main__':
    start_server()

