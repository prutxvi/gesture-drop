import os
import requests

text_to_send = "Hello Mobile!"
res = requests.post("http://127.0.0.1:5000/save", json={"text": text_to_send})
print("Status:", res.status_code)
