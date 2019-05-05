import json

import requests

res = requests.post('http://localhost:8080/tasks', data=json.dumps({'url': 'http://www.google.pl'}))
print(res.status_code)
print(res.text)
print(res.headers)

