import csv
from datetime import datetime
import pytz
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import time

SCOPES = ['https://www.googleapis.com/auth/calendar']
TIMEZONE = 'America/Los_Angeles'

def get_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def get_or_create_calendar(name="Class Schedule", timezone=TIMEZONE):
    service = get_service()

    calendar_list = service.calendarList().list().execute()
    for cal in calendar_list.get('items', []):
        if cal['summary'] == name:
            print(f"✅ Found existing calendar: {name}")
            return cal['id']

    calendar = {'summary': name, 'timeZone': timezone}
    created_calendar = service.calendars().insert(body=calendar).execute()
    print(f"✅ Created new calendar: {name}")
    return created_calendar['id']

def add_events_from_csv(calendar_id, filename):
    service = get_service()
    tz = pytz.timezone(TIMEZONE)
    schedule = []

    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            start_time = tz.localize(datetime.fromisoformat(row['start']))
            end_time = tz.localize(datetime.fromisoformat(row['end']))

            event = {
                'summary': row['summary'],
                'location': row['location'],
                'description': row['description'],
                'start': {'dateTime': start_time.isoformat(), 'timeZone': TIMEZONE},
                'end': {'dateTime': end_time.isoformat(), 'timeZone': TIMEZONE}
            }

            created = service.events().insert(calendarId=calendar_id, body=event).execute()
            time.sleep(1)
            event_id = created['id']
            retrieved = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

            schedule.append({
                'summary': retrieved['summary'],
                'location': retrieved.get('location', ''),
                'description': retrieved.get('description', ''),
                'start': retrieved['start']['dateTime'],
                'end': retrieved['end']['dateTime']
            })

    print("\n📅 Your Class Schedule:\n")
    for evt in schedule:
        print(f"{evt['summary']} | {evt['start']} - {evt['end']} | {evt['location']}")
        if evt['description']:
            print(f"  Description: {evt['description']}")
        print("---------------------------------------------------")

if __name__ == '__main__':
    calendar_id = get_or_create_calendar("Class Schedule")
    add_events_from_csv(calendar_id, 'schedule.csv')
