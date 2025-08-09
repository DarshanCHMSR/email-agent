from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.adk.agent import Agent
from google.adk.agent import UserMessage
import os
import base64
from email.mime.text import MIMEText


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def get_gmail_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


# Initialize the Gmail service
gmail_service = get_gmail_service()


# Initialize the Agent first
email_agent = Agent(
    "email_agent",
    "An agent that can read, send, delete, and draft emails using the Gmail API.",
    tools=[] # Tools will be added after their definitions
)


@email_agent.tool
def read_emails(query: str, num_emails: int = 5):
    """Reads the most recent emails from the user's inbox based on a query.

    Args:
        query (str): The search query to filter emails (e.g., "from:sender@example.com subject:meeting").
        num_emails (int): The maximum number of emails to read (default is 5).

    Returns:
        str: A summary of the emails found, or a message indicating no emails were found.
    """
    try:
        results = (
            gmail_service.users()
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
                gmail_service.users()
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


@email_agent.tool
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
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": raw_message}
        send_message = (
            gmail_service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        return f"Email sent successfully! Message Id: {send_message['id']}"
    except HttpError as error:
        return f"An error occurred: {error}"


@email_agent.tool
def delete_email(message_id: str):
    """Deletes an email by its message ID.

    Args:
        message_id (str): The ID of the email to delete.

    Returns:
        str: A message indicating whether the email was deleted successfully or if an error occurred.
    """
    try:
        gmail_service.users().messages().delete(userId="me", id=message_id).execute()
        return f"Email with ID {message_id} deleted successfully."
    except HttpError as error:
        return f"An error occurred: {error}"


@email_agent.tool
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
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": raw_message}
        draft = (
            gmail_service.users()
            .drafts()
            .create(userId="me", body={"message": create_message})
            .execute()
        )
        return f"Draft created successfully! Draft Id: {draft['id']}"
    except HttpError as error:
        return f"An error occurred: {error}"


# Assign tools to the agent after they are defined
email_agent.tools = [
    read_emails,
    send_email,
    delete_email,
    create_draft,
]
