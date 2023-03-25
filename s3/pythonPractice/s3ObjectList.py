#********************Author: Somnath Das***********************
#********Please ensure awscli is configured properly***********

import boto3
from botocore.exceptions import ClientError
from colorama import Fore, Back, Style

s3_client = boto3.client('s3')

#Prints available objects in a bucket...
def printBucketContents(bucket_name):
  print("\n***************************************************************************")
  print("Objects available in the selected bucket: %s >>>>" % bucket_name)
  cont_resp = s3_client.list_objects(Bucket=bucket_name)
  for item in cont_resp['Contents']:
    print("\t" + item['Key'] + ' [size in Bytes:', item['Size'], ']')
#Section ends here.

bucket_name = input("Please enter your bucket name: ")

try:
  printBucketContents(bucket_name)
except ClientError as e:
  print(e)
  input("Wait till exit: ")

