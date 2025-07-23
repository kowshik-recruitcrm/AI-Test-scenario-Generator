"""Image tool for processing feature images and extracting information."""

import logging
import base64
from typing import List, Dict, Any
from pathlib import Path
from PIL import Image
import io
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from config import Config

logger = logging.getLogger(__name__)

class ImageTool:
    """Tool for processing and analyzing feature images."""
    
    def __init__(self):
        """Initialize the Image tool with Gemini Vision model."""
        self.config = Config()
        self.vision_model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Gemini Vision model."""
        try:
            self.vision_model = ChatGoogleGenerativeAI(
                model="gemini-2.5-pro",  # Google Gemini 2.5 Pro with vision
                google_api_key=self.config.GOOGLE_API_KEY,
                temperature=self.config.TEMPERATURE
            )
            logger.info("Gemini Vision model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Vision model: {e}")
            raise
    
    def load_images(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Load and validate images from file paths.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of dictionaries containing image data and metadata
        """
        loaded_images = []
        
        for image_path in image_paths:
            try:
                path = Path(image_path)
                if not path.exists():
                    logger.warning(f"Image file not found: {image_path}")
                    continue
                
                # Validate image format
                try:
                    with Image.open(image_path) as img:
                        # Convert to RGB if necessary
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Resize if too large (max 4MP for Gemini)
                        max_size = (2048, 2048)
                        if img.size[0] * img.size[1] > 4000000:
                            img.thumbnail(max_size, Image.Resampling.LANCZOS)
                        
                        # Convert to base64
                        buffer = io.BytesIO()
                        img.save(buffer, format='JPEG', quality=85)
                        image_data = base64.b64encode(buffer.getvalue()).decode()
                        
                        loaded_images.append({
                            'path': image_path,
                            'filename': path.name,
                            'data': image_data,
                            'format': 'JPEG',
                            'size': img.size
                        })
                        
                        logger.info(f"Successfully loaded image: {path.name}")
                
                except Exception as e:
                    logger.error(f"Failed to process image {image_path}: {e}")
                    continue
                    
            except Exception as e:
                logger.error(f"Error loading image {image_path}: {e}")
                continue
        
        logger.info(f"Loaded {len(loaded_images)} images successfully")
        return loaded_images
    
    def analyze_images(self, images: List[Dict[str, Any]]) -> str:
        """
        Analyze images using Gemini Vision to extract feature information.
        
        Args:
            images: List of image dictionaries from load_images()
            
        Returns:
            Combined analysis of all images as string
        """
        try:
            if not images:
                return "No images provided for analysis"
            
            analyses = []
            
            for idx, image in enumerate(images, 1):
                try:
                    # Create prompt for feature analysis
                    prompt = """
                    Analyze this UI/feature image and provide detailed information about:
                    
                    1. **UI Components**: What UI elements, buttons, forms, menus are visible?
                    2. **User Interactions**: What user actions/interactions are possible?
                    3. **Feature Functionality**: What feature or functionality does this represent?
                    4. **Data Flow**: What data inputs/outputs are visible?
                    5. **User Experience**: What is the expected user journey/workflow?
                    6. **Edge Cases**: What potential edge cases or error scenarios can you identify?
                    7. **Integration Points**: What external systems or components might be involved?
                    
                    Provide a comprehensive analysis that would help in creating test scenarios.
                    """
                    
                    # Prepare message with image
                    message = HumanMessage(
                        content=[
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image['data']}"
                                }
                            }
                        ]
                    )
                    
                    # Get analysis from Gemini Vision
                    response = self.vision_model.invoke([message])
                    
                    analysis = f"""
=== Image Analysis {idx}: {image['filename']} ===
File: {image['path']}
Size: {image['size'][0]}x{image['size'][1]}

{response.content}

{"=" * 60}
"""
                    analyses.append(analysis)
                    logger.info(f"Successfully analyzed image: {image['filename']}")
                    
                except Exception as e:
                    logger.error(f"Failed to analyze image {image['filename']}: {e}")
                    analyses.append(f"Error analyzing {image['filename']}: {e}")
                    continue
            
            combined_analysis = "\n\n".join(analyses)
            logger.info(f"Completed analysis of {len(images)} images")
            
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Error in image analysis: {e}")
            return f"Error analyzing images: {e}"
    
    def extract_ui_elements(self, images: List[Dict[str, Any]]) -> List[str]:
        """
        Extract specific UI elements from images for test scenario creation.
        
        Args:
            images: List of image dictionaries
            
        Returns:
            List of identified UI elements
        """
        try:
            if not images:
                return []
            
            ui_elements = []
            
            for image in images:
                try:
                    prompt = """
                    Extract and list all UI elements visible in this image. Focus on:
                    - Buttons and their labels
                    - Input fields and forms
                    - Navigation menus
                    - Dialog boxes and modals
                    - Tables and lists
                    - Links and clickable elements
                    
                    Return a simple bullet-point list of UI elements.
                    """
                    
                    message = HumanMessage(
                        content=[
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image['data']}"
                                }
                            }
                        ]
                    )
                    
                    response = self.vision_model.invoke([message])
                    ui_elements.append(f"From {image['filename']}: {response.content}")
                    
                except Exception as e:
                    logger.error(f"Failed to extract UI elements from {image['filename']}: {e}")
                    continue
            
            return ui_elements
            
        except Exception as e:
            logger.error(f"Error extracting UI elements: {e}")
            return []
    
    def validate_images(self, image_paths: List[str]) -> Dict[str, bool]:
        """
        Validate that all provided image paths are accessible and valid.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Dictionary mapping image paths to validation status
        """
        validation_results = {}
        
        for image_path in image_paths:
            try:
                path = Path(image_path)
                if not path.exists():
                    validation_results[image_path] = False
                    continue
                
                # Try to open and validate the image
                with Image.open(image_path) as img:
                    # Basic validation - check if it's a valid image
                    img.verify()
                    validation_results[image_path] = True
                    
            except Exception as e:
                logger.error(f"Image validation failed for {image_path}: {e}")
                validation_results[image_path] = False
        
        return validation_results 