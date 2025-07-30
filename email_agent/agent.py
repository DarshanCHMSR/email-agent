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

# Load environment variables from .env file
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

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


# Gmail service will be initialized when needed
gmail_service = None

def ensure_gmail_service():
    """Lazy initialization of Gmail service"""
    global gmail_service
    if gmail_service is None:
        gmail_service = get_gmail_service()
    return gmail_service


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


def analyze_intent(user_input: str):
    """Analyzes user input to determine the intended email operation.
    
    Args:
        user_input (str): The user's request or query.
        
    Returns:
        str: The identified intent ('read', 'send', 'delete', 'draft', or 'general').
    """
    # Convert to lowercase for easier matching
    input_lower = user_input.lower()
    
    # Define intent patterns (more comprehensive)
    read_patterns = [
        r'\b(read|show|get|fetch|find|search|list|check|display|view)\b.*\b(email|message|mail|inbox)\b',
        r'\b(inbox|unread|recent|latest|new)\b',
        r'\bfrom\b.*@.*\.(com|org|net|edu|gov)',
        r'\bsubject\b.*:',
        r'\bhow many\b.*\bemail',
        r'\bshow.*\b(from|last|week|month|today)',
        r'\bcheck.*\b(inbox|mail|email)',
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
    
    # Check patterns and return intent (order matters for overlapping patterns)
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

# Create the Gemini model instance with API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key or api_key == "your-api-key-here":
    raise ValueError(
        "Please set your Google AI API key in the .env file. "
        "Get your API key from: https://aistudio.google.com/app/apikey"
    )

# Get model name from environment with smart fallback
preferred_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-002")

# List of models to try in order of preference (most stable first)
model_candidates = [
    preferred_model,
    "gemini-1.5-flash-002",  # Stable versioned model
    "gemini-1.5-flash-001",  # Older stable version
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
            # Add generation config for better reliability
            generation_config={
                "temperature": 0.1,  # Lower temperature for more consistent responses
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        # CRITICAL: Override the default model after creation
        gemini_model.model = model_name
        print(f"✅ Successfully initialized {model_name}")
        break
    except Exception as e:
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

def route_email_request(user_input: str):
    """Routes the user request to the appropriate email function based on intent analysis.
    
    Args:
        user_input (str): The user's request or query.
        
    Returns:
        str: A message indicating which function would be called for this request.
    """
    intent = analyze_intent(user_input)
    
    if intent == 'read':
        return f"🎯 Intent: READ - This request would use the read_emails function to search and retrieve emails. Request: '{user_input}'"
    elif intent == 'send':
        return f"🎯 Intent: SEND - This request would use the send_email function to compose and send an email. Request: '{user_input}'"
    elif intent == 'delete':
        return f"🎯 Intent: DELETE - This request would use the delete_email function to remove emails. Request: '{user_input}'"
    elif intent == 'draft':
        return f"🎯 Intent: DRAFT - This request would use the create_draft function to save an email draft. Request: '{user_input}'"
    else:
        return f"🎯 Intent: GENERAL - This is a general query. I can help you with reading emails, sending emails, deleting emails, or creating drafts. Request: '{user_input}'"

# Create routing tool
route_email_tool = FunctionTool(route_email_request)

# Create a smart email agent that uses intent-based tool selection
def smart_email_handler(user_input: str):
    """Handles email requests by analyzing intent and providing appropriate guidance.
    
    Args:
        user_input (str): The user's request or query.
        
    Returns:
        str: Response with guidance on how to handle the request.
    """
    intent = analyze_intent(user_input)
    
    if intent == 'read':
        return f"📧 I understand you want to read/search emails. To help you with '{user_input}', I would use the read_emails function. Please provide:\n1. Search query (e.g., 'from:sender@example.com' or 'subject:meeting')\n2. Number of emails to retrieve (1-50)\n\nExample: read_emails('from:john@example.com', 10)"
    elif intent == 'send':
        return f"📤 I understand you want to send an email. To help you with '{user_input}', I would use the send_email function. Please provide:\n1. Recipient email address\n2. Subject line\n3. Email body content\n\nExample: send_email('recipient@example.com', 'Meeting Reminder', 'Don't forget about our meeting tomorrow.')"
    elif intent == 'delete':
        return f"🗑️ I understand you want to delete emails. To help you with '{user_input}', I would use the delete_email function. Please provide:\n1. The message ID of the email to delete\n\nNote: You can find message IDs by first reading emails with read_emails function."
    elif intent == 'draft':
        return f"📝 I understand you want to create a draft. To help you with '{user_input}', I would use the create_draft function. Please provide:\n1. Recipient email address\n2. Subject line\n3. Email body content\n\nExample: create_draft('recipient@example.com', 'Draft Subject', 'Draft content here.')"
    else:
        return f"👋 Hello! I'm your email assistant. I can help you with:\n\n📧 **Reading emails**: Search and retrieve emails from your inbox\n📤 **Sending emails**: Compose and send new messages\n🗑️ **Deleting emails**: Remove unwanted messages\n📝 **Creating drafts**: Save emails for later\n\nWhat would you like to do with your emails today?"

# Create the smart handler tool
smart_handler_tool = FunctionTool(smart_email_handler)

# Main email agent with intelligent routing and all email tools
email_agent = Agent(
    name="email_agent",
    description="""You are an intelligent email assistant that helps users manage their Gmail account. 

IMPORTANT: You have access to these email functions:
- read_emails(query, num_emails): Search and retrieve emails
- send_email(to, subject, body): Send new emails  
- delete_email(message_id): Delete specific emails
- create_draft(to, subject, body): Create email drafts
- analyze_intent(user_input): Analyze what the user wants to do

ROUTING LOGIC:
1. For reading/searching emails (keywords: show, find, search, list, check, inbox, recent, unread): Use read_emails()
2. For sending emails (keywords: send, compose, write + email/message): Use send_email()
3. For deleting emails (keywords: delete, remove, trash + email/message): Use delete_email()
4. For creating drafts (keywords: draft, save + email/message): Use create_draft()
5. For general greetings or help: Provide friendly assistance

BEHAVIOR:
- Always analyze the user's intent first using analyze_intent() if unclear
- Use the most appropriate function based on the user's request
- For read requests, use reasonable defaults (query="" for all emails, num_emails=10)
- For send/draft requests, ask for missing information (recipient, subject, body)
- For delete requests, explain that you need a message ID (get it from read_emails first)
- Be helpful and conversational while being efficient

Your goal is to reduce API calls by using only the most relevant function for each request.""",
    model=gemini_model,
    tools=[read_emails_tool, send_email_tool, delete_email_tool, create_draft_tool, analyze_intent_tool]
)

# Export all agents for potential direct access
__all__ = [
    'email_agent',      # Main routing agent
    'read_agent',       # Specialized read agent
    'send_agent',       # Specialized send agent  
    'delete_agent',     # Specialized delete agent
    'draft_agent',      # Specialized draft agent
    'route_email_request',  # Direct routing function
    'analyze_intent'    # Intent analysis function
]

print("✅ Email agent system initialized with specialized routing")
print("📧 Available agents: read, send, delete, draft")
print("🎯 Main agent will automatically route requests to appropriate specialized agents")
