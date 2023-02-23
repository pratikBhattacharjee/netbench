# Name : Pratik Bhattacharjee, UID: 3035767425
# Development Platform: Pycharm EDU
# Python version: 3.8

import sys
import socket
import time


def server(argv):
    # assigned port 40740 from the list
    port = 40740

    # Creating a server socket with TCP
    socketServer = socket.socket()
    socketServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        # binding the socket with the assigned port
        socketServer.bind(('', port))
    except socket.error as errmsg:
        print("Socket bind error: ", errmsg)
        sys.exit(1)
    socketServer.listen()
    print("Server is ready and listening at: ", socketServer.getsockname())
    try:
        conn, addr = socketServer.accept()
    except socket.error as emsg:
        print("Socket accept error: ", emsg)
        sys.exit(1)
    # print out client socket connection address
    print("A client has connected and it is at: ", addr)

    # Test 1
    print("\nStart Test1 - Large Transfer")
    print("From server to client")
    # Creating a byte object of the size
    msg = "a" * 200000000
    # beginning to send the file
    datasizeremaining = 200000000
    sectionStart = 0
    start_time = time.perf_counter()
    while datasizeremaining > 0:
        # Sending 1000 bytes at a time
        section = msg[sectionStart:sectionStart + 1000]
        sectionStart += 1000
        # Setting up progress bar
        if datasizeremaining % 5000000 == 0:
            print('* ', end='')
            sys.stdout.flush()
        try:
            conn.sendall(section.encode('ascii'))
        except socket.error as emsg:
            print("Problem sending file", emsg)
            sys.exit(1)
        datasizeremaining -= 1000
    print()

    # recieve the socket message
    try:
        ok = conn.recv(5).decode("ascii")
    except socket.error as emsg:
        print("Message recieve error", emsg)
    if ok != "abcde":
        sys.exit(1)
    end_time = time.perf_counter()
    print("Sent total: 200000000 bytes")
    print("Elapsed time:", "%.3f" % (end_time - start_time), 's')
    print("Throughput(from server to client):", "%.3f" % (200 * 8 / (end_time - start_time)), "Mb/s")

    # Now we will receive data from the client
    print("From client to server")
    # receive the data from the server
    remaining = 200000000
    dataRecieved = ""
    while remaining > 0:
        try:
            #recieve data from the client
            rmsg = conn.recv(1000)
        except socket.error as emsg:
            print("Error receiving data", emsg)
            sys.exit(1)
        #convert the byte recieved into string
        rmsg_string = rmsg.decode('ascii')
        dataRecieved += rmsg_string
        #check if the msg is empty
        if rmsg == b"":
            print("Connection is broken")
            sys.exit(1)
        remaining -= len(rmsg_string)
    print("Received total: 200000000 bytes")
    #Send the confirmation 5 byte msg
    try:
        conn.sendall(b'abcde')
    except socket.error as emsg:
        print("problem sending the 5 byte message: ", emsg)
        sys.exit(1)

    # Test 2
    print("\nStart test2 - small transfer\nFrom server to client")
    # Creating a byte object of the size 10000
    msg = "a" * 10000
    # beginning to send the file
    datasizeremaining = 10000
    sectionStart = 0
    start_time = time.perf_counter()
    while datasizeremaining > 0:
        section = msg[sectionStart:sectionStart + 1000]
        sectionStart += 1000
        if datasizeremaining % 1000 == 0:
            print('* ', end='')
        try:
            #Send message after encoding it
            conn.sendall(section.encode('ascii'))
        except socket.error as emsg:
            print("Problem sending file", emsg)
            sys.exit(1)
        datasizeremaining -= 1000
    print()

    ok = conn.recv(5).decode("ascii")
    if ok != "abcde":
        sys.exit(1)
    end_time = time.perf_counter()
    print("Sent total: 10000 bytes")
    print("Elapsed time:", "%.5f" % (end_time - start_time), 's')
    print("Throughput(from server to client):", "%.3f" % (0.01 * 8 / (end_time - start_time)), "Mb/s")

    # Now we will receive data from the client
    print("From client to server")
    # receive the data from the server
    remaining = 10000
    dataRecieved = ""
    while remaining > 0:
        try:
            rmsg = conn.recv(1000)
        except socket.error as emsg:
            print("Error receiving data", emsg)
            sys.exit(1)
        # Decode message after receiving
        rmsg_string = rmsg.decode('ascii')
        dataRecieved += rmsg_string
        if rmsg == b"":
            print("Connection is broken")
            sys.exit(1)
        remaining -= len(rmsg_string)
    print("Received total: 10000 bytes")
    #Send confirmation 5 byte message
    try:
        conn.sendall(b'abcde')
    except socket.error as emsg:
        print("problem sending the 5 byte message: ", emsg)
        sys.exit(1)

    # close the sockets using TCP
    socketServer.close()
    conn.close()

    # Test 3
    print("\nStart test3 - UDP pingpong")
    # Getting server ready for UDP transmission
    # creating UDP socket
    socketServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socketServer.bind(('', port))

    # Starting to send data
    print("From server to client")
    # distinct message for checking
    msg = "a11ee".encode('ascii')
    total_time = 0
    for i in range(5):
        start_time = time.perf_counter()
        try:
            socketServer.sendto(msg, addr)
        except socket.error as emsg:
            print("Problem sending UDP message (server side)", emsg)
            sys.exit(1)
        try:
            echomsg, echoaddr = socketServer.recvfrom(5)
        except socket.error as emsg:
            print("Error recieving msg: ", emsg)
        end_time = time.perf_counter()
        print("Reply from", echoaddr[0], ": time = ", "%.5f" % (end_time - start_time), "s")
        total_time += end_time - start_time

    print("Average RTT: %5f" % (total_time / 5))

    # Starting to recieve data
    print("From client to server")
    # Send and receive data 5 times
    for i in range(5):
        # Receive data
        try:
            msg, senderAddress = socketServer.recvfrom(5)
        except socket.error as emsg:
            print(emsg)
            sys.exit(1)
        # Check if sender address is correct
        if msg.decode('ascii') != "a11ee":
            sys.exit(1)
        # Send data
        try:
            socketServer.sendto(msg, addr)
        except socket.error as emsg:
            print(emsg)
            sys.exit(1)
        print('* ', end='')
    print("\nEnd of all benchmarks.")





if __name__ == '__main__':
    if len(sys.argv) == 1:
        # One arguments to run the server
        server(sys.argv)
    else:
        print("Invalid commmand line arguments -- Try Again!")
        sys.exit(1)
