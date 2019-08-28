#This program performs major tasks of ec2 and elbv2
#This is written by Somnath Das
#Please make sure aws-cli is configured properly. This program do not require any credentials externally.

import sys
import boto3
from botocore.exceptions import ClientError
from colorama import Fore, Back, Style

ec2 = boto3.resource('ec2')
client = boto3.client('ec2')
elb = boto3.client('elbv2')
atscl = boto3.client('autoscaling')
vpc_id = ""




#|||Method declarations starts here....
#This section selects an string item from given list and returns selected str...
def selectItemfromList(get_list, call_name):
	print("\n************************************************************")
	print("Now please select a/an %s from available list of %s \b(s)>>" % (call_name, call_name))
	len_get_list = len(get_list)
	if len_get_list == 0:
		print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("The %s list is empty!" % call_name)
		input("Please enter any character to exit: ")
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
		if call_name == "Aso-Subnet":
			return sel_item, chs_item
		else:
			return sel_item
#Selection of an item from list ends and returns str.

#This section creates a new sublist with selected items from a bigger list...
def selectPartialList(get_list, call_name):
	sel_list = []
	new_list = []
	print("\n************************************************************")
	print("Now please select one or more %s \b(s) from available list of %s \b(s)>>" % (call_name, call_name))
	len_get_list = len(get_list)
	for aa in range(0, len_get_list):
		new_list.append(get_list[aa])
	while True:
		len_new_list = len(new_list)
		if len_new_list == 0:
			print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print("No %s is available to select, Exiting from selection!" % call_name, Fore.RESET)
			input("Please enter any character to exit: ")
			break
		print("\nAvailable %s(s) to choose from:\nIndex" % call_name)
		for aa in range(0, len_new_list):
			print(aa, end=' ')
			print(new_list[aa])
		print("Please choose an index from 0 to %d from above list: " %(len_get_list-1), end='')
		try:
			chs_index = int(input())
		except:
			print(Fore.RED+"That is not a valid number, Try again...."+Fore.RESET)
			continue
		if chs_index >= 0 and chs_index < len_get_list:
			sel_list.append(new_list[chs_index])
			new_list[chs_index:chs_index+1] = []
		else:
			print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print("Wrong input, please choose an index number from given range!"+Fore.RESET)
			input("Please enter any character to continue: ")
		print("\nDo you want to add more "+call_name+" now? \nEnter 'y' to add further item or any other key to exit: ", end='')
		yn_check = input()
		if yn_check == "y" or yn_check == "Y":
			continue
		else:
			print("\nOkay! Exit has been requested from selection process!")
			break
	return sel_list
#This ends sublist generation from main list and returns list.

#This section creates a custom VPC...
def createVPC():
	print("\n********************************************************")
	print("This is VPC creation wizard")
	print("********************************************************")
	print("Please enter a name for the new VPC: ", end='')
	vpc_nm = str(input())
	print("Please enter the CIDR block for new VPC(format: x.x.x.x/x ): ", end='')
	vpc_cidr_blk = str(input())
	print("Creating VPC...............")
	vpc = ec2.create_vpc(CidrBlock=vpc_cidr_blk)
	vpc.create_tags(Tags=[{"Key": "Name", "Value": "%s" % vpc_nm}])
	created_vpcid = str(vpc.id)
	return created_vpcid
#VPC creation ends and Returns str.

#This section lists all the available VPCs...
def getVPCs():
	list_vpc = []
	print("Please wait while getting the VPC list...........")
	response = client.describe_vpcs()
	for item in response["Vpcs"]:
		list_vpc.append(item["VpcId"])
	return list_vpc
#VPC listing ends and returns list.

#This section selects a VPC from available list...
def chooseVPC():
	get_vpc = getVPCs()
	len_get_vpc = len(get_vpc)
	if len_get_vpc == 0:
		print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No VPC is available, please create a VPC first> ")
		input("Please enter any character to continue: ")
		sel_vpc_id = createVPC()
	elif len_get_vpc >= 1:
		call_name = "VPC"
		sel_vpc_id = selectItemfromList(get_vpc, call_name)
	return sel_vpc_id
#VPC ID selection ends and returns str.

#This block deletes a VPC.
def deleteVPC():
	print(Fore.RED+"********************************************************")
	print("You are now going to VPC: %s! It will delete related items! Please be careful!")
	print("You are now into VPC:", vpc_id)
	print("********************************************************"+Fore.RESET)
	input("Please enter any character to continue: ")
	running_instlist = getRunningInstances()
	if len(running_instlist) >= 1:
		print("There are one or more running instance(s) in this VPC, so can't delete the VPC!")
		input("Please enter any character to exit: ")
		return ""
	elif len(running_instlist) == 0:
		print("Do you really want to delete the VPC? y/n: ", end='')
		yn_check = input()
		if yn_check == "y" or yn_check == "Y":
			response = client.delete_vpc(VpcId=vpc_id)
			print("Deleted VPC: ", vpc_id)
			return "DELVPC"
		else:
			print("Abort!")
			return ""
#This end VPC deletion block.

#This section lists availability zones...
def getAZs():
	az_list = []
	print("Please wait while getting the AZ list...........")
	response = client.describe_availability_zones()
	for item in response['AvailabilityZones']:
		if item['State'] == 'available':
			az_list.append(item['ZoneName'])
	return az_list
#Section ends and returns list.

#This section selects an availability zone...
def chooseAZ():
	az_list = getAZs()
	call_name = "AvailabilityZone"
	az_name = selectItemfromList(az_list, call_name)
	return az_name
#This ends AZ selection and returns str.

#This section creates a subnet in selected VPC...
def createSubnet():
	print("\n********************************************************")
	print("This is Subnet creation wizard")
	print("********************************************************")
	print("Please enter a name for the new subnet: ", end='')
	sub_nm = str(input())
	print("\nPlease select an Availability Zone first>")
	az_name = chooseAZ()
	print("\nPlease enter the CIDR block for new Subnet(format: x.x.x.x/x ): ", end='')
	sub_cidr_blk = str(input())
	print("Creating Subnet.....................")
	subnet = ec2.create_subnet(AvailabilityZone=az_name, CidrBlock=sub_cidr_blk, VpcId=vpc_id)
	subnet.create_tags(Tags=[{"Key": "Name", "Value": "%s" % sub_nm}])
	created_subnet = str(subnet.id)
	print("Do you want to auto enable public IP assignemnet? y/n: ", end='')
	yn_ip = input()
	if yn_ip == "y" or yn_ip == "Y":
		response = client.modify_subnet_attribute(
			MapPublicIpOnLaunch={
				'Value': True
			},
			SubnetId=created_subnet
		)
		print("Public IP assignemnet will be auto enabled for this subnet: ", created_subnet)
	else:
		print("Public IP assignemnet will be disabled for this subnet: ", created_subnet)
	return created_subnet
#Subnet creation ends and returns str.

#This section lists available subnets in selected VPC...
def getSubnets():
	available_subnets = []
	print("Please wait while getting the Subnet list...........")
	response = client.describe_subnets(
		Filters=[
			{
				'Name': 'vpc-id',
				'Values': [vpc_id]
			},
		]
	)
	for item in response["Subnets"]:
		available_subnets.append(item["SubnetId"])
	return available_subnets
#Listing subnets ends and returns a list.

#This section will choose a subnet...
def chooseSubnet():
	get_subnet = getSubnets()
	len_get_subnet = len(get_subnet)
	if len_get_subnet == 0:
		print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No subnet is available in the selected VPC: %s, please create a subnet first> " % vpc_id)
		input("Please enter any character to continue: ")
		subnet_id = createSubnet()
	elif len_get_subnet >= 1:
		call_name = "Subnet"
		subnet_id = selectItemfromList(get_subnet, call_name)
	return subnet_id
#This ends subnet selection and returns str.

#This section deletes a Subnet...
def deleteSubnet():
	print("********************************************************")
	print("You are now going to a Subnet! Please be careful!")
	print("********************************************************")
	input("Please enter any character to continue: ")
	subnet_list = getSubnets()
	if len(subnet_list) == 0:
		print("No subnet found in your selected VPC: ", vpc_id)
		input("Enter any character to exit: ")
		return ""
	elif len(subnet_list) >= 1:
		running_instlist = []
		call_name = "Subnet"
		subnet_id = selectItemfromList(subnet_list, call_name)
		resp = client.describe_instances(
			Filters=[
				{
					'Name': 'subnet-id',
					'Values': [subnet_id]
				},
				{
					'Name': 'instance-state-name',
					'Values': ['running']
				},
			]
		)
		for reservation in resp["Reservations"]:
			for instance in reservation["Instances"]:
				running_instlist.append(instance["InstanceId"])
		if len(running_instlist) >= 1:
			print("Cannot delete the selected Subnet: %s as one or more running instance(s) are found in this subnet!" % subnet_id)
			return ""
		elif len(running_instlist) == 0:
			response = client.delete_subnet(SubnetId=subnet_id)
			print("Deleted Subnet: ", subnet_id)
			return "Done"
#This ends subnet deletion.

#This section creates an IGW and attaches it to a VPC...
def createIGW():
	print("\n********************************************************")
	print("This is Internet Gateway creation wizard.")
	print("********************************************************")
	print("Please enter the name for your IGW: ", end='')
	ig_nm = str(input())
	print("Creating IGW..............")
	ig = ec2.create_internet_gateway()
	ig.create_tags(Tags=[{"Key": "Name", "Value": "%s" % ig_nm}])
	vpc = ec2.Vpc(vpc_id)
	vpc.attach_internet_gateway(InternetGatewayId=ig.id)
	ig_id = str(ig.id)
	print("\nAttached IGW: %s with VPC: %s" % (ig_id, vpc_id))
	return ig_id
#This ends IGW creation and returns str.

#This section returns the IGW IDs in selected VPC...
def getIGWs():
	available_igw = []
	print("Please wait while getting the IGW list...........")
	response = client.describe_internet_gateways(
		Filters=[
			{
				'Name': 'attachment.vpc-id',
				'Values': [vpc_id]
			},
		]
	)
	for item in response['InternetGateways']:
		available_igw.append(item['InternetGatewayId'])
	return available_igw
