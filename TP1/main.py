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
from datetime import datetime
from creationModule import *
from send_requests import *
from delete_process import * 
from metrics_visualization import *

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

        
    """
    key_id="ASIA37YNGERBT6X6LQTC"
    access_key="ndrRz7s0K2gKwCdexLh3F7tSvLrhDNtkEHv1Gozg"
    session_token="FwoGZXIvYXdzEKr//////////wEaDBO5ze9K0vRG+ashZCLOAU0/95fFC+tjNFPeM7QOEnhtztXUO0eZZytXAEulebfcWHep2MZKlMhgjsqtOGxS1hZ7HfvoXW9bsTwMVnT3DBavYP6PPINFXQjexeEegaalIRXaKKwufyF6feVMVH6XkXRxqY6E1Tc7/yJwaO3nR5hqjVj+SRgqjY7K8pzA7/gaxopW6nt8Xu/M5XlRq951SIlps2YKxyesvYsEud0uGlDztap7uyR7kEbDdUJwDYVShJuRnRgYR45n7K3C25xGQZdRhHrgjXZ234BewLBQKI+40agGMi1+WsdAzD767xhcOfSXY6FCqB7ZGdHFdVEMq6ASBqlAc+Zp7dtDqBqwT2PYHko="
    ami_id ='ami-03a6eaae9938c858c'
    """
#1============================>SETUP

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

    #--------------------------------------Creating a keypair, or check if it already exists-----------------------------------
    
    key_pair_name = create_keypair('lab1_keypair', ec2_serviceclient)

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
    listeners=[]
    listener_group1=create_listener(elbv2_serviceclient,load_balancerarn,target_group_1,80) 
    listener_group2=create_listener(elbv2_serviceclient,load_balancerarn,target_group_2,8080)
    listeners.append(listener_group1)
    listeners.append(listener_group2)
    print('Listeners created')

    #Create listeners rules
    rules=[]

    rule_list_1=create_listener_rule(elbv2_serviceclient,listener_group1,target_group_1,'/cluster1')
    rule_list_2=create_listener_rule(elbv2_serviceclient,listener_group2,target_group_2,'/cluster2')
    
    rules.append(rule_list_1)
    rules.append(rule_list_2)

    print('Listners rules created')

#2============================>Benchemarking

    #------------------------------------------Sending requests -----------------------------------------------------------------------
    url = elbv2_serviceclient.describe_load_balancers()['LoadBalancers'][0]['DNSName']
    
    StartDate=datetime.utcnow()

    for path in ['cluster1','cluster2']:

        first_sending_thread=Thread(target=first_thread,args=(url,path))
        second_sending_thread=Thread(target=second_thread,args=(url,path))
        
        first_sending_thread.start()
        second_sending_thread.start()
        
        first_sending_thread.join()
        second_sending_thread.join()
    
    EndDate=datetime.utcnow()

    print('script terminated')
    #---------------------------------------------Plot metrics -----------------------------------------------------------------------
    





#3============================>Termination and deletion

    #Terminate EC2 instances when not needed
    total_instances=instances_t2+instances_m4
    terminate_instances(ec2_serviceresource,total_instances)
    print('Instances terminated')
    time.sleep(20)
    delete_load_balancer(elbv2_serviceclient,load_balancerarn,listeners,rules)
    print('load balancer terminated')
    time.sleep(20)
    
    delete_target_groups(elbv2_serviceclient,[target_group_1,target_group_2]) 
    print('deleted target groups') 