#!/usr/bin/env python3
"""
Test script to verify ADK server is working with the correct model.
"""

import requests
import json
import time

def test_adk_server():
    """Test if the ADK server is responding correctly."""
    print("🧪 Testing ADK Server Connection")
    print("=" * 50)
    
    # Common ADK server URLs to try
    urls_to_try = [
        "http://localhost:8000",   # Most common ADK port
        "http://127.0.0.1:8000",
        "http://localhost:8080",
        "http://localhost:3000", 
        "http://localhost:5000",
    ]
    
    for url in urls_to_try:
        try:
            print(f"🔍 Trying {url}...")
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ ADK server found at {url}")
                return url
        except requests.exceptions.RequestException:
            print(f"❌ No server at {url}")
            continue
    
    print("⚠️ Could not find ADK server. Make sure it's running.")
    return None

def test_model_compatibility():
    """Test if the model is working correctly."""
    print("\n🤖 Testing Model Compatibility")
    print("=" * 40)
    
    try:
        # Import and test the agent directly
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from email_agent.agent import analyze_intent
        
        # Test a simple intent analysis
        result = analyze_intent("can you delete a mail")
        print(f"✅ Model working! Intent analysis result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ADK Server and Model Compatibility Test")
    print("=" * 60)
    
    # Test server connection
    server_url = test_adk_server()
    
    # Test model compatibility
    model_working = test_model_compatibility()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"🌐 ADK Server: {'✅ Running' if server_url else '❌ Not found'}")
    print(f"🤖 Model: {'✅ Working' if model_working else '❌ Failed'}")
    
    if server_url and model_working:
        print("\n🎉 Everything is working correctly!")
        print(f"🌐 Access your email agent at: {server_url}")
        print("💬 Try asking: 'can you delete a mail'")
    else:
        print("\n⚠️ Some issues detected:")
        if not server_url:
            print("   - Start ADK server with: adk web")
        if not model_working:
            print("   - Check your API key and model configuration")