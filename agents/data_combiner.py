"""Data Combiner Agent for combining multiple data sources using LLM."""

import logging
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from config import Config

logger = logging.getLogger(__name__)

class DataCombinerAgent:
    """Agent for combining document, image, and impact area data using LLM."""
    
    def __init__(self, config: Config):
        """Initialize the Data Combiner Agent."""
        self.config = config
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the Gemini LLM."""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.MODEL_NAME,
                google_api_key=self.config.GOOGLE_API_KEY,
                temperature=self.config.TEMPERATURE,
                max_tokens=self.config.MAX_TOKENS
            )
            logger.info("Gemini LLM initialized successfully for data combination")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini LLM: {e}")
            raise
    
    def combine_data_sources(self, data_sources: Dict[str, str]) -> str:
        """
        Combine all data sources into a comprehensive analysis.
        
        Args:
            data_sources: Dictionary containing different data types:
                - 'document': Content from Word document/PRD
                - 'images': Analysis from feature images  
                - 'excel': Data from impact areas Excel
            
        Returns:
            Combined and analyzed content for test scenario generation
        """
        try:
            logger.info("Starting data combination process")
            
            # Create comprehensive prompt for combining data
            prompt = self._create_combination_prompt(data_sources)
            
            # Get LLM analysis
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            
            combined_analysis = response.content
            
            logger.info(f"Successfully combined data sources into {len(combined_analysis)} character analysis")
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Error combining data sources: {e}")
            raise
    
    def _create_combination_prompt(self, data_sources: Dict[str, str]) -> str:
        """
        Create a comprehensive prompt for combining all data sources.
        
        Args:
            data_sources: Dictionary of data source content
            
        Returns:
            Formatted prompt for LLM analysis
        """
        prompt_parts = [
            "You are a Senior Business Analyst tasked with analyzing multiple data sources to create a comprehensive understanding of a feature or enhancement.",
            "",
            "## TASK:",
            "Analyze and combine the provided data sources to create a unified analysis that will be used for generating high-level test scenarios.",
            "",
            "## ANALYSIS FRAMEWORK:",
            "1. **Feature Overview**: What is the main feature/enhancement being developed?",
            "2. **Key Requirements**: What are the core functional and non-functional requirements?",
            "3. **User Journey**: How will users interact with this feature?",
            "4. **System Impact**: What systems, components, and processes are affected?",
            "5. **Risk Areas**: What areas need special attention for testing?",
            "6. **Integration Points**: How does this feature integrate with existing systems?",
            "",
            "## PROVIDED DATA SOURCES:",
            ""
        ]
        
        # Add JIRA issue content if available
        if 'jira' in data_sources and data_sources['jira'].strip():
            prompt_parts.extend([
                "### JIRA ISSUE REQUIREMENTS:",
                data_sources['jira'],
                ""
            ])
        
        # Add image analysis if available
        if 'images' in data_sources and data_sources['images'].strip():
            prompt_parts.extend([
                "### UI/FEATURE IMAGES ANALYSIS:",
                data_sources['images'],
                ""
            ])
        
        # Add impact areas if available
        if 'excel' in data_sources and data_sources['excel'].strip():
            prompt_parts.extend([
                "### IMPACT AREAS DATA:",
                data_sources['excel'],
                ""
            ])
        
        # Add analysis instructions
        prompt_parts.extend([
            "## ANALYSIS INSTRUCTIONS:",
            "",
            "Create a comprehensive analysis that:",
            "- Synthesizes information from all available data sources",
            "- Identifies the core feature functionality and user flows",
            "- Maps out system dependencies and integration points",
            "- Highlights areas that will need thorough testing",
            "- Provides context for generating appropriate test scenarios",
            "",
            "## OUTPUT FORMAT:",
            "Provide a structured analysis covering:",
            "1. **Feature Summary** (2-3 sentences)",
            "2. **Core Requirements** (bullet points)",
            "3. **User Interaction Flow** (step-by-step)",
            "4. **System Components Impacted** (organized by category)",
            "5. **Critical Testing Areas** (areas requiring focused testing)",
            "6. **Integration & Dependencies** (external systems/services)",
            "",
            "Make your analysis detailed enough to support comprehensive test scenario generation, but focused on the most important aspects for testing coverage.",
            "",
            "Begin your analysis now:"
        ])
        
        return "\n".join(prompt_parts)
    
    def validate_data_completeness(self, data_sources: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate the completeness and quality of provided data sources.
        
        Args:
            data_sources: Dictionary of data source content
            
        Returns:
            Dictionary containing validation results and recommendations
        """
        try:
            logger.info("Validating data completeness")
            
            validation_results = {
                'data_source_status': {},
                'completeness_scores': {},
                'overall_completeness': 0,
                'recommendations': [],
                'sufficient_for_generation': False
            }
            
            total_score = 0
            source_count = 0
            
            # Validate document content
            if 'document' in data_sources:
                doc_content = data_sources['document'].strip()
                if doc_content:
                    doc_score = min(len(doc_content) / 1000, 1.0)  # Normalize to 0-1
                    validation_results['data_source_status']['document'] = 'Available'
                    validation_results['completeness_scores']['document'] = doc_score
                    total_score += doc_score
                    source_count += 1
                else:
                    validation_results['data_source_status']['document'] = 'Empty'
                    validation_results['recommendations'].append("Document content is empty")
            else:
                validation_results['data_source_status']['document'] = 'Missing'
                validation_results['recommendations'].append("No document content provided")
            
            # Validate image analysis
            if 'images' in data_sources:
                img_content = data_sources['images'].strip()
                if img_content:
                    img_score = min(len(img_content) / 500, 1.0)  # Normalize to 0-1
                    validation_results['data_source_status']['images'] = 'Available'
                    validation_results['completeness_scores']['images'] = img_score
                    total_score += img_score
                    source_count += 1
                else:
                    validation_results['data_source_status']['images'] = 'Empty'
                    validation_results['recommendations'].append("Image analysis is empty")
            else:
                validation_results['data_source_status']['images'] = 'Missing'
                validation_results['recommendations'].append("No image analysis provided")
            
            # Validate impact areas
            if 'excel' in data_sources:
                excel_content = data_sources['excel'].strip()
                if excel_content:
                    excel_score = min(len(excel_content) / 300, 1.0)  # Normalize to 0-1
                    validation_results['data_source_status']['excel'] = 'Available'
                    validation_results['completeness_scores']['excel'] = excel_score
                    total_score += excel_score
                    source_count += 1
                else:
                    validation_results['data_source_status']['excel'] = 'Empty'
                    validation_results['recommendations'].append("Impact areas data is empty")
            else:
                validation_results['data_source_status']['excel'] = 'Missing'
                validation_results['recommendations'].append("No impact areas data provided")
            
            # Calculate overall completeness
            if source_count > 0:
                validation_results['overall_completeness'] = total_score / source_count
                validation_results['sufficient_for_generation'] = (
                    source_count >= 1 and validation_results['overall_completeness'] > 0.3
                )
            
            # Add quality recommendations
            if validation_results['overall_completeness'] < 0.5:
                validation_results['recommendations'].append(
                    "Consider providing more detailed content in available data sources"
                )
            
            if source_count < 2:
                validation_results['recommendations'].append(
                    "Having multiple data sources will improve test scenario quality"
                )
            
            logger.info(f"Data validation completed. Overall completeness: {validation_results['overall_completeness']:.2f}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating data completeness: {e}")
            return {
                'overall_completeness': 0,
                'sufficient_for_generation': False,
                'error': str(e)
            } 