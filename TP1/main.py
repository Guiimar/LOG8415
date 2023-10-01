#STEPS# 
#On est dans la région us-east 1, qui a 6 avaibility zones 
#C’est demandé de créer les instances EC2 dans différents AZ (On peut utiliser AZ a,b,c pour EC2s du Target group 1 et AZ d,e,f pour Target group 2)
#Dans la région , il faut créer un VPC (Virtual private clouds) notre réseau privé.
#Puis  ajouter des subnets au VPC (Un subnet par AZ). 
#On crée les instances EC2 (inputs={TBD}) Avec Flask
#Create Target Group (inputs={TBD})
#Enregistrer les instances dans les targets groups (inputs={TBD})
#S’assurer que si on envoie une requete au TG1 , seuls EC2s de TG1 répondent, de même pour TG2.
#Créer un load balancer (inputs={TBD})
#Créer des listeners (routes qui lient les load balancers aux targets routes) (inputs={TBD})
#Créer des listeners rules ( règles de liaison de traffic entre les listeners) (inputs={TBD})

import configparser
import boto3
import time

#Function to create a service resource for ec2: 
def resource_ec2(aws_access_key_id, aws_secret_access_key, aws_session_token):
    ec2_serviceresource =  boto3.resource('ec2',
                       'us-east-1',
                       aws_access_key_id= aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key ,
                      aws_session_token= aws_session_token) 
    

    
    return(ec2_serviceresource)

#Function to create a service client for ec2
def client_ec2(aws_access_key_id, aws_secret_access_key, aws_session_token):
    ec2_serviceclient =  boto3.client('ec2',
                       'us-east-1',
                       aws_access_key_id= aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key ,
                      aws_session_token= aws_session_token) 
   
    
    return(ec2_serviceclient)

#Function to create a service client for elbv2
def client_elbv2(aws_access_key_id, aws_secret_access_key, aws_session_token):
    elbv2_serviceclient =  boto3.client('elbv2',
                       'us-east-1',
                       aws_access_key_id= aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key ,
                      aws_session_token= aws_session_token) 
    

    
    return(elbv2_serviceclient)


#---------------------------------------------To re check----------------------------------------------
'Function to create a new vpc (Maybe no need for this, just use default vpc)'
def create_vpc(CidrBlock,resource):
   VPC_Id=resource.create_vpc(CidrBlock=CidrBlock).id
   return VPC_Id

'Function to create security group (Maybe no need for this, just use get securty group of default vpc)'
def create_security_group(Description,Groupe_name,vpc_id,resource):

    Security_group_ID=resource.create_security_group(
        Description=Description,
        GroupName=Groupe_name,
        VpcId=vpc_id).id
    
    Security_group=resource.SecurityGroup(Security_group_ID)
    
    #Add an inbounded allowing inbounded traffics of all protocols, from and to all ports, and all Ipranges.  
    Security_group.authorize_ingress(
         IpPermissions=[
            {'FromPort':-1,
             'ToPort':-1,
             'IpProtocol':'-1',
             'IpRanges':[{'CidrIp':'0.0.0.0/0'}]
            }]
    )       
    return Security_group_ID

#------------------------------------------------End----------------------------------------------------


#Function to create ec2 instances : 
def create_instance_ec2(num_instances,ami_id,
    instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons):
    instances=[]
    for i in range(num_instances):
        instance=ec2_serviceresource.create_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_pair_name,
            MinCount=1,
            MaxCount=1,
            Placement={'AvailabilityZone':Availabilityzons[i]},
            SecurityGroupIds=[security_group_id] if security_group_id else [],
            TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'lab1-ec2-instance-'+str(instance_type)+ str(i + 1)
                            },
                        ]
                    },
                ]
        )
        instances.append(instance[0].id)
        print ('Instance: ',i+1,' having the Id: ',instance[0], ' in Availability Zone: ', Availabilityzons[i], 'is created')
        #print(f'{instances[i]} is starting')
   
    return instances

#Function to create target groups : 
def create_target_group(targetname,vpc_id,port, elbv2_serviceclient):
    tg_response=elbv2_serviceclient.create_target_group(
        Name=targetname,
        Protocol='HTTP',
        Port=port,
        VpcId=vpc_id,
        TargetType ='instance'
    )
    target_group_arn = tg_response["TargetGroups"][0]["TargetGroupArn"]    
    return target_group_arn

#Function to register targets in target groups : 
def register_targets(elbv2_serviceclient,instances_ids,target_group_arn,port):
    targets=[]
    for instance_id in instances_ids:
        targets.append({"Id":instance_id,"Port":port})

    tg_registered=elbv2_serviceclient.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=targets
    )
    return tg_registered

#Function to create load balancer : 
def create_load_balancer(elbv2_seviceclient,LB_name,subnets,security_group):
    response = elbv2_seviceclient.create_load_balancer(
        Name=LB_name,
        Subnets=subnets,
        SecurityGroups=[security_group]
                )
    load_balancer_arn = response["LoadBalancers"][0]["LoadBalancerArn"]
  

    return load_balancer_arn

