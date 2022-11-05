from __future__ import print_function

import base64
from email.message import EmailMessage
import os.path
import pickle 

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from os import path
import pandas as pd
import datetime
from datetime import timedelta
import json
import uuid
import get_emissions


data = get_emissions.emissions_json()

for address in data['email']:
    start = 0
    end = 0
    event_param = {
        'location': '200 W, NY, NY',
        'start': {
            'timeZone': 'America/New_York'
        },
        'end': {
            'timeZone': 'America/New_York'
        },
        'attendees': [
            address
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 1},
                {'method': 'popup', 'minutes': 1}
            ]
        },
    }

    count = 0 
    for i in range(len(data['time'])):
        start = data['time'][i]
        topic = data['prompt'][i]

        end = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S+00:00')
        end = end + timedelta(minutes = 30)
        end = end.replace(tzinfo=datetime.timezone.utc).isoformat()

        event_param["start"]["dateTime"] = start
        event_param["end"]["dateTime"] = end
        event_param['description'] = 'Cut your carbon footprints by taking action on ['+topic +'],post on the app to see how your friends are tackling this prompt!'
        event_param['summary'] = 'Carboff: '+ topic 
        print(event_param['attendees'])

        SCOPES = ['https://www.googleapis.com/auth/calendar.events']
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        if count >= 0:
            try:
                event_id = str(uuid.uuid1().int)
                event_param['id'] = event_id
                service = build('calendar', 'v3', credentials=creds)
                event = service.events().insert(calendarId='primary', body=event_param).execute()
                print("[CARBOFF]: Calendar event added!")

            except HttpError as error:
                print(F'An error occurred: {error}')
                send_message = None

        else: 
            event = service.events().get(calendarId='primary', eventId = event_id).execute()
            event['summary'] = 'Appointment at Somewhere'
            updated_event = service.events().update(calendarId='primary', body=event_param, eventId = event_id).execute()
        
        count += 1
