#******************Author:Somnath Das**********************
#******AWS-CLI should be configured prior to run this******
#Inserting an item into existing DynamoDB table.

import boto3

client = boto3.client('dynamodb')

# Table (bookstore) was already created with Partition Key 'category' and Sort Key as 'bookid' which is unique.
response = client.put_item(
  TableName='bookstore',
  Item={
    #This is the primary key which contains the partition key and sort key
    'category': {'S': 'sci-fi'},
    'bookid': {'S': 'bk002' },
    #Now the other columns to be inserted into the table
    'bookname': {'S': 'Ghanada Samagra'},
    'author': {'S': 'Pemendra Mitra'},
    'yop': {'N': '1980'},
    'language': {'S': 'Bengali'},
    'country': {'S': 'India'}
  }
)
