"""Simple Scenario Analyzer Agent for generating feature summaries."""

import logging
import json
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScenarioAnalyzerAgent:
    """
    Simple agent that generates a summary about the feature and test scenarios.
    """
    
    def __init__(self):
        """Initialize the Scenario Analyzer Agent."""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=Config.MODEL_NAME,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
                google_api_key=Config.GOOGLE_API_KEY
            )
            logger.info("ScenarioAnalyzerAgent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ScenarioAnalyzerAgent: {e}")
            raise

    def analyze_scenarios(self, 
                         scenarios: List[Dict[str, Any]], 
                         original_analysis: str) -> Dict[str, Any]:
        """
        Generate a simple summary about the feature and test scenarios.
        
        Args:
            scenarios: List of generated scenarios
            original_analysis: Original combined analysis used for generation
            
        Returns:
            Simple summary results
        """
        try:
            logger.info(f"Generating simple summary for {len(scenarios)} scenarios")
            
            # Generate summary
            summary_report = self._generate_summary(scenarios, original_analysis)
            
            # Return simple results
            return {
                'total_scenarios': len(scenarios),
                'approval_status': 'approved',  # All scenarios are approved in this simple version
                'approved_scenarios': scenarios,  # All scenarios are approved
                'rejected_scenarios': [],
                'summary_report': summary_report
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                'total_scenarios': len(scenarios),
                'approval_status': 'approved',
                'approved_scenarios': scenarios,
                'rejected_scenarios': [],
                'summary_report': f"Error generating summary: {e}"
            }

    def _generate_summary(self, scenarios: List[Dict[str, Any]], original_analysis: str) -> str:
        """Generate a simple summary about the feature and test scenarios."""
        try:
            scenarios_json = json.dumps(scenarios, indent=2)
            
            prompt = f"""
You are a QA Documentation Assistant. Generate a concise summary report covering these three points:

## ORIGINAL ANALYSIS:
{original_analysis}

## GENERATED TEST SCENARIOS:
{scenarios_json}

## SUMMARY REPORT REQUIREMENTS:

Please provide a clear summary covering exactly these three areas using proper markdown formatting:

### 1. FEATURE SUMMARY
- What feature/enhancement are we testing?
- What are the key capabilities and functionalities?

### 2. TEST SCENARIO GENERATION APPROACH  
- How were these test scenarios generated?
- What data sources were used (PRD, images, impact areas)?
- What methodology was applied?

### 3. TESTING COVERAGE
- What areas and categories are covered by these scenarios?
- What types of testing are included (functional, integration, etc.)?
- How many scenarios were generated in each category?

IMPORTANT: Format your response using proper markdown syntax with:
- **Bold text** for emphasis
- *Italic text* for categories
- Clear section headers (### for main sections)
- Bullet points with proper indentation
- Professional formatting that will render beautifully in Streamlit

Make it visually appealing and well-structured for web display.
"""
            
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            
            return response.content
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return f"Summary generation failed: {e}"

    def generate_approval_report(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate a markdown-formatted approval report for Streamlit rendering.
        
        Args:
            analysis_results: Analysis results from analyze_scenarios
            
        Returns:
            Markdown-formatted approval report
        """
        try:
            total_scenarios = analysis_results.get('total_scenarios', 0)
            summary_report = analysis_results.get('summary_report', 'No summary available')
            
            report = f"""# 📋 Test Scenario Analysis Report

## 📊 Scenario Statistics
- **Total Scenarios Generated:** {total_scenarios}
- **Status:** ✅ All scenarios approved

## 🎯 Feature & Testing Summary
{summary_report}

## ✅ Conclusion
Successfully generated **{total_scenarios} test scenarios** covering the feature requirements.

---
*Report Generated: {self._get_timestamp()}*
"""
            return report
            
        except Exception as e:
            logger.error(f"Error generating approval report: {e}")
            return f"**Report generation failed:** {e}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for reports."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S") 