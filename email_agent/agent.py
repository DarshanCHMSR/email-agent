from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.adk import Agent
from google.adk.tools import FunctionTool
from google.adk.models import Gemini
import os
import base64
from email.mime.text import MIMEText
from dotenv import load_dotenv
import re
from typing import Optional

# Load environment variables from .env file
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive"
]

def get_gmail_service():
    creds = None
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    token_path = os.path.join(parent_dir, "token.json")
    credentials_path = os.path.join(parent_dir, "credentials.json")
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def get_calendar_service():
    """Initialize Google Calendar service with the same credentials as Gmail"""
    creds = None
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    token_path = os.path.join(parent_dir, "token.json")
    credentials_path = os.path.join(parent_dir, "credentials.json")
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def get_drive_service():
    """Initialize Google Drive service with the same credentials as Gmail and Calendar"""
    creds = None
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    token_path = os.path.join(parent_dir, "token.json")
    credentials_path = os.path.join(parent_dir, "credentials.json")
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return build("drive", "v3", credentials=creds)


# Gmail, Calendar, and Drive services will be initialized when needed
gmail_service = None
calendar_service = None
drive_service = None

def ensure_gmail_service():
    """Lazy initialization of Gmail service"""
    global gmail_service
    if gmail_service is None:
        gmail_service = get_gmail_service()
    return gmail_service


def ensure_calendar_service():
    """Lazy initialization of Calendar service"""
    global calendar_service
    if calendar_service is None:
        calendar_service = get_calendar_service()
    return calendar_service


def ensure_drive_service():
    """Lazy initialization of Drive service"""
    global drive_service
    if drive_service is None:
        drive_service = get_drive_service()
    return drive_service


def read_emails(query: str, num_emails: int):
    """Reads the most recent emails from the user's inbox based on a query.

    Args:
        query (str): The search query to filter emails (e.g., "from:sender@example.com subject:meeting").
        num_emails (int): The maximum number of emails to read. Should be between 1 and 50.

    Returns:
        str: A summary of the emails found, or a message indicating no emails were found.
    """
    # Ensure num_emails is within reasonable bounds
    if num_emails <= 0:
        num_emails = 5
    elif num_emails > 50:
        num_emails = 50
    try:
        service = ensure_gmail_service()
        results = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=num_emails)
            .execute()
        )
        messages = results.get("messages", [])

        if not messages:
            return "No emails found matching your query."

        email_summary = []
        for message in messages:
            msg = (
                service.users()
                .messages()
                .get(userId="me", id=message["id"])
                .execute()
            )
            headers = msg["payload"]["headers"]
            subject = next(filter(lambda h: h["name"] == "Subject", headers), {}).get(
                "value", "No Subject"
            )
            sender = next(filter(lambda h: h["name"] == "From", headers), {}).get(
                "value", "Unknown Sender"
            )
            snippet = msg.get("snippet", "No snippet available.")
            email_summary.append(
                f"From: {sender}\nSubject: {subject}\nSnippet: {snippet}\n---"
            )
        return "\n".join(email_summary)
    except HttpError as error:
        return f"An error occurred: {error}"


def send_email(to: str, subject: str, body: str):
    """Sends an email to the specified recipient.

    Args:
        to (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body content of the email.

    Returns:
        str: A message indicating whether the email was sent successfully or if an error occurred.
    """
    try:
        service = ensure_gmail_service()
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": raw_message}
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        return f"Email sent successfully! Message Id: {send_message['id']}"
    except HttpError as error:
        return f"An error occurred: {error}"


def delete_email(message_id: str):
    """Deletes an email by its message ID.

    Args:
        message_id (str): The ID of the email to delete.

    Returns:
        str: A message indicating whether the email was deleted successfully or if an error occurred.
    """
    try:
        service = ensure_gmail_service()
        service.users().messages().delete(userId="me", id=message_id).execute()
        return f"Email with ID {message_id} deleted successfully."
    except HttpError as error:
        return f"An error occurred: {error}"


def create_draft(to: str, subject: str, body: str):
    """Creates a draft email.

    Args:
        to (str): The recipient's email address.
        subject (str): The subject of the draft email.
        body (str): The body content of the draft email.

    Returns:
        str: A message indicating whether the draft was created successfully or if an error occurred.
    """
    try:
        service = ensure_gmail_service()
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": raw_message}
        draft = (
            service.users()
            .drafts()
            .create(userId="me", body={"message": create_message})
            .execute()
        )
        return f"Draft created successfully! Draft Id: {draft['id']}"
    except HttpError as error:
        return f"An error occurred: {error}"


# ==================== GOOGLE CALENDAR FUNCTIONS ====================

def create_calendar_event(summary: str, start_datetime: str, end_datetime: str, description: str = "", location: str = ""):
    """Creates a new event in Google Calendar.

    Args:
        summary (str): The title/summary of the event.
        start_datetime (str): Start time in ISO format (e.g., "2024-01-15T10:00:00-07:00").
        end_datetime (str): End time in ISO format (e.g., "2024-01-15T11:00:00-07:00").
        description (str, optional): Description of the event.
        location (str, optional): Location of the event.

    Returns:
        str: A message indicating whether the event was created successfully or if an error occurred.
    """
    try:
        service = ensure_calendar_service()
        
        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_datetime,
                'timeZone': 'America/Los_Angeles',  # You can make this configurable
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'America/Los_Angeles',
            },
        }
        
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        return f"Calendar event created successfully! Event ID: {event_result.get('id')}\nEvent Link: {event_result.get('htmlLink')}"
    except HttpError as error:
        return f"An error occurred while creating calendar event: {error}"


