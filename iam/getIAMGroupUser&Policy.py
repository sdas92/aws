#********************Author: Somnath Das***********************
#********Please ensure awscli is configured properly***********
#**This script get the IAM group and members & roles***********

#Import all dependency modules
import boto3
from botocore.exceptions import ClientError

#Global Variables
acc_id = '0123456789'
acc_name = "Your Account Name"

#Create IAM client & resource objects. Then get all group names.
iam_client = boto3.client('iam')
iam = boto3.resource('iam')

#Create a CSV file with all details.
def getGroupUsersPolicy(group_list):
  print("\nGetting Groups, Users and Attached Policies. Please wait.....")
  csv_file = open("awsRBACReport.txt","w")
  csv_file.write("AccountID,AccountName,User's Group Display Name,User SignIn Name,AttachedPolicies\n")
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
  print("\nCreated the RBAC report for %d number of groups" % (len(group_list)))


#Get Users, Attached Policies for non group users.
def nonGroupUsers():
  print("\nGetting users and attached policies for Non Group Users. Please wait.....")
  cntr = 0
  all_usr = iam_client.list_users()
  csv_file = open("awsRBACReport.txt","a")
  for user in all_usr['Users']:
    usr_nm = str(user['UserName'])
    response = iam_client.list_groups_for_user(
      UserName=usr_nm
    )
    if len(response['Groups']) == 0:
      attch_pl = iam_client.list_attached_user_policies(
        UserName=usr_nm
      )
      usr_pl = []
      for policy in attch_pl['AttachedPolicies']:
        usr_pl.append(policy['PolicyName'])
      usr_pl_txt = ""
      for policy in usr_pl:
        usr_pl_txt += str(policy)
        usr_pl_txt += " + "
      if len(usr_pl_txt) > 1:
        usr_pl_txt = usr_pl_txt[:-2]
      else:
        usr_pl_txt = "null"
      csv_file.write("%s,%s,None,%s,%s\n" % (acc_id, acc_name, usr_nm, usr_pl_txt))
      cntr = cntr + 1
  csv_file.close()
  print("\nCreated the RBAC report for %d non group users" % cntr)


#Main method..
def main():
  group_list = []
  all_grp = iam_client.list_groups()
  for group in all_grp['Groups']:
    group_list.append(str(group['GroupName']))
  getGroupUsersPolicy(group_list)
  nonGroupUsers()

main()
