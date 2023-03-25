#********************Author: Somnath Das***********************
#********Please ensure awscli is configured properly***********
#**We can perform several operations on S3 bucket interactively

import os
import boto3
from botocore.exceptions import ClientError
from colorama import Fore, Back, Style

s3_client = boto3.client('s3')

#Select an item from list...
def selectItemfromList(get_list, call_name):
  print("\n************************************************************")
  print("Now please select a/an %s from available list of %s \b(s)>>" % (call_name, call_name))
  len_get_list = len(get_list)
  if len_get_list == 0:
    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("The %s list is empty!" % call_name)
    input("Please enter any character to continue: ")
    return ""
  elif len_get_list >= 1:
    print("\nAvailable %s \b(s) in your list:\nIndex" % call_name)
    for aa in range(0,len_get_list):
      print(aa, end=' ')
      print(get_list[aa])
    while True:
      print("Please choose an index number of %s from 0 to %d as showon above: " % (call_name, len_get_list-1), end='')
      try:
        chs_item = int(input())
      except:
        print(Fore.RED+"That is not a valid number, Try again...."+Fore.RESET)
        continue
      if chs_item >= 0 and chs_item < len_get_list:
        sel_item = get_list[chs_item]
        break
      else:
        print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Wrong input, please choose an index number in given range!"+Fore.RESET)
        input("Please enter any character to continue: ")
    if call_name == "XXX" or call_name == "YYY":
      return sel_item, chs_item
    else:
      return sel_item
#Item selection Ends.


#Uploads a file to the S3 bucket...
def uploadFileToS3(file_name, bucket_name, object_name):
  print("\n***************************************************************************")
  try:
    print("Uploading your file: %s to selected bucket: %s. Please wait...." % (file_name, bucket_name))
    response = s3_client.upload_file(file_name, bucket_name, object_name)
  except ClientError as e:
    print(Fore.RED, e, Fore.RESET)
    input("Please enter any key to continue: ")
#Upload ends.


#Returns a list of available buckets...
def getBucketList():
  bkt_list = []
  print("\n***************************************************************************")
  print("Getting all bucket details. Please wait....")
  bkt_resp = s3_client.list_buckets()
  for bucket in bkt_resp['Buckets']:
    bkt_list.append(bucket['Name'])
  return bkt_list
#Method ends.


#Prints available buckets' dettails...
def printBuckets():
  print("\n***************************************************************************")
  print("Getting all bucket details. Please wait....")
  bkt_resp = s3_client.list_buckets()
  print("Total available buckets:", len(bkt_resp['Buckets']))
  for bucket in bkt_resp['Buckets']:
    create_date = str(bucket['CreationDate'])
    bkt_nm = bucket['Name']
    print(Fore.GREEN + bkt_nm + Fore.RESET + " was created on: " + create_date + " and owner is: " + Fore.CYAN + bkt_resp['Owner']['DisplayName'] + Fore.RESET)
#Bucket print ends.


#Gets a list of all objects from a selected bucket...
def getObjectList(bucket_name):
  obj_list = []
  print("\n***************************************************************************")
  print("Getting all object details. Please wait...")
  cont_resp = s3_client.list_objects(Bucket=bucket_name)
  for item in cont_resp['Contents']:
    obj_list.append(item['Key'])
  return obj_list
#Method ends.


#Prints available objects in a bucket...
def printBucketContents(bucket_name):
  print("\n***************************************************************************")
  print("Objects available in the selected bucket: %s >>>>" % bucket_name)
  cont_resp = s3_client.list_objects(Bucket=bucket_name)
  for item in cont_resp['Contents']:
    print("\t" + item['Key'] + ' [size in Bytes:', item['Size'], ']')
#Section ends here.


#Create a new bucket...
def createBucket(bucket_name):
  print("\n***************************************************************************")
  print("Creating your bucket. Please wait...")
  s3_client.create_bucket(Bucket=bucket_name)
#Method definition ends.


#Delete your bucket...
def deleteBucket(bucket_name):
  print("\n***************************************************************************")
  print("Deleting your bucket. Please wait...")
  s3_client.delete_bucket(Bucket=bucket_name)
#Method definition ends.


#Download a file from S3 bucket..
def downloadFileFromS3(bucket_name, object_name, file_name):
  print("\n***************************************************************************")
  print("Downloading your file. Please wait...")
  response = s3_client.download_file(bucket_name, object_name, file_name)
#Method ends.


#Delete an item/file from your bucket...
def deleteObject(bucket_name, object_name):
  print("\n***************************************************************************")
  print("Deleting your file from S3 bucket. Please wait...")
  response = s3_client.delete_object(
    Bucket=bucket_name,
    Key=object_name
  )
#Method definition ends.