def read_calendar_events(max_results: int = 10, time_min: str = "", time_max: str = ""):
    """Reads upcoming events from Google Calendar.

    Args:
        max_results (int): Maximum number of events to retrieve (default: 10).
        time_min (str, optional): Lower bound for events in ISO format.
        time_max (str, optional): Upper bound for events in ISO format.

    Returns:
        str: A summary of the upcoming events or a message if no events found.
    """
    try:
        service = ensure_calendar_service()
        
        # If no time_min specified, use current time
        if not time_min:
            from datetime import datetime
            time_min = datetime.utcnow().isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max if time_max else None,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "No upcoming events found."
        
        event_summary = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title')
            location = event.get('location', 'No Location')
            description = event.get('description', 'No Description')
            
            event_summary.append(
                f"Event: {summary}\nStart: {start}\nLocation: {location}\nDescription: {description}\n---"
            )
        
        return "\n".join(event_summary)
    except HttpError as error:
        return f"An error occurred while reading calendar events: {error}"


def delete_calendar_event(event_id: str):
    """Deletes a calendar event by its ID.

    Args:
        event_id (str): The ID of the calendar event to delete.

    Returns:
        str: A message indicating whether the event was deleted successfully or if an error occurred.
    """
    try:
        service = ensure_calendar_service()
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return f"Calendar event with ID {event_id} deleted successfully."
    except HttpError as error:
        return f"An error occurred while deleting calendar event: {error}"


def update_calendar_event(event_id: str, summary: str = "", start_datetime: str = "", end_datetime: str = "", description: str = "", location: str = ""):
    """Updates an existing calendar event.

    Args:
        event_id (str): The ID of the event to update.
        summary (str, optional): New title/summary of the event.
        start_datetime (str, optional): New start time in ISO format.
        end_datetime (str, optional): New end time in ISO format.
        description (str, optional): New description of the event.
        location (str, optional): New location of the event.

    Returns:
        str: A message indicating whether the event was updated successfully or if an error occurred.
    """
    try:
        service = ensure_calendar_service()
        
        # First, retrieve the existing event
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # Update only the provided fields
        if summary:
            event['summary'] = summary
        if location:
            event['location'] = location
        if description:
            event['description'] = description
        if start_datetime:
            event['start']['dateTime'] = start_datetime
        if end_datetime:
            event['end']['dateTime'] = end_datetime
        
        updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        return f"Calendar event updated successfully! Event ID: {updated_event.get('id')}"
    except HttpError as error:
        return f"An error occurred while updating calendar event: {error}"


# Google Drive Functions
def list_drive_files(query: str = "", max_results: int = 10):
    """Lists files from Google Drive based on a search query.

    Args:
        query (str): Search query to filter files (e.g., "type:pdf" or "name:report").
        max_results (int): Maximum number of files to return (1-100).

    Returns:
        str: A summary of the files found, or a message indicating no files were found.
    """
    # Ensure max_results is within reasonable bounds
    if max_results <= 0:
        max_results = 10
    elif max_results > 100:
        max_results = 100
    
    try:
        service = ensure_drive_service()
        
        # Build search query
        search_query = query if query else ""
        
        results = service.files().list(
            q=search_query,
            pageSize=max_results,
            fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, webViewLink, parents)"
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            return f"No files found matching query: '{query}'" if query else "No files found in your Drive."
        
        file_list = []
        for file in files:
            name = file.get('name', 'Unknown')
            file_id = file.get('id', 'Unknown')
            mime_type = file.get('mimeType', 'Unknown')
            size = file.get('size', 'Unknown size')
            modified = file.get('modifiedTime', 'Unknown date')
            web_link = file.get('webViewLink', 'No link')
            
            # Convert size to readable format if available
            if size != 'Unknown size' and size.isdigit():
                size_bytes = int(size)
                if size_bytes < 1024:
                    size_str = f"{size_bytes} bytes"
                elif size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes / 1024:.1f} KB"
                elif size_bytes < 1024 * 1024 * 1024:
                    size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                else:
                    size_str = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
            else:
                size_str = "Unknown size"
            
            file_list.append(
                f"📄 Name: {name}\n"
                f"   ID: {file_id}\n"
                f"   Type: {mime_type}\n"
                f"   Size: {size_str}\n"
                f"   Modified: {modified}\n"
                f"   Link: {web_link}\n---"
            )
        
        return f"Found {len(files)} files:\n\n" + "\n".join(file_list)
    
    except HttpError as error:
        return f"An error occurred while listing Drive files: {error}"


def create_drive_folder(folder_name: str, parent_folder_id: Optional[str] = None):
    """Creates a new folder in Google Drive.

    Args:
        folder_name (str): Name of the folder to create.
        parent_folder_id (str): ID of the parent folder (optional, defaults to root).

    Returns:
        str: Success message with folder ID and link, or error message.
    """
    try:
        service = ensure_drive_service()
        
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        # Add parent folder if specified
        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]
        
        folder = service.files().create(
            body=folder_metadata,
            fields='id, webViewLink'
        ).execute()
        
        folder_id = folder.get('id')
        web_link = folder.get('webViewLink')
        
        return f"Folder '{folder_name}' created successfully!\nFolder ID: {folder_id}\nLink: {web_link}"
    
    except HttpError as error:
        return f"An error occurred while creating Drive folder: {error}"


