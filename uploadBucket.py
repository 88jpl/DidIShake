import boto3
from boto3 import session
# from botocore.client import Config
from boto3.s3.transfer import S3Transfer

# env variables import
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# assign env to global variable
ACCESS_KEY = os.environ.get("do-spaces-key")
SECERET_ACCESS_KEY = os.environ.get("do-spaces-seceret-api-key")
ENDPOINT_URL = os.environ.get("do-spaces-endpoint-url")
SPACE =  os.environ.get("do-spaces-space")


class UploadImage:
    
    # saving to quaker/public/
    def uploadSingleToSpace(self, filePath, fileName):
        mySession = session.Session()
        client = mySession.client('s3',
                                region_name='sfo3', 
                                endpoint_url=ENDPOINT_URL,
                                aws_access_key_id=ACCESS_KEY,
                                aws_secret_access_key=SECERET_ACCESS_KEY)
        transfer = S3Transfer(client)
        # switch to dynamic file naming not static
        transfer.upload_file(fileName, SPACE, filePath+"/"+fileName)
        response = client.put_object_acl(ACL='public-read', Bucket=SPACE, Key="%s/%s" % (filePath, fileName))
        return response
    
