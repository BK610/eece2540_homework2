#!/usr/bin/env python
import socket
import sys
import random
import re
import hashlib

buffMAX = 4096
numOpMAX = 100

defaultPort = 12000
secretKey="This key is secret"


def generate_secretFlag(neuid,SK):
    '''Generate a secret given a neuid and a secret key'''
    return hashlib.sha256(SK + neuid).hexdigest()


def generate_maths():
    ''' Generate functions to compute. These are generated randomly with format as n1 op n2, where  n1,n2 are random(1,1000)'''
    
    # Generate operations
    op_list = ['+', '-', '*', '/']
    num1 = random.randint(1, 1000)
    num2 = random.randint(1, 1000)
    op = random.choice(op_list)
    # Generate string
    maths = str(num1) + " " + op + " " + str(num2)
    # Generate expected solution
    if op == '+':
        sol = num1 + num2
    elif op == '-':
        sol = num1 - num2
    elif op == '*':
        sol = num1 * num2
    elif op == '/':
        sol = num1 / num2
    # Output contains the expression and expected solution
    output = maths, sol
    return output


def main(serverPort,SK):
    # Create Socket - IP/TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind Socket to IP address
    s.bind(('', serverPort))
    s.listen(5)
    while True:

        # Start accepting Client's requests
        print("Server - Ready to accept connections. Waiting...")
        conn, address = s.accept()
        print("Connection has been established | " + "IP " + address[0] + " | Port " + str(address[1]))

        # Send commands to the Client
        i = 1
        HELLO_format = "ece2540 HELLO \d*"
        r = re.compile(HELLO_format)

        data = conn.recv(buffMAX)  # Server is blocked expecting message from Client
        a = data.decode()  # Received string from Client is supposed to be encoded.
        msg = str(a)  # Actual message sent by the Client

        if r.match(msg):
            arg_array = re.split(" +", msg)
            neuid = arg_array[2]
            # Create Secret flag
            secretFlag = generate_secretFlag(neuid,SK)

            while i<100:
                # Generate expression and send it to Client
                expression, solution = generate_maths()  # Obtain expression and expected solution
                cmd = "ece2540 STATUS " + expression  # String to send to Client with Math operation
                conn.send(cmd.encode('utf-8'))  # Encode string before sending it

                # Wait until Client gets back with answer
                client_response = conn.recv(buffMAX)
                if not client_response:
                    conn.close()
                    break

                # Decode Client's solution
                client_response.decode()
                if not client_response.decode() or client_response.decode() != str(solution):
                    msg = "ece2540 ERROR - Incorrect solution. Closing socket. Please, start process over"
                    conn.send(str.encode(msg))
                    conn.close()
                    break

                # Increment number of attempts
                i = i + 1

            # The Client receives the secretFlag after completing numOpMAX operations
            if i == numOpMAX:
                print("\tSTUDENT SUCCESS!")
                print("\tNEUID {0} -> {1}").format(neuid, secretFlag)
                msg = "ece2540 BYE " + secretFlag
                conn.send(str.encode(msg))
        else:
            print("Connection terminated: message format is not correct")
            msg = "ece2540 ERROR - Expected format: ece2540 HELLO myNEUID, myNEUID particular for each student"
            conn.send(str.encode(msg))
            conn.close()

        # Close Socket connection with Client to accept new connections
        conn.close()
        print("Connection is closed")

if __name__ == '__main__':
    if len(sys.argv)>1:
        main(int(sys.argv[1]),secretKey)
    else:
        main(int(defaultPort),secretKey)
