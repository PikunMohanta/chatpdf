"""
AWS S3 Storage Manager for PDFPixie
Handles PDF file uploads, downloads, and signed URL generation
"""

import boto3
import os
import logging
from botocore.exceptions import ClientError
from typing import BinaryIO, Optional

logger = logging.getLogger(__name__)


class S3FileManager:
    """
    Manages file operations with AWS S3
    """
    
    def __init__(self):
        """Initialize S3 client with AWS credentials"""
        self.enabled = all([
            os.getenv('AWS_ACCESS_KEY_ID'),
            os.getenv('AWS_SECRET_ACCESS_KEY'),
            os.getenv('S3_BUCKET_NAME')
        ])
        
        if self.enabled:
            self.s3_client = boto3.client(
                's3',
                region_name=os.getenv('AWS_REGION', 'ap-southeast-1'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            self.bucket_name = os.getenv('S3_BUCKET_NAME')
            logger.info(f"S3 storage enabled for bucket: {self.bucket_name}")
        else:
            logger.warning("S3 storage disabled - missing AWS credentials")
    
    async def upload_pdf(self, file_obj: BinaryIO, filename: str, user_id: str = "anonymous") -> dict:
        """
        Upload PDF to S3 with user folder structure
        
        Args:
            file_obj: File object to upload
            filename: Original filename
            user_id: User identifier for folder organization
            
        Returns:
            dict: Upload result with s3_key and signed_url
        """
        if not self.enabled:
            return {
                'success': False,
                'error': 'S3 storage not configured',
                'fallback': 'local'
            }
        
        try:
            # Create key with user folder: user_123/document_abc.pdf
            s3_key = f"{user_id}/{filename}"
            
            # Upload file
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': 'application/pdf',
                    'Metadata': {
                        'user_id': user_id,
                        'original_filename': filename
                    }
                }
            )
            
            logger.info(f"Successfully uploaded {filename} to S3: {s3_key}")
            
            # Generate signed URL (valid for 24 hours)
            signed_url = self._generate_signed_url(s3_key, expires_in=86400)
            
            return {
                'success': True,
                's3_key': s3_key,
                'signed_url': signed_url,
                'bucket': self.bucket_name
            }
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fallback': 'local'
            }
    
    async def download_pdf(self, s3_key: str) -> Optional[bytes]:
        """
        Download PDF from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            bytes: PDF file content or None if failed
        """
        if not self.enabled:
            return None
        
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"Successfully downloaded from S3: {s3_key}")
            return response['Body'].read()
            
        except ClientError as e:
            logger.error(f"S3 download failed: {str(e)}")
            return None
    
    async def delete_pdf(self, s3_key: str) -> bool:
        """
        Delete PDF from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            bool: True if deleted successfully
        """
        if not self.enabled:
            return False
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"Successfully deleted from S3: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 delete failed: {str(e)}")
            return False
    
    def _generate_signed_url(self, s3_key: str, expires_in: int = 3600) -> Optional[str]:
        """
        Generate signed URL for PDF access
        
        Args:
            s3_key: S3 object key
            expires_in: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            str: Signed URL or None if failed
        """
        if not self.enabled:
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expires_in
            )
            return url
            
        except ClientError as e:
            logger.error(f"Failed to generate signed URL: {str(e)}")
            return None
    
    async def get_signed_url(self, s3_key: str, expires_in: int = 3600) -> Optional[str]:
        """
        Public method to get signed URL
        
        Args:
            s3_key: S3 object key
            expires_in: URL expiration time in seconds
            
        Returns:
            str: Signed URL or None if failed
        """
        return self._generate_signed_url(s3_key, expires_in)
    
    def is_enabled(self) -> bool:
        """Check if S3 storage is enabled"""
        return self.enabled


# Global S3 manager instance
s3_manager = S3FileManager()
