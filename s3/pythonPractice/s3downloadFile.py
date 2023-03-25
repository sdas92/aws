import boto3
import logging
import os
from botocore.exceptions import ClientError
from colorama import Fore, Back, Style

s3_client = boto3.client('s3')

#Download a file from S3 bucket..
def downloadFileFromS3(bucket, object_name, file_name):
  response = s3_client.download_file(bucket, object_name, file_name)
  return response
#Method ends.

print(Fore.GREEN + "Available files under current directory before downloading>>>" + Fore.RESET)
os.system('ls')
object_name = input("Please enter the file name to downlaod: ")
bucket = input("Please enter the bucket name: ")
file_name = object_name

try:
  response = downloadFileFromS3(bucket, object_name, file_name)
  print("Download was successful. Please check the below listing>>")
  os.system('ls')
except ClientError as e:
  logging.error(e)
  input("Please enter any key to exit: ")