#Function to create listeners:
def create_listener(elbv2_seviceclient,load_balancer_arn,target_group_arn,port):
    response_listener=elbv2_seviceclient.create_listener(
    LoadBalancerArn=load_balancer_arn,
    Port=port,
    Protocol='HTTP',
    DefaultActions=[
        {
            'TargetGroupArn': target_group_arn,
            'Type':'forward'
        },
    ]
    )
    response_listener_arn=response_listener["Listeners"][0]["ListenerArn"]
   
    return response_listener_arn

#Function to create listener rules
def create_listener_rule(elbv2_seviceclient,listener_arn, target_group_arn, path):
    response = elbv2_seviceclient.create_rule(
        ListenerArn=listener_arn,
        Priority=1,
        Conditions=[
            {
                'Field': 'path-pattern',
                'Values': [path]
            }
        ],
        Actions=[
            {
                'Type': 'forward',
                'ForwardConfig': {
                    'TargetGroups': [{'TargetGroupArn': target_group_arn}]
                }
            }
        ]
    )
    response_rule_listener = response['Rules'][0]['RuleArn']
    return response_rule_listener

#------------------------------------Functions for EC2s instances termination and Load balancer and target groups deletion ----------------------------------------------------
#Function to terminate EC2 instances when not needed
def terminate_instances(ec2_serviceresource,instances_ids):
    for id in instances_ids:
        ec2_serviceresource.Instance(id).terminate()
    return("Instances terminated")

#Function to delete LoadBalancer when not needed
def delete_load_balancer(elbv2_seviceclient,load_balancer_arn):
    elbv2_seviceclient.delete_load_balancer(
        LoadBalancerArn=load_balancer_arn
    )
    return("Load Balancer deleted")

#Function to delete target groups when not needed
def delete_target_groups(elbv2_seviceclient,target_groups_arns):
    for arn in target_groups_arns:
        elbv2_seviceclient.delete_target_group(
        TargetGroupArn=arn
    )
    return("Target Groups deleted")


# Here is the main program :

if __name__ == '__main__':
    # Get credentials from the config file :
    config_object = configparser.ConfigParser()
    with open("credentials.ini","r") as file_object:
        config_object.read_file(file_object)
        key_id = config_object.get("resource","aws_access_key_id")
        access_key = config_object.get("resource","aws_secret_access_key")
        session_token = config_object.get("resource","aws_session_token")
        ami_id = config_object.get("ami","ami_id")

    key_pair_name = "vockey"
        
    """
    key_id="ASIA37YNGERBT6X6LQTC"
    access_key="ndrRz7s0K2gKwCdexLh3F7tSvLrhDNtkEHv1Gozg"
    session_token="FwoGZXIvYXdzEKr//////////wEaDBO5ze9K0vRG+ashZCLOAU0/95fFC+tjNFPeM7QOEnhtztXUO0eZZytXAEulebfcWHep2MZKlMhgjsqtOGxS1hZ7HfvoXW9bsTwMVnT3DBavYP6PPINFXQjexeEegaalIRXaKKwufyF6feVMVH6XkXRxqY6E1Tc7/yJwaO3nR5hqjVj+SRgqjY7K8pzA7/gaxopW6nt8Xu/M5XlRq951SIlps2YKxyesvYsEud0uGlDztap7uyR7kEbDdUJwDYVShJuRnRgYR45n7K3C25xGQZdRhHrgjXZ234BewLBQKI+40agGMi1+WsdAzD767xhcOfSXY6FCqB7ZGdHFdVEMq6ASBqlAc+Zp7dtDqBqwT2PYHko="
    ami_id ='ami-03a6eaae9938c858c'
    """
    #--------------------------------------Creating ec2 and elbv2 resource and client services--------------------------------
    #Create ec2 service resource with our credentials:
    ec2_serviceresource = resource_ec2(key_id, access_key, session_token)
    print("============> ec2 resource creation has been made succesfuly!!!!<=================")
    #Create ec2 service client with our credentials:
    ec2_serviceclient = client_ec2(key_id, access_key, session_token)
    print("============> ec2 client creation has been made succesfuly!!!!<=================")
    #Create elbv2 service client with our credentials:
    elbv2_serviceclient = client_elbv2(key_id, access_key, session_token)
    print("============> elbv2 client creation has been made succesfuly!!!!<=================")

    #---------------------------------------------------Get default VPC ID----------------------------------------------------
    #Get default vpc description : 
    default_vpc = ec2_serviceclient.describe_vpcs(
        Filters=[
            {'Name':'isDefault',
             'Values':['true']},
        ]
    )
    default_vpc_desc = default_vpc.get("Vpcs")
   
    # Get default vpc id : 
    vpc_id = default_vpc_desc[0].get('VpcId')