#This ends IGW listing and returns list.

#This section gets an IGW ID with given VPC ID...
def chooseIGW():
	get_igw = getIGWs()
	len_get_ig = len(get_igw)
	if len_get_ig == 0:
		print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No IGW found to be attached with the VPC, please create an IGW then>>")
		input("Please enter any character to continue: ")
		ig_id = createIGW()
	elif len_get_ig >= 1:
		call_name = "IGW"
		ig_id = selectItemfromList(get_igw, call_name)
	return ig_id
#This ends IGW selection and returns str.

#This section detaches a IGW from current VPC.
def detachIGW():
	print("********************************************************")
	print("You are now going to detach an IGW from current VPC: %s! Please be careful!" % vpc_id)
	print("********************************************************")
	input("Please enter any character to continue: ")
	igw_list = getIGWs()
	if len(igw_list) == 0:
		print("No IGW is attached to current VPC:", vpc_id)
		input("Please enter any character to exit: ")
		return ""
	elif len(igw_list) >= 1:
		call_name = "InternetGateway"
		ig_id = selectItemfromList(igw_list, call_name)
		response = client.detach_internet_gateway(
			InternetGatewayId=ig_id,
			VpcId=vpc_id
		)
		print("IGW: %s has been detached from VPC: %s" % (ig_id, vpc_id))
		return "Done"
#This section ends here.

#This section deletes an IGW.
def deleteIGW():
	print("********************************************************")
	print("You can delete an IGW which is not attached to any VPC.")
	print("********************************************************")
	input("Please enter any character to continue: ")
	resp = client.describe_internet_gateways()
	igw_list = []
	for item in resp['InternetGateways']:
		if len(item['Attachments']) == 0:
			igw_list.append(item['InternetGatewayId'])
	if len(igw_list) == 0:
		print("No IGW found in your account which is completely detached from all VPCs!")
		input("Please enter any character to exit: ")
		return ""
	elif len(igw_list) >= 1:
		call_name = "InternetGateway"
		ig_id = selectItemfromList(igw_list, call_name)
		response = client.delete_internet_gateway(InternetGatewayId=ig_id)
		print("Deleted IGW: ", ig_id)
		return "Done"
#This ends the block.

#This section creates a custom RT in selected VPC...
def createRT():
	print("\n********************************************************")
	print("This is Route Table creation wizard.")
	print("********************************************************")
	print("Please enter a name for your route table: ", end='')
	rt_nm = str(input())
	vpc = ec2.Vpc(vpc_id)
	rt = vpc.create_route_table()
	rt.create_tags(Tags=[{"Key": "Name", "Value": "%s" % rt_nm}])
	print("Do you want to attach IGW to this route table? y/n: ", end='')
	yn_rt = input()
	if yn_rt == "y" or yn_rt == "Y":
		print("Please enter the destination CIDR block(format: x.x.x.x/x ): ", end='')
		rt_cidr = str(input())
		ig_id = chooseIGW()
		route = rt.create_route(
			DestinationCidrBlock=rt_cidr,
			GatewayId=ig_id
		)
	else:
		print("IGW route is skipped for this RT!")
	rt_id = str(rt.id)
	return rt_id
#RT creation ends here and returns str.

#This section gets RT list in selected VPC...
def getRTs():
	available_rt = []
	print("Please wait while getting the RT list...........")
	response = client.describe_route_tables(
		Filters=[
			{
				'Name': 'vpc-id',
				'Values': [vpc_id]
			},
		]
	)
	for item in response['RouteTables']:
		available_rt.append(item['RouteTableId'])
	return available_rt
#RT list generation ends here and returns list.

#This section selects a RT in selected VPC...
def chooseRT():
	get_rt = getRTs()
	len_get_rt = len(get_rt)
	if len_get_rt == 0:
		print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No RT is found in your VPC: %s, please create a RT then> " % vpc_id)
		input("Please enter any character to continue: ")
		rt_id = createRT()
	elif len_get_rt >= 1:
		call_name = "RouteTable"
		rt_id = selectItemfromList(get_rt, call_name)
	return rt_id
#This ends RT selection and returns str.

