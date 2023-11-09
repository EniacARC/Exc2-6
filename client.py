"""
Author: Yonathan Chapal
Program name: Exc 2.6
Description: a basic client for the commands server
Date: 8/11/2023
"""
import socket
import os
import struct
import logging

# define network constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 17207
Q_LEN = 1
MAX_PACKET = 1024
COMMAND_LEN = 4
HEADER_LEN = 2
STOP_SERVER_CONNECTION = "EXIT"
STRUCT_PACK_SIGN = 'H'
ERR_INPUT = "Command must be 4 characters long!"

# define log constants
LOG_FORMAT = '%(levelname)s | %(asctime)s | %(processName)s | %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/loggerClient.log'


def send(client_socket, data):
    """
    sends the data to the server. makes sure all the data was sent successfully

    :param: client_socket
    :type: network socket
    :param: data
    :type: str
    :return: if the message was sent successfully: 0 for yes, 1 for no
    :rtype: int
    """
    try:
        # send the message
        sent = 0
        while sent < len(data):
            sent += client_socket.send(data[sent:].encode())

        # signal the message was sent successfully
        return 0
    except socket.error as err:
        logging.error(f"error while trying to send message from client: {err}")
        # signal something went wrong
        return 1


def receive(client_socket):
    """
    receives a response from the server, and it's length. makes sure all the message was received.

    :param: client_socket
    :type: network socket
    :return: the server's response, ('' for unsuccessful response)
    :rtype: str
    """
    try:
        # receive the response length
        net_len = b''
        while len(net_len) < HEADER_LEN:
            net_packet = client_socket.recv(HEADER_LEN - len(net_len))
            if net_packet == '':
                return ''
            net_len += net_packet

        packet_len = socket.ntohs(struct.unpack(STRUCT_PACK_SIGN, net_len)[0])
        # receive the actual response
        packet = ''
        while len(packet) < packet_len:
            buf = client_socket.recv(packet_len - len(packet)).decode()
            if buf == '':
                return ''
            packet += buf
        return packet

    except socket.error as err:
        logging.error(f"error while receiving data from server: {err}")
        return ''


def main():
    # define an ipv4 tcp socket and listen for an incoming connection
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        logging.info(f"trying to connect to server at ({SERVER_IP}, {SERVER_PORT})")
        client.connect((SERVER_IP, SERVER_PORT))
        logging.info("client established connection with server")
        want_to_exit = False
        while not want_to_exit:
            command = input().upper()
            logging.debug(f"user entered: {command}")

            if len(command) == COMMAND_LEN:
                if send(client, command) != 1:
                    res = receive(client)

                    if res != '':
                        print(res)
                        logging.debug(f"the server responded with {res}")
                    else:
                        print("error while receiving response from server!")
                        want_to_exit = True

                else:
                    print("error! couldn't send data to server!")
                    want_to_exit = True

                if command == STOP_SERVER_CONNECTION:
                    want_to_exit = True
            else:
                print(ERR_INPUT)

    except socket.error as err:
        logging.error(f"error in communication with server: {err}")

    except KeyboardInterrupt:
        logging.warning("user has stopped the program using keyboard interrupt!")
        print("stopping client.py")

        # sending the EXIT command to the server
        # note: even if I didn't add this part the server would still close the socket,
        # and everything would work as expected. It's just more correct to do it this way.
        if send(client, STOP_SERVER_CONNECTION) != 1:
            res = receive(client)
            if res != '':
                print(res)
                logging.debug(f"the server responded with {res}")

    finally:
        client.close()
        print("client disconnected")
        logging.info("terminated client")


if __name__ == '__main__':
    # make sure we have a logging directory and configure the logging
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    main()
