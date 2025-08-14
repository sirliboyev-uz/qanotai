"""
Storage service for handling audio file uploads to S3/DigitalOcean Spaces
"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self):
        """Initialize S3/Spaces client"""
        self.client = boto3.client(
            's3',
            endpoint_url=settings.SPACES_ENDPOINT,
            aws_access_key_id=settings.SPACES_KEY,
            aws_secret_access_key=settings.SPACES_SECRET,
            region_name=settings.SPACES_REGION
        )
        self.bucket = settings.SPACES_BUCKET
    
    async def generate_upload_url(
        self,
        key: str,
        content_type: str = "audio/webm",
        expires_in: int = None
    ) -> str:
        """
        Generate a presigned URL for uploading a file
        
        Args:
            key: S3/Spaces object key
            content_type: MIME type of the file
            expires_in: URL expiration time in seconds
        
        Returns:
            Presigned upload URL
        """
        if expires_in is None:
            expires_in = settings.UPLOAD_URL_EXPIRY
        
        try:
            url = self.client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': key,
                    'ContentType': content_type
                },
                ExpiresIn=expires_in
            )
            logger.info(f"Generated upload URL for {key}")
            return url
        except ClientError as e:
            logger.error(f"Failed to generate upload URL: {e}")
            raise
    
    async def generate_download_url(
        self,
        key: str,
        expires_in: int = 3600
    ) -> str:
        """
        Generate a presigned URL for downloading a file
        
        Args:
            key: S3/Spaces object key
            expires_in: URL expiration time in seconds
        
        Returns:
            Presigned download URL
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': key
                },
                ExpiresIn=expires_in
            )
            logger.info(f"Generated download URL for {key}")
            return url
        except ClientError as e:
            logger.error(f"Failed to generate download URL: {e}")
            raise
    
    async def delete_file(self, key: str) -> bool:
        """
        Delete a file from storage
        
        Args:
            key: S3/Spaces object key
        
        Returns:
            True if successful
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"Deleted file {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    async def get_file_metadata(self, key: str) -> Optional[Dict]:
        """
        Get metadata for a file
        
        Args:
            key: S3/Spaces object key
        
        Returns:
            File metadata or None if not found
        """
        try:
            response = self.client.head_object(Bucket=self.bucket, Key=key)
            return {
                'size': response['ContentLength'],
                'content_type': response.get('ContentType'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag')
            }
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.warning(f"File not found: {key}")
                return None
            logger.error(f"Failed to get file metadata: {e}")
            raise
    
    async def download_file(self, key: str) -> bytes:
        """
        Download a file from storage
        
        Args:
            key: S3/Spaces object key
        
        Returns:
            File content as bytes
        """
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            content = response['Body'].read()
            logger.info(f"Downloaded file {key}")
            return content
        except ClientError as e:
            logger.error(f"Failed to download file: {e}")
            raise