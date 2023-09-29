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
import random

# Define a client connection :
def client_connection_ec2(aws_access_key_id, aws_secret_access_key, aws_session_token):
    ec2 =  boto3.client('ec2',
                       'us-east-1',
                       aws_access_key_id= aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key ,
                      aws_session_token= aws_session_token) 
    print("\n\n===================> Client connection <======================\n\n")
    print("\n\tClient connection has been made succesfuly!!!!\n")
    print("\n\n==============================================================")

    return(ec2)

#Function to establish connection with AWS CLI credentials: 
def create_connection_ec2(aws_access_key_id, aws_secret_access_key, aws_session_token):
    ec2 =  boto3.resource('ec2',
                       'us-east-1',
                       aws_access_key_id= aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key ,
                      aws_session_token= aws_session_token) 
    return(ec2)

def create_vpc(CidrBlock,resource):
    VPC_Id=resource.create_vpc(CidrBlock=CidrBlock).id
    return VPC_Id

#Function to create security group with adding inbounded rules with all permissions:
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


#Function to create EC2 instances : 
def create_instance_ec2(num_instances,ami_id,
    instance_type,key_pair_name,resource,security_group_id,Availabilityzons):
    instances=[]
    for i in range(num_instances):
        instance=resource.create_instances(
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
        print ('Creating instance: ',i+1,' having the Id: ',instance[0], ' in Availability Zone: ', Availabilityzons[i], 'is starting\n')
        #print(f'{instances[i]} is starting')

    return instances

#Function to create target groups : 
def create_target_group(targetname,vpc_id,port, resource):
    tg_response=resource.create_target_group(
        Name=targetname,
        Protocol='HTTP',
        Port=port,
        VpcId=vpc_id,
        TargetType ='instance'
    )
    target_group_arn = tg_response["TargetGroups"][0]["TargetGroupArn"]    
    return target_group_arn

#Function to register targets in target groups : 
def register_targets(instances_ids,target_group_arn,port):
    targets=[]
    for instance_id in instances_ids:
        targets.append({"Id":instance_id,"Port":port})

    tg_registered=client.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=targets
    )

    return tg_registered


#Function to create load balancer : 
def create_load_balancer(subnets,security_group):
    response = client.create_load_balancer(
        Name="my-load-balancer",
        Subnets=subnets,
        SecurityGroups=[security_group]
                )
    load_balancer_arn = response["LoadBalancers"][0]["LoadBalancerArn"]

    return load_balancer_arn

#Function to create listeners:
def create_listener(load_balancer_arn,target_group_arn,port):
    response_listener=client.create_listener(
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
def create_listener_rule(listener_arn, target_group_arn, path):
    response = client.create_rule(
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


# Function to terminate EC2 instances when not needed
def terminate_instances(instances_ids,resource):
    for x in instances_ids:
        resource.Instance(x).terminate()
    return("Instances terminated")


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
    # Create a client connection mainly to get the standard Vpc ID :
    client = client_connection_ec2(key_id, access_key, session_token)

    # Get the first VPC description dict : 
    response = client.describe_vpcs()
    vpc_desc = response.get("Vpcs")
    #print(vpc_desc)

    # Get the first VPC id in the list of the dict returned by vpc_responce : 
    vpc_id = vpc_desc[0].get('VpcId')
    #print(vpc_id)

    
    # Connection created : 
    ec2 = create_connection_ec2(key_id, access_key, session_token)
    
    
    # The step is to perform later on :
    """
    # Create Vpc : 
    vpc_id= create_vpc('172.31.0.0/16',ec2)
    print("\n\n"+vpc_id+"\n\n")
    """
    
# ==========================================================================================================
    # =============> Pensez plutôt a recupérer le security_group par default avec les instructions ci-dessous
    #===========================================================================================================
    #Get the standard security group from the standard VPC :

    sg_dict = client.describe_security_groups(Filters=[
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
    #print(security_group_id)

    # Creation of a security group is to perform later on
    """
    security_group_id = (sg_dict.get("SecurityGroups")[0]).get("GroupId")    
    #print(security_group_id)
    # Create security group for vpcId : 
    security_group_id = create_security_group('Security_group_created_for_lab','Security_group',vpc_id,ec2)
    print("\n"+security_group_id+"\n")"""
    
    
    #Get the standard subnets from the standard VPC :
    subnets= client.describe_subnets(Filters=[
         {
            'Name': 'vpc-id',
            'Values': [
                vpc_id,
            ]
        }
    ])
    print(subnets)
    #subnets=['subnet-053bd769717aa1641','subnet-00aebad3742819994']

    
    # Create 4 instances with t2.large as intance type
    #By choice, we create the 4 EC2 instances for Cluster 1 in availability zones us-east-1a and us-east-1b: 
    Availabilityzons_Cluster1=['us-east-1a','us-east-1b','us-east-1a','us-east-1b','us-east-1a']
    instance_type = "t2.large"
    print("\n\n Creating instances of Cluster 1 with type : t2.large\n\n")
    instances_t2= create_instance_ec2(5,ami_id, instance_type,key_pair_name,ec2,security_group_id,Availabilityzons_Cluster1)
    #print(instances_t2)
    print("\n\n Instances created succefuly instance type : t2.large")


    # Create 5 instances with m4.large as instance type:
    #By choice, we create the 5 EC2 instances for Cluster 2 in avaibility zones us-east-1c and us-east-1d: 
    Availabilityzons_Cluster2=['us-east-1c','us-east-1d','us-east-1c','us-east-1d']
    instance_type = "m4.large"
    print("\n\n Creating instances, type : m4.large\n\n")
    instances_m4= create_instance_ec2(4,ami_id, instance_type,key_pair_name,ec2,security_group_id,Availabilityzons_Cluster2)
    #print(instances_m4)
    print("\n\n Instances created succefuly instance type  : m4.large")

    #Creaye the two targets groups (Clusters)
    target_group_1=create_target_group('TargetGroup1',vpc_id,80, ec2)
    target_group_2=create_target_group('TargetGroup2',vpc_id,8080, ec2)

    time.sleep(120)

    # Targets registration on target groups
    register_targets(instances_t2,target_group_1,80)
    register_targets(instances_m4,target_group_2,8080)


    #Create Load balancer 
    load_balancer=create_load_balancer(subnets,security_group_id)
    print('load balancer')

    #Create listeners listener
    listener_group1=create_listener(load_balancer,target_group_1,80)

    listener_group2=create_listener(load_balancer,target_group_2,8080)
    print('Listeners créés')

    #Create listeners rules
    rule_list_1=create_listener_rule(listener_group1,target_group_1,'/cluster1')
    rule_list_2=create_listener_rule(listener_group2,target_group_2,'/cluster2')
    print('Règles créées')

    """
    #Terminate EC2 instances when not needed
    total_instances=instances_t2+instances_m4
    time.sleep(160)
    terminate_instances(total_instances,ec2)
    print("Instances terminated")
    """