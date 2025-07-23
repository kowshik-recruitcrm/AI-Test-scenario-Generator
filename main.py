"""Main orchestrator for the Test Scenario Generator."""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from config import Config
from tools import JiraTool, ImageTool, ExcelTool
from agents import DataCombinerAgent, ScenarioGeneratorAgent, ScenarioAnalyzerAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestScenarioGenerator:
    """Main class for generating test scenarios from multiple data sources."""
    
    def __init__(self):
        """Initialize the Test Scenario Generator with all tools and agents."""
        try:
            # Validate configuration
            Config.validate_config()
            
            # Initialize tools
            self.jira_tool = JiraTool()
            self.image_tool = ImageTool()
            self.excel_tool = ExcelTool()
            
            # Initialize agents
            self.data_combiner = DataCombinerAgent(Config())
            self.scenario_generator = ScenarioGeneratorAgent()
            self.scenario_analyzer = ScenarioAnalyzerAgent()
            
            logger.info("Test Scenario Generator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Test Scenario Generator: {e}")
            raise

    def generate_scenarios_from_inputs(self, 
                                     jira_issue_input: Optional[str] = None,
                                     image_paths: Optional[List[str]] = None,
                                     excel_path: Optional[str] = None,
                                     output_filename: Optional[str] = None) -> str:
        """
        Generate test scenarios from JIRA issue, images, and Excel file.
        
        Args:
            jira_issue_input: JIRA issue key (e.g., 'PW-3416') or full URL
            image_paths: List of paths to feature images
            excel_path: Path to Excel file with impact areas
            output_filename: Output filename for scenarios (optional)
            
        Returns:
            Path to generated Excel file with scenarios
        """
        # Validate inputs
        if not any([jira_issue_input, image_paths, excel_path]):
            raise ValueError("At least one data source must be provided (JIRA issue, images, or Excel file)")
        
        try:
            logger.info("Starting test scenario generation...")
            
            # Step 1: Load data from all sources
            data_sources = {}
            loading_errors = []
            
            # Load JIRA issue data
            if jira_issue_input and jira_issue_input.strip():
                try:
                    logger.info(f"Loading JIRA issue: {jira_issue_input}")
                    issue_data = self.jira_tool.load_issue_from_input(jira_issue_input.strip())
                    
                    if issue_data:
                        jira_text = self.jira_tool.format_issue_for_analysis(issue_data)
                        if jira_text and jira_text.strip():
                            data_sources['jira'] = jira_text
                            logger.info(f"Successfully loaded JIRA issue data ({len(jira_text)} characters)")
                        else:
                            loading_errors.append("JIRA issue appears to have no content")
                    else:
                        loading_errors.append("Failed to extract content from JIRA issue")
                except Exception as e:
                    error_msg = f"Failed to load JIRA issue data: {e}"
                    logger.warning(error_msg)
                    loading_errors.append(error_msg)
            else:
                logger.info("No JIRA issue provided")
            
            # Load image data
            if image_paths and len(image_paths) > 0:
                try:
                    logger.info(f"Analyzing {len(image_paths)} images")
                    # First load the images, then analyze them
                    loaded_images = self.image_tool.load_images(image_paths)
                    if loaded_images:
                        image_data = self.image_tool.analyze_images(loaded_images)
                        if image_data and image_data.strip():
                            data_sources['images'] = image_data
                            logger.info(f"Successfully analyzed images ({len(image_data)} characters)")
                        else:
                            loading_errors.append("Image analysis returned empty results")
                    else:
                        loading_errors.append("Failed to load images")
                except Exception as e:
                    error_msg = f"Failed to analyze images: {e}"
                    logger.warning(error_msg)
                    loading_errors.append(error_msg)
            else:
                logger.info("No images provided")
            
            # Load Excel data
            if excel_path:
                try:
                    logger.info(f"Loading Excel file: {excel_path}")
                    excel_data = self.excel_tool.load_impact_areas(excel_path)
                    if excel_data:
                        impact_text = self.excel_tool.extract_impact_areas_text(excel_data)
                        if impact_text and impact_text.strip():
                            data_sources['excel'] = impact_text
                            logger.info(f"Successfully loaded Excel impact areas ({len(impact_text)} characters)")
                        else:
                            loading_errors.append("Excel file appears to contain no usable text data")
                    else:
                        loading_errors.append("Failed to load Excel file data")
                except Exception as e:
                    error_msg = f"Failed to load Excel data: {e}"
                    logger.warning(error_msg)
                    loading_errors.append(error_msg)
            else:
                logger.info("No Excel file provided")
            
            # Check if we have any valid data sources
            if not data_sources:
                error_details = "No valid data sources were loaded. "
                if loading_errors:
                    error_details += "Errors encountered: " + "; ".join(loading_errors)
                else:
                    error_details += "Please provide at least one of: JIRA issue key/URL, images, or Excel file."
                
                logger.error(error_details)
                raise ValueError(error_details)
            
            logger.info(f"Successfully loaded {len(data_sources)} data source(s): {list(data_sources.keys())}")
            
            # Step 2: Combine data using AI agent
            logger.info("Combining data sources using AI...")
            combined_analysis = self.data_combiner.combine_data_sources(data_sources)
            
            # Step 3: Generate scenarios using AI agent
            logger.info("Generating test scenarios using AI...")
            scenarios = self.scenario_generator.generate_scenarios(combined_analysis)
            
            # Step 4: Analyze scenarios using AI agent
            logger.info("Analyzing generated scenarios using AI...")
            analysis_results = self.scenario_analyzer.analyze_scenarios(scenarios, combined_analysis)
            
            # Step 5: Save results
            if not output_filename:
                output_filename = f"test_scenarios_{Path().resolve().name}.xlsx"
            
            output_path = Path(Config.OUTPUT_DIR) / output_filename
            
            # Save approved scenarios to Excel
            approved_scenarios = analysis_results.get('approved_scenarios', scenarios)
            result_path = self.excel_tool.save_scenarios_to_excel(approved_scenarios, str(output_path))
            
            # Save analysis report
            report_path = str(output_path).replace('.xlsx', '_analysis_report.txt')
            analysis_report = self.scenario_analyzer.generate_approval_report(analysis_results)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(analysis_report)
            
            logger.info(f"Test scenario generation completed successfully!")
            logger.info(f"Results saved to: {result_path}")
            logger.info(f"Analysis report saved to: {report_path}")
            
            return result_path
            
        except Exception as e:
            logger.error(f"Error generating test scenarios: {e}")
            raise

    def quick_test(self, 
                   test_jira_content: Optional[str] = None,
                   test_images_description: Optional[str] = None,
                   test_impact_areas: Optional[str] = None) -> str:
        """
        Quick test method using sample data or provided test data.
        
        Args:
            test_jira_content: Optional test JIRA content
            test_images_description: Optional test image analysis
            test_impact_areas: Optional test impact areas
            
        Returns:
            Path to generated Excel file
        """
        logger.info("Running quick test with sample data...")
        
        try:
            # Default sample data
            sample_jira = test_jira_content or """
JIRA ISSUE: PW-3416
============================================================
SUMMARY: Work & Education Description should be rich-text
TYPE: Requirement
STATUS: Development Planned
PRIORITY: Medium

DESCRIPTION:
As a recruiter, I want the ability to use rich text formatting tools in the description fields of candidate work experience and education history so that I can create more presentable, organized, and easy-to-read records.

OVERVIEW:
Currently, the description fields in the candidate's work experience and education history sections only allow plain text input. This limitation makes it difficult for users to present detailed and organized information, such as job responsibilities or educational achievements. Adding a rich text editor to these fields will enable users to format text, improving readability and professionalism.

BUSINESS CONTEXT:
Recruit CRM aims to provide recruiters and hiring managers with tools to document candidate profiles effectively. Enhancing the description fields with a rich text editor will enable better data presentation.

IN SCOPE:
- Adding a rich text editor to the description fields in:
  - Candidate work experience
  - Candidate education history
- Supporting all formatting options

ACCEPTANCE CRITERIA:
- Add Rich Text Editor: When user views description field, rich text editor with formatting options is displayed
- Apply Text Formatting: When user applies formatting, selected text is formatted as chosen
- Save Formatted Data: When user saves, formatted text is saved and displayed consistently
"""
            
            sample_images = test_images_description or """
UI Analysis of Rich Text Editor Feature:

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
   - Version control for description updates
"""
            
            sample_impact = test_impact_areas or """
Impacted Systems and Components:

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
- Browser compatibility testing frameworks
"""
            
            # Create data sources
            data_sources = {
                'jira': sample_jira,
                'images': sample_images,
                'excel': sample_impact
            }
            
            # Combine data
            combined_analysis = self.data_combiner.combine_data_sources(data_sources)
            
            # Generate scenarios
            scenarios = self.scenario_generator.generate_scenarios(combined_analysis)
            
            # Analyze scenarios
            analysis_results = self.scenario_analyzer.analyze_scenarios(scenarios, combined_analysis)
            
            # Save results
            output_path = Path(Config.OUTPUT_DIR) / "quick_test_scenarios.xlsx"
            
            # Save approved scenarios to Excel
            approved_scenarios = analysis_results.get('approved_scenarios', scenarios)
            result_path = self.excel_tool.save_scenarios_to_excel(approved_scenarios, str(output_path))
            
            # Save analysis report
            report_path = str(output_path).replace('.xlsx', '_analysis_report.txt')
            analysis_report = self.scenario_analyzer.generate_approval_report(analysis_results)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(analysis_report)
            
            logger.info(f"Quick test completed successfully!")
            logger.info(f"Results saved to: {result_path}")
            
            return result_path
            
        except Exception as e:
            logger.error(f"Error in quick test: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    generator = TestScenarioGenerator()
    
    # Quick test
    result = generator.quick_test()
    print(f"Quick test results: {result}")
    
    # Example with JIRA issue
    # result = generator.generate_scenarios_from_inputs(
    #     jira_issue_input="PW-3416",
    #     image_paths=["ui_mockup.png"],
    #     excel_path="impact_areas.xlsx"
    # ) 