#Main function definition...
def main():
  while True:
    print("\n***************************************************************************")
    print('''1. List all buckets.
2. Display all objects in selected bucket.
3. Create a S3 bucket.
4. Delete a S3 bucket.
5. Upload a local file to S3-bucket.
6. Download a file from S3-bucket.
7. Delete a file from S3 bucket.
911. Quit!
''')
    try:
      prog_exe = int(input("Enter your choice: "))
    except:
      print(Fore.RED + "That is not a valid input! Try again!!" + Fore.RESET)
      input("Enter any key to continue: ")
      continue
    if prog_exe == 1:
      printBuckets()
    elif prog_exe == 2:
      bkt_list = getBucketList()
      if len(bkt_list) >= 1:
        call_name = 'Bucket'
        bucket_name = selectItemfromList(bkt_list, call_name)
        try:
          printBucketContents(bucket_name)
        except KeyError:
          print("No object found in the selected bucket!")
          input("Enter any key to continue: ")
          continue
      else:
        print(Fore.RED + "No bucket found in your account in the selected region!" + Fore.RESET)
        input("Enter any key to continue: ")
        continue
    elif prog_exe == 3:
      bucket_name = input("Enter your bucket name: ")
      try:
        createBucket(bucket_name)
        print("Bucket: %s was created successfully." % bucket_name)
      except ClientError as e:
        print(e)
        input("Enter any key to continue: ")
    elif prog_exe == 4:
      input("\n**Please make sure the bucket is empty. Enter any character. ")
      print("Please select a bucket to delete>>")
      bkt_list = getBucketList()
      if len(bkt_list) >= 1:
        call_name = 'Bucket'
        bucket_name = selectItemfromList(bkt_list, call_name)
        try:
          deleteBucket(bucket_name)
          print("Deleted the bucket: %s" % bucket_name)
        except ClientError as e:
          print(e)
          input("Enter any key to continue: ")
      else:
        print(Fore.RED + "No bucket found in your account in the selected region!" + Fore.RESET)
        input("Enter any key to continue: ")
        continue
    elif prog_exe == 5:
      bkt_list = getBucketList()
      if len(bkt_list) >= 1:
        call_name = 'Bucket'
        bucket_name = selectItemfromList(bkt_list, call_name)
        print(Fore.GREEN + "Available files under current directory>>>" + Fore.RESET)
        os.system('ls')
        file_name = input("Please enter the file name: ")
        object_name = file_name
        try:
          uploadFileToS3(file_name, bucket_name, object_name)
          print(Fore.GREEN, "Your file:'{0}' has been uploaded into bucket: '{1}'".format(file_name, bucket_name), Fore.RESET)
        except (FileNotFoundError) as e:
          print(e)
          input("Enter any key to continue: ")
      else:
        print(Fore.RED + "No bucket found in your account in the selected region!" + Fore.RESET)
        input("Enter any key to continue: ")
    elif prog_exe == 6:
      bkt_list = getBucketList()
      if len(bkt_list) >= 1:
        call_name = 'Bucket'
        bucket_name = selectItemfromList(bkt_list, call_name)
        try:
          obj_list = getObjectList(bucket_name)
        except KeyError:
          print("No object found in the selected bucket!")
          input("Enter any key to continue: ")
          continue
        call_name = 'Object'
        object_name = selectItemfromList(obj_list, call_name)
        file_name = object_name
        try:
          downloadFileFromS3(bucket_name, object_name, file_name)
          print("Download was successful. Please check the below listing>>")
          os.system('ls')
        except ClientError as e:
          print(e)
          input("Enter any key to continue: ")
      else:
        print(Fore.RED + "No bucket found in your account in the selected region!" + Fore.RESET)
        input("Enter any key to continue: ")
        continue
    elif prog_exe == 7:
      bkt_list = getBucketList()
      if len(bkt_list) >= 1:
        call_name = 'Bucket'
        bucket_name = selectItemfromList(bkt_list, call_name)
        try:
          obj_list = getObjectList(bucket_name)
        except KeyError:
          print("No object found in the selected bucket!")
          input("Enter any key to continue: ")
          continue
        call_name = 'Object'
        object_name = selectItemfromList(obj_list, call_name)
        try:
          deleteObject(bucket_name, object_name)
          print("Deleted the object {0} from your bucket {1}!".format(object_name, bucket_name))
        except ClientError as e:
          print(e)
          input("Enter any key to continue: ")
      else:
        print(Fore.RED + "No bucket found in your account in the selected region!" + Fore.RESET)
        input("Enter any key to continue: ")
        continue
    elif prog_exe == 911:
      print("Exit from program requested! Enter any key to exit: ", end='')
      input()
      break
    else:
      print(Fore.RED + "That is an invalid option! Please try again..." + Fore.RESET)
      continue
#Main method ends.

main()
print("Thanks from Somnath _/\_ \n")
