#********************Author: Somnath Das***********************
#********Please ensure awscli is configured properly***********

import boto3
#import logging
from botocore.exceptions import ClientError
from colorama import Fore, Back, Style

s3_client = boto3.client('s3')

#Delete an item from your bucket...
def deleteObject(bucket_name, key):
  response = s3_client.delete_object(
    Bucket=bucket_name,
    Key=key
  )
#Method definition ends.

bucket_name = input("Enter your bucket name: ")
obj_name = input("Enter the object name: ")

try:
  deleteObject(bucket_name, obj_name)
  print("Deleted the object {0} from your bucket {1}!".format(obj_name, bucket_name))
except ClientError as e:
  print(e)
  input("Wait till exit: ")

