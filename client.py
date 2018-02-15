#!/usr/bin/env python
import sys
import argparse
import socket
import operator

# Create the socket using the given port and hostname
def socket_setup(port, hostname):
    host = socket.gethostbyname(hostname)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        s.connect((host, port))
        return s
    except:
        sys.exit("Failed to create connection at host {} and port {}."
            .format(hostname, port))

if __name__ == "__main__":
    # Hostname, port, and NUID information
    hostname = 'zeta.coe.neu.edu'
    p = 50000
    nuid = '001735965'

    # Create socket to connect to appropriate hostname and port
    s = socket_setup(p, hostname)
    
    # 1. Send HELLO message
    s.send(("ece2540 HELLO {}".format(nuid)).encode('utf-8'))
    
    # 2. Receive first message and split the input (by spaces) to parse into
    #      the math problem
    data = s.recv(256)
    splitdata = data.split()
    
    # Map string representations to actual math operators, including proper
    #   floor division
    ops = {"+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.floordiv}
    
    # 3. Continue processing math problems until a message is received that is
    #      not a STATUS message
    while((splitdata[0] == b"ece2540") & (splitdata[1] == b"STATUS")):
        # Convert byte operator to str, and byte numbers to ints
        op = splitdata[3].decode()
        num1 = int(splitdata[2])
        num2 = int(splitdata[4])
        
        # Get the answer to the math problem
        ans = ops[op](num1, num2)
        
        # 4. Send answer to the server
        s.send(("{}".format(ans)).encode('utf-8'))
        
        # 5. Receive next message and split to parse
        data = s.recv(256)
        splitdata = data.split()

    # 6. Check that the message is the BYE message, and output the secret flag
    if(splitdata[1] == b"BYE"):
        print(splitdata[2].decode())
        
        s.close()
        
        sys.exit(0)
    
    # 7. If a message is received in an incorrect format, error:
    s.close()
    sys.exit("Received incorrect message. Ending communication. Message:\n{}".format(data))
