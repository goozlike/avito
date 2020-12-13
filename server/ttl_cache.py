import time
import fnmatch
import json

class ttl_cache():
    def __init__(self):
        self._storage = {}
        self._time = {}
        self._ttl = {}

    def hset(self, key, fields, values):
        if key not in self._storage or type(self._storage[key]) != type({}):
            self._storage[key] = {}
            self._time[key] = time.time()
            self._ttl[key] = -1
        
        for i, field in enumerate(fields):
            self._storage[key][field] = values[i]
        
        return len(fields)
    
    def hget(self, key, field):
        if key not in self._storage or type(self._storage[key]) != type({}):
            return None
        else:
            if field in self._storage[key]:
                return self._storage[key][field]
            else:
                return None
    
    def lset(self, key, ind, val):
        if key not in self._storage or type(self._storage[key]) != type([]):
            return None
        elif len(self._storage[key]) <= abs(ind):
            return None
        else:
            self._storage[key][ind] = val
            return 'OK'

    def lget(self, key, ind):
        if key not in self._storage or type(self._storage[key]) != type([]):
            return None
        elif len(self._storage[key]) <= abs(ind):
            return None
        else:
            return self._storage[key][ind]

    def set_value(self, key, value, ttl=-1):
        self._storage[key] = value
        self._time[key] = time.time()
        self._ttl[key] = int(ttl)

    def check_time(self, key):
        if key not in self._storage:
            return False
        if self._ttl[key] == -1:
            return True 
        if self._time[key] + self._ttl[key] < time.time():
            self.delete(key)
            return False
        else:
            return True
    
    def get(self, key):
        if self.check_time(key):
            return self._storage[key]
        else:
            return None

    def keys(self, pat):
        res = []
        pat = pat.replace('^', '!')
        for key in self._storage.keys():
            if self.check_time(key) and fnmatch.fnmatch(key, pat):
                res.append(key)
        if len(res) == 0:
            return None
        return res

    def delete(self, key):
        res = self._storage.pop(key, None)
        self._time.pop(key, None)
        self._ttl.pop(key, None)
        
        if res is not None:
            return 1
        else:
            return 0
        
    def save(self):
        try:
            storage_file = open('storage.json', 'w')
            json.dump(self._storage, storage_file)

            time_file = open('time.json', 'w')
            json.dump(self._time, time_file)

            ttl_file = open('ttl.json', 'w')
            json.dump(self._ttl, ttl_file)

            storage_file.close()
            time_file.close()
            ttl_file.close()
        except:
            return None

        return 'OK'

