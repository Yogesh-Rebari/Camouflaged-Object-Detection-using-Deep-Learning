import requests
r = requests.get('http://127.0.0.1:5000/predict')
print('Status:', r.status_code)
print(r.text[:1000])
with open('predict_resp.html','w',encoding='utf8') as f:
    f.write(r.text)
print('Saved to predict_resp.html')
