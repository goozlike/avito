
import socket
import sys
import select
import json
import argparse
from transport import send, recv

class Client(object):

    def __init__(self, host='localhost', port=8081):
        # Quit flag
        self.flag = False

        self.port = int(port)
        self.host = host
        print(self.host, self.port)
        # Connect to server at port
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((self.host, self.port))
            print('Connected to Redis server %d' % self.port)
            
        except socket.error:
            print('Could not connect to Redis server %d' % self.port)
            sys.exit(1)
    
    #CLIENT API 

    #SET
    #PARAMS:
    # - key (string)
    # - value (string, list, dict)
    # - ttl (float seconds)
    # - nx  (1, 0) only set the key if it does not already exist
    # - xx (1, 0) only set the key if it already exist
    # - get (1, 0) return old value
    # RETURN:
    # - 'OK' if success
    # - value (string, list, dict) if get=1 and key exists
    # - None if get=1 and key doesn't exist or nx/xx condition wasn't met
    def set(self, key, value, ttl=-1, nx=0, xx=0, get=0):
        #making request for server
        req = {}
        req['type'] = 'SET'
        req['key'] = key
        req['value'] = value
        req['ttl'] = ttl

        if nx:
            req['nx'] = 1
        
        if xx:
            req['xx'] = 1

        if nx + xx > 1:
            print('Bad request')
            return -1
        
        if get:
            req['get'] = 1

        #send request
        send(self.server, req)
        #return response from server
        return recv(self.server)
    
    #GET
    #PARAMS:
    # - key (string)
    #RETURN:
    # - value (string, list, dict) if key exists
    # - None if key doesn't exists
    def get(self, key):
        #make request
        req = {}
        req['type'] = 'GET'
        req['key'] = key
        #send to server
        send(self.server, req)
        #return server's response
        return recv(self.server)
    
    #DEL
    #PARAMS:
    # - keys (list) list of keys to delete
    #RETURN:
    # - int how many keys were deleted from storage
    def delete(self, keys):
        req = {}
        req['type'] = 'DEL'
        req['keys'] = keys
        send(self.server, req)
        return recv(self.server)

    #KEYS
    #PARAMS:
    # - pat (string) pattern to match keys with
    #RETURN:
    # - keys (list) list of existing keys matched to pattern
    def keys(self, pat):
        req = {}
        req['type'] = 'KEYS'
        req['pat'] = pat
        send(self.server, req)
        return recv(self.server)

    #HSET
    #PARAMS:
    # - key (string)
    # - fields (list) list of fields
    # - values (list) list of values value[i] will be set in fields[i]
    #RETURN:
    # - num of inserted values
    def hset(self, key, fields, values):
        req = {}
        req['type'] = 'HSET'
        req['key'] = key
        req['fields'] = fields
        req['values'] = values
        send(self.server, req)
        return recv(self.server)



    #HGET
    #PARAMS:
    # - key (string)
    # - field (string) list of fields
    #RETURN:
    # - value in that field
    def hget(self, key, field):
        req = {}
        req['type'] = 'HGET'
        req['key'] = key
        req['field'] = field
        send(self.server, req)
        return recv(self.server)


    
    #LSET
    #PARAMS:
    # - key (string)
    # - ind (int) index of list
    # - value to insert in ind position of list
    #RETURN:
    # - 'OK' if success None else    
    def lset(self, key, ind, val):
        req = {}
        req['type'] = 'LSET'
        req['key'] = key
        req['ind'] = ind
        req['value'] = val
        send(self.server, req)
        return recv(self.server)


    #LGET
    #PARAMS:
    # - key (string)
    # - ind (int) index of list
    #RETURN:
    # - value of list[ind] or None if ind out of range or key doesn't exist
    def lget(self, key, ind):
        req = {}
        req['type'] = 'LGET'
        req['key'] = key
        req['ind'] = ind
        send(self.server, req)
        return recv(self.server)

    #SAVE
    #RETURN:
    # - 'OK' if success
    def save(self):
        req = {}
        req['type'] = 'SAVE'
        send(self.server, req)
        return recv(self.server)

    
    #SEND PASSWORD
    def send_pas(self, pas):
        send(self.server, pas)


    #client loop for serving from stdin
    def run(self):
        while not self.flag:
            sys.stdout.flush()

            try:
                # Wait for input from stdin & socket
                inputready, outputready, exceptrdy = select.select([sys.stdin, self.server], [],[])

                for s in inputready:

                    if s == self.server:

                        data = recv(self.server)
                        if not data:
                            print('Shutting down')
                            self.flag = True
                            break

                        else:
                            print(data)

                    #serve client requests from terminal
                    elif s == sys.stdin:
                        res = None
                        try:
                            data = s.readline()[:-1].split(' ')
                            

                            #to store list and dict from terminal u should use spaces
                            #SET list example:
                            # - SET key ["a","b","c"]
                            #SET dict example:
                            # - SET key {"a":["g","f"],"d":"p"}
                            if data[0] == 'SET':
                                key = data[1]
                                value = data[2]
                                ttl = -1
                                nx = 0
                                xx = 0
                                get = 0

                                if 'EX' in data[3:] and len(data[3:]) > data[3:].index('EX') + 1:
                                    ttl = float(data[3:][data[3:].index('EX') + 1])
                                if 'PX' in data[3:] and len(data[3:]) > data[3:].index('PX') + 1:
                                    if ttl != -1:
                                        ttl += float(data[3:][data[3:].index('PX') + 1]) / 1000
                                    else:
                                        ttl = float(data[3:][data[3:].index('PX') + 1]) / 1000

                                if 'NX' in data[3:]:
                                    nx = 1
                                
                                if 'XX' in data[3:]:
                                    xx = 1

                                if 'GET' in data[3:]:
                                    get = 1
                                
                                try:
                                    value = json.loads(value)
                                except:
                                    pass
                                
                                res = self.set(key, value, ttl, nx, xx, get)
                                  
                            elif data[0] == 'GET':
                                res = self.get(data[1])

                            elif data[0] == 'KEYS':
                                res = self.keys(data[1])
                            
                            elif data[0] == 'DEL':
                                res = self.delete(data[1:])

                            elif data[0] == 'HSET':
                                key = data[1]
                                fields = []
                                values = []
                                for i, tok in enumerate(data[2:]):
                                    if i % 2 == 0:
                                        fields.append(tok)
                                    else:
                                        try:
                                            tok = json.loads(tok)
                                        except:
                                            pass
                                        values.append(tok)
                                if len(fields) != len(values):
                                    print('Bad request')
                                    continue

                                res = self.hset(key, fields, values)
                            
                            elif data[0] == 'HGET':
                                key = data[1]
                                field = data[2]

                                res = self.hget(key, field)

                            elif data[0] == 'LSET':
                                key = data[1]
                                ind = data[2]
                                val = data[3]

                                try:
                                    val = json.loads(val)
                                except:
                                    pass

                                res = self.lset(key, ind, val)
                            
                            elif data[0] == 'LGET':
                                key = data[1]
                                ind = data[2]
                                res = self.lget(key, ind)
                            
                            elif data[0] == 'SAVE':
                                res = self.save()
                            
                            #To answer SEND PASSWORD question
                            #client need to send PASSWORD ****** request
                            elif data[0] == 'PASSWORD':
                                self.send_pas(data[1])
                                continue

                            else:
                                print('Bad request type')
                                continue
                                
                            print(res)


                        except:
                            print('Bad request')

            except KeyboardInterrupt:
                print('Interruption')
                self.server.close()
                break


            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest='port', help='server port', default=8081)
    parser.add_argument('-l', dest='host', help='host', default='localhost')
    args = parser.parse_args()
    print(args)
    client = Client(host=args.host, port=int(args.port))
    client.run()