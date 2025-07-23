#!/usr/bin/env python3
"""
Example usage of the Test Scenario Generator with JIRA integration.
"""

import os
from pathlib import Path
from main import TestScenarioGenerator

def main():
    """Main example function demonstrating JIRA integration."""
    
    print("🚀 Test Scenario Generator - JIRA Integration Example")
    print("=" * 60)
    
    # Initialize the generator
    generator = TestScenarioGenerator()
    
    # Example 1: Quick Test (using sample data)
    print("\n1️⃣ Running Quick Test with Sample Data...")
    try:
        result_path = generator.quick_test()
        print(f"✅ Quick test completed! Results: {result_path}")
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
    
    # Example 2: Generate from real JIRA issue
    print("\n2️⃣ Generating from Real JIRA Issue...")
    try:
        # Using PW-3416 as example JIRA issue
        result_path = generator.generate_scenarios_from_inputs(
            jira_issue_input="PW-3416",  # Can also use full URL
            output_filename="pw_3416_test_scenarios.xlsx"
        )
        print(f"✅ Generated scenarios from JIRA issue! Results: {result_path}")
    except Exception as e:
        print(f"❌ JIRA generation failed: {e}")
    
    # Example 3: JIRA + Images + Excel (complete workflow)
    print("\n3️⃣ Complete Workflow Example (JIRA + Images + Excel)...")
    
    # Check if sample files exist
    sample_image = "sample_ui_mockup.png"  # User would provide actual images
    sample_excel = "sample_impact_areas.xlsx"  # User would provide actual Excel
    
    print("📋 For complete workflow, you would provide:")
    print(f"   - JIRA Issue: PW-3416 (or any issue key/URL)")
    print(f"   - Images: {sample_image} (UI mockups, wireframes)")
    print(f"   - Excel: {sample_excel} (impact areas, components)")
    print()
    
    # Example with sample data since files may not exist
    custom_jira = """
JIRA ISSUE: DEMO-001
============================================================
SUMMARY: Enhanced User Profile Management
TYPE: Feature
STATUS: In Development
PRIORITY: High

DESCRIPTION:
As a user, I want to be able to manage my profile information more effectively so that I can keep my data up-to-date and personalized.

OVERVIEW:
The current user profile system lacks modern features and has limited customization options. This enhancement will provide a comprehensive profile management experience with advanced features.

BUSINESS CONTEXT:
Improving user profile management will increase user engagement and satisfaction, leading to better retention rates.

IN SCOPE:
- Profile picture upload and management
- Personal information editing with validation
- Privacy settings and visibility controls
- Account activity monitoring
- Profile completion progress tracking

ACCEPTANCE CRITERIA:
- Users can upload and crop profile pictures
- All personal information fields are editable with proper validation
- Users can control who sees their profile information
- Activity log shows recent profile changes
- Progress indicator shows profile completion percentage
"""
    
    custom_images = """
UI Analysis of Enhanced Profile Management:

1. Profile Picture Management:
   - Drag-and-drop image upload interface
   - Built-in cropping and editing tools
   - Preview functionality before saving
   - Support for multiple image formats

2. Information Form Design:
   - Clean, organized form layout with sections
   - Real-time validation with helpful error messages
   - Auto-save functionality for user convenience
   - Mobile-responsive design

3. Privacy Controls:
   - Granular privacy settings with toggle switches
   - Clear explanations of what each setting does
   - Preview of how profile appears to others
   - Quick privacy presets (Public, Friends, Private)

4. Activity Monitoring:
   - Timeline view of recent profile changes
   - Filter options by date and activity type
   - Export functionality for activity history
   - Visual indicators for different types of changes
"""
    
    custom_impact = """
Impacted Systems and Components:

Backend Services:
- User authentication and session management
- File upload and image processing services
- Data validation and sanitization APIs
- Privacy and permission management systems
- Activity logging and audit services

Frontend Systems:
- User profile components and forms
- Image upload and cropping widgets
- Privacy settings interface
- Activity timeline components
- Progress tracking visualizations

Database:
- User profile table schema updates
- Image metadata and storage references
- Privacy settings and permissions
- Activity log tables
- File storage and CDN integration

External Dependencies:
- Image processing libraries (ImageMagick, Sharp)
- Cloud storage services (AWS S3, CloudFront)
- Email notification services
- Real-time update frameworks (WebSockets)
- Analytics and tracking systems
"""
    
    try:
        # Generate with custom sample data
        result_path = generator.quick_test(
            test_jira_content=custom_jira,
            test_images_description=custom_images,
            test_impact_areas=custom_impact
        )
        print(f"✅ Complete workflow example completed! Results: {result_path}")
    except Exception as e:
        print(f"❌ Complete workflow failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Examples completed!")
    print("\n📝 To use with your own data:")
    print("1. Configure JIRA credentials in .env file")
    print("2. Use your JIRA issue keys (e.g., 'PROJ-123')")
    print("3. Provide actual UI mockups and Excel files")
    print("4. Run: generator.generate_scenarios_from_inputs()")

if __name__ == "__main__":
    main() 