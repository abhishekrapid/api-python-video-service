from extensions import (
    os
)
import boto3


class VideoProvider:
    def __init__(self):
        self.provider = os.getenv('video_provider')
        if self.provider == 'aws':
            self.provider_client = boto3.client(service_name=os.getenv('aws_storage_name'),
                                                region_name=os.getenv('aws_region_name'),
                                                aws_access_key_id=os.getenv('aws_access_key_id'),
                                                aws_secret_access_key=os.getenv('aws_secret_access_key'))

    def delete_video(self, file_name):
        if self.provider == 'aws':
            response = self.provider_client.delete_object(Bucket=os.getenv('aws_bucket'), Key=file_name)
            print(response)

    def delete_videos(self, file_name_list):
        if self.provider == 'aws':
            response = self.provider_client.delete_objects(
                Bucket=os.getenv('aws_bucket'),
                Delete={"Objects": file_name_list},
            )
            print(response)

    def generate_pre_signed_url(self, file_name):
        return self.provider_client.generate_presigned_post(
            Bucket=os.getenv('aws_bucket'),
            Key=file_name,
            ExpiresIn=120
        )

    def generate_url(self, file_name):
        return self.provider_client.generate_presigned_url('get_object',
                                                           Params={'Bucket': os.getenv('aws_bucket'), 'Key': file_name},
                                                           ExpiresIn=50)

    def download_video_from_provider(self, file_name, server_path):
        try:
            self.provider_client.download_file(os.getenv('aws_bucket'), file_name, server_path)
            return True
        except Exception as e:
            print(e)
            return False