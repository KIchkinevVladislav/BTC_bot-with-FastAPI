import requests
from config import api_url

res = requests.get(f'{api_url}/users')
print(res.json())
