"""Excel tool for loading and processing impacted areas data."""

import logging
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
from config import Config

logger = logging.getLogger(__name__)

class ExcelTool:
    """Tool for loading and processing Excel files containing impacted areas data."""
    
    def __init__(self):
        """Initialize the Excel tool."""
        self.config = Config()
    
    def load_impact_areas(self, excel_path: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Load impacted areas data from Excel file.
        
        Args:
            excel_path: Path to the Excel file
            sheet_name: Specific sheet name to load (optional)
            
        Returns:
            Dictionary containing the loaded data and metadata
        """
        try:
            path = Path(excel_path)
            if not path.exists():
                raise FileNotFoundError(f"Excel file not found: {excel_path}")
            
            logger.info(f"Loading Excel file: {excel_path}")
            
            # Load Excel file
            if sheet_name:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                logger.info(f"Loaded sheet '{sheet_name}' from {path.name}")
            else:
                # Load first sheet if no sheet name specified
                df = pd.read_excel(excel_path)
                logger.info(f"Loaded first sheet from {path.name}")
            
            # Basic data validation
            if df.empty:
                logger.warning(f"Excel file {path.name} is empty")
                return {
                    'data': df,
                    'summary': "Excel file is empty",
                    'row_count': 0,
                    'column_count': 0,
                    'columns': []
                }
            
            # Clean data
            df = self._clean_dataframe(df)
            
            # Generate summary
            summary = self._generate_summary(df, path.name)
            
            result = {
                'data': df,
                'summary': summary,
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': df.columns.tolist(),
                'file_path': excel_path
            }
            
            logger.info(f"Successfully loaded {len(df)} rows and {len(df.columns)} columns")
            return result
            
        except Exception as e:
            logger.error(f"Error loading Excel file {excel_path}: {e}")
            raise
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the dataframe by removing empty rows and columns.
        
        Args:
            df: Input dataframe
            
        Returns:
            Cleaned dataframe
        """
        try:
            # Remove completely empty rows and columns
            df = df.dropna(how='all')
            df = df.dropna(axis=1, how='all')
            
            # Strip whitespace from string columns
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip()
                    # Replace 'nan' strings with actual NaN
                    df[col] = df[col].replace('nan', pd.NA)
            
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning dataframe: {e}")
            return df
    
    def _generate_summary(self, df: pd.DataFrame, filename: str) -> str:
        """
        Generate a comprehensive summary of the Excel data.
        
        Args:
            df: Dataframe to summarize
            filename: Name of the Excel file
            
        Returns:
            Formatted summary string
        """
        try:
            summary_parts = [
                f"=== Excel Data Summary: {filename} ===",
                f"Total Rows: {len(df)}",
                f"Total Columns: {len(df.columns)}",
                "",
                "Column Information:"
            ]
            
            # Add column details
            for col in df.columns:
                non_null_count = df[col].notna().sum()
                data_type = str(df[col].dtype)
                
                # Get unique values for categorical columns (if reasonable number)
                unique_values = ""
                if df[col].dtype == 'object' and df[col].nunique() <= 20:
                    unique_vals = df[col].dropna().unique()
                    if len(unique_vals) > 0:
                        unique_values = f" | Unique values: {', '.join(map(str, unique_vals[:10]))}"
                        if len(unique_vals) > 10:
                            unique_values += "..."
                
                summary_parts.append(
                    f"  - {col}: {non_null_count}/{len(df)} non-null ({data_type}){unique_values}"
                )
            
            # Add sample data preview
            summary_parts.extend([
                "",
                "Sample Data (First 3 rows):",
                str(df.head(3).to_string(index=False))
            ])
            
            # Identify potential impact area columns
            impact_columns = self._identify_impact_columns(df)
            if impact_columns:
                summary_parts.extend([
                    "",
                    "Potential Impact Area Columns:",
                    ", ".join(impact_columns)
                ])
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Error generating summary for {filename}: {e}"
    
    def _identify_impact_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Identify columns that likely contain impact area information.
        
        Args:
            df: Input dataframe
            
        Returns:
            List of column names that likely contain impact information
        """
        impact_keywords = [
            'impact', 'area', 'component', 'module', 'system', 'feature',
            'service', 'api', 'endpoint', 'database', 'table', 'function',
            'class', 'method', 'file', 'page', 'screen', 'workflow'
        ]
        
        impact_columns = []
        
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in impact_keywords):
                impact_columns.append(col)
        
        return impact_columns
    
    def extract_impact_areas_text(self, excel_data: Dict[str, Any]) -> str:
        """
        Extract impact areas as formatted text for LLM processing.
        
        Args:
            excel_data: Dictionary returned from load_impact_areas()
            
        Returns:
            Formatted text describing impact areas
        """
        try:
            df = excel_data['data']
            if df.empty:
                return "No impact areas data available"
            
            text_parts = [
                "=== IMPACTED AREAS ===",
                excel_data['summary'],
                "",
                "Detailed Impact Areas Data:"
            ]
            
            # Convert dataframe to readable format
            for idx, row in df.iterrows():
                row_text = f"Entry {idx + 1}:"
                for col, value in row.items():
                    if pd.notna(value) and str(value).strip():
                        row_text += f"\n  - {col}: {value}"
                text_parts.append(row_text)
                text_parts.append("")
            
            return "\n".join(text_parts)
            
        except Exception as e:
            logger.error(f"Error extracting impact areas text: {e}")
            return f"Error processing impact areas: {e}"
    
    def get_all_sheets(self, excel_path: str) -> List[str]:
        """
        Get all sheet names from an Excel file.
        
        Args:
            excel_path: Path to the Excel file
            
        Returns:
            List of sheet names
        """
        try:
            excel_file = pd.ExcelFile(excel_path)
            sheets = excel_file.sheet_names
            logger.info(f"Found {len(sheets)} sheets in {excel_path}: {sheets}")
            return sheets
            
        except Exception as e:
            logger.error(f"Error reading sheets from {excel_path}: {e}")
            return []
    
    def load_multiple_sheets(self, excel_path: str, sheet_names: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Load multiple sheets from an Excel file.
        
        Args:
            excel_path: Path to the Excel file
            sheet_names: List of specific sheet names to load (optional)
            
        Returns:
            Dictionary mapping sheet names to their data
        """
        try:
            if sheet_names is None:
                sheet_names = self.get_all_sheets(excel_path)
            
            all_sheets_data = {}
            
            for sheet_name in sheet_names:
                try:
                    sheet_data = self.load_impact_areas(excel_path, sheet_name)
                    all_sheets_data[sheet_name] = sheet_data
                    logger.info(f"Successfully loaded sheet: {sheet_name}")
                except Exception as e:
                    logger.error(f"Failed to load sheet {sheet_name}: {e}")
                    continue
            
            return all_sheets_data
            
        except Exception as e:
            logger.error(f"Error loading multiple sheets: {e}")
            return {}
    
    def validate_excel_file(self, excel_path: str) -> bool:
        """
        Validate that the Excel file exists and is readable.
        
        Args:
            excel_path: Path to the Excel file
            
        Returns:
            True if file is valid, False otherwise
        """
        try:
            path = Path(excel_path)
            if not path.exists():
                logger.error(f"Excel file does not exist: {excel_path}")
                return False
            
            if path.suffix.lower() not in ['.xlsx', '.xls']:
                logger.error(f"File is not an Excel file: {excel_path}")
                return False
            
            # Try to read the file
            pd.read_excel(excel_path, nrows=1)
            logger.info(f"Excel file validation successful: {excel_path}")
            return True
            
        except Exception as e:
            logger.error(f"Excel file validation failed for {excel_path}: {e}")
            return False
    
    def save_scenarios_to_excel(self, scenarios: List[Dict[str, Any]], output_path: str) -> str:
        """
        Save generated test scenarios to an Excel file.
        
        Args:
            scenarios: List of scenario dictionaries
            output_path: Path for the output Excel file
            
        Returns:
            Path to the saved file
        """
        try:
            # Filter scenarios to only include the 4 required fields
            simplified_scenarios = []
            for scenario in scenarios:
                simplified_scenario = {
                    'ID': scenario.get('id', ''),
                    'Category': scenario.get('category', ''),
                    'Scenario': scenario.get('scenario', ''),
                    'Priority': scenario.get('priority', '')
                }
                simplified_scenarios.append(simplified_scenario)
            
            # Convert scenarios to DataFrame
            df = pd.DataFrame(simplified_scenarios)
            
            # Ensure output directory exists
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to Excel with formatting
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Test_Scenarios', index=False)
                
                # Get the workbook and worksheet
                worksheet = writer.sheets['Test_Scenarios']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 80)  # Increased max width for scenario column
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Make header row bold
                for cell in worksheet[1]:
                    cell.font = cell.font.copy(bold=True)
            
            logger.info(f"Successfully saved {len(scenarios)} scenarios to {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error saving scenarios to Excel: {e}")
            raise 