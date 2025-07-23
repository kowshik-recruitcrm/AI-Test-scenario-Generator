"""Confluence tool for loading PRD content from Confluence pages."""

import logging
from typing import List, Optional
from langchain_community.document_loaders import ConfluenceLoader
from langchain.schema import Document
from config import Config

logger = logging.getLogger(__name__)

class ConfluenceTool:
    """Tool for loading content from Confluence pages."""
    
    def __init__(self):
        """Initialize the Confluence tool with configuration."""
        self.config = Config()
        self.loader = None
        self._initialize_loader()
    
    def _initialize_loader(self):
        """Initialize the Confluence loader with authentication."""
        try:
            self.loader = ConfluenceLoader(
                url=self.config.CONFLUENCE_URL,
                username=self.config.CONFLUENCE_USERNAME,
                api_key=self.config.CONFLUENCE_API_TOKEN,
            )
            logger.info("Confluence loader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Confluence loader: {e}")
            raise
    
    def load_prd_content(self, page_ids: List[str]) -> List[Document]:
        """
        Load PRD content from Confluence pages.
        
        Args:
            page_ids: List of Confluence page IDs to load
            
        Returns:
            List of Document objects containing the loaded content
        """
        try:
            logger.info(f"Loading content from Confluence pages: {page_ids}")
            
            documents = []
            for page_id in page_ids:
                try:
                    # Load specific page by ID
                    page_docs = self.loader.load(page_ids=[page_id])
                    documents.extend(page_docs)
                    logger.info(f"Successfully loaded page {page_id}")
                except Exception as e:
                    logger.error(f"Failed to load page {page_id}: {e}")
                    continue
            
            return documents
            
        except Exception as e:
            logger.error(f"Error loading Confluence content: {e}")
            raise
    
    def load_by_space_and_title(self, space_key: str, page_title: str) -> List[Document]:
        """
        Load content by space key and page title.
        
        Args:
            space_key: Confluence space key
            page_title: Title of the page to load
            
        Returns:
            List of Document objects containing the loaded content
        """
        try:
            logger.info(f"Loading page '{page_title}' from space '{space_key}'")
            
            documents = self.loader.load(
                space_key=space_key,
                include_patterns=[page_title],
                max_pages=1
            )
            
            if documents:
                logger.info(f"Successfully loaded page '{page_title}'")
            else:
                logger.warning(f"No content found for page '{page_title}' in space '{space_key}'")
            
            return documents
            
        except Exception as e:
            logger.error(f"Error loading page by title: {e}")
            raise
    
    def extract_content_summary(self, documents: List[Document]) -> str:
        """
        Extract and summarize content from loaded documents.
        
        Args:
            documents: List of loaded Document objects
            
        Returns:
            Combined content summary as string
        """
        try:
            if not documents:
                return "No content available from Confluence"
            
            content_parts = []
            for doc in documents:
                # Extract metadata
                title = doc.metadata.get('title', 'Untitled')
                url = doc.metadata.get('url', '')
                
                # Add structured content
                content_parts.append(f"=== {title} ===")
                if url:
                    content_parts.append(f"URL: {url}")
                content_parts.append(doc.page_content)
                content_parts.append("=" * 50)
            
            combined_content = "\n\n".join(content_parts)
            logger.info(f"Extracted content summary from {len(documents)} documents")
            
            return combined_content
            
        except Exception as e:
            logger.error(f"Error extracting content summary: {e}")
            return f"Error processing Confluence content: {e}"
    
    def validate_connection(self) -> bool:
        """
        Validate the Confluence connection.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Try to load a simple test - this will validate credentials
            test_docs = self.loader.load(max_pages=1)
            logger.info("Confluence connection validated successfully")
            return True
        except Exception as e:
            logger.error(f"Confluence connection validation failed: {e}")
            return False 