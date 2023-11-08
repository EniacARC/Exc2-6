"""
Author: Yonathan Chapal
Program name: Exc 2.6
Description: a basic commands server
Date: 8/11/2023
"""
import socket
import random
import struct
from datetime import datetime
import os
import logging

# define network constants
LISTEN_IP = '0.0.0.0'
LISTEN_PORT = 17207
Q_LEN = 1
MAX_PACKET = 4
SHORT_SIZE = 2
STRUCT_PACK_SIGN = 'H'
SERVER_NAME = "Yonathan's Awesome Server"
WELCOME_MSG = "Hello, Welcome to My Server. You can use the following commands: |NAME|TIME|NAME|EXIT|"
DISCONNECT_MSG = "Thank You For Using Our Services! Goodbye."
ERROR_INPUT_MSG = "Error! Please enter a valid command: |NAME|TIME|RAND|EXIT|"

# define log constants
LOG_FORMAT = '%(levelname)s | %(asctime)s | %(processName)s | %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/loggerServer.log'


# define server functions
def get_time():
    """
    gets the current time in Hour:Minute:Second format

    :return: the current time
    :rtype: str
    """
    current_time = datetime.now()
    return current_time.strftime("%H:%M:%S")


def get_name():
    """
    gets the server's name

    :return: the SERVER_NAME constant
    :rtype: str
    """
    return SERVER_NAME


def get_rand_int():
    """
    create a random number between 1-10 (including both ends)
    :return: the number that was generated in the range of 1-10
    :rtype: str
    """
    return str(random.randint(1, 10))


# send and receive funcs for the server that follow the established protocol
def receive(comm_socket):
    """
    receives a command from the client that is 4 bytes and makes sure all the message was received
    :param: comm_socket
    :type: socket
    :return: the command from the client
    :rtype: str
    """
    # according to the protocol established the client command should be bytes long.

    # makes sure all 4 bytes were sent
    try:
        pac = ''
        while len(pac) < MAX_PACKET:
            buf = comm_socket.recv(MAX_PACKET - len(pac)).decode()
            if buf == '':
                return ''
            pac += buf
        return pac.upper()
    except socket.error as err:
        logging.error(f"error while trying to receive message from client: {err}")
    finally:
        return ''


def send(comm_socket, data):
    data_len_net = socket.htons(len(data))
    sent = 0
    try:
        # send message length
        while sent < SHORT_SIZE:
            sent += comm_socket.send(struct.pack(STRUCT_PACK_SIGN, data_len_net)[sent:])

        # send the message
        sent = 0
        while sent < len(data):
            sent += comm_socket.send(data[sent:].encode())

        # signal the message was sent successful
        return 0
    except socket.error as err:
        logging.error(f"error while trying to send message: {err}")
        # signal somthing went wrong
        return 1


def main():
    print("test")
    """
    the main function; responsible for running the server code
    """
    # define an ipv4 tcp socket and listen for an incoming connection
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        serv.bind((LISTEN_IP, LISTEN_PORT))
        serv.listen(Q_LEN)
        logging.debug(f"server is listening on port {LISTEN_PORT}")
        while True:
            # accept connection
            conn, addr = serv.accept()
            logging.info("connection established")
            disconnect = False

            while not disconnect:
                try:
                    # check if req was successful, terminate connection if not
                    req = receive(conn)
                    if req != '':
                        logging.info(f"client entered: {req}")
                        # execute the command as per the client input.
                        # checks the message was sent successfully, terminate connection if not
                        if req == "TIME":
                            curr_time = get_time()
                            logging.debug(f"sending client: {curr_time}")
                            if send(conn, curr_time) == 1:
                                break

                        elif req == "NAME":
                            name = get_name()
                            logging.debug(f"sending client: {name}")
                            if send(conn, name) == 1:
                                break

                        elif req == "RAND":
                            num = get_rand_int()
                            logging.debug(f"sending client: {num}")
                            if send(conn, num) == 1:
                                break
                        elif req == "EXIT":
                            logging.info("user wants to disconnect")
                            break

                        else:
                            logging.info("command is not recognised by the server!")
                            logging.debug(f"sending client: {ERROR_INPUT_MSG}")
                            if send(conn, ERROR_INPUT_MSG) == 1:
                                break

                except socket.error as err:
                    logging.error(f"error in communication with client: {err}")

                finally:
                    conn.close()
                    logging.info("terminated connection with client socket")

    except socket.error as err:
        logging.error(f"error while opening server socket: {err}")

    finally:
        serv.close()


if __name__ == "__main__":
    # make sure we have a logging directory and configure the logging
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    main()