def delete_drive_file(file_id: str):
    """Deletes a file or folder from Google Drive.

    Args:
        file_id (str): The ID of the file or folder to delete.

    Returns:
        str: Success or error message.
    """
    try:
        service = ensure_drive_service()
        
        # Get file info first for confirmation
        file_info = service.files().get(fileId=file_id, fields='name, mimeType').execute()
        file_name = file_info.get('name', 'Unknown')
        file_type = "folder" if file_info.get('mimeType') == 'application/vnd.google-apps.folder' else "file"
        
        # Delete the file
        service.files().delete(fileId=file_id).execute()
        
        return f"Successfully deleted {file_type} '{file_name}' (ID: {file_id})"
    
    except HttpError as error:
        if error.resp.status == 404:
            return f"File with ID '{file_id}' not found. It may have already been deleted."
        return f"An error occurred while deleting Drive file: {error}"


def share_drive_file(file_id: str, email: str, role: str = "reader"):
    """Shares a Google Drive file with a specific user.

    Args:
        file_id (str): The ID of the file to share.
        email (str): Email address of the user to share with.
        role (str): Permission level - "reader", "writer", or "owner".

    Returns:
        str: Success or error message.
    """
    try:
        service = ensure_drive_service()
        
        # Validate role
        valid_roles = ["reader", "writer", "owner"]
        if role not in valid_roles:
            return f"Invalid role '{role}'. Valid roles are: {', '.join(valid_roles)}"
        
        # Get file info
        file_info = service.files().get(fileId=file_id, fields='name, webViewLink').execute()
        file_name = file_info.get('name', 'Unknown')
        web_link = file_info.get('webViewLink', 'No link')
        
        # Create permission
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
        
        service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id',
            sendNotificationEmail=True
        ).execute()
        
        return f"Successfully shared '{file_name}' with {email} as {role}.\nFile link: {web_link}"
    
    except HttpError as error:
        if error.resp.status == 404:
            return f"File with ID '{file_id}' not found."
        return f"An error occurred while sharing Drive file: {error}"


