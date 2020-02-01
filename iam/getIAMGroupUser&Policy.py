#********************Author: Somnath Das***********************
#********Please ensure awscli is configured properly***********
#**This script get the IAM group and members & roles***********
#****Account ID,Account Name,Group Name,User Name,Role*********

#Import all dependency modules
import boto3
from botocore.exceptions import ClientError

#Global Variables
acc_id = '12345'
acc_name = "LOREAL AMER"

#Create IAM client & resource objects. Then get all group names.
iam_client = boto3.client('iam')
iam = boto3.resource('iam')

#Create a CSV file with all details.
def getGroupUsersPolicy(group_list):
  print("Getting Groups, Users and Attached Policies. Please wait.....")
  csv_file = open("awsRBACReport.txt","w")
  csv_file.write("Account ID,Account Name,Group Name,User Name,Role\n")
  for group in group_list:
    attch_pl = iam_client.list_attached_group_policies(
      GroupName=group
    )
    grp_pl = []
    for policy in attch_pl['AttachedPolicies']:
      grp_pl.append(policy['PolicyName'])
    group_itr = iam.Group(group)
    user_itr = group_itr.users.all()
    user_list = list(user_itr)
    for user in user_list:
      usr_nm = user.user_name
      grp_pl_txt = ""
      for policy in grp_pl:
        grp_pl_txt += str(policy)
        grp_pl_txt += " + "
      if len(grp_pl_txt) > 1:
        grp_pl_txt = grp_pl_txt[:-2]
      else:
        grp_pl_txt = 'null'
      csv_file.write("%s,%s,%s,%s,%s\n" % (acc_id, acc_name, group, usr_nm, grp_pl_txt))
  csv_file.close()
  print("Created the RBAC report for %d number of groups" % (len(group_list)))

def main():
  group_list = []
  all_grp = iam_client.list_groups()
  for group in all_grp['Groups']:
    group_list.append(str(group['GroupName']))
  getGroupUsersPolicy(group_list)

main()
