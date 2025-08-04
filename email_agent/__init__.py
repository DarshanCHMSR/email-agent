from .agent import email_calendar_agent, email_agent

# Main agent (with calendar functionality)
root_agent = email_calendar_agent

# Backward compatibility
# email_agent is now an alias for email_calendar_agent