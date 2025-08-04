from .agent import email_calendar_drive_agent, email_agent, email_calendar_agent

# Main agent (with email, calendar, and drive functionality)
root_agent = email_calendar_drive_agent

# Backward compatibility
# email_agent is now an alias for email_calendar_drive_agent
# email_calendar_agent is also an alias for email_calendar_drive_agent