def analyze_intent(user_input: str):
    """Analyzes user input to determine the intended operation.
    Uses enhanced local pattern matching to minimize API calls during server overload.
    
    Args:
        user_input (str): The user's request or query.
        
    Returns:
        str: The identified intent ('read', 'send', 'delete', 'draft', 'calendar_create', 'calendar_read', 'calendar_delete', 'calendar_update', 'drive_list', 'drive_create', 'drive_delete', 'drive_share', or 'general').
    """
    # Convert to lowercase for easier matching
    input_lower = user_input.lower().strip()
    
    # Enhanced patterns to catch more cases locally (reduces API calls)
    
    # Drive operations patterns
    drive_list_patterns = [
        r'\b(list|show|find|search|get|view|display)\b.*\b(files|drive|documents|folder|folders)\b',
        r'\bmy\b.*\b(drive|files|documents|folders)\b',
        r'\b(what|show).*\b(files|documents)\b.*\b(in|on)\b.*\bdrive\b',
        r'\bshow.*\bdrive\b.*\b(files|content)\b',
        r'\b(browse|explore)\b.*\bdrive\b',
        r'\b(recent|latest)\b.*\b(files|documents)\b.*\bdrive\b'
    ]
    
    drive_create_patterns = [
        r'\b(create|make|new)\b.*\b(folder|directory)\b',
        r'\b(add|create)\b.*\b(folder|directory)\b.*\b(to|in)\b.*\bdrive\b',
        r'\bmake.*\b(new|a)\b.*\bfolder\b',
        r'\bcreate.*\bfolder\b.*\b(named|called)\b',
        r'\bnew\b.*\b(folder|directory)\b.*\bdrive\b'
    ]
    
    drive_delete_patterns = [
        r'\b(delete|remove|trash)\b.*\b(file|folder|document)\b',
        r'\bdelete\b.*\bfrom\b.*\bdrive\b',
        r'\bremove\b.*\b(file|folder|document)\b.*\bdrive\b',
        r'\btrash\b.*\b(file|folder)\b',
        r'\b(clean|clear)\b.*\bdrive\b'
    ]
    
    drive_share_patterns = [
        r'\b(share|grant|give)\b.*\b(access|permission)\b',
        r'\bshare\b.*\b(file|folder|document)\b.*\bwith\b',
        r'\b(give|grant)\b.*\b(access|permission)\b.*\bto\b',
        r'\bshare\b.*\bdrive\b.*\bfile\b',
        r'\bmake.*\b(public|shared|accessible)\b'
    ]
    
    # Calendar operations patterns
    calendar_create_patterns = [
        r'\b(create|add|schedule|book|set)\b.*\b(event|meeting|appointment|calendar)\b',
        r'\b(schedule|book|set up)\b.*\b(meeting|appointment|call|event)\b',
        r'\b(add|create)\b.*\b(to|in)\b.*\b(calendar|schedule)\b',
        r'\b(new|create)\b.*\b(calendar|event|appointment|meeting)\b',
        r'\bmake.*\b(appointment|meeting|event)\b',
        r'\bbook.*\b(meeting|appointment|time|slot)\b'
    ]
    
    calendar_read_patterns = [
        r'\b(show|list|get|check|see|view|display)\b.*\b(events|calendar|schedule|appointments|meetings)\b',
        r'\b(what|when).*\b(next|upcoming|today|tomorrow|week)\b.*\b(events|meetings|appointments)\b',
        r'\bmy\b.*\b(calendar|schedule|events|meetings|appointments)\b',
        r'\b(upcoming|next|today|tomorrow)\b.*\b(events|meetings|appointments)\b',
        r'\bcheck.*\b(calendar|schedule|agenda)\b',
        r'\bwhat.*\b(meetings|events|appointments)\b.*\b(do i have|are there|today|tomorrow)\b'
    ]
    
    calendar_delete_patterns = [
        r'\b(delete|remove|cancel)\b.*\b(event|meeting|appointment)\b',
        r'\bcancel.*\b(meeting|appointment|event|calendar)\b',
        r'\bremove.*\bfrom.*\bcalendar\b',
        r'\bdelete.*\b(calendar|event|meeting|appointment)\b'
    ]
    
    calendar_update_patterns = [
        r'\b(update|modify|change|edit|reschedule)\b.*\b(event|meeting|appointment)\b',
        r'\breschedule.*\b(meeting|appointment|event)\b',
        r'\bchange.*\b(time|date)\b.*\b(meeting|appointment|event)\b',
        r'\bmove.*\b(meeting|appointment|event)\b',
        r'\bedit.*\b(event|meeting|appointment|calendar)\b',
        r'\breschedule.*\b(the|my)\b.*\b(meeting|event|appointment)\b.*\b(to|for)\b'
    ]
    
    # Email operations patterns (existing)
    read_patterns = [
        r'\b(read|show|get|fetch|find|search|list|check|display|view|see|browse)\b.*\b(email|message|mail|inbox)\b',
        r'\b(inbox|unread|recent|latest|new|messages|emails)\b',
        r'\bfrom\b.*@.*\.(com|org|net|edu|gov)',
        r'\bsubject\b.*:',
        r'\bhow many\b.*\bemail',
        r'\bshow.*\b(from|last|week|month|today|recent)',
        r'\bcheck.*\b(inbox|mail|email)',
        r'\b(count|number).*\b(email|message)',
        r'\blist.*\b(email|message|mail)'
    ]
    
    send_patterns = [
        r'\b(send|compose|write)\b.*\b(email|message|mail)\b',
        r'\b(send|email)\b.*\b(to|@)\b',
        r'\bcompose\b.*\b(message|email|mail)\b',
        r'\bemail\b.*\bto\b.*@.*\.(com|org|net|edu|gov)',
        r'\bwrite.*\bemail\b.*\b(about|to|regarding)',
        r'\bsend.*\b(report|document|file)\b.*\bto\b'
    ]
    
    delete_patterns = [
        r'\b(delete|remove|trash|clear)\b.*\b(email|message|mail)\b',
        r'\bdelete\b.*\bmessage\b',
        r'\bremove\b.*\bfrom\b.*\binbox\b',
        r'\btrash\b.*\b(old|spam|promotional)\b',
        r'\bclear\b.*\b(inbox|spam|junk)\b',
        r'\bremove.*\b(spam|promotional|junk)\b.*\b(email|message)',
        r'\bremove.*\b(the|all)\b.*\b(spam|promotional|old)\b',
        r'\bdelete.*\b(all|the)\b.*\b(spam|promotional|junk)\b.*\bemail',
        r'\bdelete.*\bspam\b.*\bemail'
    ]
    
    draft_patterns = [
        r'\b(draft|save)\b.*\b(email|message|mail)\b',
        r'\bcreate\b.*\bdraft\b',
        r'\bsave\b.*\b(message|email|mail)\b.*\bdraft\b',
        r'\bdraft\b.*\b(email|message)\b.*\bto\b',
        r'\bsave.*\bas.*\bdraft\b',
        r'\bdraft.*\b(an|a)\b.*\bemail\b.*\bto\b'
    ]
    
    # Quick keyword checks first (faster than regex)
    # Drive checks first
    if any(word in input_lower for word in ["share", "grant", "give"]) and any(word in input_lower for word in ["access", "permission", "with", "to"]):
        return "drive_share"
    
    if any(word in input_lower for word in ["list", "show", "find", "browse"]) and any(word in input_lower for word in ["files", "drive", "documents", "folder"]):
        return "drive_list"
    
    if any(word in input_lower for word in ["create", "make", "new"]) and any(word in input_lower for word in ["folder", "directory"]):
        return "drive_create"
    
    # Check for drive delete (be careful not to conflict with email delete)
    if any(word in input_lower for word in ["delete", "remove", "trash"]) and any(word in input_lower for word in ["file", "folder", "document", "drive"]):
        return "drive_delete"
    
    # Calendar checks - reschedule should be checked first since it's specific
    if "reschedule" in input_lower and any(word in input_lower for word in ["meeting", "event", "appointment", "the meeting", "my meeting"]):
        return "calendar_update"
    
    if any(word in input_lower for word in ["schedule", "create", "add", "book"]) and any(word in input_lower for word in ["meeting", "event", "appointment", "calendar"]):
        return "calendar_create"
    
    # Special case for "what meetings do I have" type queries
    if "what" in input_lower and any(word in input_lower for word in ["meetings", "events", "appointments"]) and any(phrase in input_lower for phrase in ["do i have", "are there", "today", "tomorrow"]):
        return "calendar_read"
    
    if any(word in input_lower for word in ["show", "list", "check", "upcoming", "next"]) and any(word in input_lower for word in ["events", "meetings", "calendar", "appointments", "schedule"]):
        return "calendar_read"
    
    if any(word in input_lower for word in ["cancel", "delete", "remove"]) and any(word in input_lower for word in ["meeting", "event", "appointment"]):
        return "calendar_delete"
    
    if any(word in input_lower for word in ["update", "change", "modify", "edit"]) and any(word in input_lower for word in ["meeting", "event", "appointment"]):
        return "calendar_update"
    
    # Email checks (existing)
    # Special case for the failing query
    if "can you delete" in input_lower and "mail" in input_lower:
        return "delete"
    
    # Simple keyword checks for common cases
    if any(word in input_lower for word in ["delete", "remove", "trash"]) and any(word in input_lower for word in ["email", "mail", "message"]):
        return "delete"
    
    if any(word in input_lower for word in ["show", "list", "read", "check"]) and any(word in input_lower for word in ["email", "mail", "inbox", "message"]):
        return "read"
    
    if "draft" in input_lower:
        return "draft"
    
    if any(word in input_lower for word in ["send", "compose", "write"]) and ("@" in input_lower or "to" in input_lower):
        return "send"
    
    # Fallback to regex patterns for complex cases
    # Drive patterns first (since they're new and should take precedence for drive-related queries)
    for pattern in drive_list_patterns:
        if re.search(pattern, input_lower):
            return "drive_list"
    
    for pattern in drive_create_patterns:
        if re.search(pattern, input_lower):
            return "drive_create"
    
    for pattern in drive_delete_patterns:
        if re.search(pattern, input_lower):
            return "drive_delete"
    
    for pattern in drive_share_patterns:
        if re.search(pattern, input_lower):
            return "drive_share"
    
    # Calendar patterns
    for pattern in calendar_create_patterns:
        if re.search(pattern, input_lower):
            return "calendar_create"
    
    for pattern in calendar_read_patterns:
        if re.search(pattern, input_lower):
            return "calendar_read"
    
    for pattern in calendar_delete_patterns:
        if re.search(pattern, input_lower):
            return "calendar_delete"
    
    for pattern in calendar_update_patterns:
        if re.search(pattern, input_lower):
            return "calendar_update"
    
    # Email patterns (existing)
    for pattern in read_patterns:
        if re.search(pattern, input_lower):
            return "read"
    
    for pattern in delete_patterns:
        if re.search(pattern, input_lower):
            return "delete"
    
    for pattern in draft_patterns:
        if re.search(pattern, input_lower):
            return "draft"
    
    for pattern in send_patterns:
        if re.search(pattern, input_lower):
            return "send"
    
    # Default to general if no specific pattern matches
    return "general"


