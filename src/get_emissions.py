import requests
from requests.auth import HTTPBasicAuth
from os import path
import pandas as pd
import datetime
from datetime import timedelta
import json
import user_prefs

def emissions_json():
    #defining time window for carbon emissions api
    now = datetime.datetime.now(datetime.timezone.utc)+ timedelta(hours = 1)
    now = now.replace(minute=0, second=0, microsecond=0)
    end = now + timedelta(hours = 23)
    now = now.isoformat()
    end = end.isoformat()


    #setting information for api call
    param = {
        'location': 'eastus',
        'windowSize': 1,
        'dataStartAt': now,
        'dataEndAt': end

    }

    header = {
        'accept': 'application/json'
    }
    login_url = 'https://carbon-aware-api.azurewebsites.net/emissions/forecasts/current?'

    #call api 
    get = requests.get(login_url, headers = header, params = param)
    print(get.status_code,get.reason)

    #convert to accesible pandas dataframe
    get = get.json()[0]
    optimal = get["optimalDataPoints"]
    # print("optimal time period: ",optimal[0]['timestamp'])
    # ["forecastData"]
    df = pd.json_normalize(get["forecastData"])

    #adding information about time for further filter
    df["hour"] = df['timestamp'].apply(lambda x: x[11:13])
    df['within_hours'] = df["hour"].apply(lambda x: "yes" if (int(x) > 12 or int(x) <4) else "no")
    df = df[df["within_hours"]=="yes"]

    #finding the peak time for carbon emissions
    data = {}
    data['time'] = []
    window = 4
    start = 0 

    for i in range(len(df)//(12*window)):
        end = start + 12*window
        data['time'].append(max(df['timestamp'].iloc[start:end,]))
        start = end+1 

    emails = []
    users = user_prefs.get_users()
    for user in users:
        emails.append(user['email'])
    data['email'] = emails
    data['prompt'] = ['Transportation','Computer Tabs', 'Electricity']
    # print(data)
    return data

