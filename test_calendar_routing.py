#!/usr/bin/env python3
"""
Test script for the enhanced email and calendar agent routing system.
This script shows how different user inputs are routed to appropriate specialized agents.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_agent.agent import analyze_intent, route_email_request

def test_calendar_intent_analysis():
    """Test the enhanced intent analysis function with calendar inputs."""
    print("📅 Testing Calendar Intent Analysis System")
    print("=" * 50)
    
    test_cases = [
        # Calendar create intents
        ("schedule a meeting with John tomorrow at 2 PM", "calendar_create"),
        ("create a calendar event for the team meeting", "calendar_create"),
        ("book an appointment for next Monday", "calendar_create"),
        ("add a new event to my calendar", "calendar_create"),
        ("set up a meeting for Friday afternoon", "calendar_create"),
        
        # Calendar read intents
        ("show me my calendar for today", "calendar_read"),
        ("what meetings do I have tomorrow?", "calendar_read"),
        ("list my upcoming events", "calendar_read"),
        ("check my schedule for next week", "calendar_read"),
        ("what's on my calendar?", "calendar_read"),
        
        # Calendar delete intents
        ("cancel my meeting with Sarah", "calendar_delete"),
        ("delete the team meeting event", "calendar_delete"),
        ("remove the appointment from my calendar", "calendar_delete"),
        ("cancel tomorrow's event", "calendar_delete"),
        
        # Calendar update intents
        ("reschedule the meeting to 3 PM", "calendar_update"),
        ("change the time of my appointment", "calendar_update"),
        ("update the meeting location", "calendar_update"),
        ("modify the event description", "calendar_update"),
        ("edit the calendar event", "calendar_update"),
        
        # Email intents (existing - should still work)
        ("show me my recent emails", "read"),
        ("send an email to john@example.com", "send"),
        ("delete spam emails", "delete"),
        ("create a draft email", "draft"),
        
        # General intents
        ("help me with calendar and email", "general"),
        ("what can you do?", "general"),
    ]
    
    correct_predictions = 0
    total_predictions = len(test_cases)
    
    for user_input, expected_intent in test_cases:
        predicted_intent = analyze_intent(user_input)
        is_correct = predicted_intent == expected_intent
        status = "✅" if is_correct else "❌"
        
        print(f"{status} '{user_input}' -> {predicted_intent} (expected: {expected_intent})")
        
        if is_correct:
            correct_predictions += 1
    
    accuracy = (correct_predictions / total_predictions) * 100
    print(f"\n📊 Overall Accuracy: {correct_predictions}/{total_predictions} ({accuracy:.1f}%)")
    
    return accuracy

def demonstrate_enhanced_routing():
    """Demonstrate the enhanced routing system with calendar capabilities."""
    print("\n🎯 Demonstrating Enhanced Agent Routing System")
    print("=" * 50)
    
    sample_requests = [
        "show me emails from last week",
        "schedule a team meeting for tomorrow at 10 AM", 
        "send a thank you email to client@company.com",
        "what meetings do I have today?",
        "delete the promotional emails",
        "cancel my appointment with the doctor",
        "create a draft for the quarterly report",
        "reschedule the meeting to next Friday"
    ]
    
    for request in sample_requests:
        intent = analyze_intent(request)
        print(f"📝 Request: '{request}'")
        print(f"🎯 Detected Intent: {intent}")
        
        if intent.startswith('calendar_'):
            agent_type = f"calendar {intent.split('_')[1]}"
            print(f"📅 This would call the specialized {agent_type} agent")
        elif intent in ['read', 'send', 'delete', 'draft']:
            print(f"📧 This would call the specialized email {intent} agent")
        else:
            print(f"💡 This would provide general assistance")
        
        print("-" * 30)

def show_calendar_capabilities():
    """Show the calendar management capabilities."""
    print("\n📅 Calendar Management Capabilities")
    print("=" * 50)
    
    capabilities = [
        {
            "category": "📅 Creating Events",
            "examples": [
                "Schedule a meeting with John tomorrow at 2 PM",
                "Create a calendar event for the team meeting",
                "Book an appointment for next Monday at 9 AM",
                "Add a new event to my calendar"
            ]
        },
        {
            "category": "📖 Viewing Events", 
            "examples": [
                "Show me my calendar for today",
                "What meetings do I have tomorrow?",
                "List my upcoming events for this week",
                "Check my schedule for next Monday"
            ]
        },
        {
            "category": "✏️ Updating Events",
            "examples": [
                "Reschedule the meeting to 3 PM",
                "Change the location of my appointment",
                "Update the meeting description",
                "Modify the event time to next Friday"
            ]
        },
        {
            "category": "🗑️ Deleting Events",
            "examples": [
                "Cancel my meeting with Sarah",
                "Delete the team meeting event",
                "Remove the appointment from calendar",
                "Cancel tomorrow's event"
            ]
        }
    ]
    
    for capability in capabilities:
        print(f"\n{capability['category']}:")
        for example in capability['examples']:
            intent = analyze_intent(example)
            print(f"  • \"{example}\" → {intent}")

if __name__ == "__main__":
    print("🚀 Enhanced Email & Calendar Agent Routing System Test")
    print("=" * 60)
    
    # Test enhanced intent analysis
    accuracy = test_calendar_intent_analysis()
    
    # Demonstrate enhanced routing
    demonstrate_enhanced_routing()
    
    # Show calendar capabilities
    show_calendar_capabilities()
    
    print("\n" + "=" * 60)
    print("📋 Test Results:")
    print(f"   Enhanced Intent Analysis Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 85:
        print("🎉 Excellent! The enhanced system is working perfectly!")
    elif accuracy >= 70:
        print("✅ Good! The system is working well with minor improvements needed.")
    else:
        print("⚠️ The system needs improvements in intent recognition.")
    
    print("\n📚 What's New:")
    print("   📅 Calendar event creation, viewing, updating, and deletion")
    print("   🎯 Enhanced intent analysis for calendar operations")
    print("   🔄 Backward compatibility with existing email functionality")
    print("   🤖 Unified agent that handles both email and calendar requests")
    
    print("\n💡 Next Steps:")
    print("   1. Run: pip install -r requirements.txt")
    print("   2. Ensure Google Calendar API is enabled in your Google Cloud Console")
    print("   3. Start ADK server: adk web")
    print("   4. Test with real calendar queries like 'schedule a meeting for tomorrow'")