# Create FunctionTool instances for each function
read_emails_tool = FunctionTool(read_emails)
send_email_tool = FunctionTool(send_email)
delete_email_tool = FunctionTool(delete_email)
create_draft_tool = FunctionTool(create_draft)
analyze_intent_tool = FunctionTool(analyze_intent)

# Calendar function tools
create_calendar_event_tool = FunctionTool(create_calendar_event)
read_calendar_events_tool = FunctionTool(read_calendar_events)
delete_calendar_event_tool = FunctionTool(delete_calendar_event)
update_calendar_event_tool = FunctionTool(update_calendar_event)

# Drive function tools
list_drive_files_tool = FunctionTool(list_drive_files)
create_drive_folder_tool = FunctionTool(create_drive_folder)
delete_drive_file_tool = FunctionTool(delete_drive_file)
share_drive_file_tool = FunctionTool(share_drive_file)

# Create the Gemini model instance with API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key or api_key == "your-api-key-here":
    raise ValueError(
        "Please set your Google AI API key in the .env file. "
        "Get your API key from: https://aistudio.google.com/app/apikey"
    )

# Get model name from environment with smart fallback
preferred_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# List of models to try in order of preference (most stable first)
model_candidates = [
    preferred_model,
    "gemini-1.5-flash",  # Try older stable version first
    "gemini-1.5-flash",  # Stable versioned model
    "gemini-1.5-pro",        # Pro model (more capacity)
    "gemini-1.5-flash",      # Latest (might be overloaded)
]

# Remove duplicates while preserving order
seen = set()
model_candidates = [x for x in model_candidates if not (x in seen or seen.add(x))]

print(f"🤖 Trying models in order: {model_candidates}")

gemini_model = None
for model_name in model_candidates:
    try:
        print(f"🔄 Attempting to initialize {model_name}...")
        gemini_model = Gemini(
            api_key=api_key,
            # Add generation config for better reliability and reduced API calls
            generation_config={
                "temperature": 0.1,  # Lower temperature for more consistent responses
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,  # Reduced to minimize API load
                # Add retry configuration
                "candidate_count": 1,  # Only generate one candidate to reduce load
            }
        )
        # CRITICAL: Override the default model after creation
        gemini_model.model = model_name
        print(f"✅ Successfully initialized {model_name}")
        print(f"🎯 Model will use reduced token limit to minimize API load")
        break
    except Exception as e:
        error_msg = str(e).lower()
        if "503" in error_msg or "overloaded" in error_msg:
            print(f"⚠️ {model_name} is overloaded, trying next model...")
        elif "404" in error_msg or "not found" in error_msg:
            print(f"⚠️ {model_name} not available in this API version, trying next model...")
        else:
            print(f"❌ Failed to initialize {model_name}: {e}")
        continue

if gemini_model is None:
    raise RuntimeError("❌ Failed to initialize any Gemini model. Check your API key and network connection.")

# Create specialized agents for each email operation
read_agent = Agent(
    name="email_reader",
    description="Specialized agent for reading and searching emails. Handles queries about finding, listing, and retrieving email content from Gmail.",
    model=gemini_model,
    tools=[read_emails_tool]
)

