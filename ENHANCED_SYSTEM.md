# Enhanced Email & Calendar Agent Routing System

## Overview

The enhanced email agent system now includes comprehensive **Google Calendar management** alongside the existing Gmail functionality. This unified system implements intelligent routing to specialized agents for both email and calendar operations, maintaining the efficient architecture while expanding capabilities.

## New Calendar Features

### 📅 Calendar Operations

The system now supports four main calendar operations:

#### 1. **Create Calendar Events** (`calendar_create_agent`)
- **Function**: `create_calendar_event(summary, start_datetime, end_datetime, description, location)`
- **Purpose**: Schedule new meetings, appointments, and events
- **Example Queries**:
  - "Schedule a meeting with John tomorrow at 2 PM"
  - "Create a calendar event for the team meeting"
  - "Book an appointment for next Monday at 9 AM"
  - "Add a new event to my calendar"

#### 2. **Read Calendar Events** (`calendar_read_agent`)
- **Function**: `read_calendar_events(max_results, time_min, time_max)`
- **Purpose**: View upcoming events and check schedule
- **Example Queries**:
  - "Show me my calendar for today"
  - "What meetings do I have tomorrow?"
  - "List my upcoming events for this week"
  - "Check my schedule for next Monday"

#### 3. **Update Calendar Events** (`calendar_update_agent`)
- **Function**: `update_calendar_event(event_id, summary, start_datetime, end_datetime, description, location)`
- **Purpose**: Modify existing events and reschedule meetings
- **Example Queries**:
  - "Reschedule the meeting to 3 PM"
  - "Change the location of my appointment"
  - "Update the meeting description"
  - "Modify the event time to next Friday"

#### 4. **Delete Calendar Events** (`calendar_delete_agent`)
- **Function**: `delete_calendar_event(event_id)`
- **Purpose**: Cancel meetings and remove events
- **Example Queries**:
  - "Cancel my meeting with Sarah"
  - "Delete the team meeting event"
  - "Remove the appointment from calendar"
  - "Cancel tomorrow's event"

## Enhanced Intent Analysis

The `analyze_intent()` function has been expanded to recognize calendar-related requests:

### New Intent Types
- `calendar_create` - Creating new calendar events
- `calendar_read` - Viewing calendar events and schedule
- `calendar_update` - Modifying existing events
- `calendar_delete` - Canceling/removing events

### Pattern Recognition Examples
```python
# Calendar creation patterns
"schedule a meeting" → calendar_create
"book an appointment" → calendar_create
"add to calendar" → calendar_create

# Calendar reading patterns  
"show my calendar" → calendar_read
"upcoming meetings" → calendar_read
"check my schedule" → calendar_read

# Calendar update patterns
"reschedule meeting" → calendar_update
"change appointment time" → calendar_update
"modify event" → calendar_update

# Calendar deletion patterns
"cancel meeting" → calendar_delete
"delete event" → calendar_delete
"remove appointment" → calendar_delete
```

## Architecture Updates

### 🏗️ **Unified Agent Structure**

```
📧 Email Agents (Existing)
├── read_agent - Email reading/searching
├── send_agent - Email sending  
├── delete_agent - Email deletion
└── draft_agent - Email draft creation

📅 Calendar Agents (New)
├── calendar_create_agent - Event creation
├── calendar_read_agent - Event viewing
├── calendar_update_agent - Event modification
└── calendar_delete_agent - Event deletion

🎯 Main Agent
└── email_calendar_agent - Unified routing agent
```

### **Enhanced Main Agent**

The `email_calendar_agent` (aliased as `email_agent` for backward compatibility) now includes:

- **Email Tools**: read_emails, send_email, delete_email, create_draft
- **Calendar Tools**: create_calendar_event, read_calendar_events, update_calendar_event, delete_calendar_event
- **Analysis Tool**: analyze_intent (enhanced with calendar patterns)

## Setup Requirements

### 🔧 **Additional Dependencies**
```bash
pip install -r requirements.txt
```

The updated `requirements.txt` includes:
- All existing email dependencies
- `datetime` for calendar time handling
- Google Calendar API access via existing `google-api-python-client`

### 🔑 **Google Calendar API Setup**

1. **Enable Calendar API** in Google Cloud Console:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to APIs & Services > Library
   - Search for "Google Calendar API"
   - Click "Enable"

2. **Update OAuth Scopes**:
   The system now requests these scopes:
   ```python
   SCOPES = [
       "https://www.googleapis.com/auth/gmail.modify",      # Existing
       "https://www.googleapis.com/auth/calendar"           # New
   ]
   ```

