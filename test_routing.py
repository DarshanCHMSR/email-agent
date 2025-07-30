#!/usr/bin/env python3
"""
Test script to demonstrate the email agent routing system.
This script shows how different user inputs are routed to appropriate specialized agents.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_agent.agent import analyze_intent, route_email_request

def test_intent_analysis():
    """Test the intent analysis function with various user inputs."""
    print("🧪 Testing Intent Analysis System")
    print("=" * 50)
    
    test_cases = [
        # Read intents
        ("show me my recent emails", "read"),
        ("find emails from john@example.com", "read"),
        ("check my inbox", "read"),
        ("list unread messages", "read"),
        ("how many emails do I have?", "read"),
        
        # Send intents
        ("send an email to sarah@company.com", "send"),
        ("compose a message to the team", "send"),
        ("email the report to manager@company.com", "send"),
        ("write an email about the meeting", "send"),
        
        # Delete intents
        ("delete this email", "delete"),
        ("remove the spam messages", "delete"),
        ("trash the old emails", "delete"),
        
        # Draft intents
        ("create a draft email", "draft"),
        ("save this message as draft", "draft"),
        ("draft an email to the client", "draft"),
        
        # General intents
        ("help me with email", "general"),
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
    print(f"\n📊 Accuracy: {correct_predictions}/{total_predictions} ({accuracy:.1f}%)")
    
    return accuracy

def demonstrate_routing():
    """Demonstrate the routing system (without actually calling Gmail API)."""
    print("\n🎯 Demonstrating Agent Routing System")
    print("=" * 50)
    
    # Note: This would normally call the actual agents, but we'll just show the routing logic
    sample_requests = [
        "show me emails from last week",
        "send a thank you email to client@company.com", 
        "delete the promotional emails",
        "create a draft for the quarterly report"
    ]
    
    for request in sample_requests:
        intent = analyze_intent(request)
        print(f"📝 Request: '{request}'")
        print(f"🎯 Routed to: {intent} agent")
        print(f"💡 This would call the specialized {intent} agent with only the {intent} tool")
        print("-" * 30)

if __name__ == "__main__":
    print("🚀 Email Agent Routing System Test")
    print("=" * 60)
    
    # Test intent analysis
    accuracy = test_intent_analysis()
    
    # Demonstrate routing
    demonstrate_routing()
    
    print("\n✅ Test completed!")
    print(f"📈 Intent analysis accuracy: {accuracy:.1f}%")
    print("🎯 Routing system ready for production use")
    
    if accuracy >= 80:
        print("🎉 System performance is excellent!")
    elif accuracy >= 60:
        print("⚠️  System performance is acceptable but could be improved")
    else:
        print("❌ System performance needs improvement")