send_agent = Agent(
    name="email_sender", 
    description="Specialized agent for sending emails. Handles composing and sending new email messages through Gmail.",
    model=gemini_model,
    tools=[send_email_tool]
)

delete_agent = Agent(
    name="email_deleter",
    description="Specialized agent for deleting emails. Handles removal of specific email messages from Gmail.",
    model=gemini_model,
    tools=[delete_email_tool]
)

draft_agent = Agent(
    name="email_drafter",
    description="Specialized agent for creating email drafts. Handles saving email messages as drafts in Gmail.",
    model=gemini_model,
    tools=[create_draft_tool]
)

# Create specialized calendar agents
calendar_create_agent = Agent(
    name="calendar_creator",
    description="Specialized agent for creating calendar events. Handles scheduling meetings, appointments, and events in Google Calendar.",
    model=gemini_model,
    tools=[create_calendar_event_tool]
)

calendar_read_agent = Agent(
    name="calendar_reader",
    description="Specialized agent for reading calendar events. Handles viewing, listing, and checking upcoming events and meetings from Google Calendar.",
    model=gemini_model,
    tools=[read_calendar_events_tool]
)

calendar_delete_agent = Agent(
    name="calendar_deleter",
    description="Specialized agent for deleting calendar events. Handles removal and cancellation of events and meetings in Google Calendar.",
    model=gemini_model,
    tools=[delete_calendar_event_tool]
)

calendar_update_agent = Agent(
    name="calendar_updater",
    description="Specialized agent for updating calendar events. Handles modification, rescheduling, and editing of existing events in Google Calendar.",
    model=gemini_model,
    tools=[update_calendar_event_tool]
)

# Create specialized drive agents
drive_list_agent = Agent(
    name="drive_lister",
    description="Specialized agent for listing and searching Google Drive files. Handles viewing, finding, and browsing files and folders in Google Drive.",
    model=gemini_model,
    tools=[list_drive_files_tool]
)

drive_create_agent = Agent(
    name="drive_creator",
    description="Specialized agent for creating folders in Google Drive. Handles making new folders and directories in Google Drive.",
    model=gemini_model,
    tools=[create_drive_folder_tool]
)

drive_delete_agent = Agent(
    name="drive_deleter",
    description="Specialized agent for deleting files and folders from Google Drive. Handles removal and trashing of Drive items.",
    model=gemini_model,
    tools=[delete_drive_file_tool]
)

drive_share_agent = Agent(
    name="drive_sharer",
    description="Specialized agent for sharing Google Drive files and folders. Handles granting access permissions to users.",
    model=gemini_model,
    tools=[share_drive_file_tool]
)

def route_email_request(user_input: str):
    """Routes the user request to the appropriate function based on intent analysis.
    
    Args:
        user_input (str): The user's request or query.
        
    Returns:
        str: A message indicating which function would be called for this request.
    """
    intent = analyze_intent(user_input)
    
    # Email routing
    if intent == 'read':
        return f"🎯 Intent: READ - This request would use the read_emails function to search and retrieve emails. Request: '{user_input}'"
    elif intent == 'send':
        return f"🎯 Intent: SEND - This request would use the send_email function to compose and send an email. Request: '{user_input}'"
    elif intent == 'delete':
        return f"🎯 Intent: DELETE - This request would use the delete_email function to remove emails. Request: '{user_input}'"
    elif intent == 'draft':
        return f"🎯 Intent: DRAFT - This request would use the create_draft function to save an email draft. Request: '{user_input}'"
    
    # Calendar routing
    elif intent == 'calendar_create':
        return f"📅 Intent: CALENDAR CREATE - This request would use the create_calendar_event function to schedule a new event. Request: '{user_input}'"
    elif intent == 'calendar_read':
        return f"📅 Intent: CALENDAR READ - This request would use the read_calendar_events function to view calendar events. Request: '{user_input}'"
    elif intent == 'calendar_delete':
        return f"📅 Intent: CALENDAR DELETE - This request would use the delete_calendar_event function to cancel an event. Request: '{user_input}'"
    elif intent == 'calendar_update':
        return f"📅 Intent: CALENDAR UPDATE - This request would use the update_calendar_event function to modify an event. Request: '{user_input}'"
    
    # Drive routing
    elif intent == 'drive_list':
        return f"💾 Intent: DRIVE LIST - This request would use the list_drive_files function to view Drive files. Request: '{user_input}'"
    elif intent == 'drive_create':
        return f"💾 Intent: DRIVE CREATE - This request would use the create_drive_folder function to make a new folder. Request: '{user_input}'"
    elif intent == 'drive_delete':
        return f"💾 Intent: DRIVE DELETE - This request would use the delete_drive_file function to remove a Drive file. Request: '{user_input}'"
    elif intent == 'drive_share':
        return f"💾 Intent: DRIVE SHARE - This request would use the share_drive_file function to share a Drive file. Request: '{user_input}'"
    
    else:
        return f"🎯 Intent: GENERAL - This is a general query. I can help you with emails (reading, sending, deleting, drafts), calendar (creating, viewing, updating, deleting events), and Drive (listing files, creating folders, deleting files, sharing files). Request: '{user_input}'"

# Create routing tool
route_email_tool = FunctionTool(route_email_request)

