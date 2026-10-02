"""
Supabase Storage Integration for Legal AI
Handles PDF uploads and downloads from Supabase Storage
Based on Nexus project architecture - user_id/doc_id.pdf structure
"""
import os
import logging
from typing import Optional, Tuple
from django.conf import settings

logger = logging.getLogger(__name__)

class SupabaseStorage:
    """Handle file uploads/downloads to Supabase Storage"""
    
    def __init__(self):
        try:
            self.supabase_url = settings.SUPABASE_URL
            self.supabase_key = settings.SUPABASE_KEY
            self.bucket_name = "pdfs"  # Match Nexus project bucket name
            self.client = None
            
            # Validate credentials on init
            if not self.supabase_url or not self.supabase_key:
                logger.error(f"❌ CRITICAL: Supabase credentials missing! URL={bool(self.supabase_url)}, KEY={bool(self.supabase_key)}")
            else:
                logger.info(f"✅ SupabaseStorage initialized with URL: {self.supabase_url[:30]}...")
        except Exception as e:
            logger.error(f"❌ CRITICAL: SupabaseStorage __init__ failed: {e}", exc_info=True)
            raise
        
    def get_client(self):
        """Get or create Supabase client"""
        try:
            if not self.client:
                from supabase import create_client, Client
                logger.info(f"🔌 Creating Supabase client for {self.supabase_url[:30]}...")
                self.client = create_client(self.supabase_url, self.supabase_key)
                logger.info("✅ Supabase client created successfully")
            return self.client
        except Exception as e:
            logger.error(f"❌ CRITICAL: Failed to create Supabase client: {e}", exc_info=True)
            raise
    
    def ensure_bucket_exists(self) -> bool:
        """
        Create bucket if it doesn't exist
        Uses 'pdfs' bucket name (matching Nexus project)
        Bucket should be PRIVATE with RLS policies
        """
        try:
            logger.info(f"📦 Checking if bucket '{self.bucket_name}' exists...")
            client = self.get_client()
            
            # Try to get bucket
            try:
                bucket = client.storage.get_bucket(self.bucket_name)
                logger.info(f"✅ Bucket '{self.bucket_name}' already exists")
                return True
            except Exception as get_error:
                # Bucket doesn't exist, try to create it
                logger.warning(f"⚠️  Bucket doesn't exist: {get_error}, attempting to create...")
                try:
                    # Create PRIVATE bucket (not public)
                    # Access control via storage paths: {user_id}/{doc_id}.pdf
                    client.storage.create_bucket(
                        self.bucket_name,
                        options={"public": False}  # Private bucket with path-based access
                    )
                    logger.info(f"✅ Created PRIVATE bucket '{self.bucket_name}'")
                    return True
                except Exception as create_error:
                    logger.error(f"❌ Failed to create bucket: {create_error}", exc_info=True)
                    logger.warning("💡 You need to manually create the 'pdfs' bucket in Supabase Dashboard")
                    return False
        except Exception as e:
            logger.error(f"❌ CRITICAL: ensure_bucket_exists failed: {e}", exc_info=True)
            return False
    
    def upload_pdf(self, user_id: int, doc_id: int, file_bytes: bytes, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Upload PDF to Supabase Storage
        Storage path: {user_id}/{doc_id}.pdf (Nexus-style structure)
        
        Args:
            user_id: Django user ID
            doc_id: Document ID
            file_bytes: PDF file content as bytes
            filename: Original filename (for logging)
            
        Returns:
            Tuple of (success: bool, storage_path: Optional[str])
        """
        try:
            # Storage path: user_id/doc_id.pdf
            storage_path = f"{user_id}/{doc_id}.pdf"
            logger.info(f"🚀 Uploading PDF: {filename} → {storage_path} ({len(file_bytes)} bytes)")
            
            # Ensure bucket exists
            if not self.ensure_bucket_exists():
                logger.error("❌ Bucket not ready, cannot upload")
                return False, None
            
            client = self.get_client()
            
            # Upload to Supabase Storage
            logger.info(f"📤 Uploading to Supabase Storage...")
            response = client.storage.from_(self.bucket_name).upload(
                path=storage_path,
                file=file_bytes,
                file_options={
                    "content-type": "application/pdf",
                    "cache-control": "3600"
                }
            )
            
            logger.info(f"✅ Upload successful! Path: {storage_path}")
            return True, storage_path
            
        except Exception as e:
            logger.error(f"❌ CRITICAL: upload_pdf failed for {filename}: {e}", exc_info=True)
            return False, None
    
    def get_signed_url(self, storage_path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Get signed URL for PDF access (for private buckets)
        
        Args:
            storage_path: Path in bucket (e.g., "123/456.pdf")
            expires_in: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Signed URL or None if failed
        """
        try:
            logger.info(f"🔗 Generating signed URL for {storage_path}...")
            client = self.get_client()
            
            result = client.storage.from_(self.bucket_name).create_signed_url(
                storage_path,
                expires_in
            )
            
            if result and 'signedURL' in result:
                signed_url = result['signedURL']
                logger.info(f"✅ Signed URL generated: {signed_url[:50]}...")
                return signed_url
            else:
                logger.error(f"❌ No signed URL in response: {result}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get signed URL for {storage_path}: {e}", exc_info=True)
            return None
    
    def download_pdf(self, storage_path: str) -> Optional[bytes]:
        """
        Download PDF from Supabase Storage
        
        Args:
            storage_path: Path in bucket (e.g., "123/456.pdf")
            
        Returns:
            File content as bytes or None if failed
        """
        try:
            logger.info(f"📥 Downloading PDF from {storage_path}...")
            client = self.get_client()
            file_data = client.storage.from_(self.bucket_name).download(storage_path)
            logger.info(f"✅ Downloaded {len(file_data)} bytes from Supabase")
            return file_data
        except Exception as e:
            logger.error(f"❌ Failed to download from Supabase: {e}", exc_info=True)
            return None
    
    def delete_pdf(self, storage_path: str) -> bool:
        """
        Delete PDF from Supabase Storage
        
        Args:
            storage_path: Path in bucket to delete (e.g., "123/456.pdf")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"🗑️  Deleting {storage_path} from Supabase...")
            client = self.get_client()
            client.storage.from_(self.bucket_name).remove([storage_path])
            logger.info(f"✅ Deleted from Supabase: {storage_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete from Supabase: {e}", exc_info=True)
            return False


# Global instance
supabase_storage = SupabaseStorage()
