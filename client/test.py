
from client import Client
import time
import pytest



def test_set_get():
    client = Client()
    #check str storing
    res = client.set('key', 'value')
    assert(res == 'OK')
    res = client.get('key')
    assert(res == 'value')
    assert(res == 'value')

    #check list storing
    res = client.set('key', ['1', '2'])
    assert(res == 'OK')
    res = client.get('key')
    assert(res == ['1', '2'])
    assert(res[1] == '2')

    #check dict storing
    res = client.set('key', {'a' : ['1', '2'], 'b' : 'c'})
    assert(res == 'OK')
    res = client.get('key')
    assert(res == {'a' : ['1', '2'], 'b' : 'c'})
    assert(res['b'] == 'c')

    #check get from not existing key
    res = client.get('aaa')
    assert(res is None)

    #check set with get flag
    res = client.set('key', 'a', get=1)
    assert(res == {'a' : ['1', '2'], 'b' : 'c'})

    res = client.set('key1', 'a', get=1)
    assert(res is None)

    #check nx flag
    res = client.set('key', 'b', get=1, nx=1)
    assert(res is None)
    res = client.get('key')
    assert(res == 'a')

    res = client.set('key', 'b', nx=1)
    assert(res is None)
    res = client.get('key')
    assert(res == 'a')

    res = client.set('key2', 'b', nx=1)
    assert(res == 'OK')
    res = client.get('key2')
    assert(res == 'b')

    #check xx flag
    res = client.set('key', 'b', get=1, xx=1)
    assert(res == 'a')
    res = client.get('key')
    assert(res == 'b')

    res = client.set('key', 'a', xx=1)
    assert(res == 'OK')
    res = client.get('key')
    assert(res == 'a')

    res = client.set('key3', 'a', xx=1, get=1)
    assert(res is None)

    #delete everything
    res = client.keys('*')
    del_res = client.delete(res)
    assert(len(res) == del_res)
    
    print('GET and SET test: OK')

def test_ttl():
    client = Client()

    #set key with ttl
    res = client.set('key', '1', ttl=3)
    assert(res == 'OK')
    #check it setted
    res = client.get('key')
    assert(res == '1')

    time.sleep(3)
    #check it expired
    res = client.get('key')
    assert(res == None)


    print('TTL test: OK')

def test_keys():
    client = Client()

    #delete all keys
    keys = client.keys('*')
    res = client.delete(keys)
    if keys:
        assert(res == len(keys))
    else:
        assert(res == 0)

    #add new keys
    keys = ['hello', 'hallo', 'heeeello', 'hbllo', 'hllo', 'age', 'lastname']
    for key in keys:
        res = client.set(key, 'a')
        assert(res == 'OK')
    
    #checking patterns
    keys = client.keys('h?llo')
    assert(set(keys) == set(['hello', 'hallo', 'hbllo']))

    keys = client.keys('h*llo')
    assert(set(keys) == set(['hello', 'hallo', 'heeeello', 'hbllo', 'hllo']))

    keys = client.keys('h[ae]llo')
    assert(set(keys) == set(['hello', 'hallo']))

    keys = client.keys('h[^e]llo')
    assert(set(keys) == set(['hbllo', 'hallo']))

    keys = client.keys('h[a-b]llo')
    assert(set(keys) == set(['hbllo', 'hallo']))

    keys = client.keys('a??')
    assert(set(keys) == set(['age']))

    keys = client.keys('*name*')
    assert(set(keys) == set(['lastname']))

    keys = client.keys('*name*')
    assert(set(keys) == set(['lastname']))

    keys = client.keys('*')
    assert(set(keys) == set(['hello', 'hallo', 'heeeello', 'hbllo', 'hllo', 'age', 'lastname']))

    #delete everything
    res = client.keys('*')
    del_res = client.delete(res)
    assert(len(res) == del_res)

    print('KEYS test: OK')


def test_delete():
    client = Client()

    keys = ['1', '2', '3']
    for key in keys:
        res = client.set(key, 'a')
        assert(res == 'OK')

    
    res = client.delete(['1', '2', '4'])
    assert(res == 2)

    keys = client.keys('*')
    assert(keys == ['3'])

    del_res = client.delete(keys)
    assert(len(keys) == del_res)

    print('DEL test: OK')

def test_hget_hset():
    client = Client()

    res = client.set('key', {'a' : 'b'})
    assert(res == 'OK')

    res = client.hget('key', 'a')
    assert(res == 'b')

    res = client.hset('key', ['a', 'd'], ['t', 'p'])
    assert(res == 2)

    res = client.hget('key', 'a')
    assert(res == 't')

    res = client.set('nh', '1')
    assert(res == 'OK')
    res = client.hget('nh', '1')
    assert(res is None)

    res = client.hset('nh', ['f1', 'f2', 'f3'], ['v1', 'v2', 'v3'])
    assert(res == 3)

    res = client.keys('*')
    assert(set(res) == set(['nh', 'key']))
    print('HGET HSET OK')

def test_lset_lget():
    client = Client()

    res = client.set('k', '1')
    assert(res == 'OK')

    assert(client.lget('k', 0) is None)
    assert(client.lset('k', 0, 'a') is None)
    assert(client.set('k', ['1', '2', '3']) == 'OK')
    assert(client.lget('k', 1) == '2')
    assert(client.lget('k', 5) is None)
    assert(client.lset('k', 1, '5') == 'OK')
    assert(client.lget('k', 1) == '5')

    print('LSET LGET OK')

