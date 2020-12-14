Для того чтобы запустить сервер и тесты нужно выполнить следующую команду: docker-compose build && docker-compose up -d server && docker-compose run client && docker-compose down
В консоли будут выведены результаты тестирования. Сами тесты находятся в файле client/test.py


Для того чтобы локально запустить сервер нужно ввести команду python3 server/server.py, также можно по желанию указать в аргументах порт флагом -p (по умолчанию 8081), максимальное число одновременно подключенных клиентов -m (default 100) и авторизацию -a (defult 0, 1 to auth mode)
В другом окне терминала можно запустить клиент командой python3 client/client.py также можно по желанию указать в аргументах хост (-l) и порт(-p) (по умолчанию  localhost и 8081)

После этого в терминале с запущенным клиентом можно вводить команды SET, GET, DEL, KEYS, HGET, HSET, LGET, LSET синтаксис команд соответсвует соотвествующим из документации Redis (https://redis.io/commands). Только стоит отметить, что команды LGET нет в оригинальной имплементации и она устроена следующим образом: LGET key index и возвращает либо значение по этому ключу+индексу или None.

При включенной авторизации для пароли смотрятся в файле server/pass.json и там они лежат в виде словаря addr : password и как и написано в документации Redis администритор должен сам назначать пароли для клиентов. 
При подключению к серверу, который был запущен с флагом -a 1, при установлении соединения сервер отправляет клиенту сообщение SEND PASSWORD, на которое клиент должен ответить PASSWORD /..client_password../ и при совпадении этого пароля с тем, который находится в server/pass.json авторизация прошла успешно, иначе соединение сбрасывается и клиент должен будет заново попробовать подключиться. Для тестирования этой функции нужно поднять локально сервер и клиент, после чего сервер напишет что пришло соединение adr = (ip, port) нужно скопировать это значение, и поместить в файл server/pass.json пару adr : password, сохранить этот файл и ввести такой же пароль в клиенте.

Также в классе Client есть команды, которые позволяют пользоваться функциями без ввода из stdin:

SET - сохраняет по ключу значение, возможно с ttl (-1 == inf)
PARAMS:
 - key (string)
 - value (string, list, dict)
 - ttl (float seconds)
 - nx  (1, 0) only set the key if it does not already exist
 - xx (1, 0) only set the key if it already exist
 - get (1, 0) return old value
 RETURN:
 - 'OK' if success
 - value (string, list, dict) if get=1 and key exists
 - None if get=1 and key doesn't exist or nx/xx condition wasn't met

GET - по ключу получаем значение или None
PARAMS:
 - key (string)
RETURN:
 - value (string, list, dict) if key exists
 - None if key doesn't exists   

DEL - удалить значение по ключу
PARAMS:
 - keys (list) list of keys to delete
RETURN:
 - int how many keys were deleted from storage  


KEYS - возвращает список ключей удовлетворяющих паттерну
PARAMS:
 - pat (string) pattern to match keys with
RETURN:
 - keys (list) list of existing keys matched to pattern  
 
HSET - устанавливает по ключу в указанные поля указанные значения
PARAMS:
 - key (string)
 - fields (list) list of fields
 - values (list) list of values value[i] will be set in fields[i]
RETURN:
 - num of inserted values
 
HGET - возвращает значение по ключу в указанном поле или None
PARAMS:
 - key (string)
 - field (string) list of fields
RETURN:
 - value in that field   


LSET - устанавливает значение в списке доступном по данному ключу на данном индексе 
PARAMS:
 - key (string)
 - ind (int) index of list
 - value to insert in ind position of list
RETURN:
 - 'OK' if success None else   

LGET - возвращает значение в списке по ключу в данноми индексе
PARAMS:
 - key (string)
 - ind (int) index of list
RETURN:
 - value of list[ind] or None if ind out of range or key doesn't exist  
 
SAVE - сохраняет состояние БД в файлы
RETURN:
 - 'OK' if success
