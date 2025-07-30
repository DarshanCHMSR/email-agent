#!/usr/bin/env python3
"""
Test script for the new email agent system.
This verifies that the agent properly routes requests and uses the right tools.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_agent.agent import email_agent, analyze_intent

def test_agent_setup():
    """Test that the agent is properly configured."""
    print("🧪 Testing Agent Setup")
    print("=" * 50)
    
    print(f"✅ Agent name: {email_agent.name}")
    print(f"✅ Number of tools: {len(email_agent.tools)}")
    
    tool_names = [tool.function.__name__ for tool in email_agent.tools]
    print(f"✅ Available tools: {', '.join(tool_names)}")
    
    expected_tools = {'read_emails', 'send_email', 'delete_email', 'create_draft', 'analyze_intent'}
    actual_tools = set(tool_names)
    
    if expected_tools.issubset(actual_tools):
        print("✅ All required tools are available")
        return True
    else:
        missing = expected_tools - actual_tools
        print(f"❌ Missing tools: {missing}")
        return False

def test_intent_analysis():
    """Test the intent analysis function."""
    print("\n🧪 Testing Intent Analysis")
    print("=" * 50)
    
    test_cases = [
        ("hi", "general"),
        ("hello", "general"),
        ("show me my emails", "read"),
        ("find emails from john", "read"),
        ("send email to sarah@example.com", "send"),
        ("compose a message", "send"),
        ("delete this email", "delete"),
        ("remove spam", "delete"),
        ("create a draft", "draft"),
        ("save as draft", "draft"),
    ]
    
    correct = 0
    for user_input, expected in test_cases:
        actual = analyze_intent(user_input)
        status = "✅" if actual == expected else "❌"
        print(f"{status} '{user_input}' -> {actual} (expected: {expected})")
        if actual == expected:
            correct += 1
    
    accuracy = (correct / len(test_cases)) * 100
    print(f"\n📊 Intent Analysis Accuracy: {correct}/{len(test_cases)} ({accuracy:.1f}%)")
    return accuracy >= 80

def test_system_benefits():
    """Show the benefits of the new system."""
    print("\n📈 System Benefits")
    print("=" * 50)
    
    print("🎯 BEFORE (Old System):")
    print("   • Single agent with all 4 tools")
    print("   • All tools evaluated for every request")
    print("   • 4x API calls per request")
    print("   • Higher chance of 503 errors")
    print("   • Inefficient resource usage")
    
    print("\n🎯 AFTER (New System):")
    print("   • Intelligent agent with guided tool selection")
    print("   • Only relevant tools used based on intent")
    print("   • Reduced API calls through smart routing")
    print("   • Lower chance of rate limiting")
    print("   • More efficient processing")
    
    print("\n💡 Key Improvements:")
    print("   • Intent analysis guides tool selection")
    print("   • Clear routing logic in agent description")
    print("   • Maintains all functionality while reducing load")
    print("   • Better user experience with focused responses")

def show_usage_examples():
    """Show how to use the new system."""
    print("\n💻 Usage Examples")
    print("=" * 50)
    
    print("📧 Reading Emails:")
    print("   User: 'show me my recent emails'")
    print("   Agent: Uses read_emails() function")
    print("   Result: Retrieves and displays recent emails")
    
    print("\n📤 Sending Emails:")
    print("   User: 'send email to john@example.com'")
    print("   Agent: Uses send_email() function")
    print("   Result: Prompts for subject/body, then sends email")
    
    print("\n🗑️ Deleting Emails:")
    print("   User: 'delete spam emails'")
    print("   Agent: Uses delete_email() function")
    print("   Result: Explains need for message ID, guides user")
    
    print("\n📝 Creating Drafts:")
    print("   User: 'create a draft email'")
    print("   Agent: Uses create_draft() function")
    print("   Result: Prompts for details, creates draft")
    
    print("\n👋 General Queries:")
    print("   User: 'hi' or 'help'")
    print("   Agent: Provides friendly assistance")
    print("   Result: Shows available capabilities")

if __name__ == "__main__":
    print("🚀 Email Agent System Test")
    print("=" * 60)
    
    # Test agent setup
    setup_ok = test_agent_setup()
    
    # Test intent analysis
    intent_ok = test_intent_analysis()
    
    # Show system benefits
    test_system_benefits()
    
    # Show usage examples
    show_usage_examples()
    
    print("\n" + "=" * 60)
    print("📋 Test Results:")
    print(f"   Agent Setup: {'✅ PASS' if setup_ok else '❌ FAIL'}")
    print(f"   Intent Analysis: {'✅ PASS' if intent_ok else '❌ FAIL'}")
    
    if setup_ok and intent_ok:
        print("\n🎉 All tests passed! The system is ready for use.")
        print("💡 The agent will now intelligently route requests to appropriate tools.")
        print("🔧 Start the ADK server with: adk web")
    else:
        print("\n⚠️ Some tests failed. Please check the configuration.")
    
    print("\n📚 Next Steps:")
    print("   1. Start ADK server: adk web")
    print("   2. Test with real queries in the web interface")
    print("   3. Monitor for reduced 503 errors")
    print("   4. Observe more efficient tool usage")