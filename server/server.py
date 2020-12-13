import select
import socket
import argparse
import sys
import json
from ttl_cache import ttl_cache
from transport import send, recv



class Server(object):
    
    def __init__(self, port=8081, max_clients=100, auth=0):
  
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('',port))
        self.auth = auth
        print('Listening to port', port, '...')
        self.server.listen(max_clients)

        #main storage
        self.storage = ttl_cache()

    
    def check_password(self, addr, pas):
        password_file = open('pass.json', 'r')
        passwords = json.load(password_file)
        if str(addr) in passwords and passwords[str(addr)] == pas:
            return True
        else:
            return False


    #main loop to serve requests
    def serve(self):

        inputs = [self.server]

        while True:
            try:
                inputready, outputready, exceptready = select.select(inputs, [], [])
            except (select.error):
                break

            for s in inputready:
                #adding new clients
                if s == self.server:
                    #handle the server socket
                    client, address = self.server.accept()
                    print('got connection from', address)
                    if self.auth:
                        send(client, 'SEND PASSWORD')
                        res = recv(client)
                        if not self.check_password(address, res):
                            send(client, "BAD PASSWORD")
                            client.close()
                            continue
                        else:
                            send(client, "OK")
                        
                    inputs.append(client)

                #handle clients sockets
                else:
                    try:
                        req = recv(s)
                        if req:
                            
                            #handle SET request
                            if req['type'] == 'SET':
                                
                                key = req['key']
                                value = req['value']
                                if 'ttl' in req:
                                    ttl = int(req['ttl'])
                                else:
                                    ttl = -1
                                
                                old_v = self.storage.get(key)
                                res = {}
                                res = 'OK'
                                if 'xx' in req:
                                    if old_v is not None:
                                        self.storage.set_value(key, value, ttl)
                                    else:
                                        res = None
                                        
                                elif 'nx' in req:
                                    if old_v is None and 'get' not in req:
                                        self.storage.set_value(key, value, ttl)
                                    else:
                                        res = None
                                else:
                                    self.storage.set_value(key, value, ttl)
                                if res:
                                    if 'get' in req:
                                        res = old_v
                                    
                                send(s, res)

                            if req['type'] == 'HSET':
                                key = req['key']
                                fields = req['fields']
                                values = req['values']

                                res = self.storage.hset(key, fields, values)
                                send(s, res)

                            if req['type'] == 'HGET':
                                key = req['key']
                                field = req['field']

                                res = self.storage.hget(key, field)
                                send(s, res)

                            if req['type'] == 'LSET':
                                key = req['key']
                                ind = int(req['ind'])
                                val = req['value']

                                res = self.storage.lset(key, ind, val)
                                send(s, res)
                            
                            if req['type'] == 'LGET':
                                key = req['key']
                                ind = int(req['ind'])

                                res = self.storage.lget(key, ind)
                                send(s, res)

                            if req['type'] == 'SAVE':
                                res = self.storage.save()
                                send(s, res)

                               

                            #hadle GET requests
                            elif req['type'] == 'GET':
    
                                key = req['key']
                                value = self.storage.get(key)                        
                                send(s, value)

                            #handle DEL request
                            elif req['type'] == 'DEL':
                                if len(req) != 2:
                                    send(s, 'Wrong request')
                                    continue
                                keys = req['keys']
                                res = 0
                                if keys is not None:
                                    for key in keys:
                                        res += self.storage.delete(key)
                                msg = res
                                send(s, msg)
                                
                            #handle KEYS request
                            if req['type'] == 'KEYS':
                                if 'pat' in req:
                                    pat = req['pat']
                                else:
                                    pat = '*'

                                keys = self.storage.keys(pat)
                                res = keys
                                send(s, res)


                        else:
                            print('chatserver: %d hung up' % s.fileno())
                            s.close()
                            inputs.remove(s)
                                
                    except (socket.error):
                        inputs.remove(s)
        self.server.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest='port', help='server port', default=8081)
    parser.add_argument('-a', dest='auth', help='auth', default=0)
    parser.add_argument('-m', dest='m', help='max clients', default=100)
    args = parser.parse_args()

    Server(port=int(args.port), auth=args.auth, max_clients=int(args.m)).serve()