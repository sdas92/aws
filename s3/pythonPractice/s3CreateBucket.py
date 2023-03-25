#********************Author: Somnath Das***********************
#********Please ensure awscli is configured properly***********

import boto3
#import logging
from botocore.exceptions import ClientError
from colorama import Fore, Back, Style

s3_client = boto3.client('s3')

#Create a new bucket...
def createBucket(bucket_name):
  s3_client.create_bucket(Bucket=bucket_name)
#Method definition ends.

bucket_name = input("Enter your bucket name: ")
try:
  createBucket(bucket_name)
  print("Bucket: %s was created successfully." % bucket_name)
except ClientError as e:
  print(e)
  input("Wait till exit: ")

