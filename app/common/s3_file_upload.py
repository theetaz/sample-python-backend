import boto3
from app.config import settings
import re
from fastapi import UploadFile


class S3FileClient:
    s3_instance = None
    instance_type = 's3'
    bucket_name = settings.AWS_S3_BUCKET_NAME

    def __init__(self):
        self.s3_instance = boto3.client(
            self.instance_type,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION
        )

    def upload_file_if_not_exists(self, folder_name, file_name, file_content, content_type):

        # if file name has spaces and special characters, replace them with hyphen using regex
        sanitized_filename = re.sub(r'[^a-zA-Z0-9.]', '-', file_name)
        file_path = f"{folder_name}/{sanitized_filename}"

        try:
            self.s3_instance.head_object(
                Bucket=self.bucket_name, Key=file_path)
            print(f"Checking if file exists: {file_path}")
            return f"https://{self.bucket_name}.s3.amazonaws.com/{file_path}"
        except:
            self.s3_instance.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=file_content,
                ContentType=content_type
            )
            return f"https://{self.bucket_name}.s3.amazonaws.com/{file_path}"

    def upload_file(self, file_name, file_content, content_type):

        # if file name has spaces and special characters, replace them with hyphen using regex
        sanitized_filename = re.sub(r'[^a-zA-Z0-9.]', '-', file_name)

        self.s3_instance.put_object(
            Bucket=self.bucket_name,
            Key=sanitized_filename,
            Body=file_content,
            ContentType=content_type
        )
        return f"https://{self.bucket_name}.s3.amazonaws.com/{sanitized_filename}"

    async def http_to_s3_upload(self, upload_file: UploadFile) -> str:

        upload_file.file.seek(0)
        file_content: UploadFile = await upload_file.read()

        # if file name has spaces and special characters, replace them with hyphen using regex
        sanitized_filename = re.sub(
            r'[^a-zA-Z0-9.]', '-', upload_file.filename)

        self.s3_instance.put_object(
            Bucket=self.bucket_name,
            Key=sanitized_filename,
            Body=file_content,
            ContentType=upload_file.content_type
        )
        return f"https://{self.bucket_name}.s3.amazonaws.com/{sanitized_filename}"

    def delete_file(self, file_name):
        self.s3_instance.delete_object(
            Bucket=self.bucket_name,
            Key=file_name
        )
        return True

    def get_file(self, file_name):
        return self.s3_instance.get_object(
            Bucket=self.bucket_name,
            Key=file_name
        )
