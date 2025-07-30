#!/usr/bin/env python3
"""
Example usage of the new Email Agent Routing System.
This script demonstrates how the routing system works with different types of requests.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_agent.agent import (
    email_agent,           # Main routing agent
    read_agent,           # Specialized agents
    send_agent,
    delete_agent,
    draft_agent,
    analyze_intent,       # Utility functions
    route_email_request
)

def demonstrate_routing():
    """Demonstrate the routing system with various example requests."""
    
    print("🚀 Email Agent Routing System Demo")
    print("=" * 60)
    
    # Example requests that would be routed to different agents
    example_requests = [
        {
            "request": "Show me emails from last week",
            "expected_agent": "read",
            "description": "Reading/searching emails"
        },
        {
            "request": "Send a meeting reminder to team@company.com",
            "expected_agent": "send", 
            "description": "Sending new emails"
        },
        {
            "request": "Delete all spam emails from my inbox",
            "expected_agent": "delete",
            "description": "Deleting unwanted emails"
        },
        {
            "request": "Create a draft for the quarterly report email",
            "expected_agent": "draft",
            "description": "Creating email drafts"
        },
        {
            "request": "What can you help me with?",
            "expected_agent": "general",
            "description": "General queries (defaults to read agent)"
        }
    ]
    
    print("🎯 Intent Analysis and Routing Demonstration:")
    print("-" * 60)
    
    for i, example in enumerate(example_requests, 1):
        request = example["request"]
        expected = example["expected_agent"]
        description = example["description"]
        
        # Analyze intent
        detected_intent = analyze_intent(request)
        
        # Show routing decision
        print(f"\n{i}. {description}")
        print(f"   📝 Request: \"{request}\"")
        print(f"   🎯 Detected Intent: {detected_intent}")
        print(f"   ✅ Expected: {expected}")
        
        # Show which agent would be called
        if detected_intent == expected or (detected_intent == "general" and expected == "general"):
            status = "✅ CORRECT"
        else:
            status = "❌ INCORRECT"
            
        print(f"   {status} - Would route to {detected_intent} agent")
        
        # In a real scenario, you would call:
        # response = route_email_request(request)
        # But we're not calling Gmail API in this demo
        
    print("\n" + "=" * 60)

def show_agent_capabilities():
    """Show what each specialized agent can do."""
    
    print("\n🤖 Specialized Agent Capabilities:")
    print("-" * 60)
    
    agents_info = [
        {
            "name": "Read Agent",
            "variable": "read_agent",
            "capabilities": [
                "Search emails by sender, subject, or content",
                "List recent, unread, or specific emails",
                "Retrieve email details and snippets",
                "Count emails matching criteria"
            ]
        },
        {
            "name": "Send Agent", 
            "variable": "send_agent",
            "capabilities": [
                "Compose and send new emails",
                "Send emails to single or multiple recipients",
                "Handle email formatting and attachments",
                "Confirm successful delivery"
            ]
        },
        {
            "name": "Delete Agent",
            "variable": "delete_agent", 
            "capabilities": [
                "Delete specific emails by ID",
                "Remove emails matching criteria",
                "Clean up spam and promotional emails",
                "Bulk delete operations"
            ]
        },
        {
            "name": "Draft Agent",
            "variable": "draft_agent",
            "capabilities": [
                "Create email drafts for later sending",
                "Save work-in-progress emails",
                "Prepare templates and responses",
                "Store emails for review and editing"
            ]
        }
    ]
    
    for agent_info in agents_info:
        print(f"\n📧 {agent_info['name']} ({agent_info['variable']}):")
        for capability in agent_info['capabilities']:
            print(f"   • {capability}")

def show_performance_benefits():
    """Explain the performance benefits of the routing system."""
    
    print("\n📈 Performance Benefits:")
    print("-" * 60)
    
    benefits = [
        {
            "metric": "API Calls Reduced",
            "before": "4 tools evaluated per request",
            "after": "1 tool evaluated per request", 
            "improvement": "~75% reduction"
        },
        {
            "metric": "Response Time",
            "before": "Multiple tool evaluations",
            "after": "Single focused tool call",
            "improvement": "Faster responses"
        },
        {
            "metric": "Error Rate",
            "before": "Higher chance of 503 errors",
            "after": "Reduced rate limiting",
            "improvement": "More reliable"
        },
        {
            "metric": "Resource Usage",
            "before": "All agents loaded for each request",
            "after": "Only relevant agent used",
            "improvement": "More efficient"
        }
    ]
    
    for benefit in benefits:
        print(f"\n🎯 {benefit['metric']}:")
        print(f"   Before: {benefit['before']}")
        print(f"   After:  {benefit['after']}")
        print(f"   Result: {benefit['improvement']}")

def usage_examples():
    """Show code examples for using the system."""
    
    print("\n💻 Usage Examples:")
    print("-" * 60)
    
    examples = [
        {
            "title": "Basic Usage (Recommended)",
            "code": '''from email_agent.agent import email_agent

# The main agent automatically routes requests
response = email_agent.run("show me my recent emails")
print(response)'''
        },
        {
            "title": "Direct Agent Access",
            "code": '''from email_agent.agent import read_agent, send_agent

# Use specific agents directly
emails = read_agent.run("find emails from john@example.com")
result = send_agent.run("send thank you email to client@company.com")'''
        },
        {
            "title": "Manual Routing",
            "code": '''from email_agent.agent import analyze_intent, route_email_request

# Analyze intent first
intent = analyze_intent("delete spam emails")
print(f"Detected intent: {intent}")

# Then route manually
response = route_email_request("delete spam emails")'''
        }
    ]
    
    for example in examples:
        print(f"\n📝 {example['title']}:")
        print("```python")
        print(example['code'])
        print("```")

if __name__ == "__main__":
    # Run the demonstration
    demonstrate_routing()
    show_agent_capabilities()
    show_performance_benefits()
    usage_examples()
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed!")
    print("💡 The routing system is ready for production use.")
    print("📚 See ROUTING_SYSTEM.md for detailed documentation.")
    print("🧪 Run test_routing.py to verify system performance.")