#!/usr/bin/env python3
"""
Test script for the enhanced email, calendar, and drive agent routing system.
This script shows how different user inputs are routed to appropriate specialized agents.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_agent.agent import analyze_intent, route_email_request

def test_drive_intent_analysis():
    """Test the enhanced intent analysis function with drive inputs."""
    print("💾 Testing Drive Intent Analysis System")
    print("=" * 50)
    
    test_cases = [
        # Drive list intents
        ("show me my drive files", "drive_list"),
        ("list all documents in drive", "drive_list"),
        ("find PDF files in my drive", "drive_list"),
        ("what files do I have in drive", "drive_list"),
        ("browse my drive folders", "drive_list"),
        ("search for reports in drive", "drive_list"),
        
        # Drive create intents
        ("create a new folder", "drive_create"),
        ("make a folder called Projects", "drive_create"),
        ("add a new directory to drive", "drive_create"),
        ("create folder named Documents", "drive_create"),
        
        # Drive delete intents
        ("delete this file from drive", "drive_delete"),
        ("remove folder from drive", "drive_delete"),
        ("trash the document", "drive_delete"),
        ("delete old files from drive", "drive_delete"),
        
        # Drive share intents
        ("share this file with john@example.com", "drive_share"),
        ("give access to the document", "drive_share"),
        ("grant permission to view the folder", "drive_share"),
        ("make the file public", "drive_share"),
        ("share drive file with team", "drive_share"),
        
        # Calendar create intents (existing - should still work)
        ("schedule a meeting with John tomorrow at 2 PM", "calendar_create"),
        ("create a calendar event for the team meeting", "calendar_create"),
        
        # Calendar read intents (existing - should still work)
        ("show me my calendar for today", "calendar_read"),
        ("what meetings do I have tomorrow?", "calendar_read"),
        
        # Calendar delete intents (existing - should still work)
        ("cancel my meeting with Sarah", "calendar_delete"),
        
        # Calendar update intents (existing - should still work)
        ("reschedule the meeting to 3 PM", "calendar_update"),
        
        # Email intents (existing - should still work)
        ("show me my recent emails", "read"),
        ("send an email to john@example.com", "send"),
        ("delete spam emails", "delete"),
        ("create a draft email", "draft"),
        
        # General intents
        ("help me with drive and email", "general"),
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
    """Demonstrate the enhanced routing system with drive capabilities."""
    print("\n🎯 Demonstrating Enhanced Agent Routing System")
    print("=" * 50)
    
    sample_requests = [
        "show me emails from last week",
        "list my drive files", 
        "schedule a team meeting for tomorrow at 10 AM", 
        "create a new folder called Projects",
        "send a thank you email to client@company.com",
        "share the document with john@example.com",
        "what meetings do I have today?",
        "delete old files from drive",
        "cancel my appointment with the doctor",
        "find PDF files in my drive"
    ]
    
    for request in sample_requests:
        intent = analyze_intent(request)
        print(f"📝 Request: '{request}'")
        print(f"🎯 Detected Intent: {intent}")
        
        if intent.startswith('drive_'):
            agent_type = f"drive {intent.split('_')[1]}"
            print(f"💾 This would call the specialized {agent_type} agent")
        elif intent.startswith('calendar_'):
            agent_type = f"calendar {intent.split('_')[1]}"
            print(f"📅 This would call the specialized {agent_type} agent")
        elif intent in ['read', 'send', 'delete', 'draft']:
            print(f"📧 This would call the specialized email {intent} agent")
        else:
            print(f"💡 This would provide general assistance")
        
        print("-" * 30)

def show_drive_capabilities():
    """Show the drive management capabilities."""
    print("\n💾 Google Drive Management Capabilities")
    print("=" * 50)
    
    capabilities = [
        {
            "category": "📂 Listing Files",
            "examples": [
                "Show me my drive files",
                "List all documents in drive", 
                "Find PDF files in my drive",
                "What files do I have in drive?",
                "Browse my drive folders",
                "Search for reports in drive"
            ]
        },
        {
            "category": "📁 Creating Folders", 
            "examples": [
                "Create a new folder",
                "Make a folder called Projects",
                "Add a new directory to drive",
                "Create folder named Documents"
            ]
        },
        {
            "category": "🗑️ Deleting Files",
            "examples": [
                "Delete this file from drive",
                "Remove folder from drive", 
                "Trash the document",
                "Delete old files from drive"
            ]
        },
        {
            "category": "🔗 Sharing Files",
            "examples": [
                "Share this file with john@example.com",
                "Give access to the document",
                "Grant permission to view the folder",
                "Make the file public",
                "Share drive file with team"
            ]
        }
    ]
    
    for capability in capabilities:
        print(f"\n{capability['category']}:")
        for example in capability['examples']:
            intent = analyze_intent(example)
            print(f"  • \"{example}\" → {intent}")

def show_integration_capabilities():
    """Show how all three services work together."""
    print("\n🔄 Integrated Email, Calendar & Drive Capabilities")
    print("=" * 50)
    
    integration_examples = [
        {
            "scenario": "📧➡️📅 Email to Calendar",
            "example": "I received an email about a meeting, let me schedule it",
            "workflow": ["Read email", "Create calendar event"]
        },
        {
            "scenario": "📅➡️💾 Calendar to Drive", 
            "example": "I have a meeting, let me find the presentation files",
            "workflow": ["Check calendar", "List drive files", "Share presentation"]
        },
        {
            "scenario": "💾➡️📧 Drive to Email",
            "example": "I need to send the report I have in Drive",
            "workflow": ["Find file in drive", "Send email with file link"]
        },
        {
            "scenario": "🔄 Full Integration",
            "example": "Meeting reminder with shared documents",
            "workflow": ["Create calendar event", "Share drive folder", "Send email notification"]
        }
    ]
    
    for integration in integration_examples:
        print(f"\n{integration['scenario']}:")
        print(f"  📝 Scenario: {integration['example']}")
        print(f"  🔄 Workflow: {' → '.join(integration['workflow'])}")

if __name__ == "__main__":
    print("🚀 Enhanced Email, Calendar & Drive Agent Routing System Test")
    print("=" * 60)
    
    # Test enhanced intent analysis with drive
    accuracy = test_drive_intent_analysis()
    
    # Demonstrate enhanced routing
    demonstrate_enhanced_routing()
    
    # Show drive capabilities
    show_drive_capabilities()
    
    # Show integration capabilities
    show_integration_capabilities()
    
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
    print("   💾 Google Drive file listing, folder creation, file deletion, and sharing")
    print("   📅 Calendar event creation, viewing, updating, and deletion")
    print("   📧 Email management (reading, sending, deleting, drafts)")
    print("   🎯 Enhanced intent analysis for all three services")
    print("   🔄 Unified agent that handles email, calendar, and drive requests")
    print("   🤝 Backward compatibility with existing functionality")
    
    print("\n💡 Next Steps:")
    print("   1. Run: pip install -r requirements.txt")
    print("   2. Ensure Google Drive API is enabled in your Google Cloud Console")
    print("   3. Delete token.json to re-authenticate with Drive permissions")
    print("   4. Start ADK server: adk web")
    print("   5. Test with real queries like 'show my drive files' or 'create a folder'")