# Create a smart handler that covers both email and calendar requests
def smart_email_calendar_drive_handler(user_input: str):
    """Handles email, calendar, and drive requests by analyzing intent and providing appropriate guidance.
    
    Args:
        user_input (str): The user's request or query.
        
    Returns:
        str: Response with guidance on how to handle the request.
    """
    intent = analyze_intent(user_input)
    
    # Email intents
    if intent == 'read':
        return f"📧 I understand you want to read/search emails. To help you with '{user_input}', I would use the read_emails function. Please provide:\n1. Search query (e.g., 'from:sender@example.com' or 'subject:meeting')\n2. Number of emails to retrieve (1-50)\n\nExample: read_emails('from:john@example.com', 10)"
    elif intent == 'send':
        return f"📤 I understand you want to send an email. To help you with '{user_input}', I would use the send_email function. Please provide:\n1. Recipient email address\n2. Subject line\n3. Email body content\n\nExample: send_email('recipient@example.com', 'Meeting Reminder', 'Don't forget about our meeting tomorrow.')"
    elif intent == 'delete':
        return f"🗑️ I understand you want to delete emails. To help you with '{user_input}', I would use the delete_email function. Please provide:\n1. The message ID of the email to delete\n\nNote: You can find message IDs by first reading emails with read_emails function."
    elif intent == 'draft':
        return f"📝 I understand you want to create a draft. To help you with '{user_input}', I would use the create_draft function. Please provide:\n1. Recipient email address\n2. Subject line\n3. Email body content\n\nExample: create_draft('recipient@example.com', 'Draft Subject', 'Draft content here.')"
    
    # Calendar intents
    elif intent == 'calendar_create':
        return f"📅 I understand you want to create a calendar event. To help you with '{user_input}', I would use the create_calendar_event function. Please provide:\n1. Event title/summary\n2. Start date and time (ISO format: 2024-01-15T10:00:00-07:00)\n3. End date and time (ISO format: 2024-01-15T11:00:00-07:00)\n4. Description (optional)\n5. Location (optional)\n\nExample: create_calendar_event('Team Meeting', '2024-01-15T10:00:00-07:00', '2024-01-15T11:00:00-07:00', 'Weekly team sync', 'Conference Room A')"
    elif intent == 'calendar_read':
        return f"� I understand you want to view calendar events. To help you with '{user_input}', I would use the read_calendar_events function. Please provide:\n1. Maximum number of events to show (optional, default: 10)\n2. Start time filter (optional, ISO format)\n3. End time filter (optional, ISO format)\n\nExample: read_calendar_events(5) for next 5 events"
    elif intent == 'calendar_delete':
        return f"🗑️ I understand you want to delete a calendar event. To help you with '{user_input}', I would use the delete_calendar_event function. Please provide:\n1. The event ID of the calendar event to delete\n\nNote: You can find event IDs by first reading calendar events with read_calendar_events function."
    elif intent == 'calendar_update':
        return f"✏️ I understand you want to update a calendar event. To help you with '{user_input}', I would use the update_calendar_event function. Please provide:\n1. The event ID of the event to update\n2. New title (optional)\n3. New start time (optional, ISO format)\n4. New end time (optional, ISO format)\n5. New description (optional)\n6. New location (optional)\n\nExample: update_calendar_event('event_id_here', 'New Meeting Title', '2024-01-15T14:00:00-07:00', '2024-01-15T15:00:00-07:00')"
    
    # Drive intents
    elif intent == 'drive_list':
        return f"💾 I understand you want to list Drive files. To help you with '{user_input}', I would use the list_drive_files function. Please provide:\n1. Search query (optional, e.g., 'type:pdf' or 'name:report')\n2. Maximum number of files to show (optional, default: 10)\n\nExample: list_drive_files('type:pdf', 15) to find PDF files"
    elif intent == 'drive_create':
        return f"📁 I understand you want to create a Drive folder. To help you with '{user_input}', I would use the create_drive_folder function. Please provide:\n1. Folder name\n2. Parent folder ID (optional, defaults to root)\n\nExample: create_drive_folder('Project Files') to create a folder in root"
    elif intent == 'drive_delete':
        return f"🗑️ I understand you want to delete a Drive file/folder. To help you with '{user_input}', I would use the delete_drive_file function. Please provide:\n1. The file/folder ID to delete\n\nNote: You can find file IDs by first listing files with list_drive_files function."
    elif intent == 'drive_share':
        return f"🔗 I understand you want to share a Drive file. To help you with '{user_input}', I would use the share_drive_file function. Please provide:\n1. File ID to share\n2. Email address of the person to share with\n3. Permission level (optional: 'reader', 'writer', or 'owner', default: 'reader')\n\nExample: share_drive_file('file_id_here', 'user@example.com', 'writer')"
    
    else:
        return f"👋 Hello! I'm your assistant for emails, calendar, and Google Drive management. I can help you with:\n\n📧 **Email Management**:\n• Reading emails: Search and retrieve emails from your inbox\n• Sending emails: Compose and send new messages\n• Deleting emails: Remove unwanted messages\n• Creating drafts: Save emails for later\n\n📅 **Calendar Management**:\n• Creating events: Schedule meetings, appointments, and events\n• Viewing events: See your upcoming schedule and events\n• Updating events: Modify existing meetings and appointments\n• Deleting events: Cancel meetings and remove events\n\n💾 **Google Drive Management**:\n• Listing files: Browse and search your Drive files and folders\n• Creating folders: Organize your files with new folders\n• Deleting files: Remove files and folders from Drive\n• Sharing files: Grant access to files and folders with others\n\nWhat would you like to do today?"

# Create the smart handler tool
smart_handler_tool = FunctionTool(smart_email_calendar_drive_handler)

