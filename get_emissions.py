import requests
from requests.auth import HTTPBasicAuth
from os import path
import pandas as pd
from datetime import datetime, timedelta
  
today = datetime.now()
tomorrow = today + timedelta(1)
tomorrow = str(tomorrow.strftime('%Y-%m-%d'))

param = {
    'location': 'eastus',
    'windowSize': 1,
    'dataStartAt': tomorrow+'T00:40:00Z',
    'dataEndAt': tomorrow+'T10:00:00Z'
}

header = {
    'accept': 'application/json'
}
login_url = 'https://carbon-aware-api.azurewebsites.net/emissions/forecasts/current?'
get = requests.get(login_url, headers = header, params = param)
print(get.status_code,get.reason)
get = get.json()[0]
optimal = get["optimalDataPoints"]
print("optimal time period: ",optimal[0]['timestamp'])
# ["forecastData"]
df = pd.json_normalize(get["forecastData"])
df.to_csv("emission_data_test.csv", index = False)
