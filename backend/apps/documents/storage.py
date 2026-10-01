"""
Supabase Storage Integration for Legal AI
Handles PDF uploads and downloads from Supabase Storage
"""
import os
import logging
from typing import Optional, Tuple
from django.conf import settings
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class SupabaseStorage:
    """Handle file uploads/downloads to Supabase Storage"""
    
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.bucket_name = "legal-documents"  # Storage bucket name
        self.client: Optional[Client] = None
        
    def get_client(self) -> Client:
        """Get or create Supabase client"""
        if not self.client:
            self.client = create_client(self.supabase_url, self.supabase_key)
        return self.client
    
    def ensure_bucket_exists(self) -> bool:
        """Create bucket if it doesn't exist"""
        try:
            client = self.get_client()
            # Try to get bucket
            try:
                client.storage.get_bucket(self.bucket_name)
                logger.info(f"Bucket '{self.bucket_name}' already exists")
                return True
            except Exception:
                # Bucket doesn't exist, create it
                client.storage.create_bucket(
                    self.bucket_name,
                    options={"public": False}  # Private bucket
                )
                logger.info(f"Created bucket '{self.bucket_name}'")
                return True
        except Exception as e:
            logger.error(f"Failed to ensure bucket exists: {str(e)}")
            return False
    
    def upload_file(self, file_path: str, destination_path: str) -> Tuple[bool, Optional[str]]:
        """
        Upload file to Supabase Storage
        
        Args:
            file_path: Local file path to upload
            destination_path: Destination path in bucket (e.g., "cases/1/document.pdf")
            
        Returns:
            Tuple of (success: bool, public_url: Optional[str])
        """
        try:
            # Ensure bucket exists
            if not self.ensure_bucket_exists():
                return False, None
            
            client = self.get_client()
            
            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Upload to Supabase
            response = client.storage.from_(self.bucket_name).upload(
                path=destination_path,
                file=file_data,
                file_options={"content-type": "application/pdf"}
            )
            
            # Get public URL (with authentication)
            public_url = client.storage.from_(self.bucket_name).get_public_url(destination_path)
            
            logger.info(f"✅ Uploaded file to Supabase: {destination_path}")
            return True, public_url
            
        except Exception as e:
            logger.error(f"❌ Failed to upload file to Supabase: {str(e)}")
            return False, None
    
    def upload_file_bytes(self, file_bytes: bytes, destination_path: str, content_type: str = "application/pdf") -> Tuple[bool, Optional[str]]:
        """
        Upload file bytes directly to Supabase Storage
        
        Args:
            file_bytes: File content as bytes
            destination_path: Destination path in bucket
            content_type: MIME type of file
            
        Returns:
            Tuple of (success: bool, public_url: Optional[str])
        """
        try:
            # Ensure bucket exists
            if not self.ensure_bucket_exists():
                return False, None
            
            client = self.get_client()
            
            # Upload to Supabase
            response = client.storage.from_(self.bucket_name).upload(
                path=destination_path,
                file=file_bytes,
                file_options={"content-type": content_type}
            )
            
            # Get public URL
            public_url = client.storage.from_(self.bucket_name).get_public_url(destination_path)
            
            logger.info(f"✅ Uploaded bytes to Supabase: {destination_path}")
            return True, public_url
            
        except Exception as e:
            logger.error(f"❌ Failed to upload bytes to Supabase: {str(e)}")
            return False, None
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """
        Download file from Supabase Storage
        
        Args:
            file_path: Path in bucket to download
            
        Returns:
            File content as bytes or None if failed
        """
        try:
            client = self.get_client()
            file_data = client.storage.from_(self.bucket_name).download(file_path)
            logger.info(f"✅ Downloaded file from Supabase: {file_path}")
            return file_data
        except Exception as e:
            logger.error(f"❌ Failed to download file from Supabase: {str(e)}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from Supabase Storage
        
        Args:
            file_path: Path in bucket to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = self.get_client()
            client.storage.from_(self.bucket_name).remove([file_path])
            logger.info(f"✅ Deleted file from Supabase: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete file from Supabase: {str(e)}")
            return False
    
    def get_signed_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Get signed URL for private file access
        
        Args:
            file_path: Path in bucket
            expires_in: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Signed URL or None if failed
        """
        try:
            client = self.get_client()
            signed_url = client.storage.from_(self.bucket_name).create_signed_url(
                file_path,
                expires_in
            )
            return signed_url.get('signedURL')
        except Exception as e:
            logger.error(f"❌ Failed to get signed URL: {str(e)}")
            return None


# Global instance
supabase_storage = SupabaseStorage()
