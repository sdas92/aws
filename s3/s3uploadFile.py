#********************Author: Somnath Das***********************
#********Please ensure awscli is configured properly***********

import boto3
import logging
import os
from botocore.exceptions import ClientError
from colorama import Fore, Back, Style

s3_client = boto3.client('s3')

def uploadFileToS3(file_name, bucket, object_name):
  response = s3_client.upload_file(file_name, bucket, object_name)

print(Fore.GREEN + "Available files under current directory>>>" + Fore.RESET)
os.system('ls')
file_name = input("Please enter the file name: ")
bucket = input("Please enter the bucket name: ")
object_name = file_name

try:
  uploadFileToS3(file_name, bucket, object_name)
except ClientError as e:
  logging.error(e)
  input("Please enter any key to exit: ")