#This section associates a subnet in RT(Requires a RT ID and Subnet ID as input)...
def rtSubAssociate():
	tmp_sub = ""
	rt_list = getRTs()
	subnet_list = getSubnets()
	if len(rt_list) == 0:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No route table is found! Please create a RT first and make sure you have minimum one Subnet, then run Subnet Assocoaition again!"+Fore.RESET)
		input("Please enter any character to exit: ")
		return ""
	if len(subnet_list) == 0:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No Subnet is found! Please create a Subnet first and make sure you have minimum one RT, then run Subnet Assocoaition again!"+Fore.RESET)
		input("Please enter any character to exit: ")
		return ""
	call_name = "RouteTable"
	rt_id = selectItemfromList(rt_list, call_name)
	call_name = "Subnet"
	subnet_id = selectItemfromList(subnet_list, call_name)
	response = client.describe_route_tables(
		Filters=[
			{
				'Name': 'route-table-id',
				'Values': [rt_id]
			},
		]
	)
	for item in response['RouteTables']:
		rt_sub = item['Associations']
	match_flag = "no"
	for item in rt_sub:
		for item1 in item:
			if item1 == "SubnetId":
				match_flag = "yes"
		if match_flag == "yes":
			tmp_sub = item['SubnetId']
		elif match_flag == "no":
			tmp_sub = ""
	if tmp_sub == subnet_id:
		print(Fore.GREEN+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("The subnet: %s is already associated with RT: %s!" % (subnet_id, rt_id), Fore.RESET)
		input("Please enter any character to exit: ")
		return "Already associated!"
	print("Please wait while task is being performed.........")
	rt_aso = ec2.RouteTable(rt_id)
	rt_aso.associate_with_subnet(SubnetId=subnet_id)
	print("Associated Subnet:"+subnet_id+" in RT:"+rt_id)
	return "Done"
#Subnet association ends here.

#This section deletes a subnet association with RT...
def rtDeleteAsso():
	print("********************************************************")
	print("You are now going to de-associate a subnet from selected RT! Please be careful!")
	print("********************************************************")
	input("Please enter any character to continue: ")
	rt_list = getRTs()
	if len(rt_list) == 0:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No RT found in your VPC: ", vpc_id, Fore.RESET)
		input("Please enter any character to exit: ")
		return ""
	elif len(rt_list) >= 1:
		call_name = "RouteTable"
		rt_id = selectItemfromList(rt_list, call_name)
		associated_subnets = []
		rt_aso_ids = []
		aso_sub_ids = []
		resp = client.describe_route_tables(
			Filters=[
				{
					'Name': 'route-table-id',
					'Values': [rt_id]
				},
			]
		)
		for item in resp['RouteTables']:
			associated_subnets = (item['Associations'])
		for item in associated_subnets:
			rt_aso_ids.append(item['RouteTableAssociationId'])
			aso_sub_ids.append(item['SubnetId'])
		if len(aso_sub_ids) == 0:
			print("No subnet is associated with this RT: ", rt_id)
			input("Please enter any character to exit: ")
			return ""
		elif len(aso_sub_ids) >= 1:
			call_name = "Aso-Subnet"
			print("Please select the subnet which you want to remove from RT association.")
			input("Please enter any character to continue: ")
			subnet_id, chs_index = selectItemfromList(aso_sub_ids, call_name)
			rt_aso_id = rt_aso_ids[chs_index]
			rt_aso = ec2.RouteTableAssociation(rt_aso_id)
			response = rt_aso.delete()
			print("Deleted subnet association of Subnet: %s from RT: %s" % (subnet_id, rt_id))
			return "Done"
#This ends the block.

#This section deletes a toute from a RT.
def deleteRoute():
	print("********************************************************")
	print("You are now going to de-associate a subnet from selected RT! Please be careful!")
	print("********************************************************")
	input("Please enter any character to continue: ")
	rt_list = getRTs()
	if len(rt_list) == 0:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No RT found in your VPC: ", vpc_id, Fore.RESET)
		input("Please enter any character to exit: ")
		return ""
	elif len(rt_list) >= 1:
		print("Please select a RT first to delete a route from that RT>>")
		call_name = "RouteTable"
		rt_id = selectItemfromList(rt_list, call_name)
		resp = client.describe_route_tables(
			Filters=[
				{
					'Name': 'route-table-id',
					'Values': [rt_id]
				},
			]
		)
		rt_routes = []
		for item in resp['RouteTables']:
			rt_routes = item['Routes']
		if len(rt_routes) == 0:
			print("No routes found in RT:", rt_id)
			input("Please enter any character to exit: ")
			return ""
		elif len(rt_routes) >= 1:
			rt_dest_cidrs = []
			print("The routes in RT: %s are as below:" % rt_id)
			for item in rt_routes:
				print(item)
			for item in rt_routes:
				rt_dest_cidrs.append(item['DestinationCidrBlock'])
			call_name = "DestinationCidrBlock"
			rt_sel_cidr = selectItemfromList(rt_dest_cidrs, call_name)
			response = client.delete_route(
				DestinationCidrBlock=rt_sel_cidr,
				RouteTableId=rt_id
			)
			print("Deleted the selected route from RT:", rt_id)
			return "Done"
#This ends the block.

#This section deletes a route table...
def deleteRT():
	print("********************************************************")
	print("You are now going to delete a RT! Please be careful!")
	print("********************************************************")
	input("Please enter any character to continue: ")
	rt_list = getRTs()
	if len(rt_list) == 0:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No RT found in your VPC: ", vpc_id, Fore.RESET)
		input("Please enter any character to exit: ")
		return ""
	elif len(rt_list) >= 1:
		print("Please select a RT which you want to delete>>")
		call_name = "RouteTable"
		rt_id = selectItemfromList(rt_list, call_name)
		response = client.delete_route_table(RouteTableId=rt_id)
		print("Deleted RT: ", rt_id)
		return rt_id
#This ends the RT deletion block.

#This section creates security group in selected VPC...
def createSG():
	print("\nThis is Security Group creation wizard.")
	print("Please enter a security group name: ", end='')
	sg_nm = str(input())
	print("Please enter a description(about this SG) string: ", end='')
	sg_dscrp = str(input())
	sec_grp = ec2.create_security_group(GroupName=sg_nm, Description=sg_dscrp, VpcId=vpc_id)
	print("Please define Inbound rule as prompted below. Please note, outbound rule will be open for all traffic to everywhere.")
	print("Please enter the CIDR(format: x.x.x.x/x) for inbound rule: ", end='')
	sg_cidr = str(input())
	print("Please enter the protocol name(tcp/udp/icmp): ", end='')
	sg_proto = str(input())
	print("Please enter the port number to open: ", end='')
	sg_port = int(input())
	print("Please wait while creating SG......")
	sec_grp.authorize_ingress(
		CidrIp=sg_cidr,
		IpProtocol=sg_proto,
		FromPort=sg_port,
		ToPort=sg_port
	)
	sg_id = str(sec_grp.id)
	return sg_id
#This ends SG creation and returns str.

#This section gets security group list in selected VPC...
def getSGs():
	available_sg = []
	print("Getting the SG list...........")
	response = client.describe_security_groups(
		Filters=[
			{
				'Name': 'vpc-id',
				'Values': [vpc_id]
			},
		]
	)
	for item in response['SecurityGroups']:
		available_sg.append(item['GroupId'])
	return available_sg
#SG lising ends here and returns list.

#This sections creates a sublist of available SGs...
def chooseSGs():
	get_sg = getSGs()
	call_name = "SecurityGroups"
	sel_sg = selectPartialList(get_sg, call_name)
	return sel_sg
#Selection of security groups ends here and returns list.

#This section deletes a SG...
def deleteSG():
	print("********************************************************")
	print("You are now going to delete a SG! Please be careful!")
	print("********************************************************")
	sg_list = getSGs()
	if len(sg_list) == 0:
		print("No Sg is available to delete!")
		input("Enter any character to exit from this wizard: ")
		return ""
	elif len(sg_list) >= 1:
		call_name = "SecurityGroup"
		sg_id = selectItemfromList(sg_list, call_name)
		response = client.delete_security_group(GroupId=sg_id)
		print("Deleted SG: ", sg_id)
		return sg_id
#This ends SG deletion block.

#This section creates an application load balancer...
def createLB():
	print("\n********************************************************")
	print("This wizard creates a new load balancer.")
	print("********************************************************")
	print("Please note: you can select two or more subnets but no two subnets should belong in same AZ. That means, you need to choose the subnets whose AZs are defferent from each other.")
	input("Please enter any character to continue: ")
	print("\n##You need to select atleast two or more subnets and all should belong to different AZs!##")
	subnet_list = getSubnets()
	sel_sub = []
	len_sub = len(subnet_list)
	if len_sub == 0:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No subnet is found, you need to create atleast two subnets in different AZ first! Please run Subnet creattion wizard before LB creation!"+Fore.RESET)
		input("Please enter any character to exit from LB creation: ")
		return ""
	elif len_sub == 1:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("Only one subnet is found in VPC, you need to create atleast one more subnet in other AZ first! Please run Subnet creattion wizard before LB creation!"+Fore.RESET)
		input("Please enter any character to exit from LB creation: ")
		return ""
	elif len_sub >= 2:
		while True:
			all_match_flag = "sameaz"
			print("\nPlease take a note of available subnets and their respective AZs before Subnet selection. Please make sure you select two or more subnets from different availability zones!")
			print("SubnetID\tAZ_Name")
			for bb in range(0,len_sub):
				first_sub = str(subnet_list[bb])
				resp1 = client.describe_subnets(SubnetIds=[first_sub])
				for item in resp1['Subnets']:
					check1 = item['AvailabilityZone']
				print("%s\t%s" % (first_sub, check1))
				for aa in range(bb+1,len_sub):
					next_subs = str(subnet_list[aa])
					resp2 = client.describe_subnets(SubnetIds=[next_subs])
					for item in resp2['Subnets']:
						check2 = item['AvailabilityZone']
					if check1 != check2:
						all_match_flag = "difaz"
						break
			if all_match_flag == "sameaz":
				print(Fore>RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
				print("All Subnets belong to single AZ: %s, No Subnet found from any other AZ! Please create another Subnet in other AZ then run LB creation again!" % check2, Fore.RESET)
				input("Please enter any character to continue: ")
				return ""
				break
			call_name = "Subnet"
			sel_sub = selectPartialList(subnet_list, call_name)
			len_sel_sub = len(sel_sub)
			if len_sel_sub < 2:
				print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
				print("You need to select atleast two subnets to proceed, please select two subnets>>"+Fore.RESET)
				input("Please enter any character to continue: ")
				continue
			elif len_sel_sub >= 2:
				match_flag = "no"
				for bb in range(0,len_sel_sub):
					first_sub = str(sel_sub[bb])
					resp1 = client.describe_subnets(SubnetIds=[first_sub])
					for item in resp1['Subnets']:
						check1 = item['AvailabilityZone']
					for aa in range(bb+1,len_sel_sub):
						next_subs = str(sel_sub[aa])
						resp2 = client.describe_subnets(SubnetIds=[next_subs])
						for item in resp2['Subnets']:
							check2 = item['AvailabilityZone']
						if check1 == check2:
							match_flag = "yes"
							break
				if match_flag == "no":
					break
				elif match_flag == "yes":
					print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
					print("Two or more Subnets are in same AZ: %s, please choose the subnets again>>" % check2, Fore.RESET)
					input("Please enter any character to continue: ")
					continue
	print("Please enter a name for the new load balancer: ", end='')
	lb_name = str(input())
	sel_sg = chooseSGs()
	print("Creating LB.................")
	response = elb.create_load_balancer(
		Name=lb_name,
		Subnets=sel_sub,
		SecurityGroups=sel_sg,
		Scheme='internet-facing',
		IpAddressType='ipv4'
	)
	for item in response['LoadBalancers']:
		lb_arn = item['LoadBalancerArn']
		lb_dns = item['DNSName']
	print("\n********************************************************")
	print(Fore.RED+"Please note your load balancer DNS: ", lb_dns, Fore.RESET)
	print("Created LB ARN: ", lb_arn)
	input("Please enter any character to exit now: ")
	return lb_arn
#This ends LB creation and returns str.

#This section lists LBs...
def getLBs():
	lb_arn = []
	print("Getting the LB list............")
	response = elb.describe_load_balancers()
	for item in response['LoadBalancers']:
		if item['VpcId'] == vpc_id:
			lb_arn.append(item['LoadBalancerArn'])
	return lb_arn
#LB listing ends here and returns list.

#This section selects a LB...
def chooseLB():
	get_lb = getLBs()
	len_get_lb = len(get_lb)
	if len_get_lb == 0:
		print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No load balancer is found, please create one now>>")
		input("Please enter any character to continue: ")
		lb_arn = createLB()
	elif len_get_lb >= 1:
		call_name = "LoadBalancer"
		lb_arn = selectItemfromList(get_lb, call_name)
	return lb_arn
#This finishes lb selection and returns str.

#This section deletes a LB...
def deleteLB():
	print("********************************************************")
	print("You are now going to delete a LB! Please be careful!")
	print("********************************************************")
	lb_list = getLBs()
	if len(lb_list) == 0:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No load balancer is found in VPC: ", vpc_id, Fore.RESET)
		input("Enter any character to exit from this wizard: ")
		return ""
	elif len(lb_list) >= 1:
		call_name = "LoadBalancer"
		lb_arn = selectItemfromList(lb_list, call_name)
		response = elb.delete_load_balancer(LoadBalancerArn=lb_arn)
		print("Deleted LB: ", lb_arn)
		return lb_arn
#This ends LB deletion block.

#This creates a target group...
def createTG():
	print("\n********************************************************")
	print("This is Target Group creation wizard.")
	print("********************************************************")
	print("Please enter your target group name: ", end='')
	tg_name = str(input())
	while True:
		print("\nFor HTTP(80) target group enter '1' or '2' for HTTPS(443): ", end='')
		yn_tg_proto = int(input())
		if yn_tg_proto == 1:
			tg_proto = "HTTP"
			print("Okay '%s' target group has been selected." % tg_proto)
			tg_port = 80
			break
		elif yn_tg_proto == 2:
			tg_proto = "HTTPS"
			print("Okay '%s' takes group has been selected." % tg_proto)
			tg_port = 443
			break
		else:
			print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print("Wrong input, please enter either '1' or '2'!"+Fore.RESET)
			input("Please enter any character to continue: ")
	print("Please enter health check path: ", end='')
	health_path = str(input())
	print("Please enter health check interval(sec.): ", end='')
	health_interval = int(input())
	print("Please enter health check timeout(sec.): ", end='')
	health_timeout = int(input())
	print("Please enter the healthy threshold count number: ", end='')
	healthy_cnt = int(input())
	print("Please enter unhealthy threshold count number: ", end='')
	unhealthy_cnt = int(input())
	print("Creating TG.................")
	response = elb.create_target_group(
		Name=tg_name,
		Protocol=tg_proto,
		Port=tg_port,
		VpcId=vpc_id,
		HealthCheckProtocol=tg_proto,
		HealthCheckEnabled=True,
		HealthCheckPath=health_path,
		HealthCheckIntervalSeconds=health_interval,
		HealthCheckTimeoutSeconds=health_timeout,
		HealthyThresholdCount=healthy_cnt,
		UnhealthyThresholdCount=unhealthy_cnt,
		TargetType='instance'
	)
	for item in response['TargetGroups']:
		tg_arn = item['TargetGroupArn']
	return tg_arn
#This ends TG creation and returns str.

#This lists available TGs...
def getTGs():
	tg_arn = []
	print("Please wait while getting the list.........")
	response = elb.describe_target_groups()
	for item in response['TargetGroups']:
		if item['VpcId'] == vpc_id:
			tg_arn.append(item['TargetGroupArn'])
	return tg_arn
#Listing TGs ends here and returns list.

#This section selects a TG...
def chooseTG():
	get_tg = getTGs()
	len_get_tg = len(get_tg)
	if len_get_tg == 0:
		print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No target group is found, please create one now>>")
		input("Please enter any character to continue: ")
		tg_arn = createTG()
	elif len_get_tg >= 1:
		call_name = "TargetGroup"
		tg_arn = selectItemfromList(get_tg, call_name)
	return tg_arn
#TG selection ends here and returns str.

#This section creates a target listener for a load balancer...
def createListener(tg_arn):
	lb_arn = chooseLB()
	response = elb.describe_target_groups(
		TargetGroupArns=[tg_arn]
	)
	for item in response['TargetGroups']:
		tg_proto = item['Protocol']
		tg_port = item['Port']
	print("Creating the TG-LB listener.......")
	response = elb.create_listener(
		LoadBalancerArn=lb_arn,
		Protocol=tg_proto,
		Port=tg_port,
		DefaultActions=[
			{
				'Type': 'forward',
				'TargetGroupArn':tg_arn
			},
		]
	)
	print(response["Listeners"])
#TG listener creation ends here and no return item.

#This section registers instances into the selected TG...
def registerTargets():
	runinst_list = getRunningInstances()
	len_runinst = len(runinst_list)
	if len_runinst == 0:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No running instance is found in the VPC. Please follow 'launch instance' step first!"+Fore.RESET)
		input("Please enter any character to exit: ")
		return ""
	tg_list = getTGs()
	if len(tg_list) == 0:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No Target Group found! Please create a TG and make sure your have one running instance in same VPC to run this wizard again!"+Fore.RESET)
		input("Please enter any character to exit: ")
		return ""
	print("\n********************************************************")
	print("Choose one or more running instances to register those instances in TG. \n Please select the instances and a target group.")
	print("********************************************************")
	call_name = "RunningInstance"
	sel_runinst = selectPartialList(runinst_list, call_name)
	len_sel_runinst = len(sel_runinst)
	call_name = "TargetGroup"
	tg_arn = selectItemfromList(tg_list, call_name)
	rgstrd_insts = []
	tmp_list = []
	response = elb.describe_target_health(TargetGroupArn=tg_arn)
	for item in response['TargetHealthDescriptions']:
		tmp_list.append(item['Target'])
	for item in tmp_list:
		rgstrd_insts.append(item['Id'])
	for aa in range(0, len_sel_runinst):
		match_flag = "no"
		runinst_id = str(sel_runinst[aa])
		if len(rgstrd_insts) >= 1:
			for item in rgstrd_insts:
				if item == runinst_id:
					match_flag = "yes"
					break
		if match_flag == "yes":
			print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print("Instance: %s is already registered in this TG, so skipping registration of current instance and proceeding to register next instance(s) if there is/are more selected instances left!" % runinst_id, Fore.RESET)
			input("Please enter any character to continue: ")
			continue
		response = elb.register_targets(
			TargetGroupArn=tg_arn,
			Targets=[
				{
					'Id':runinst_id,
				},
			]
		)
	return "Instances are registered in TG: Done"
#This ends TG-Instance registration.

#This section deregisters an instance from a TG...
def deregisterTarget():
	print("********************************************************")
	print("You are now going to remove an instance from its registered target group! Please be careful!")
	print("********************************************************")
	input("Please enter any character to continue: ")
	tg_list = getTGs()
	if len(tg_list) == 0:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No target group is found in VPC: ", vpc_id, Fore.RESET)
		input("Enter any character to exit from this wizard: ")
		return ""
	elif len(tg_list) >= 1:
		call_name = "TargetGroup"
		tg_arn = selectItemfromList(tg_list, call_name)
		rgstrd_insts = []
		tmp_list = []
		response = elb.describe_target_health(TargetGroupArn=tg_arn)
		for item in response['TargetHealthDescriptions']:
			tmp_list.append(item['Target'])
		for item in tmp_list:
			rgstrd_insts.append(item['Id'])
		if len(rgstrd_insts) == 0:
			print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print("This target group has no(zero) registered instance!")
			input("Enter any character to exit from this wizard: ")
			return ""
		elif len(rgstrd_insts) >= 1:
			call_name = "Registered-Target"
			inst_id = selectItemfromList(rgstrd_insts, call_name)
			response = elb.deregister_targets(
				TargetGroupArn=tg_arn,
				Targets=[
					{
						'Id': inst_id,
					},
				]
			)
			print("Deregistered instance:%s from TG:%s" % (inst_id, tg_arn))
			return "Done"
#This ends deregistration of an instance.

#This section deletes a TG...
def deleteTG():
	print("********************************************************")
	print("You are now going to delete a TG! Please be careful!")
	print("********************************************************")
	input("Please enter any character to continue: ")
	tg_list = getTGs()
	if len(tg_list) == 0:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No target group is found in VPC: ", vpc_id, Fore.RESET)
		input("Enter any character to exit from this wizard: ")
		return ""
	elif len(tg_list) >= 1:
		call_name = "TargetGroup"
		tg_arn = selectItemfromList(tg_list, call_name)
		resp = elb.describe_target_groups(TargetGroupArns=[tg_arn])
		for item in resp['TargetGroups']:
			tmp_lb_arn = item['LoadBalancerArns']
		if len(tmp_lb_arn) == 1:
			print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print("Target group is currently in use by a listener or a rule from LB: %s, so cannot perform this delete operation" %tmp_lb_arn, Fore.RESET)
			input("Enter any character to exit from this wizard: ")
			return ""
		elif len(tmp_lb_arn) == 0:
			response = elb.delete_target_group(TargetGroupArn=tg_arn)
			print("Deleted TG: ", tg_arn)
			return tg_arn
#This ends TG deletion block.



#This section gets a list of running instances...
def getRunningInstances():
	running_instlist = []
	response = client.describe_instances(
		Filters=[
			{
				'Name': 'vpc-id',
				'Values': [vpc_id]
			},
			{
				'Name': 'instance-state-name',
				'Values': ['running']
			},
		]
	)
	for reservation in (response["Reservations"]):
		for instance in reservation["Instances"]:
			running_instlist.append(instance["InstanceId"])
	return running_instlist
#This ends listing running instances in selected VPC.

#This section lists stopped instances...
def getStoppedInstances():
	stopped_instlist = []
	response = client.describe_instances(
		Filters=[
			{
				'Name': 'vpc-id',
				'Values': [vpc_id]
			},
			{
				'Name': 'instance-state-name',
				'Values': ['stopped']
			},
		]
	)
	for reservation in (response["Reservations"]):
		for instance in reservation["Instances"]:
			stopped_instlist.append(instance["InstanceId"])
	return stopped_instlist
#Section ends here and returns list.

#This mothod will select the desired AMI...
def chooseAMI():
	ami_list = []
	tmp_devlist = []
	dev_list = []
	while True:
		print("Do you want to provide AMI ID manually or want to choose AMI from community? \nEnter 'm' for manual entry or 'c' to choose an AMI from community: ", end='')
		tmp_check = input()
		if tmp_check == 'm' or tmp_check == 'M':
			ami_id = input("Please enter the AMI ID: ")
			try:
				resp = client.describe_images(ImageIds=[ami_id])
				dev_list = resp['Images'][0]['BlockDeviceMappings']
				return ami_id, dev_list
				break
			except ClientError as e:
				print(Fore.RED, "Some error occurred! Error code is: ", e.response['Error']['Code'])
				print("Reason: ", e.response['Error']['Message'], Fore.RESET)
				print("For more information please visit> " + Fore.GREEN, "https://docs.aws.amazon.com/" + Fore.RESET)
				input("Please enter any character to reselect AMI again!: ")
				continue
		elif tmp_check == 'c' or tmp_check == 'C':
			oslist = ['Amazon Linux', 'CentOS', 'Debian', 'Gentoo', 'openSUSE', 'Red Hat', 'SUSE Linux', 'Ubuntu', 'Windows']
			call_name = "Operating System"
			sel_os = selectItemfromList(oslist, call_name)
			sel_os = '*'+sel_os+'*'
			while True:
				print("\nPlease choose an architecture type. \nEnter '0' for '32-bit (x86)', '1' for '64-bit (x86)', 2 for '64-bit (Arm)': ", end='')
				try:
					chs_index = int(input())
				except:
					print(Fore.RED+"Oops! That is not a valid number! Try again...."+Fore.RESET)
					input("Enter any character to continue: ")
				if chs_index == 0:
					arch_type = 'i386'
					break
				elif chs_index == 1:
					arch_type = 'x86_64'
					break
				elif chs_index == 2:
					arch_type = 'arm64'
					break
				else:
					print(Fore.RED+"Wrong selection! Please enter 0/1/2 only!"+Fore.RESET)
					print("\nPlease enter any character to continue")
					continue
			print("Please wait while we get the AMI list.........")
			try:
				resp = client.describe_images(
					Filters=[
						{
							'Name': 'architecture',
							'Values': [arch_type]
						},
						{
							'Name': 'description',
							'Values': [sel_os]
						},
						{
							'Name': 'root-device-type',
							'Values': ['ebs']
						},
						{
							'Name': 'image-type',
							'Values': ['machine']
						},
						{
							'Name': 'virtualization-type',
							'Values': ['hvm']
						},
					]
				)
			except ClientError as e:
				print(Fore.RED, "Some error occurred! Error code is: ", e.response['Error']['Code'])
				print("Reason: ", e.response['Error']['Message'], Fore.RESET)
				print("For more information please visit>" + Fore.GREEN, "https://docs.aws.amazon.com/" + Fore.RESET)
				input("Please enter any character to continue reselection of AMI: ")
				continue
			if len(resp['Images']) == 0:
				print("No AMI found with the OS + Architecture combination! Please enter AMI ID manually or follow the selection process again.")
				input("Please enter any character to continue: ")
				continue
			elif len(resp['Images']) >= 1:
				tmp_list = resp['Images']
				len_respami = len(tmp_list)
				if len_respami > 10:
					aa = 0
					bb = 10
					loop_cntr = int(len_respami/10)
					if len_respami > (loop_cntr*10):
						loop_cntr += 1
					for y in range(0,loop_cntr):
						ami_list = []
						dev_list = []
						if (len_respami-bb) >= 10:
							print(Fore.GREEN,"\nListing AMIs from %d to %d of total %d" % (aa+1,bb,len_respami), Fore.RESET)
						elif (len_respami-bb) < 10:
							print(Fore.GREEN,"\nListing AMIs from %d to %d of total %d" % (aa+1,len_respami,len_respami), Fore.RESET)
						for x in range(aa,bb):
							tmp_amilist = []
							tmp_devlist = []
							tmp_amilist.append(tmp_list[x]['ImageId'])
							tmp_amilist.append(tmp_list[x]['Description'])
							ami_list.append(tmp_amilist)
							print("********************************************************")
							print(tmp_list[x]['Name'],'-',tmp_list[x]['ImageId'])
							print(tmp_list[x]['Description'])
						print("\nEnter 'y' to choose an AMI from the above list or any other character to go to next page: ", end='')
						yn_check = input()
						if yn_check == "y" or yn_check == "Y":
							print("Please select an AMI from this list then>")
							break
						else:
							aa = int(bb)
							bb += 10
							continue
					break
				elif len_respami <= 10:
					print(Fore.GREEN,"\nListing AMIs from 1 to %d of total %d" % (len_respami,len_respami), Fore.RESET)
					for x in range(0,len_respami):
						tmp_amilist = []
						tmp_devlist = []
						tmp_amilist.append(tmp_list[x]['ImageId'])
						tmp_amilist.append(tmp_list[x]['Description'])
						ami_list.append(tmp_amilist)
						print("********************************************************")
						print(tmp_list[x]['Name'],'-',tmp_list[x]['ImageId'])
						print(tmp_list[x]['Description'])
					break
	call_name = "AMI"
	print(ami_list)
	ami_id, dev_pos = selectItemfromList(ami_list, call_name)
	resp = client.describe_images(ImageIds=[ami_id])
	dev_list = resp['Images'][0]['BlockDeviceMappings']
	return ami_id, dev_list
#AMI selection ends here & Returns the AMI ID(str) and Disk configuration(list).

#Selection of hardware type.
def chooseInstanceType():
	gp_inst_list = ['a1.medium','a1.large','a1.xlarge','a1.2xlarge','a1.4xlarge','m4.large','m4.xlarge','m4.2xlarge','m4.4xlarge','m4.10xlarge','m4.16xlarge','m5.large','m5.xlarge','m5.2xlarge','m5.4xlarge','m5.12xlarge','m5.24xlarge','m5.metal','m5a.large','m5a.xlarge','m5a.2xlarge','m5a.4xlarge','m5a.12xlarge','m5a.24xlarge','m5ad.large','m5ad.xlarge','m5ad.2xlarge','m5ad.4xlarge','m5ad.12xlarge','m5ad.24xlarge','m5d.large','m5d.xlarge','m5d.2xlarge','m5d.4xlarge','m5d.12xlarge','m5d.24xlarge','m5d.metal','t2.nano','t2.micro','t2.small','t2.medium','t2.large','t2.xlarge','t2.2xlarge','t3.nano','t3.micro','t3.small','t3.medium','t3.large','t3.xlarge','t3.2xlarge','t3a.nano','t3a.micro','t3a.small','t3a.medium','t3a.large','t3a.xlarge','t3a.2xlarge']
	co_inst_list = ['c4.large','c4.xlarge','c4.2xlarge','c4.4xlarge','c4.8xlarge','c5.large','c5.xlarge','c5.2xlarge','c5.4xlarge','c5.9xlarge','c5.18xlarge','c5d.large','c5d.xlarge','c5d.2xlarge','c5d.4xlarge','c5d.9xlarge','c5d.18xlarge','c5n.large','c5n.xlarge','c5n.2xlarge','c5n.4xlarge','c5n.9xlarge','c5n.18xlarge']
	mo_inst_list = ['r4.large','r4.xlarge','r4.2xlarge','r4.4xlarge','r4.8xlarge','r4.16xlarge','r5.large','r5.xlarge','r5.2xlarge','r5.4xlarge','r5.12xlarge','r5.24xlarge','r5.metal','r5a.large','r5a.xlarge','r5a.2xlarge','r5a.4xlarge','r5a.12xlarge','r5a.24xlarge','r5ad.large','r5ad.xlarge','r5ad.2xlarge','r5ad.4xlarge','r5ad.12xlarge','r5ad.24xlarge','r5d.large','r5d.xlarge','r5d.2xlarge','r5d.4xlarge','r5d.12xlarge','r5d.24xlarge','r5d.metal','u-6tb1.metal','u-9tb1.metal','u-12tb1.metal','x1.16xlarge','x1.32xlarge','x1e.xlarge','x1e.2xlarge','x1e.4xlarge','x1e.8xlarge','x1e.16xlarge','x1e.32xlarge','z1d.large','z1d.xlarge','z1d.2xlarge','z1d.3xlarge','z1d.6xlarge','z1d.12xlarge','z1d.metal']
	so_inst_list = ['d2.xlarge','d2.2xlarge','d2.4xlarge','d2.8xlarge','h1.2xlarge','h1.4xlarge','h1.8xlarge','h1.16xlarge','i3.large','i3.xlarge','i3.2xlarge','i3.4xlarge','i3.8xlarge','i3.16xlarge','i3.metal']
	ac_inst_list = ['f1.2xlarge','f1.4xlarge','f1.16xlarge','g3s.xlarge','g3.4xlarge','g3.8xlarge','g3.16xlarge','p2.xlarge','p2.8xlarge','p2.16xlarge','p3.2xlarge','p3.8xlarge','p3.16xlarge','p3dn.24xlarge']
	print("Please visit AWS site> "+Fore.GREEN+"https://aws.amazon.com/ec2/instance-types/ "+Fore.RESET+"to get more information before selecting an Instance Type.")
	input("Please enter any character to continue: ")
	while True:
		print("\nPlease choose an instance category. \nEnter '1' to select an instance type from 'General Purpose' family.\nEnter '2' for 'Compute Optimized' family. \nEnter '3' for 'Memory Optimized' family. \nEnter '4' for 'Storage Optimized' family. \nEnter '5' for 'Accelerated Computing' family")
		try:
			chs_index = int(input("Please enter your choice: "))
		except:
			print(Fore.RED+"Oops! That is not a valid number. Try again..."+Fore.RESET)
			input("Please enter any character to continue: ")
			continue
		if chs_index == 1:
			call_name = "General Purpose Instance"
			sel_inst = selectItemfromList(gp_inst_list, call_name)
			return sel_inst
			break
		elif chs_index == 2:
			call_name = "Compute Optimized Instance"
			sel_inst = selectItemfromList(co_inst_list, call_name)
			return sel_inst
			break
		elif chs_index == 3:
			call_name = "Memory Optimized Instance"
			sel_inst = selectItemfromList(mo_inst_list, call_name)
			return sel_inst
			break
		elif chs_index == 4:
			call_name = "Storage Optimized Instance"
			sel_inst = selectItemfromList(so_inst_list, call_name)
			return sel_inst
			break
		elif chs_index == 5:
			call_name = "Accelerated Computing Instance"
			sel_inst = selectItemfromList(ac_inst_list, call_name)
			return sel_inst
			break
		else:
			print("Wrong selection!! Please reselect again...")
			input("Enter any character to continue: ")
			continue
#Instance type selection ends here.

#This section launches user defined EC2 instance(s)...
def launchInstance():
	print("\n************************************************************")
	print("Now please go through the steps to select your EC2 settigs>>")
	print("************************************************************\n")
	print("Please select an AMI")
	ami_id, get_dev = chooseAMI()
	min_dsk_sz = int(get_dev[0]['Ebs']['VolumeSize'])
	dsk_typ = str(get_dev[0]['Ebs']['VolumeType'])
	print("\n************************************************************")
	print("Please select an instance type>>")
	get_inst = chooseInstanceType()
	print("\n************************************************************")
	print("How many EC2 instances are you going to launch? Enter the number(minimum 1): ", end='')
	inst_count = int(input())
	print("\n************************************************************")
	subnet_id = chooseSubnet()
	print("\n************************************************************")
	usr_script = ""
	print("\nDo you want to provide any user data i.e. bootstrap script? Enter 'y' to write or other letter to skip: ", end=' ')
	yn_btscr = input()
	usr_script = ""
	if yn_btscr == "y" or yn_btscr == "Y":
		print("\nEnter the script commands line by line. Press 'Ctrl+D' to finish.>>")
		ln_read = sys.stdin.readlines()
		len_ln_rd = len(ln_read)
		for aa in range(0,len_ln_rd):
			usr_script += ln_read[aa]
	else:
		print("\nNo user data provided, it will boot the raw OS.")
	print("************************************************************")
	print("\nDo you want to define the boot drive type/size etc (If you do not specify, it will go with default). y/n: ", end=' ')
	yn_disk = input()
	if yn_disk == "y" or yn_disk == "Y":
		while True:
			print("Enter the size of the boot disk in GiB(minimum for your selected AMI is: %d GiB): " % min_dsk_sz)
			get_dev[0]['Ebs']['VolumeSize'] = int(input())
			if get_dev[0]['Ebs']['VolumeSize'] >= min_dsk_sz:
				print("Press 1 for 'General Purpose SSD' or 2 for 'Magnetic': ", end='')
				try:
					dsk_typ_chk = int(input())
				except:
					print(Fore.RED+"Oops! That is not a valid number! Try again..."+Fore.RESET)
					input("Please enter any character to continue: ")
					continue
				if dsk_typ_chk == 1:
					get_dev[0]['Ebs']['VolumeType'] = "gp2"
					break
				elif dsk_typ_chk == 2:
					get_dev[0]['Ebs']['VolumeType'] = "standard"
					break
				else:
					print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
					print("Wrong selection while choosing disk type!"+Fore.RESET)
					input("Please enter any character to continue: ")
					continue
			else:
				print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
				print("\nYou need to provide disk size >= minimum size ie. >= %dGiB", min_dsk_sz, Fore.RESET)
				input("Please enter any character to continue: ")
	else:
		print("\nProceeding with default disk configuration of %dGiB %s disk" % (min_dsk_sz, dsk_typ))
	print("\n************************************************************")
	tag_key = "Name"
	tag_val = str(input("Please enter a tag name for your instance(s): "))
	print("\n************************************************************")
	sg_list = chooseSGs()
	print("\n************************************************************")
	print("##Please make sure your key name is 100% correct or else you will not be able to login to this instance(s)##")
	while True:
		ky_nm = str(input("Please enter your login key pair name (.pem file name): "))
		print("\nYou have given '%s' as your key file name, do you confirm if it is correct? y/n: " % ky_nm, end=' ')
		yn_key = input()
		if yn_key == "y" or yn_key == "Y":
			print("You have confirmed the key name as '%s'" % ky_nm)
			break
		else:
			print("Then please enter the correct key name again!!")
			input("Please enter any character to continue: ")
			continue
	print("************************************************************\n")
	print("Now launching your instance(s)............")
	response = client.run_instances(
		BlockDeviceMappings=get_dev,
		ImageId=ami_id,
		InstanceType=get_inst,
		KeyName=ky_nm,
		MaxCount=inst_count,
		MinCount=inst_count,
		SecurityGroupIds=sg_list,
		SubnetId=subnet_id,
		UserData=usr_script,
		TagSpecifications=[
			{
				'ResourceType': 'instance',
				'Tags': [
					{
						'Key': tag_key,
						'Value': tag_val
					},
				]
			},
		]
	)
	print("\nPlease note your instances' details>>")
	print("************************************************************")
	launch_inst_ids = []
	for item in response['Instances']:
		print(item)
		launch_inst_ids.append(item['InstanceId'])
	return launch_inst_ids
#This ends EC2 launch and returns list.

#This section creates Lauch Configuration....
def createLaunchConfiguration():
	print("\n************************************************************")
	print("This is Launch Configuration Creation wizard.")
	print("************************************************************")
	print("Please enter a name for your new launch configuration: ", end='')
	launch_nm = str(input())
	print("************************************************************")
	print("\nPlease choose an AMI>>")
	ami_id, get_dev = chooseAMI()
	min_dsk_sz = int(get_dev[0]['Ebs']['VolumeSize'])
	dsk_typ = str(get_dev[0]['Ebs']['VolumeType'])
	print("\n************************************************************")
	print("Please select an instance type>>")
	get_inst = chooseInstanceType()
	print("\n************************************************************")
	usr_script = ""
	print("\nDo you want to provide any user data i.e. bootstrap script? Enter 'y' to write or other letter to skip: ", end=' ')
	yn_btscr = input()
	usr_script = ""
	if yn_btscr == "y" or yn_btscr == "Y":
		print("\nEnter the script commands line by line. Press 'Ctrl+D' to finish.>>")
		ln_read = sys.stdin.readlines()
		len_ln_rd = len(ln_read)
		for aa in range(0,len_ln_rd):
			usr_script += ln_read[aa]
	else:
		print("\nNo user data provided, any EC2 launched using this Lauch Configuration will not have any bootscript!.")
	print("\n************************************************************")
	print("Do you want to define the boot drive type/size etc (If you do not specify, it will go with default). y/n: ", end=' ')
	yn_disk = input()
	if yn_disk == "y" or yn_disk == "Y":
		while True:
			print("Enter the size of the boot disk in GiB(minimum for your selected AMI is: %d GiB): " % min_dsk_sz)
			get_dev[0]['Ebs']['VolumeSize'] = int(input())
			if get_dev[0]['Ebs']['VolumeSize'] >= min_dsk_sz:
				print("Press 1 for 'SSD' or 2 for 'Magnetic: ", end='')
				try:
					dsk_typ_chk = int(input())
				except:
					print(Fore.RED+"Oops! That is not a valid number! Try again..."+Fore.RESET)
					input("Please enter any character to continue: ")
					continue
				if dsk_typ_chk == 1:
					get_dev[0]['Ebs']['VolumeType'] = "gp2"
					break
				elif dsk_typ_chk == 2:
					get_dev[0]['Ebs']['VolumeType'] = "standard"
					break
				else:
					print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
					print("Wrong selection while choosing disk type!"+Fore.RESET)
					input("Please enter any character to continue: ")
					continue
			else:
				print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
				print("You need to provide disk size >= minimum size ie. >= %dGiB", min_dsk_sz, Fore.RESET)
				input("Please enter any character to continue: ")
	else:
		print("\nProceeding with default disk configuration of %dGiB %s disk" % (min_dsk_sz, dsk_typ))
	print("\n************************************************************")
	sg_list = chooseSGs()
	print("\n************************************************************")
	print("##Please make sure your key name is 100% correct or else you will not be able to login to this instance(s)##")
	while True:
		ky_nm = str(input("Please enter your login key pair name (.pem file name): "))
		print("You have given '%s' as your key file name, do you confirm if it is correct? y/n: " % ky_nm, end=' ')
		yn_key = input()
		if yn_key == "y" or yn_key == "Y":
			print("You have confirmed the key name as '%s'" % ky_nm)
			break
		else:
			print("Then please enter the correct key name again!!")
	print("************************************************************\n")
	print("Now creating launch configuration............")
	response = atscl.create_launch_configuration(
		LaunchConfigurationName=launch_nm,
		ImageId=ami_id,
		KeyName=ky_nm,
		SecurityGroups=sg_list,
		UserData=usr_script,
		InstanceType=get_inst,
		BlockDeviceMappings=get_dev,
		InstanceMonitoring={'Enabled': False}
	)
	print("Created Lauch Configuration named: %s" % launch_nm)
	return launch_nm
#This ends launch configuration creation and returns str.

#This section gets the list of available launch configuration...
def getLaunchConfigurations():
	available_lnchconf = []
	print("Getting the list...........")
	response = atscl.describe_launch_configurations()
	for item in response['LaunchConfigurations']:
		available_lnchconf.append(item['LaunchConfigurationName'])
	return available_lnchconf
#This ends the section and returns list.

#This deletes a launch configuration...
def deleteLaunchConfiguration():
	print("************************************************************")
	print("Now you are going to delete a Lauch Configuration! Please be careful!")
	print("************************************************************")
	input("Please enter any character to continue: ")
	lc_list = getLaunchConfigurations()
	if len(lc_list) == 0:
		print("No Lauch Configuration found!")
		input("Please enter any character to exit: ")
		return ""
	elif len(lc_list) >= 1:
		call_name = "LauchConfiguration"
		lc_name = selectItemfromList(lc_list, call_name)
		match_flag = "no"
		asg_nm = ""
		resp = atscl.describe_auto_scaling_groups()
		for item in resp['AutoScalingGroups']:
			launch_nm = item['LaunchConfigurationName']
			if launch_nm == lc_name:
				asg_nm = item['AutoScalingGroupName']
				match_flag = "yes"
				break
		if match_flag == "yes":
			print("The selected launch configuration: %s is being used by ASG: %s, so can't delete the launch configuration!" % (lc_name, asg_nm))
			input("Please enter any character to exit: " )
			return ""
		elif match_flag == "no":
			response = atscl.delete_launch_configuration(LaunchConfigurationName=lc_name)
			print("Deleted launch configuration: ", lc_name)
			return "Done"
#This ends the section.

#This section creates a autoscaling group...
def createAutoScaling():
	available_lnchconf = getLaunchConfigurations()
	if len(available_lnchconf) == 0:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No Launch Configuration found! Please create one and the re run this AutoScale program!"+Fore.RESET)
		input("Please enter any character to exit: ")
		return ""
	subnet_list = getSubnets()
	if len(subnet_list) == 0:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No subnet is found! Please create atleast one subnet first and re run ASG again!"+Fore.RESET)
		input("Please enter any character to exit: ")
		return ""
	print("\n************************************************************")
	print("Welcome to Auto Scale Group wizard")
	print("************************************************************")
	call_name = "LauchConfiguration"
	launch_nm = selectItemfromList(available_lnchconf, call_name)
	match_flag = "no"
	resp1 = atscl.describe_launch_configurations(LaunchConfigurationNames=[launch_nm])
	for item in resp1['LaunchConfigurations']:
		lnchconf_sg = item['SecurityGroups']
	len_lnchconf_sg = len(lnchconf_sg)
	for aa in range(0, len_lnchconf_sg):
		sg1 = str(lnchconf_sg[aa])
		main_sg_list = getSGs()
		len_main_sg_list = len(main_sg_list)
		for bb in range(0, len_main_sg_list):
			sg2 = str(main_sg_list[bb])
			if sg1 == sg2:
				match_flag = "yes"
				break
	if match_flag == "no":
		print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("It seems that the selected LauchConfiguration: %s contains one or more SG(one unmatch is: %s) from other VPC! Please check the launch configuration first!" % (launch_nm, sg2))
		input("Please enter any character to exit: ")
		return ""
	print("************************************************************")
	print("Please enter the autoscaling group name: ", end='')
	asg_nm = str(input())
	print("What will be the minimum number of instances to be lauched(minimum 1)?: ", end='')
	min_asg = int(input())
	print("What will be the maximum number of instances as a contribution of ASG(>= %d) ?: " % min_asg, end='')
	max_asg = int(input())
	print("Please enter the default cooldown period(sec.): ", end='')
	asg_cool = int(input())
	print("Do you want to add 'Name' tag to the ASG instances (Otherwise it will be named as 'AutoServer') y/n: ", end='')
	yn_asg_tag = input()
	tag_key = "Name"
	if yn_asg_tag == "y" or yn_asg_tag == "Y":
		print("Please enter a desired name: ", end='')
		tag_val = input()
	else:
		tag_val = "AutoServer"
	available_tg = getTGs()
	call_name = "Subnet"
	while True:
		print("Please choose one or more Subnets to continue>")
		sel_sub = selectPartialList(subnet_list, call_name)
		if len(sel_sub) < 1:
			print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print("You need to select minimum one Subnet!, Selecte again>>")
			input("Please enter any character to continue: ")
			continue
		elif len(sel_sub) == 1:
			subnet_ids = str(sel_sub[0])
			break
		elif len(sel_sub) >= 2:
			subnet_ids = str(sel_sub[0])
			len_sel_sub = len(sel_sub)
			for aa in range(1, len_sel_sub):
				subnet_ids += ','
				subnet_ids += str(sel_sub[aa])
			break
	if len(available_tg) == 0:
		print("\nNo TG found to register the ASG instances! This wizard will create the ASG but TG registration will be skipped!")
		input("Please enter any character to continue: ")
		print("Creating ASG.........")
		response = atscl.create_auto_scaling_group(
			AutoScalingGroupName=asg_nm,
			LaunchConfigurationName=launch_nm,
			MinSize=min_asg,
			MaxSize=max_asg,
			DesiredCapacity=min_asg,
			DefaultCooldown=asg_cool,
			VPCZoneIdentifier=subnet_ids,
			HealthCheckType='EC2',
			HealthCheckGracePeriod=300,
			Tags=[
				{
					'Key': tag_key,
					'Value': tag_val
				},
			]
		)
		print("AutoScale group: %s created & instances are not registered into any TG as no TG was available" % asg_nm)
		input("Please enter any character to exit: ")
	elif len(available_tg) >= 1:
		tg_arn = chooseTG()
		response = atscl.create_auto_scaling_group(
			AutoScalingGroupName=asg_nm,
			LaunchConfigurationName=launch_nm,
			MinSize=min_asg,
			MaxSize=max_asg,
			DesiredCapacity=min_asg,
			DefaultCooldown=asg_cool,
			TargetGroupARNs=[tg_arn],
			VPCZoneIdentifier=subnet_ids,
			HealthCheckType='EC2',
			HealthCheckGracePeriod=300,
			Tags=[
				{
					'Key': tag_key,
					'Value': tag_val
				},
			]
		)
		print("Created ASG: %s and registered into TG: %s" %(asg_nm, tg_arn))
		input("Please enter any character to exit: ")
#This ends ASG creation and no return argument.

#This section lists all ASGs...
def getASGs():
	asg_list = []
	print("Getting ASG List......")
	response = atscl.describe_auto_scaling_groups()
	for item in response['AutoScalingGroups']:
		asg_list.append(item['AutoScalingGroupName'])
	return asg_list
#This ends the section.

#This section deletes an ASG...
def deleteASG():
	print("************************************************************")
	print("Now you are going to delete an AutoScalingGroup! Please be careful!")
	print("************************************************************")
	input("Please enter any character to continue: ")
	asg_list = getASGs()
	if len(asg_list) == 0:
		print("No AutoScalingGroup is found!")
		input("Please enter any character to Exit: ")
		return ""
	elif len(asg_list) >= 1:
		call_name = "AutoScalingGroup"
		asg_nm = selectItemfromList(asg_list, call_name)
		response = atscl.delete_auto_scaling_group(AutoScalingGroupName=asg_nm)
		print("Deleted ASG: ", asg_nm)
		return "Done"
#This ends the section.



#This section stops a selected running instance...
def stopInstance():
	print("************************************************************")
	print("Now you are into 'Stop-Instance' wizard, where we stop a selected running instance!")
	print("************************************************************")
	input("Please enter any character to continue: ")
	running_instlist = getRunningInstances()
	if len(running_instlist) == 0:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No running instance is found in selected VPC: ", vpc_id, Fore.RESET)
		input("Please enter any character to exit from stop-instance wizard!: ")
		return ""
	elif len(running_instlist) >= 1:
		call_name = "Running-Instance"
		inst_id = selectItemfromList(running_instlist, call_name)
		response = client.stop_instances(InstanceIds=[inst_id])
		for item in response['StoppingInstances']:
			print(item)
		print("Stopping Instance: ", inst_id)
		return inst_id
#This ends stop wizard.

#This section terminates a selected stopped instance...
def terminateInstance():
	print("************************************************************")
	print("Now you are into 'Terminate-Instance' wizard, where we terminate a selected stopped instance!")
	print("************************************************************")
	input("Please enter any character to continue: ")
	stopped_instlist = getStoppedInstances()
	if len(stopped_instlist) == 0:
		print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print("No stopped instance found in your selected VPC: ", vpc_id, Fore.RESET)
		input("Please enter any character to exit from terminate-instance wizard!: ")
		return ""
	elif len(stopped_instlist) >= 1:
		call_name = "Stopped-Instance"
		inst_id = selectItemfromList(stopped_instlist, call_name)
		response = client.terminate_instances(InstanceIds=[inst_id])
		for item in response['TerminatingInstances']:
			print(item)
		print("Terminating instance: ", inst_id)
		return inst_id
#Section ends here.





#This section displays/lists available resources...
def displayAWS():
	print(Fore.BLUE+"\n,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")
	print("This is your Display wizard of AWS resources where you can display some AWS resources.")
	print(",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n"+Fore.RESET)
	while True:
		print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
		print('''Enter '0' to display your currently selected VPC.
Enter '1' to list all your VPC IDs.
Enter '2' to list all Subnet IDs in the selected VPC.
Enter '3' to list available internet gateways attached to selected VPC.
Enter '4' to list available route tables in current VPC.
Enter '5' to list available security groups in current VPC.
Enter '6' to list running Instance IDs in current VPC.
Enter '7' to list available Load Balancers in current VPC.
Enter '8' to list available Target Groups in current VPC.
Enter '9' to display available launch configurations.
Enter '10' to display available auto scaling groups.
Enter '911' to exit from this display wizard.''')
		print("\n*Please select an option (number) to perform now: ", end='')
		try:
			input_index = int(input())
			print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
		except:
			print(Fore.RED+"Oops! That was not a valid number! Try again..."+Fore.RESET)
			input("Please enter any character to continue: ")
			continue
		if input_index == 0:
			print("Your current VPC ID is: ", vpc_id)
		elif input_index == 1:
			list_vpc = getVPCs()
			print("Available VPC IDs:\n", list_vpc)
		elif input_index == 2:
			subnet_list = getSubnets()
			if len(subnet_list) >= 1:
				print("Available Subnet IDs:\n", subnet_list)
			elif len(subnet_list) == 0:
				print("No subnets is found in VPC: ", vpc_id)
		elif input_index == 3:
			igw_list = getIGWs()
			if len(igw_list) >= 1:
				print("Available Internet Gateway IDs:\n", igw_list)
			elif len(igw_list) == 0:
				print("No IGW found!")
		elif input_index == 4:
			available_rt = getRTs()
			if len(available_rt) >= 1:
				print("Available Route Table IDs: \n", available_rt)
			elif len(available_rt) == 0:
				print("No RT found!")
		elif input_index == 5:
			available_sg = getSGs()
			if len(available_sg) >= 1:
				print("Available SG IDs: \n", available_sg)
			elif len(available_sg) == 0:
				print("No SG found!")
		elif input_index == 6:
			running_instlist = getRunningInstances()
			if len(running_instlist) >= 1:
				print("Running Instances' IDs: \n", running_instlist)
			elif len(running_instlist) == 0:
				print("No running instance is found in VPC: ", vpc_id)
		elif input_index == 7:
			lb_list = getLBs()
			if len(lb_list) >= 1:
				print("Available Load Balancers' IDs: \n", lb_list)
			elif len(lb_list) == 0:
				print("No Load Balancer found!")
		elif input_index == 8:
			tg_list = getTGs()
			if len(tg_list) >= 1:
				print("Available Target Groups' IDs:\n", tg_list)
			elif len(tg_list) == 0:
				print("No Target Group found!")
		elif input_index == 9:
			lc_list = getLaunchConfigurations()
			if len(lc_list) >= 1:
				print("Available LauchConfigurations:\n", lc_list)
			elif len(lc_list) == 0:
				print("No LauchConfiguration found!")
		elif input_index == 10:
			asg_list = getASGs()
			if len(asg_list) >= 1:
				print("Available AutoScalingGroups: \n", asg_list)
			elif len(asg_list) == 0:
				print("No AutoScalingGroup found!")
		elif input_index == 911:
			print("Okay let's exit from display wizard and go back to main menu.....")
			input("Please enter any character to exit: ")
			break
		else:
			print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print("Wrong input number! Please select a number as per given list>>"+Fore.RESET)
			input("Please enter any character to continue: ")
			continue
		print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
		input("\nPlease enter any character to continue displaying more resource items: ")
#This ends listing section and return nothing!

#This section creates/performs creation/registration tasks...
def perfTaskAWS():
	print(Fore.LIGHTMAGENTA_EX+"\n+++++++++++++++++++++++++++++++++++++++++++++++++++")
	print("This is your 'Task-Perform' wizard where you can perform some create, register some AWS resources.")
	print("+++++++++++++++++++++++++++++++++++++++++++++++++++\n"+Fore.RESET)
	while True:
		print("+++++++++++++++++++++++++++++++++++++++++++++++++++")
		print('''Enter '0' to display your currently selected VPC.
Enter '21' to create a subnet in selected VPC.
Enter '22' to create an internet gateway and attach it to the selected VPC.
Enter '23' to create a route table in current VPC.
Enter '24' to associate a subnet in a route table.
Enter '25' to create security groups in selected VPC.
Enter '26' to create a load balancer.
Enter '27' to create a target group with defined listener.
Enter '28' to register instances into target group.
Enter '29' to create launch configuration.
Enter '30' to create auto scaling group.
Enter '50' to launch an EC2 instance with user defined parameters.
Enter '911' to exit from task-perform wizard and go back to main program.''')
		print("\n*Please select an option (number) to perform now: ", end='')
		try:
			input_index = int(input())
			print("+++++++++++++++++++++++++++++++++++++++++++++++++++")
		except:
			print(Fore.RED+"Oops! That was not a valid number! Try again..."+Fore.RESET)
			input("Please enter any character to continue: ")
			continue
		try:
			if input_index == 0:
				print("Now you are into VPC: ", vpc_id)
			elif input_index == 21:
				subnet_id = createSubnet()
				print("\nCreated Subnet: ", subnet_id)
			elif input_index == 22:
				ig_id = createIGW()
				print("\nCreated IGW: ", ig_id)
			elif input_index == 23:
				rt_id = createRT()
				print("\nCreated RT: ", rt_id)
			elif input_index == 24:
				resp = rtSubAssociate()
				print(resp)
			elif input_index == 25:
				sg_id = createSG()
				print("\nCreated SG: ", sg_id)
			elif input_index == 50:
				launch_inst_ids = launchInstance()
				print("\nLaunched Instances' IDs are: ", launch_inst_ids)
			elif input_index == 26:
				lb_arn = createLB()
			elif input_index == 27:
				tg_arn = createTG()
				createListener(tg_arn)
				print("\nCreated TG ARN: ", tg_arn)
			elif input_index == 28:
				resp = registerTargets()
				print(resp)
			elif input_index == 29:
				launch_nm = createLaunchConfiguration()
			elif input_index == 30:
				createAutoScaling()
			elif input_index == 911:
				print("Okay let's exit from 'Task-Perform' wizard!")
				input("Please enter any character to exit: ")
				break
			else:
				print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
				print("Wrong input number! Please select a number as per given list>>"+Fore.RESET)
				input("Please enter any character to continue: ")
				continue
			print("+++++++++++++++++++++++++++++++++++++++++++++++++++")
			input("\nPlease enter any character to continue with more 'Perform' tasks: ")
		except ClientError as e:
			print(Fore.RED,"Some error occurred! Error code is: ", e.response['Error']['Code'])
			print("Reason: ", e.response['Error']['Message'], Fore.RESET)
			print("For more information please visit>" + Fore.GREEN + "https://docs.aws.amazon.com/" + Fore.RESET)
			input("Please enter any character to continue: ")
#This ends perform task block and returns null.

#This section deletes a selected item in AWS...
def deleteAWSResource():
	print(Back.LIGHTGREEN_EX+Fore.RED+"\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
	print("Please be very careful here, as you are into deletion/removal/termination program now!!!!!")
	print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"+Style.RESET_ALL)
	print("\nBy the way you are into VPC: ", vpc_id)
	input("Please enter any character to continue: ")
	while True:
		print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
		print('''Enter '0' to display your currently selected VPC.
Enter '1' to stop an EC2 instance in selected VPC.
Enter '2' to terminate a stopped instance.
Enter '3' to deregister an instance from a target group.
Enter '4' to delete a target group.
Enter '5' to delete a load balancer.
Enter '6' to delete a security group.
Enter '7' to delete a subnet association from RT.
Enter '8' to delete a route from a RT.
Enter '9' to delete a route table.
Enter '10' to detach an internet gateway from VPC.
Enter '11' to delete an IGW.
Enter '12' to delete an auto scaling group.
Enter '13' to delete a launch configuration.
Enter '14' to delete a Subnet.
Enter '15' to delete a VPC.
Enter '911' to return back to main program.
''')
		print("\n*Please select an option (number) to perform now: ", end='')
		try:
			input_index = int(input())
			print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
		except:
			print(Fore.RED+"Oops! That was not a valid number! Try again..."+Fore.RESET)
			input("Please enter any character to continue: ")
			continue
		try:
			if input_index == 0:
				print("Your current VPC ID is: ", vpc_id)
			elif input_index == 1:
				print("Do you really want to stop any instance? y/n: ", end='')
				yn_check = input()
				if yn_check == "y" or yn_check == "Y":
					inst_id = stopInstance()
				else:
					print("Abort!")
					continue
			elif input_index == 2:
				print("Do you really want to terminate any instance? y/n: ", end='')
				yn_check = input()
				if yn_check == "y" or yn_check == "Y":
					inst_id = terminateInstance()
				else:
					print("Abort!")
					continue
			elif input_index == 3:
				print("Do you really want to deregister a target? y/n: ", end='')
				yn_check = input()
				if yn_check == "y" or yn_check == "Y":
					stts = deregisterTarget()
				else:
					continue
			elif input_index == 4:
				print("Do you really want to delete a target group? y/n: ", end='')
				yn_check = input()
				if yn_check == "y" or yn_check == "Y":
					tg_arn = deleteTG()
				else:
					print("Abort!")
					continue
			elif input_index == 5:
				print("Do you really want to delete a load balancer? y/n: ", end='')
				yn_check = input()
				if yn_check == "y" or yn_check == "Y":
					stts = deleteLB()
				else:
					print("Abort!")
					continue
			elif input_index == 6:
				print("Do you really want to delete a security group? y/n: ", end='')
				yn_check = input()
				if yn_check == "y" or yn_check == "Y":
					stts = deleteSG()
					print(stts)
				else:
					print("Abort!")
					continue
			elif input_index == 9:
				print("Do you really want to delete a route table? y/n: ", end='')
				yn_check = input()
				if yn_check == "y" or yn_check == "Y":
					stts = deleteRT()
					print(stts)
				else:
					print("Abort!")
					continue
			elif input_index == 7:
				print("Do you really want to delete a subnet association from a RT? y/n: ", end='')
				yn_check = input()
				if yn_check == "y" or yn_check == "Y":
					stts = rtDeleteAsso()
					print(stts)
				else:
					print("Abort!")
					continue
			elif input_index == 8:
				print("Do you really want to delete a route from a RT? y/n: ", end='')
				yn_check = input()
				if yn_check == "y" or yn_check == "Y":
					stts = deleteRoute()
					print(stts)
				else:
					print("Abort!")
					continue
			elif input_index == 10:
				print("Do you really want to detach an IGW from current VPC: %s? y/n: " %vpc_id, end='')
				yn_check = input()
				if yn_check == "y" or yn_check == "Y":
					stts = detachIGW()
					print(stts)
				else:
					print("Abort!")
					continue
			elif input_index == 11:
				print("Do you really want to delete an IGW? y/n: ", end='')
				yn_check = input()
				if yn_check == "y" or yn_check == "Y":
					stts = deleteIGW()
					print(stts)
				else:
					print("Abort!")
					continue
			elif input_index == 12:
				print("Do you really want to delete an AutoScalingGroup? y/n: ", end='')
				yn_check = input()
				if yn_check == "y" or yn_check == "Y":
					stts = deleteASG()
					print(stts)
				else:
					print("Abort!")
					continue
			elif input_index == 13:
				print("Do you really want to delete a LauchConfiguration? y/n: ", end='')
				yn_check = input()
				if yn_check == "y" or yn_check == "Y":
					stts = deleteLaunchConfiguration()
					print(stts)
				else:
					print("Abort!")
					continue
			elif input_index == 14:
				print("Do you really want to delete a Subnet? y/n: ", end='')
				yn_check = input()
				if yn_check == "y" or yn_check == "Y":
					stts = deleteSubnet()
					print(stts)
				else:
					print("Abort!")
					continue
			elif input_index == 15:
				print("Do you really want to delete the current VPC? y/n: ", end='')
				yn_check = input()
				if yn_check == "y" or yn_check == "Y":
					stts = deleteVPC()
					if stts == "DELVPC":
						print("As the current VPC is deleted go back to VPC selection/creation section!")
						return "NOVPC"
				else:
					print("Abort!")
					continue
			elif input_index == 911:
				print("Okay let's exit from 'Delete-AWS-Resource' program!")
				input("Please enter any character to exit: ")
				break
			else:
				print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
				print("Wrong input number! Please select a number as per given list>>"+Fore.RESET)
				input("Please enter any character to continue: ")
				continue
			print("+++++++++++++++++++++++++++++++++++++++++++++++++++")
			input("\nPlease enter any character to continue with more 'Delete' tasks: ")
		except ClientError as e:
			print(Fore.RED, "Some error occurred! Error code is: ", e.response['Error']['Code'])
			print("Reason: ", e.response['Error']['Message'], Fore.RESET)
			print("For more information please visit>" + Fore.GREEN, "https://docs.aws.amazon.com/" + Fore.RESET)
			input("Please enter any character to continue: ")
#This end delete AWS resource section.




#This is main method declaration block...
def main():
	print(Fore.GREEN+"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	print("This is your main program, where you perform your tasks in the selected VPC: %s. \nNow let us proceed with the program" % vpc_id)
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"+Fore.RESET)
	input("Please enter any character to continue: ")
	while True:
		print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		print('''Please enter 'display' to go to display AWS resources. 
Enter 'perf' to create/perform any task on AWS resources. 
Enter 'delete' to delete/remove/terminate any selected item from aws resources.
Enter 'goback' to exit from main program and select another VPC or create a new VPC, then come back again to main program: ''')
		prgm_exe = input("*Please enter any of the above displayed phrase: ")
		prgm_exe = prgm_exe.lower()
		if prgm_exe == "display":
			displayAWS()
		elif prgm_exe == "perf":
			perfTaskAWS()
		elif prgm_exe == "delete":
			stts = deleteAWSResource()
			if stts == "NOVPC":
				return
		elif prgm_exe == "goback":
			print("Okay then, please select a VPC again or create a new one>>")
			print("Enter any character to exit: ")
			break
		else:
			print(Fore.RED+"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print("Wrong input, please follow the process again"+Fore.RESET)
			input("Enter any character to continue: ")
			continue
		print(Fore.GREEN+"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"+Fore.RESET)
		input("You came back to main program. Please enter any character to continue: ")
#....Method declarations end here.|||


#The program execution starts here...
print(Back.CYAN + Fore.RED + "\n##############################################################################################################")
print("Welcome to the 'CLI-AWS Management Console'. This program is written by Somnath Das(somnath-das@outlook.com)")
print("##############################################################################################################\n"+Style.RESET_ALL)
input("Please enter any character to continue: ")
while True:
	print(Fore.LIGHTYELLOW_EX+"\n#############################################################")
	print("You need to select/create a VPC to proceed with the program. \nPlease type 'create' & hit enter to create a new VPC or type 'select' to choose an existing VPC or type 'exit' to exit from this program: "+Fore.RESET, end='')
	prgm_exe = input()
	prgm_exe = prgm_exe.lower()
	if prgm_exe == "create":
		vpc_id = createVPC()
	elif prgm_exe == "select":
		vpc_id = chooseVPC()
	elif prgm_exe == "exit":
		print("\nOkay! Program exit has been requested!")
		input("Please enter any character to exit: ")
		break
	else:
		print(Fore.RED+"\nWrong input! Type 'select' or 'create' or 'exit'>>")
		print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"+Fore.RESET)
		input("Please enter any character to continue: ")
		continue
	print("Now all your actions will be performed in VPC: %s" % vpc_id)
	main()
	print("Current task/display session ended by user, please select/create a VPC to run tasks again>>")
print(Fore.GREEN+"Thanks from Somnath _/\_\n\n"+Fore.RESET)

