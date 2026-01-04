"""
Google Calendar Service Module
Handles OAuth authentication and calendar operations
"""
import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Use absolute paths based on script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(SCRIPT_DIR, 'token.json')

def get_calendar_service():
    """
    Gets an authenticated Google Calendar service.
    Handles OAuth flow if needed.
    """
    creds = None
    
    # Check if we have a saved token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If no valid credentials, do the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_FILE}. "
                    "Please download it from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for next time
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    service = build('calendar', 'v3', credentials=creds)
    return service


def list_upcoming_events(max_results=10):
    """
    Lists the next upcoming events in the user's calendar.
    Returns a formatted string.
    """
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "No upcoming events found."
        
        result = "Upcoming events:\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            # Parse and format the date
            if 'T' in start:
                dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                formatted_date = dt.strftime('%A %d/%m %H:%M')
            else:
                formatted_date = start
            result += f"- {event['summary']} ({formatted_date})\n"
        
        return result
        
    except HttpError as error:
        return f"Error accessing calendar: {error}"
    except Exception as e:
        return f"Error: {e}"


def create_calendar_event(title, day, time, duration_hours=1, description=""):
    """
    Creates a calendar event.
    
    Args:
        title: Event title
        day: Day of the week (e.g., "Monday")
        time: Time in HH:MM format (e.g., "10:00")
        duration_hours: Duration in hours
        description: Optional description
    
    Returns:
        Success or error message
    """
    try:
        service = get_calendar_service()
        
        # Convert day name to next occurrence
        days = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2,
            'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6,
            'lunes': 0, 'martes': 1, 'miércoles': 2, 'miercoles': 2,
            'jueves': 3, 'viernes': 4, 'sábado': 5, 'sabado': 5, 'domingo': 6
        }
        
        today = datetime.date.today()
        target_day = days.get(day.lower(), 0)
        days_ahead = target_day - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        
        event_date = today + datetime.timedelta(days=days_ahead)
        
        # Parse time
        hour, minute = map(int, time.split(':'))
        start_datetime = datetime.datetime(
            event_date.year, event_date.month, event_date.day,
            hour, minute
        )
        end_datetime = start_datetime + datetime.timedelta(hours=duration_hours)
        
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Europe/Madrid',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Europe/Madrid',
            },
        }
        
        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {title} on {event_date.strftime('%A %d/%m')} at {time}"
        
    except HttpError as error:
        return f"Error creating event: {error}"
    except Exception as e:
        return f"Error: {e}"


def delete_event_by_title(title_contains):
    """
    Deletes an event that contains the given text in its title.
    
    Args:
        title_contains: Text to search for in event titles
    
    Returns:
        Success or error message
    """
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        for event in events:
            if title_contains.lower() in event.get('summary', '').lower():
                service.events().delete(
                    calendarId='primary',
                    eventId=event['id']
                ).execute()
                return f"Deleted event: {event['summary']}"
        
        return f"No event found containing '{title_contains}'"
        
    except HttpError as error:
        return f"Error deleting event: {error}"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    # Test the calendar service
    print("Testing Google Calendar connection...")
    print(list_upcoming_events(5))

