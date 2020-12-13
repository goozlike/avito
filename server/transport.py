
import socket
import sys
import select
import json



def send(s, msg):
    msg = json.dumps(msg)
    s.send(msg.encode())

def recv(s):
    msg = s.recv(1024)
    if msg is None:
        return msg
    try:
        msg = json.loads(msg.decode())
    except:
        return None
    return msg