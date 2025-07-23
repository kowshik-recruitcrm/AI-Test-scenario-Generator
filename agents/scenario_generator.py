"""Scenario Generator Agent for creating high-level test scenarios."""

import logging
import json
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from config import Config

logger = logging.getLogger(__name__)

class ScenarioGeneratorAgent:
    """Agent for generating high-level test scenarios from combined analysis data."""
    
    def __init__(self):
        """Initialize the Scenario Generator Agent."""
        self.config = Config()
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
            logger.info("Gemini LLM initialized successfully for scenario generation")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini LLM: {e}")
            raise
    
    def generate_scenarios(self, combined_analysis: str) -> List[Dict[str, Any]]:
        """
        Generate high-level test scenarios from combined analysis.
        
        Args:
            combined_analysis: Combined analysis from DataCombinerAgent
            
        Returns:
            List of test scenario dictionaries
        """
        try:
            logger.info("Starting test scenario generation")
            
            # Create prompt for scenario generation
            prompt = self._create_scenario_generation_prompt(combined_analysis)
            
            # Get LLM response
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            
            # Parse the response to extract scenarios
            scenarios = self._parse_scenarios_response(response.content)
            
            logger.info(f"Successfully generated {len(scenarios)} test scenarios")
            return scenarios
            
        except Exception as e:
            logger.error(f"Error generating test scenarios: {e}")
            raise
    
    def _create_scenario_generation_prompt(self, combined_analysis: str) -> str:
        """
        Create a comprehensive prompt for generating test scenarios.
        
        Args:
            combined_analysis: Combined analysis data
            
        Returns:
            Formatted prompt for scenario generation
        """
        prompt = f"""
You are a professional manual QA tester for a web-based ATS+CRM application. Your goal is to create concise, high-impact test scenarios that can prevent major bugs and cover the majority of fault areas efficiently.

## COMBINED ANALYSIS DATA:
{combined_analysis}

## INSTRUCTIONS:
- Prioritize scenarios clearly as P0 (blocker), P1 (critical), P2 (major), and so on, with blockers and critical tests listed first.
- Ensure scenarios are concise yet comprehensive, avoiding redundant checks.
- Apply valid test strategies and patterns (e.g. boundary value, equivalence partitioning, happy path, negative path, exploratory where needed).
- Focus on functional flows, integrations, and data integrity relevant to an ATS+CRM.
- Output only the final prioritized list of scenarios, clearly marked by priority.

## SCENARIO CATEGORIES:
- **Functional**: Core ATS+CRM functionality testing
- **Integration**: System integration and API testing  
- **User Experience**: UI/UX and accessibility testing
- **Data**: Data handling, validation and integrity testing
- **Security**: Security, access control and authentication testing
- **Performance**: Performance, load and reliability testing

## OUTPUT FORMAT:
Generate as many scenarios as you can based on the combined data in this exact JSON structure:

```json
[
  {{
    "id": "TS001",
    "category": "Functional",
    "scenario": "Verify candidate application submission and data capture workflow",
    "priority": "P0"
  }},
  {{
    "id": "TS002", 
    "category": "Integration",
    "scenario": "Test integration between ATS and CRM modules for lead conversion",
    "priority": "P1"
  }}
]
```

## REQUIREMENTS:
- Use sequential IDs starting from TS001
- Categories must be one of: Functional, Integration, User Experience, Data, Security, Performance
- Priorities must be: P0, P1, P2, P3, P4 (P0=blocker, P1=critical, P2=major, P3=minor, P4=trivial)
- Scenarios should be concise yet comprehensive
- Focus on high-impact areas that prevent major bugs
- Be specific to ATS+CRM context but based on the provided data

Based on the combined data above, generate all the test scenarios you can to ensure comprehensive coverage of the identified features, functionality, and impact areas.
"""
        
        return prompt
    
    def _parse_scenarios_response(self, response_content: str) -> List[Dict[str, Any]]:
        """
        Parse the LLM response to extract scenario data.
        
        Args:
            response_content: Raw response from LLM
            
        Returns:
            List of parsed scenario dictionaries
        """
        try:
            # Try to find JSON in the response
            json_start = response_content.find('[')
            json_end = response_content.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_content = response_content[json_start:json_end]
                scenarios = json.loads(json_content)
                
                # Validate and clean scenarios
                validated_scenarios = []
                for i, scenario in enumerate(scenarios):
                    if self._validate_scenario(scenario):
                        validated_scenarios.append(scenario)
                    else:
                        logger.warning(f"Invalid scenario format at index {i}, skipping")
                
                return validated_scenarios
            else:
                # Fallback: try to parse as text-based scenarios
                return self._parse_text_scenarios(response_content)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON scenarios: {e}")
            return self._parse_text_scenarios(response_content)
        except Exception as e:
            logger.error(f"Error parsing scenarios response: {e}")
            return []
    
    def _validate_scenario(self, scenario: Dict[str, Any]) -> bool:
        """
        Validate that a scenario has required fields.
        
        Args:
            scenario: Scenario dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['id', 'category', 'scenario', 'priority']
        
        for field in required_fields:
            if field not in scenario or not scenario[field]:
                return False
        
        # Validate priority values
        if scenario['priority'] not in ['P0', 'P1', 'P2', 'P3', 'P4']:
            return False
        
        return True
    
    def _parse_text_scenarios(self, content: str) -> List[Dict[str, Any]]:
        """
        Fallback method to parse scenarios from text format.
        
        Args:
            content: Text content to parse
            
        Returns:
            List of scenario dictionaries
        """
        try:
            scenarios = []
            scenario_counter = 1
            
            # Split content into potential scenarios
            lines = content.split('\n')
            current_scenario = {}
            
            for line in lines:
                line = line.strip()
                
                # Look for scenario titles or headers
                if any(keyword in line.lower() for keyword in ['scenario', 'test', 'ts']):
                    if current_scenario and 'scenario' in current_scenario:
                        # Finalize previous scenario
                        self._finalize_text_scenario(current_scenario, scenario_counter)
                        scenarios.append(current_scenario)
                        scenario_counter += 1
                    
                    # Start new scenario
                    current_scenario = {
                        'id': f'TS{scenario_counter:03d}',
                        'category': 'Functional',
                        'scenario': line,
                        'priority': 'Medium'
                    }
                elif current_scenario and line:
                    # Add to scenario description
                    if current_scenario['scenario']:
                        current_scenario['scenario'] += ' ' + line
                    else:
                        current_scenario['scenario'] = line
            
            # Don't forget the last scenario
            if current_scenario and 'scenario' in current_scenario:
                self._finalize_text_scenario(current_scenario, scenario_counter)
                scenarios.append(current_scenario)
            
            logger.info(f"Parsed {len(scenarios)} scenarios from text format")
            return scenarios
            
        except Exception as e:
            logger.error(f"Error parsing text scenarios: {e}")
            return []
    
    def _finalize_text_scenario(self, scenario: Dict[str, Any], counter: int):
        """
        Finalize a text-parsed scenario by adding missing fields.
        
        Args:
            scenario: Scenario dictionary to finalize
            counter: Scenario counter for ID generation
        """
        # Ensure ID is set
        if 'id' not in scenario:
            scenario['id'] = f'TS{counter:03d}'
        
        # Determine category based on keywords
        scenario_text = scenario['scenario'].lower()
        if any(keyword in scenario_text for keyword in ['integration', 'api', 'service']):
            scenario['category'] = 'Integration'
        elif any(keyword in scenario_text for keyword in ['user', 'ui', 'interface', 'experience']):
            scenario['category'] = 'User Experience'
        elif any(keyword in scenario_text for keyword in ['data', 'database', 'storage']):
            scenario['category'] = 'Data'
        elif any(keyword in scenario_text for keyword in ['security', 'access', 'auth']):
            scenario['category'] = 'Security'
        elif any(keyword in scenario_text for keyword in ['performance', 'load', 'speed']):
            scenario['category'] = 'Performance'
        else:
            scenario['category'] = 'Functional'
        
        # Determine priority based on keywords
        if any(keyword in scenario_text for keyword in ['critical', 'core', 'main', 'primary']):
            scenario['priority'] = 'High'
        elif any(keyword in scenario_text for keyword in ['important', 'key']):
            scenario['priority'] = 'Medium'
        else:
            scenario['priority'] = 'Medium'
    
    def enhance_scenarios(self, scenarios: List[Dict[str, Any]], 
                         additional_context: str = "") -> List[Dict[str, Any]]:
        """
        Enhance existing scenarios with additional details or context.
        
        Args:
            scenarios: List of existing scenarios
            additional_context: Additional context to consider
            
        Returns:
            Enhanced scenarios
        """
        try:
            logger.info("Enhancing scenarios with additional context")
            
            if not additional_context:
                return scenarios
            
            enhanced_scenarios = []
            for scenario in scenarios:
                try:
                    enhanced_scenario = self._enhance_single_scenario(scenario, additional_context)
                    enhanced_scenarios.append(enhanced_scenario)
                except Exception as e:
                    logger.warning(f"Failed to enhance scenario {scenario.get('id', 'unknown')}: {e}")
                    enhanced_scenarios.append(scenario)  # Keep original if enhancement fails
            
            logger.info(f"Successfully enhanced {len(enhanced_scenarios)} scenarios")
            return enhanced_scenarios
            
        except Exception as e:
            logger.error(f"Error enhancing scenarios: {e}")
            return scenarios  # Return original scenarios if enhancement fails
    
    def _enhance_single_scenario(self, scenario: Dict[str, Any], 
                               additional_context: str) -> Dict[str, Any]:
        """
        Enhance a single scenario with additional details.
        
        Args:
            scenario: Original scenario
            additional_context: Additional context
            
        Returns:
            Enhanced scenario
        """
        prompt = f"""
Enhance the following test scenario based on the additional context:

Original Scenario:
{json.dumps(scenario, indent=2)}

Additional Context:
{additional_context}

Provide an enhanced version with a better scenario description while keeping the same simple format (id, category, scenario, priority).
Keep it high-level and generic.

Return only the enhanced scenario in JSON format.
"""
        
        try:
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            
            # Try to parse enhanced scenario
            enhanced = json.loads(response.content)
            
            # Validate enhanced scenario
            if self._validate_scenario(enhanced):
                return enhanced
            else:
                return scenario
                
        except Exception as e:
            logger.warning(f"Failed to enhance scenario: {e}")
            return scenario 