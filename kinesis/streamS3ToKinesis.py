#***Author: Somnath Das***
#**S3 open data set https://s3.amazonaws.com/aft-vbi-pds/index.html
#***AWS-CLI should be configured


import os
import boto3
import json
import secrets
from botocore.exceptions import ClientError
from colorama import Fore, Back, Style

src_bucket = 'aft-vbi-pds'
sku = 'BIN_FCSKU_DATA'

s3_client = boto3.client('s3')
kinesis_client = boto3.client('kinesis')


#Puts data into the kinesis stream...
def putDataIntoKinesis(csv_content, part_key, stream_name):
  try:
    response = kinesis_client.put_record(
      StreamName=stream_name,
      Data=csv_content,
      PartitionKey=part_key
    )
    return response['ResponseMetadata']['HTTPStatusCode']
  except ClientError as e:
    print(Fore.RED, e, Fore.RESET)
    input("Enter any key to continue: ")
    return 0
#Kinesis push ends.


#Fetch data from S3 as JSON, convert it as CSV and pushes into Kinesis Stream...
def dataOperation(file_counter, stream_name):
  s3_key = 'metadata/' + file_counter + '.json'
  csv_content = ""
  part_key = ""
  s3_object = s3_client.get_object(Bucket=src_bucket, Key=s3_key)
  json_payload = json.loads(s3_object['Body'].read())  #Loading the object content as JSON (dictionary) variable.
  for item in json_payload[sku]:
    product_name = ''
    for character in json_payload[sku][item]['name']:
      if character != ',' and character != "\\" and character != '"':
        product_name = product_name + character
    #Generating CSV format from JSON object
    try:
      csv_content = "{0},{1},{2},{3},{4},{5},{6},{7},{8}".format(product_name,
			json_payload[sku][item]['asin'],
			json_payload[sku][item]['length']['unit'], json_payload[sku][item]['length']['value'],
			json_payload[sku][item]['height']['unit'], json_payload[sku][item]['height']['value'],
			json_payload[sku][item]['width']['unit'], json_payload[sku][item]['width']['value'],
			json_payload[sku][item]['quantity'])
    except TypeError as e:
      continue
    rand_no = secrets.randbelow(999)
    part_key = 'pk-' + file_counter + '-' + item + '-' + str(rand_no)
    response = putDataIntoKinesis(csv_content, part_key, stream_name)
    if response == 200:
      print(">>>>>>>>>>>>>>>>>>>>>>>>>>")
      print(Fore.GREEN, "Pushed data: ", csv_content, Fore.RESET, '\n')
    elif response == 0:
      print("Kinesis error occurred!! Try again later!")
      break
#Data operation ends.


#Main function definition...
def main():
  while True:
    print("\n***************************************************************************")
    json_counter = 100001
    print("1. Perform data push from S3 to Kinesis.\n9. Quit!")
    try:
      prog_exe = int(input("Please enter your choice: "))
    except:
      print(Fore.RED + "That is not a valid input! Try again!!" + Fore.RESET)
      input("Enter any key to continue: ")
      continue
    if prog_exe == 1:
      print("\nHow many records do you want to fetch and push into Kinesis Stream? ")
      try:
        loop_counter = int(input("Please enter the number: "))
      except:
        print(Fore.RED + "That is not a valid input! Try again!!" + Fore.RESET)
        input("Enter any key to continue: ")
        continue
      stream_name = input("Please enter your Kinesis Stream name: ")
      for aa in range(0, loop_counter):
        str_jsn_cntr = str(json_counter)
        file_counter = str_jsn_cntr[1:]
        dataOperation(file_counter, stream_name)
        json_counter = json_counter + 1
    elif prog_exe == 9:
      input("Exit has been requested! Please enter any key: ")
      break
    else:
      print(Fore.RED + "That is not a valid input! Try again!!" + Fore.RESET)
      input("Enter any key to continue: ")
      continue
#Main function ends.

main()
print("Thanks from Somnath _/\_ \n\n")
