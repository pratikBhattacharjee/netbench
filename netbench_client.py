import sys
import socket
import time

def client(argv):
    # create socket and connect to server
    sockfd = None
    # TCP socket for Test 1 and Test 2
    try:
        sockfd = socket.socket()
        sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sockfd.connect((argv[1], 40740))
    except socket.error as emsg:
        print("Socket error: ", emsg)
        sys.exit(1)
    # UDP socket for Test 3
    try:
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock2.bind(sockfd.getsockname())
    except socket.error as emsg:
        print("UDP socket creation error", emsg)
    # printing out the address of the server
    print("Client has connected to server at:", (argv[1], 40740))
    # Storing the socket number for Test 3
    clientaddress = sockfd.getsockname()
    print("Client's address:", clientaddress)

    # Test 1
    print("\nStart test1 - large transfer")
    print("From server to client")
    # receive the data from the server
    remaining = 200000000
    dataRecieved = ""
    while remaining > 0:
        try:
            rmsg = sockfd.recv(1000)
        except socket.error as emsg:
            print("Error receiving data", emsg)
            sys.exit(1)
        rmsg_string = rmsg.decode('ascii')
        dataRecieved += rmsg_string
        if rmsg == b"":
            print("Connection is broken")
            sys.exit(1)
        remaining -= len(rmsg_string)
    print("Received total: 200000000 bytes")
    try:
        sockfd.sendall(b'abcde')
    except socket.error as emsg:
        print("problem sending the 5 byte message: ", emsg)
        sys.exit(1)

    # Now we want to send the data
    print("From client to server")
    # Creating a byte object of the size
    msg = "a" * 200000000
    # beginning to send the file
    datasizeremaining = 200000000
    sectionStart = 0
    start_time = time.perf_counter()
    while datasizeremaining > 0:
        # Sending 1000 bytes every time
        section = msg[sectionStart:sectionStart + 1000]
        sectionStart += 1000
        if datasizeremaining % 5000000 == 0:
            print('* ', end='')
            sys.stdout.flush()
        try:
            # Send data after encoding it
            sockfd.sendall(section.encode('ascii'))
        except socket.error as emsg:
            print("Problem sending file", emsg)
            sys.exit(1)
        datasizeremaining -= 1000
    print()

    try:
        ok = sockfd.recv(5).decode("ascii")
    except socket.error as emsg:
        print("Problem getting affirmation message: ", emsg)
    if ok != "abcde":
        sys.exit(1)
    end_time = time.perf_counter()
    print("Sent total: 200000000 bytes")
    print("Elapsed time:", "%.3f" % (end_time - start_time), 's')
    print("Throughput(from client to server):", "%.3f" % (200 * 8 / (end_time - start_time)), "Mb/s")

    # Test 2
    print("\nStart test2 - small transfer")
    print("From server to client")
    # receive the data from the server
    remaining = 10000
    dataRecieved = ""
    while remaining > 0:
        #Send 1000 byte a time
        try:
            rmsg = sockfd.recv(1000)
        except socket.error as emsg:
            print("Error receiving data", emsg)
            sys.exit(1)
        rmsg_string = rmsg.decode('ascii')
        dataRecieved += rmsg_string
        if rmsg == b"":
            print("Connection is broken")
            sys.exit(1)
        remaining -= len(rmsg_string)
    print("Received total: 10000 bytes")
    try:
        # Send 5 byte message
        sockfd.sendall(b'abcde')
    except socket.error as emsg:
        print("problem sending the 5 byte message: ", emsg)
        sys.exit(1)

    # Now we want to send the data to the server
    print("From client to server")
    # Creating a byte object of the size
    msg = "a" * 10000
    # beginning to send the file
    datasizeremaining = 10000
    sectionStart = 0
    start_time = time.perf_counter()
    while datasizeremaining > 0:
        section = msg[sectionStart:sectionStart + 1000]
        sectionStart += 1000
        try:
            sockfd.sendall(section.encode('ascii'))
        except socket.error as emsg:
            print("Problem sending file", emsg)
            sys.exit(1)
        datasizeremaining -= 1000

    ok = sockfd.recv(5).decode("ascii")
    if ok != "abcde":
        sys.exit(1)
    end_time = time.perf_counter()
    print("Sent total: 10000 bytes")
    print("Elapsed time:", "%.5f" % (end_time - start_time), 's')
    print("Throughput(from client to server):", "%.3f" % (0.01 * 8 / (end_time - start_time)), "Mb/s")

    # Test 3
    print("\nStart test3 - UDP pingpong")
    #closing the TCP socket
    sockfd.close()

    # First from the server to the client
    print("From server to client")
    for i in range(5):
        try:
            #using UDP socket created at the start of the program
            msg, senderaddress = sock2.recvfrom(5)
        except socket.error as emsg:
            print(emsg)
            sys.exit(1)
        # Check if sender address is correct
        if msg.decode('ascii') == 'a11ee':
            try:
                sock2.sendto(msg, (argv[1], 40740))
            except socket.error as emsg:
                print(emsg)
                sys.exit(1)
        else:
            sys.exit(1)
        print("* ", end='')

    # Now from the client to the server
    print("\nFrom client to server")
    msg = "a11ee".encode('ascii')
    total_time = 0
    for i in range(5):
        start_time = time.perf_counter()
        try:
            sock2.sendto(msg, (argv[1], 40740))
        except socket.error as emsg:
            print("UDP message sending error(client side)", emsg)
            sys.exit(1)

        echomsg, echoaddr = sock2.recvfrom(5)
        if echomsg.decode('ascii') != "a11ee":
            sys.exit(1)
        end_time = time.perf_counter()
        print("Reply from", echoaddr[0], ": time = ", "%.5f" % (end_time - start_time), "s")
        total_time += end_time - start_time

    print("Average RTT: %5f s" % (total_time / 5))
    print("End of all benchmarks")
    sock2.close()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        # Two arguments to run the client
        client(sys.argv)
    else:
        print("Invalid commmand line arguments -- Try Again!")
        sys.exit(1)