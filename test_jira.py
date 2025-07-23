#!/usr/bin/env python3
"""Test script for JIRA tool functionality."""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tools.jira_tool import JiraTool
from config import Config

def test_jira_configuration():
    """Test JIRA configuration and connection."""
    print("🧪 Testing JIRA Configuration")
    print("=" * 50)
    
    # Initialize JIRA tool
    jira_tool = JiraTool()
    print("✅ JiraTool initialized")
    
    # Check connection status
    status = jira_tool.get_connection_status()
    print(f"🔗 JIRA URL: {status['jira_url']}")
    print(f"👤 Username: {status['username']}")
    print(f"🔑 API Token: {'Configured' if status['has_api_token'] else 'Not configured'}")
    print(f"⚙️ Config Complete: {'Yes' if status['config_complete'] else 'No'}")
    print()
    
    if not status['config_complete']:
        print("❌ JIRA credentials not fully configured in .env file")
        print("\nPlease add the following to your .env file:")
        print("JIRA_URL=https://rcrm.atlassian.net")
        print("JIRA_USERNAME=your-email@company.com")
        print("JIRA_API_TOKEN=your-api-token")
        print("\nTo create a JIRA API token:")
        print("1. Go to https://id.atlassian.com/manage-profile/security/api-tokens")
        print("2. Click 'Create API token'")
        print("3. Copy the token to your .env file")
        return False
    
    # Test connection
    print("🔌 Testing JIRA connection...")
    connection_success = jira_tool.connect_using_config()
    
    if not connection_success:
        print("❌ Failed to connect to JIRA")
        return False
    
    print("✅ JIRA connection successful!")
    print()
    
    return True

def test_issue_input_parsing():
    """Test issue input parsing (keys and URLs)."""
    print("🔍 Testing issue input parsing...")
    
    jira_tool = JiraTool()
    
    test_inputs = [
        "SS-22801",  # Direct issue key
        "ss-22801",  # Lowercase issue key
        "https://rcrm.atlassian.net/browse/SS-22801",  # Full browse URL
        "https://rcrm.atlassian.net/issue/SS-22801",  # Alternative URL
        "https://rcrm.atlassian.net/browse/SS-22801?focusedCommentId=12345",  # URL with parameters
        "SS-12345",  # Another valid key
        "invalid-input",  # Invalid input
    ]
    
    for test_input in test_inputs:
        issue_key = jira_tool.extract_issue_key_from_url(test_input)
        print(f"Input: {test_input}")
        print(f"Extracted: {issue_key}")
        print()

def test_simplified_issue_loading():
    """Test the new simplified issue loading."""
    print("📄 Testing simplified issue loading...")
    
    # Get issue input from user
    print("You can provide either:")
    print("1. Issue key: SS-22801")
    print("2. Full URL: https://rcrm.atlassian.net/browse/SS-22801")
    
    user_input = input("\nEnter JIRA issue key or URL (or press Enter to use SS-22801): ").strip()
    
    if not user_input:
        user_input = "SS-22801"  # Default test issue
        print(f"Using default: {user_input}")
    
    jira_tool = JiraTool()
    
    # Load issue using simplified method
    print(f"\n📥 Loading issue from input: {user_input}")
    issue_data = jira_tool.load_issue_from_input(user_input)
    
    if not issue_data:
        print(f"❌ Failed to load issue from input: {user_input}")
        return False
    
    print("✅ Issue loaded successfully!")
    print(f"Key: {issue_data.get('key', 'Unknown')}")
    print(f"Summary: {issue_data.get('summary', 'No summary')}")
    print(f"Type: {issue_data.get('issue_type', 'Unknown')}")
    print(f"Status: {issue_data.get('status', 'Unknown')}")
    print(f"Description length: {len(issue_data.get('description', ''))}")
    print(f"Comments: {len(issue_data.get('comments', []))}")
    print()
    
    # Format for analysis
    print("📝 Formatting for analysis...")
    formatted_text = jira_tool.format_issue_for_analysis(issue_data)
    print(f"Formatted text length: {len(formatted_text)} characters")
    
    # Show preview of formatted text
    print("\n📋 Preview of formatted analysis:")
    print("-" * 50)
    preview_length = 500
    if len(formatted_text) > preview_length:
        print(formatted_text[:preview_length] + "...")
        print(f"\n[Showing first {preview_length} characters of {len(formatted_text)} total]")
    else:
        print(formatted_text)
    print("-" * 50)
    
    return True

def test_connection_with_sample():
    """Test connection and load a sample issue."""
    print("🔗 Testing connection with sample issue...")
    
    jira_tool = JiraTool()
    
    # Test with the known URL
    test_input = "https://rcrm.atlassian.net/browse/SS-22801"
    
    # Use the comprehensive test method
    results = jira_tool.test_jira_connection(test_input)
    
    print("📊 Test Results:")
    print(f"Connection: {'✅ Success' if results['connection_success'] else '❌ Failed'}")
    
    if results['server_info']:
        print(f"Server: {results['server_info']['title']} ({results['server_info']['version']})")
        print(f"URL: {results['server_info']['url']}")
    
    if results['test_issue_success']:
        print(f"✅ Sample issue loaded: {results['test_issue_data']['key']}")
        print(f"Summary: {results['test_issue_data']['summary']}")
        print(f"Type: {results['test_issue_data']['type']}")
        print(f"Status: {results['test_issue_data']['status']}")
    
    if results['error_messages']:
        print("\n❌ Errors:")
        for error in results['error_messages']:
            print(f"  - {error}")
    
    return results['connection_success']

def run_comprehensive_test():
    """Run comprehensive JIRA tool test with simplified interface."""
    print("🚀 Starting JIRA Tool Test (Simplified Interface)")
    print("=" * 60)
    print()
    
    # Test 1: Configuration check
    if not test_jira_configuration():
        print("❌ Configuration test failed. Please configure JIRA credentials first.")
        return False
    
    # Test 2: Input parsing
    test_issue_input_parsing()
    
    # Test 3: Connection with sample
    print("🔗 Testing connection with sample issue...")
    if not test_connection_with_sample():
        print("❌ Connection test failed.")
        return False
    
    # Test 4: Interactive issue loading
    try:
        test_simplified_issue_loading()
    except KeyboardInterrupt:
        print("\n⏭️ Skipping interactive test")
    
    print("\n🎉 All tests completed successfully!")
    print("\n✅ Your JIRA tool is ready to use!")
    print("You can now provide either issue keys (SS-22801) or full URLs!")
    return True

if __name__ == "__main__":
    try:
        run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 