#-----------------------------------------------------------To re check-------------------------------------------------------

    # The step is to perform later on :
    """
    # Create Vpc : 
    vpc_id= create_vpc('172.31.0.0/16',ec2)
    print("\n\n"+vpc_id+"\n\n")
    """
    # Creation of a security group is to perform later on
    """
    security_group_id = (sg_dict.get("SecurityGroups")[0]).get("GroupId")    
    #print(security_group_id)
    # Create security group for vpcId : 
    security_group_id = create_security_group('Security_group_created_for_lab','Security_group',vpc_id,ec2)
    print("\n"+security_group_id+"\n")"""

#--------------------------------------------------------------End--------------------------------------------------------------

#--------------------------------------Get Id of default VPC standard security group -------------------------------------------

    #Get the standard security group from the default VPC :
    sg_dict = ec2_serviceclient.describe_security_groups(Filters=[
        {
            'Name': 'vpc-id',
            'Values': [
                vpc_id,
            ]
        },

    {
            'Name': 'group-name',
            'Values': [
                "default",
            ]
        },
    
    ])

    security_group_id = (sg_dict.get("SecurityGroups")[0]).get("GroupId")    
    

#--------------------------------------Create Instances of cluster 1 ------------------------------------------------------------

    # Create 4 instances with t2.large as intance type,
    'By choice, we create the 4 EC2 instances for Cluster 1 in availability zones us-east-1a and us-east-1b'
    Availabilityzons_Cluster1=['us-east-1a','us-east-1b','us-east-1a','us-east-1b','us-east-1a']
    instance_type = "t2.large"
    print("\n Creating instances of Cluster 1 with type : t2.large")
    instances_t2= create_instance_ec2(4,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons_Cluster1)
    #print(instances_t2)
    print("\n Instances created succefuly instance type : t2.large")

#--------------------------------------Create Instances of cluster 2 -------------------------------------------------------------

    # Create 5 instances with m4.large as instance type:
    'By choice, we create the 5 EC2 instances for Cluster 2 in avaibility zones us-east-1c and us-east-1d'
    Availabilityzons_Cluster2=['us-east-1c','us-east-1d','us-east-1c','us-east-1d','us-east-1c']
    instance_type = "m4.large"
    print("\n Creating instances of Cluster 2 with type : m4.large")
    instances_m4= create_instance_ec2(5,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons_Cluster2)
    #print(instances_m4)
    print("\n Instances created succefuly instance type  : m4.large")

#--------------------------------------------Create Target groups ----------------------------------------------------------------

    #Create the two targets groups (Clusters)
    target_group_1=create_target_group('TargetGroup1',vpc_id,80, elbv2_serviceclient)
    target_group_2=create_target_group('TargetGroup2',vpc_id,8080, elbv2_serviceclient)
    print("\nTarget groups created")

    #time to wait for udate ec2 running status before registration in target groups
    time.sleep(60)

#---------------------------------------------Register Targets on target groups --------------------------------------------------

    #Targets registration on target groups
    register_targets(elbv2_serviceclient,instances_t2,target_group_1,80) 
    register_targets(elbv2_serviceclient,instances_m4,target_group_2,8080)
    print("Targets registred")

#----------------------------Get mapping between availability zones and Ids of default vpc subnets -------------------------------

    #Get the standard subnets discription from the default VPC :
    subnets_discription= ec2_serviceclient.describe_subnets(Filters=[
         {
            'Name': 'vpc-id',
            'Values': [
                vpc_id,
            ]
        }
    ])
    #Get mapping dictionary between Availability zones and subnets Ids
    mapping_AZ_subnetid={subnet['AvailabilityZone']:subnet['SubnetId'] for subnet in subnets_discription['Subnets']}
    mapping_AZ_subnetid

#--------------------------------------Create Load balancer with appropriate subnets ----------------------------------------------

    #Define appropriate subnets associated with used availabilty zones
    subnetsIds=[mapping_AZ_subnetid[AZ] for AZ in set(Availabilityzons_Cluster1).union(Availabilityzons_Cluster2)]
    #Create Load balancer 
    load_balancerarn=create_load_balancer(elbv2_serviceclient,'OurLoadBalancer',subnetsIds,security_group_id)
    print('Load balancer created')

    #Create listeners listener
    listener_group1=create_listener(elbv2_serviceclient,load_balancerarn,target_group_1,80) 
    listener_group2=create_listener(elbv2_serviceclient,load_balancerarn,target_group_2,8080)
    print('Listeners created')

    #Create listeners rules
    rule_list_1=create_listener_rule(elbv2_serviceclient,listener_group1,target_group_1,'/cluster1')
    rule_list_2=create_listener_rule(elbv2_serviceclient,listener_group2,target_group_2,'/cluster2')
    print('Listners rules created')

    """
    #Terminate EC2 instances when not needed
    total_instances=instances_t2+instances_m4
    terminate_instances(ec2_serviceresource,total_instances)
    time.sleep(20)
    delete_load_balancer(elbv2_serviceclient,load_balancerarn)
        time.sleep(20)

    delete_target_groups(elbv2_serviceclient,[target_group_1,target_group_2])  
 
    """