#********************Author: Somnath Das***********************
#********Please ensure awscli is configured properly***********

import boto3
from botocore.exceptions import ClientError
from colorama import Fore, Back, Style

s3_client = boto3.client('s3')

#Prints available buckets' dettails...
def printBuckets():
  bkt_resp = s3_client.list_buckets()
  print("Getting all bucket details. Please wait....")
  print("Total available buckets:", len(bkt_resp['Buckets']))
  for bucket in bkt_resp['Buckets']:
    create_date = str(bucket['CreationDate'])
    bkt_nm = bucket['Name']
    print(Fore.GREEN + bkt_nm + Fore.RESET + " was created on: " + create_date + " and owner is: " + Fore.CYAN + bkt_resp['Owner']['DisplayName'] + Fore.RESET)
#Bucket print ends.


printBuckets()