# Main unified agent with intelligent routing for email, calendar, and drive operations
email_calendar_drive_agent = Agent(
    name="email_calendar_drive_agent",
    description="""You are an intelligent assistant that helps users manage their Gmail account, Google Calendar, and Google Drive. 

IMPORTANT: You have access to these functions:

EMAIL FUNCTIONS:
- read_emails(query, num_emails): Search and retrieve emails
- send_email(to, subject, body): Send new emails  
- delete_email(message_id): Delete specific emails
- create_draft(to, subject, body): Create email drafts

CALENDAR FUNCTIONS:
- create_calendar_event(summary, start_datetime, end_datetime, description, location): Create new calendar events
- read_calendar_events(max_results, time_min, time_max): View upcoming calendar events
- delete_calendar_event(event_id): Delete calendar events
- update_calendar_event(event_id, summary, start_datetime, end_datetime, description, location): Update existing events

DRIVE FUNCTIONS:
- list_drive_files(query, max_results): List and search Drive files and folders
- create_drive_folder(folder_name, parent_folder_id): Create new folders in Drive
- delete_drive_file(file_id): Delete files and folders from Drive
- share_drive_file(file_id, email, role): Share Drive files with others

ANALYSIS FUNCTION:
- analyze_intent(user_input): Analyze what the user wants to do

ROUTING LOGIC:
EMAIL OPERATIONS:
1. For reading/searching emails (keywords: show, find, search, list, check, inbox, recent, unread): Use read_emails()
2. For sending emails (keywords: send, compose, write + email/message): Use send_email()
3. For deleting emails (keywords: delete, remove, trash + email/message): Use delete_email()
4. For creating drafts (keywords: draft, save + email/message): Use create_draft()

CALENDAR OPERATIONS:
5. For creating events (keywords: create, add, schedule, book + event/meeting/appointment): Use create_calendar_event()
6. For viewing events (keywords: show, list, check, upcoming + events/calendar/meetings): Use read_calendar_events()
7. For deleting events (keywords: delete, cancel, remove + event/meeting/appointment): Use delete_calendar_event()
8. For updating events (keywords: update, change, reschedule, modify + event/meeting/appointment): Use update_calendar_event()

DRIVE OPERATIONS:
9. For listing files (keywords: list, show, find, browse + files/drive/documents): Use list_drive_files()
10. For creating folders (keywords: create, make, new + folder/directory): Use create_drive_folder()
11. For deleting files (keywords: delete, remove, trash + file/folder/document + drive): Use delete_drive_file()
12. For sharing files (keywords: share, grant, give + access/permission): Use share_drive_file()

13. For general greetings or help: Provide friendly assistance about email, calendar, and drive capabilities

BEHAVIOR:
- Always analyze the user's intent first using analyze_intent() if unclear
- Use the most appropriate function based on the user's request
- For email read requests, use reasonable defaults (query="" for all emails, num_emails=10)
- For calendar read requests, use reasonable defaults (max_results=10 for upcoming events)
- For drive list requests, use reasonable defaults (query="" for all files, max_results=10)
- For send/draft/calendar create/drive create requests, ask for missing information
- For delete requests, explain that you need message/event/file IDs (get them from read/list functions first)
- Be helpful and conversational while being efficient

Your goal is to reduce API calls by using only the most relevant function for each request.""",
    model=gemini_model,
    tools=[
        # Email tools
        read_emails_tool, send_email_tool, delete_email_tool, create_draft_tool,
        # Calendar tools
        create_calendar_event_tool, read_calendar_events_tool, delete_calendar_event_tool, update_calendar_event_tool,
        # Drive tools
        list_drive_files_tool, create_drive_folder_tool, delete_drive_file_tool, share_drive_file_tool,
        # Analysis tool
        analyze_intent_tool
    ]
)

# Export all agents for potential direct access
# Maintain backward compatibility
email_agent = email_calendar_drive_agent  # For backward compatibility
email_calendar_agent = email_calendar_drive_agent  # For calendar compatibility

__all__ = [
    'email_calendar_drive_agent', # Main unified agent
    'email_agent',                # Backward compatibility alias
    'email_calendar_agent',       # Calendar compatibility alias
    
    # Specialized email agents
    'read_agent',          # Specialized read agent
    'send_agent',          # Specialized send agent  
    'delete_agent',        # Specialized delete agent
    'draft_agent',         # Specialized draft agent
    
    # Specialized calendar agents
    'calendar_create_agent',  # Calendar event creation agent
    'calendar_read_agent',    # Calendar event reading agent
    'calendar_delete_agent',  # Calendar event deletion agent
    'calendar_update_agent',  # Calendar event update agent
    
    # Specialized drive agents
    'drive_list_agent',    # Drive file listing agent
    'drive_create_agent',  # Drive folder creation agent
    'drive_delete_agent',  # Drive file deletion agent
    'drive_share_agent',   # Drive file sharing agent
    
    # Utility functions
    'route_email_request',    # Direct routing function (now handles calendar and drive too)
    'analyze_intent'          # Intent analysis function
]

print("✅ Email, Calendar, and Drive agent system initialized with specialized routing")
print("📧 Available email agents: read, send, delete, draft")
print("📅 Available calendar agents: create, read, delete, update")
print("💾 Available drive agents: list, create, delete, share")
print("🎯 Main agent will automatically route requests to appropriate specialized functions")
print("🔄 Backward compatibility maintained - 'email_agent' now includes calendar and drive functionality")
