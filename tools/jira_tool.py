"""JIRA Tool for loading data from JIRA issues using the jira Python module."""

import logging
import re
from typing import Dict, Any, List, Optional
from jira import JIRA
from jira.exceptions import JIRAError
import os
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JiraTool:
    """
    Tool for connecting to JIRA and extracting issue data.
    """
    
    def __init__(self):
        """Initialize the JIRA Tool."""
        self.jira_client = None
        self.is_connected = False
        logger.info("JiraTool initialized")

    def connect_using_config(self) -> bool:
        """
        Connect to JIRA using credentials from config/environment.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Check if JIRA credentials are configured
            if not all([Config.JIRA_URL, Config.JIRA_USERNAME, Config.JIRA_API_TOKEN]):
                logger.error("❌ JIRA credentials not configured in .env file")
                logger.info("Please add the following to your .env file:")
                logger.info("JIRA_URL=https://your-company.atlassian.net")
                logger.info("JIRA_USERNAME=your-email@company.com")
                logger.info("JIRA_API_TOKEN=your-api-token")
                return False
            
            return self.connect_to_jira(Config.JIRA_URL, Config.JIRA_USERNAME, Config.JIRA_API_TOKEN)
            
        except Exception as e:
            logger.error(f"❌ Failed to connect using config: {e}")
            return False

    def connect_to_jira(self, jira_url: str, username: str, api_token: str) -> bool:
        """
        Connect to JIRA using the provided credentials.
        
        Args:
            jira_url: JIRA instance URL (e.g., 'https://company.atlassian.net')
            username: JIRA username/email
            api_token: JIRA API token
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to JIRA: {jira_url}")
            
            # Create JIRA client with basic auth
            self.jira_client = JIRA(
                server=jira_url,
                basic_auth=(username, api_token)
            )
            
            # Test connection by getting server info
            server_info = self.jira_client.server_info()
            self.is_connected = True
            logger.info(f"✅ Successfully connected to JIRA: {server_info.get('serverTitle', 'Unknown')}")
            return True
            
        except JIRAError as e:
            logger.error(f"❌ JIRA connection failed: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to JIRA: {e}")
            self.is_connected = False
            return False

    def load_issue_from_input(self, user_input: str) -> Optional[Dict[str, Any]]:
        """
        Load JIRA issue data from user input (can be issue key or full URL).
        Automatically connects to JIRA using config if not already connected.
        
        Args:
            user_input: Either issue key (e.g., 'SS-22801') or full URL
            
        Returns:
            Dictionary containing issue data or None if failed
        """
        try:
            # Auto-connect if not connected
            if not self.is_connected:
                logger.info("Auto-connecting to JIRA using config...")
                if not self.connect_using_config():
                    return None
            
            # Extract issue key from input (works for both keys and URLs)
            issue_key = self.extract_issue_key_from_url(user_input.strip())
            
            if not issue_key:
                logger.error(f"❌ Could not extract valid issue key from: {user_input}")
                return None
            
            # Load the issue data
            return self.load_issue_data(issue_key)
            
        except Exception as e:
            logger.error(f"❌ Failed to load issue from input '{user_input}': {e}")
            return None

    def load_issue_data(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """
        Load data from a JIRA issue.
        
        Args:
            issue_key: JIRA issue key (e.g., 'PROJ-123')
            
        Returns:
            Dictionary containing issue data or None if failed
        """
        if not self.jira_client or not self.is_connected:
            logger.error("❌ Not connected to JIRA. Connection will be attempted automatically.")
            return None
            
        try:
            logger.info(f"Loading JIRA issue: {issue_key}")
            
            # Get issue with all fields
            issue = self.jira_client.issue(issue_key, expand='changelog')
            
            # Extract issue data
            issue_data = {
                'key': issue.key,
                'summary': getattr(issue.fields, 'summary', ''),
                'description': getattr(issue.fields, 'description', '') or '',
                'issue_type': getattr(issue.fields.issuetype, 'name', '') if issue.fields.issuetype else '',
                'status': getattr(issue.fields.status, 'name', '') if issue.fields.status else '',
                'priority': getattr(issue.fields.priority, 'name', '') if issue.fields.priority else '',
                'assignee': getattr(issue.fields.assignee, 'displayName', '') if issue.fields.assignee else '',
                'reporter': getattr(issue.fields.reporter, 'displayName', '') if issue.fields.reporter else '',
                'created': str(issue.fields.created) if issue.fields.created else '',
                'updated': str(issue.fields.updated) if issue.fields.updated else '',
                'labels': getattr(issue.fields, 'labels', []),
                'components': [comp.name for comp in getattr(issue.fields, 'components', [])],
                'fix_versions': [ver.name for ver in getattr(issue.fields, 'fixVersions', [])],
                'comments': [],
                'custom_fields': {}
            }
            
            # Extract comments
            if hasattr(issue.fields, 'comment') and issue.fields.comment:
                for comment in issue.fields.comment.comments:
                    issue_data['comments'].append({
                        'author': getattr(comment.author, 'displayName', '') if comment.author else '',
                        'body': comment.body or '',
                        'created': str(comment.created) if comment.created else ''
                    })
            
            # Extract custom fields that might contain acceptance criteria
            for field_name, field_value in issue.raw['fields'].items():
                if field_value and isinstance(field_value, (str, dict, list)):
                    # Look for fields that might contain requirements/acceptance criteria
                    if any(keyword in field_name.lower() for keyword in ['acceptance', 'criteria', 'requirement', 'spec']):
                        if isinstance(field_value, dict) and 'content' in field_value:
                            issue_data['custom_fields'][field_name] = field_value['content']
                        elif isinstance(field_value, str):
                            issue_data['custom_fields'][field_name] = field_value
            
            logger.info(f"✅ Successfully loaded JIRA issue: {issue_key}")
            print("\n===== Raw JIRA Issue Fields =====")
            print(issue.fields.description)
            print("===== End of Raw Fields =====\n")
            return issue_data
            
        except JIRAError as e:
            logger.error(f"❌ Failed to load JIRA issue {issue_key}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error loading JIRA issue {issue_key}: {e}")
            return None

    def extract_issue_key_from_url(self, jira_input: str) -> Optional[str]:
        """
        Extract issue key from JIRA URL or return the input if it's already a valid issue key.
        
        Args:
            jira_input: JIRA issue URL or issue key
            
        Returns:
            Issue key or None if not found
        """
        try:
            # First check if input is already a valid issue key pattern
            direct_key_pattern = r'^([A-Z]+-\d+)$'
            direct_match = re.match(direct_key_pattern, jira_input.strip().upper())
            if direct_match:
                issue_key = direct_match.group(1)
                logger.info(f"Input is already a valid issue key: {issue_key}")
                return issue_key
            
            # Try to extract from URL patterns
            url_patterns = [
                r'/browse/([A-Z]+-\d+)',  # Standard browse URL
                r'/issue/([A-Z]+-\d+)',   # Alternative URL format
                r'selectedIssue=([A-Z]+-\d+)',  # URL parameter format
                r'([A-Z]+-\d+)(?:\?|$)',  # Issue key at end of URL
            ]
            
            for pattern in url_patterns:
                match = re.search(pattern, jira_input, re.IGNORECASE)
                if match:
                    issue_key = match.group(1).upper()
                    logger.info(f"Extracted issue key from URL: {issue_key}")
                    return issue_key
            
            logger.warning(f"Could not extract valid issue key from input: {jira_input}")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting issue key from input: {e}")
            return None

    def format_issue_for_analysis(self, issue_data: Dict[str, Any]) -> str:
        """
        Format JIRA issue data into text suitable for analysis.
        
        Args:
            issue_data: Issue data from load_issue_data()
            
        Returns:
            Formatted text for analysis
        """
        try:
            analysis_parts = []
            
            # Header
            analysis_parts.append(f"JIRA ISSUE: {issue_data.get('key', 'Unknown')}")
            analysis_parts.append("=" * 60)
            
            # Basic information
            analysis_parts.append(f"SUMMARY: {issue_data.get('summary', 'No summary')}")
            analysis_parts.append(f"TYPE: {issue_data.get('issue_type', 'Unknown')}")
            analysis_parts.append(f"STATUS: {issue_data.get('status', 'Unknown')}")
            analysis_parts.append(f"PRIORITY: {issue_data.get('priority', 'Unknown')}")
            analysis_parts.append("")
            
            # Description
            description = issue_data.get('description', '').strip()
            if description:
                analysis_parts.append("DESCRIPTION:")
                analysis_parts.append(description)
                analysis_parts.append("")
            
            # Custom fields (acceptance criteria, requirements, etc.)
            custom_fields = issue_data.get('custom_fields', {})
            if custom_fields:
                analysis_parts.append("REQUIREMENTS & ACCEPTANCE CRITERIA:")
                for field_name, field_value in custom_fields.items():
                    analysis_parts.append(f"{field_name.upper()}:")
                    if isinstance(field_value, str):
                        analysis_parts.append(field_value)
                    else:
                        analysis_parts.append(str(field_value))
                    analysis_parts.append("")
            
            # Components and versions
            components = issue_data.get('components', [])
            if components:
                analysis_parts.append(f"COMPONENTS: {', '.join(components)}")
            
            fix_versions = issue_data.get('fix_versions', [])
            if fix_versions:
                analysis_parts.append(f"FIX VERSIONS: {', '.join(fix_versions)}")
            
            labels = issue_data.get('labels', [])
            if labels:
                analysis_parts.append(f"LABELS: {', '.join(labels)}")
            
            if components or fix_versions or labels:
                analysis_parts.append("")
            
            # Important comments (limit to most recent/relevant)
            comments = issue_data.get('comments', [])
            if comments:
                analysis_parts.append("RELEVANT COMMENTS:")
                # Get last 3 comments or comments with keywords
                relevant_comments = []
                keywords = ['acceptance', 'requirement', 'spec', 'test', 'criteria', 'should', 'must']
                
                for comment in comments[-5:]:  # Last 5 comments
                    comment_body = comment.get('body', '').lower()
                    if any(keyword in comment_body for keyword in keywords) or len(relevant_comments) < 3:
                        relevant_comments.append(comment)
                
                for i, comment in enumerate(relevant_comments[-3:], 1):  # Last 3 relevant
                    analysis_parts.append(f"Comment {i} ({comment.get('author', 'Unknown')}):")
                    analysis_parts.append(comment.get('body', ''))
                    analysis_parts.append("")
            
            # Metadata
            analysis_parts.append("METADATA:")
            analysis_parts.append(f"Assignee: {issue_data.get('assignee', 'Unassigned')}")
            analysis_parts.append(f"Reporter: {issue_data.get('reporter', 'Unknown')}")
            analysis_parts.append(f"Created: {issue_data.get('created', 'Unknown')}")
            analysis_parts.append(f"Updated: {issue_data.get('updated', 'Unknown')}")
            
            return "\n".join(analysis_parts)
            
        except Exception as e:
            logger.error(f"Error formatting issue data: {e}")
            return f"Error formatting JIRA issue data: {e}"

    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get current JIRA connection status and configuration info.
        
        Returns:
            Dictionary with connection status and config info
        """
        return {
            'is_connected': self.is_connected,
            'jira_url': Config.JIRA_URL if Config.JIRA_URL else 'Not configured',
            'username': Config.JIRA_USERNAME if Config.JIRA_USERNAME else 'Not configured',
            'has_api_token': bool(Config.JIRA_API_TOKEN),
            'config_complete': all([Config.JIRA_URL, Config.JIRA_USERNAME, Config.JIRA_API_TOKEN])
        }

    def test_jira_connection(self, test_issue_key: str = None) -> Dict[str, Any]:
        """
        Test JIRA connection using config and optionally load a test issue.
        
        Args:
            test_issue_key: Optional issue key to test loading
            
        Returns:
            Test results dictionary
        """
        results = {
            'connection_success': False,
            'server_info': None,
            'test_issue_success': False,
            'test_issue_data': None,
            'error_messages': []
        }
        
        try:
            # Test connection using config
            if self.connect_using_config():
                results['connection_success'] = True
                
                # Get server info
                try:
                    server_info = self.jira_client.server_info()
                    results['server_info'] = {
                        'title': server_info.get('serverTitle', 'Unknown'),
                        'version': server_info.get('version', 'Unknown'),
                        'url': Config.JIRA_URL
                    }
                except Exception as e:
                    results['error_messages'].append(f"Could not get server info: {e}")
                
                # Test issue loading if provided
                if test_issue_key:
                    issue_data = self.load_issue_from_input(test_issue_key)
                    if issue_data:
                        results['test_issue_success'] = True
                        results['test_issue_data'] = {
                            'key': issue_data.get('key'),
                            'summary': issue_data.get('summary'),
                            'type': issue_data.get('issue_type'),
                            'status': issue_data.get('status'),
                            'description_length': len(issue_data.get('description', '')),
                            'comments_count': len(issue_data.get('comments', []))
                        }
                    else:
                        results['error_messages'].append(f"Could not load test issue: {test_issue_key}")
            else:
                results['error_messages'].append("Failed to connect to JIRA using config")
                
        except Exception as e:
            results['error_messages'].append(f"Test failed: {e}")
        
        return results 