3. **Token Regeneration**:
   - Delete existing `token.json` file
   - Run the system to re-authenticate with new calendar permissions

## Usage Examples

### **Unified Usage (Recommended)**
```python
from email_agent.agent import email_calendar_agent

# Calendar operations
response = email_calendar_agent.run("schedule a meeting for tomorrow at 2 PM")
response = email_calendar_agent.run("show me my calendar for today")
response = email_calendar_agent.run("cancel the team meeting")

# Email operations (still work as before)
response = email_calendar_agent.run("show me recent emails")
response = email_calendar_agent.run("send email to john@example.com")
```

### **Direct Agent Access**
```python
from email_agent.agent import (
    calendar_create_agent, calendar_read_agent,
    read_agent, send_agent
)

# Use specialized calendar agents
events = calendar_read_agent.run("what meetings do I have today?")
result = calendar_create_agent.run("schedule team meeting tomorrow")

# Use specialized email agents  
emails = read_agent.run("show recent emails")
```

### **Manual Routing**
```python
from email_agent.agent import analyze_intent, route_email_request

# Test intent analysis
intent = analyze_intent("schedule a meeting for Friday")
print(intent)  # Output: "calendar_create"

# Route manually
response = route_email_request("show my calendar for tomorrow")
```

## Performance & Benefits

### 📈 **Maintained Efficiency**
- **Same routing principles**: Only relevant tools are called
- **API call optimization**: Single focused function per request
- **Backward compatibility**: Existing email functionality unchanged
- **Unified interface**: One agent handles both email and calendar

### 🎯 **Enhanced Capabilities**
- **Comprehensive calendar management**: Full CRUD operations
- **Intelligent routing**: Automatic detection of calendar vs email requests
- **Natural language processing**: Understands context and intent
- **Seamless integration**: Calendar and email operations in one system

## Testing

### 🧪 **Run Enhanced Tests**
```bash
# Test the enhanced routing system
python test_calendar_routing.py

# Run existing email tests (should still pass)
python test_routing.py
python test_new_system.py
```

### **Expected Results**
- Intent analysis accuracy: **85%+** (including calendar intents)
- All existing email functionality maintained
- New calendar operations working correctly
- Proper routing to specialized agents

## Migration Guide

### ✅ **Automatic Migration**
The system is designed for **seamless migration**:

1. **Existing code continues to work** - `email_agent` is now an alias for the enhanced agent
2. **New calendar features are available immediately** after authentication
3. **No breaking changes** to existing email functionality
4. **Optional calendar usage** - system works fine without calendar operations

### 🔄 **Steps to Enable Calendar**
1. Update dependencies: `pip install -r requirements.txt`
2. Enable Google Calendar API in Cloud Console
3. Delete `token.json` to re-authenticate with calendar permissions
4. Start using calendar features immediately

## Troubleshooting

### 🔍 **Common Issues**

1. **Calendar API not enabled**
   - Enable Google Calendar API in Google Cloud Console
   - Ensure the same project as Gmail API

2. **Insufficient permissions**
   - Delete `token.json` file
   - Re-authenticate with new scopes

3. **Time format errors**
   - Use ISO format: `2024-01-15T10:00:00-07:00`
   - Include timezone information

4. **Event ID not found**
   - Use `read_calendar_events` first to get event IDs
   - Event IDs are required for update/delete operations

### 📝 **Debug Commands**
```python
# Test calendar service connection
from email_agent.agent import ensure_calendar_service
service = ensure_calendar_service()  # Should not raise errors

# Test intent analysis
from email_agent.agent import analyze_intent
intent = analyze_intent("schedule meeting tomorrow")
print(intent)  # Should return "calendar_create"
```

## Future Enhancements

### 🚀 **Planned Features**
1. **Recurring events** - Support for daily/weekly/monthly recurring meetings
2. **Event invitations** - Send meeting invites via email integration
3. **Smart scheduling** - AI-powered optimal time finding
4. **Multiple calendars** - Support for different calendar types
5. **Timezone handling** - Automatic timezone detection and conversion

### 🎯 **Integration Opportunities**
- **Email-Calendar sync**: Create calendar events from email content
- **Meeting summaries**: Email meeting notes after events
- **Reminder system**: Automated email reminders for upcoming events
- **Conflict detection**: Alert for scheduling conflicts

## Conclusion

The enhanced Email & Calendar Agent Routing System successfully extends the original efficient email management architecture to include comprehensive calendar functionality. This unified approach maintains the performance benefits of specialized routing while providing users with a complete productivity management solution.

The system's intelligent intent analysis, backward compatibility, and seamless integration make it a powerful tool for managing both email communications and calendar scheduling through natural language interactions.
