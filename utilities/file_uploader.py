from os import path
from boto3 import client

def upload_file(file_name,bucket_name,object_name,allowed_extensions):
    if not file_name.endswith(tuple(allowed_extensions)):
        raise ValueError(f"File must be one of the following types: {', '.join(allowed_extensions)}")
    if object_name is None:
        object_name = path.basename(file_name)
    s3_client = client('s3')
    with open(file_name, "rb") as f:
        s3_client.upload_file(f, "good-jobs-bucket ", object_name)    
    # s3_client = client('s3', 
    #                   aws_access_key_id='AKIAZ3NAQ3IPJPLBTGHG', 
    #                   aws_secret_access_key='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', 
    #                   region_name='us-east-1'
    #                   )
    # print(s3_client)
    # response = s3_client.upload_file(file_name, bucket_name, object_name)
    # print(response)
