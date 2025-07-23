"""Streamlit web interface for the Test Scenario Generator."""

import streamlit as st
import os
import tempfile
from pathlib import Path
import pandas as pd
from datetime import datetime

from main import TestScenarioGenerator
from config import Config

# Page configuration
st.set_page_config(
    page_title="Test Scenario Generator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-header {
        font-size: 1.5rem;
        color: #ff6b6b;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
        color: #000000;
        font-weight: bold;
    }
    .success-box {
        background-color: #f0fff0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        color: #000000;
        font-weight: bold;
    }
    .warning-box {
        background-color: #fff8dc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #ffe4e1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'generator' not in st.session_state:
        st.session_state.generator = None
    if 'results' not in st.session_state:
        st.session_state.results = None

def initialize_generator():
    """Initialize the generator and check configuration."""
    try:
        st.session_state.generator = TestScenarioGenerator()
        return True, "System ready!"
    except Exception as e:
        return False, str(e)

def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🧪 Test Scenario Generator</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>AI-Powered Test Scenario Generation</strong><br>
    Upload your PRD Word document, feature images, and impact areas Excel file to generate comprehensive high-level test scenarios using Google Gemini 2.5 Pro.
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize generator and check configuration
    if not st.session_state.generator:
        is_ready, message = initialize_generator()
        if not is_ready:
            st.markdown(f"""
            <div class="error-box">
            <strong>⚠️ Configuration Error</strong><br>
            {message}<br><br>
            Please check your .env file and ensure you have:
            <ul>
            <li>GOOGLE_API_KEY set with a valid Google Gemini API key</li>
            </ul>
            See SETUP.md for detailed configuration instructions.
            </div>
            """, unsafe_allow_html=True)
            return
        else:
            st.success("✅ System initialized successfully!")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📝 Generate Scenarios", "🔬 Quick Test", "📊 Results"])
    
    with tab1:
        generate_scenarios_tab()
    
    with tab2:
        quick_test_tab()
    
    with tab3:
        results_tab()

def generate_scenarios_tab():
    """Tab for generating scenarios from actual data."""
    st.markdown('<h2 class="step-header">📝 Generate Test Scenarios</h2>', unsafe_allow_html=True)
    
    # JIRA Issue input section
    st.subheader("1. 🎫 JIRA Issue")
    
    jira_issue_input = st.text_input(
        "Enter JIRA Issue Key or URL",
        placeholder="e.g., PW-3416 or https://rcrm.atlassian.net/browse/PW-3416",
        help="Enter either the issue key (PW-3416) or the full JIRA URL"
    )
    
    if jira_issue_input:
        # Extract and show issue key
        from tools.jira_tool import JiraTool
        jira_tool = JiraTool()
        extracted_key = jira_tool.extract_issue_key_from_url(jira_issue_input.strip())
        
        if extracted_key:
            st.success(f"✅ Issue key detected: {extracted_key}")
            
            # Show JIRA connection status
            status = jira_tool.get_connection_status()
            if status['config_complete']:
                st.info(f"🔗 Will connect to: {status['jira_url']}")
            else:
                st.warning("⚠️ JIRA credentials not configured in .env file")
                with st.expander("JIRA Configuration Help"):
                    st.code("""
# Add these to your .env file:
JIRA_URL=https://rcrm.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your_api_token

# To create API token:
# 1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
# 2. Click 'Create API token'
# 3. Copy token to .env file
                    """)
        else:
            st.error("❌ Invalid JIRA issue format. Please use format like 'PW-3416' or full URL")
    
    # Image input section
    st.subheader("2. 🖼️ Feature Images")
    
    uploaded_images = st.file_uploader(
        "Upload feature images",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="Upload screenshots, mockups, or UI designs of the feature"
    )
    
    if uploaded_images:
        st.success(f"✅ {len(uploaded_images)} image(s) uploaded")
        with st.expander("Preview uploaded images"):
            cols = st.columns(min(len(uploaded_images), 3))
            for i, img in enumerate(uploaded_images[:3]):  # Show first 3 images
                with cols[i]:
                    st.image(img, caption=img.name, use_column_width=True)
    
    # Excel input section
    st.subheader("3. 📊 Impact Areas Excel File")
    
    uploaded_excel = st.file_uploader(
        "Upload impact areas Excel file",
        type=['xlsx', 'xls'],
        help="Upload Excel file containing impacted systems and components"
    )
    
    if uploaded_excel:
        st.success(f"✅ Excel file uploaded: {uploaded_excel.name}")
    
    # Output filename
    st.subheader("4. 📋 Output Settings")
    output_filename = st.text_input(
        "Output filename (optional)",
        placeholder="test_scenarios_feature_name.xlsx",
        help="Leave blank for auto-generated filename"
    )
    
    # Generate button
    st.subheader("5. 🚀 Generate Scenarios")
    
    # Check if at least one input is provided
    has_inputs = bool(jira_issue_input and jira_issue_input.strip()) or bool(uploaded_images) or bool(uploaded_excel)
    
    if not has_inputs:
        st.info("📝 Please provide at least one data source (JIRA issue, images, or Excel file) to generate scenarios.")
    
    if st.button("🔥 Generate Test Scenarios", disabled=not has_inputs, use_container_width=True):
        with st.spinner("🔄 Generating test scenarios... This may take a few minutes."):
            try:
                # Save uploaded files temporarily
                image_paths = []
                if uploaded_images:
                    for uploaded_image in uploaded_images:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_image.name}") as tmp_file:
                            tmp_file.write(uploaded_image.getvalue())
                            image_paths.append(tmp_file.name)
                
                excel_path = None
                if uploaded_excel:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
                        tmp_file.write(uploaded_excel.getvalue())
                        excel_path = tmp_file.name
                
                # Generate scenarios using JIRA issue instead of document
                result_path = st.session_state.generator.generate_scenarios_from_inputs(
                    jira_issue_input=jira_issue_input.strip() if jira_issue_input else None,
                    image_paths=image_paths if image_paths else None,
                    excel_path=excel_path,
                    output_filename=output_filename.strip() if output_filename else None
                )
                
                st.session_state.results = result_path
                
                # Cleanup temporary files
                for path in image_paths:
                    try:
                        os.unlink(path)
                    except:
                        pass
                if excel_path:
                    try:
                        os.unlink(excel_path)
                    except:
                        pass
                
                st.markdown("""
                <div class="success-box">
                <strong>🎉 Test scenarios generated successfully!</strong><br>
                Check the Results tab to view and download your scenarios.
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Error generating scenarios: {str(e)}")

def quick_test_tab():
    """Tab for quick testing with sample data."""
    st.markdown('<h2 class="step-header">🔬 Quick Test</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>ℹ️ Quick Test Feature</strong><br>
    This feature runs a test with sample JIRA issue data to verify the system is working correctly.
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🧪 Sample Data Preview")
    
    # Show sample JIRA issue
    st.subheader("🎫 Sample JIRA Issue")
    with st.expander("View Sample JIRA Content"):
        st.text_area(
            "Sample JIRA Issue Content",
            value="""JIRA ISSUE: PW-3416
============================================================
SUMMARY: Work & Education Description should be rich-text
TYPE: Requirement
STATUS: Development Planned
PRIORITY: Medium

DESCRIPTION:
As a recruiter, I want the ability to use rich text formatting tools in the description fields of candidate work experience and education history so that I can create more presentable, organized, and easy-to-read records.

OVERVIEW:
Currently, the description fields in the candidate's work experience and education history sections only allow plain text input. This limitation makes it difficult for users to present detailed and organized information, such as job responsibilities or educational achievements. Adding a rich text editor to these fields will enable users to format text, improving readability and professionalism.

ACCEPTANCE CRITERIA:
- Add Rich Text Editor: When user views description field, rich text editor with formatting options is displayed
- Apply Text Formatting: When user applies formatting, selected text is formatted as chosen
- Save Formatted Data: When user saves, formatted text is saved and displayed consistently""",
            height=200,
            disabled=True
        )
    
    st.subheader("🖼️ Sample Image Analysis")
    with st.expander("View Sample Image Analysis"):
        st.text_area(
            "Sample UI Analysis",
            value="""UI Analysis of Rich Text Editor Feature:

1. Rich Text Editor Interface:
   - WYSIWYG editor with formatting toolbar
   - Bold, italic, underline, color formatting options
   - List creation and hyperlink insertion capabilities
   - Clear formatting and undo/redo functionality

2. Candidate Profile Integration:
   - Work Experience description fields enhanced
   - Education History description fields enhanced
   - Consistent UI design with existing forms
   - Responsive design for different screen sizes

3. Data Management Features:
   - HTML content storage and retrieval
   - Content validation and sanitization
   - Export functionality for formatted content
   - Version control for description updates""",
            height=200,
            disabled=True
        )
    
    st.subheader("📊 Sample Impact Areas")
    with st.expander("View Sample Impact Areas"):
        st.text_area(
            "Sample Impact Areas",
            value="""Impacted Systems and Components:

Backend Services:
- Candidate profile management API
- Data validation and sanitization services
- HTML content storage systems
- Export and reporting services

Frontend Systems:
- Candidate profile forms and UI components
- Rich text editor integration
- Form validation and error handling
- Responsive design components

Database:
- Candidate work experience table schema
- Education history table schema
- Content versioning and audit logs
- Search indexing for formatted content

External Dependencies:
- Rich text editor library (TinyMCE/CKEditor)
- HTML sanitization libraries
- Export libraries for PDF/document generation
- Browser compatibility testing frameworks""",
            height=200,
            disabled=True
        )
    
    # Run quick test button
    st.subheader("🚀 Run Quick Test")
    
    if st.button("🧪 Run Quick Test with Sample Data", use_container_width=True):
        with st.spinner("⚡ Running quick test..."):
            try:
                result_path = st.session_state.generator.quick_test()
                st.session_state.results = result_path
                
                st.markdown("""
                <div class="success-box">
                <strong>✅ Quick test completed successfully!</strong><br>
                Check the Results tab to view the generated scenarios.
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Quick test failed: {str(e)}")

def results_tab():
    """Tab for displaying results."""
    st.markdown('<h2 class="step-header">📊 Results</h2>', unsafe_allow_html=True)
    
    if st.session_state.results:
        result_path = st.session_state.results
        
        st.markdown(f"""
        <div class="success-box">
        <strong>✅ Latest Results</strong><br>
        Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
        File: {Path(result_path).name}
        </div>
        """, unsafe_allow_html=True)
        
        # Download button
        if os.path.exists(result_path) and result_path.endswith('.xlsx'):
            with open(result_path, 'rb') as file:
                st.download_button(
                    label="📥 Download Test Scenarios (Excel)",
                    data=file.read(),
                    file_name=os.path.basename(result_path),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            # Try to display the Excel content
            try:
                df = pd.read_excel(result_path)
                st.subheader("📋 Generated Test Scenarios Preview")
                st.dataframe(df, use_container_width=True)
                
                # Summary statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Scenarios", len(df))
                with col2:
                    if 'Priority' in df.columns:
                        high_priority = len(df[df['Priority'] == 'High'])
                        st.metric("High Priority", high_priority)
                with col3:
                    if 'Category' in df.columns:
                        categories = df['Category'].nunique()
                        st.metric("Categories", categories)
                with col4:
                    if 'Priority' in df.columns:
                        medium_priority = len(df[df['Priority'] == 'Medium'])
                        st.metric("Medium Priority", medium_priority)
                
                # Category breakdown
                if 'Category' in df.columns:
                    st.subheader("📈 Scenario Distribution by Category")
                    category_counts = df['Category'].value_counts()
                    st.bar_chart(category_counts)
                
            except Exception as e:
                st.warning(f"Could not preview Excel file: {e}")
        
        # Check for analysis report
        report_path = result_path.replace('.xlsx', '_analysis_report.txt')
        if os.path.exists(report_path):
            st.subheader("📊 Analysis Report")
            with open(report_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            # Render the markdown content beautifully
            with st.expander("📋 View Full Analysis Report", expanded=True):
                st.markdown(report_content)
            
            # Download report
            st.download_button(
                label="📥 Download Analysis Report",
                data=report_content,
                file_name=os.path.basename(report_path),
                mime="text/plain",
                use_container_width=True
            )
    
    else:
        st.markdown("""
        <div class="info-box">
        <strong>ℹ️ No Results Yet</strong><br>
        Generate test scenarios using the "Generate Scenarios" or "Quick Test" tabs to see results here.
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 