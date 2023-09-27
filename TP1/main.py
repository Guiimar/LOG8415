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
#for crating the connection to EC2 : 
def create_connection_ec2(key_id, access_key, session_token):
    ec2 =  boto3.resource('ec2',
                       'us-east-1',
                       aws_access_key_id= key_id,
                       aws_secret_access_key=access_key ,
                      aws_session_token= session_token) 
    return(ec2)
    

#Create instances : 
def create_instance_ec2(num_instances,ami_id,
    instance_type,key_pair_name,resource,security_group_id):
    instances=[]
    for i in range(num_instances):
        instance=resource.create_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_pair_name,
            MinCount=1,
            MaxCount=1,
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
        print(f'{instances[i]} is starting')
    return instances

def create_target_group(targetname,vpc_id):
    tg_response=client.create_target_group(
        Name=targetname,
        Protocol='HTTP',
        Port=80,
        VpcId=vpc_id,
        TargetType ='instance'
    )
    target_group_arn = tg_response["TargetGroups"][0]["TargetGroupArn"]    
    return target_group_arn

def register_targets(instances_ids,target_group_arn):
    targets=[]
    for instance_id in instances_ids:
        targets.append({"Id":instance_id,"Port":80})

    tg_registered=client.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=targets
    )

    return tg_registered



def create_load_balancer(subnets,security_group):
    response = client.create_load_balancer(
        Name="my-load-balancer",
        Subnets=subnets,
        SecurityGroups=[security_group]
                )
    load_balancer_arn = response["LoadBalancers"][0]["LoadBalancerArn"]

    return load_balancer_arn

def create_listener(load_balancer_arn,target_group_arn):
    response_listener=client.create_listener(
    LoadBalancerArn=load_balancer_arn,
    Port=80,
    Protocol='HTTP',
    DefaultActions=[
        {
            'TargetGroupArn': target_group_arn,
            'Type':'forward'
        },
    ]
    )
    return response_listener


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
        key_id = config_object.get("resource","key_id")
        access_key = config_object.get("resource","access_key")
        session_token = config_object.get("resource","session_token")
        ami_id = config_object.get("ami","ami_id")
        
    """
    key_id="ASIA37YNGERBT6X6LQTC"
    access_key="ndrRz7s0K2gKwCdexLh3F7tSvLrhDNtkEHv1Gozg"
    session_token="FwoGZXIvYXdzEKr//////////wEaDBO5ze9K0vRG+ashZCLOAU0/95fFC+tjNFPeM7QOEnhtztXUO0eZZytXAEulebfcWHep2MZKlMhgjsqtOGxS1hZ7HfvoXW9bsTwMVnT3DBavYP6PPINFXQjexeEegaalIRXaKKwufyF6feVMVH6XkXRxqY6E1Tc7/yJwaO3nR5hqjVj+SRgqjY7K8pzA7/gaxopW6nt8Xu/M5XlRq951SIlps2YKxyesvYsEud0uGlDztap7uyR7kEbDdUJwDYVShJuRnRgYR45n7K3C25xGQZdRhHrgjXZ234BewLBQKI+40agGMi1+WsdAzD767xhcOfSXY6FCqB7ZGdHFdVEMq6ASBqlAc+Zp7dtDqBqwT2PYHko="
    ami_id ='ami-03a6eaae9938c858c'
    """

    # Connection created : 
    ec2 = create_connection_ec2(key_id, access_key, session_token)
    client = boto3.client('elbv2', region_name='us-east-1',aws_access_key_id= key_id,
                       aws_secret_access_key=access_key ,
                      aws_session_token= session_token)
    print("\n\n Connection made succefuly \n\n")

    key_pair_name = "vockey"
    security_group_id = "sg-06437851b56b69a96"

    vpc_id="vpc-0d882582a823a8039"

    subnets=['subnet-053bd769717aa1641','subnet-00aebad3742819994']
    # Create 4 instances with t2.large as intance type: 
    instance_type = "t2.large"
    print("\n\n creating instances, type : t2.large\n\n")
    instances_t2= create_instance_ec2(3,ami_id, instance_type,key_pair_name,ec2,security_group_id)
    print(instances_t2)
    print("\n\n instances created succefuly instance type : t2.large")

    # Create 4 instances with m4.large as instance type:
    instance_type = "m4.large"
    print("\n\n creating instances, type : m4.large\n\n")
    instances_m4= create_instance_ec2(3,ami_id, instance_type,key_pair_name,ec2,security_group_id)
    print(instances_m4)
    print("\n\n instances created succefuly instance type  : m4.large")

    #creation des targets groups
    target_group_1=create_target_group('TargetGroup1',vpc_id)
    target_group_2=create_target_group('TargetGroup2',vpc_id)

    time.sleep(60)

    #Enregistrement targets
    register_targets(instances_t2,target_group_1)
    register_targets(instances_m4,target_group_2)


    #Load balancer 
    load_balancer=create_load_balancer(subnets,security_group_id)
    print('load balancer')

    print(target_group_2)
    total_instances=instances_t2+instances_m4
    time.sleep(160)
    terminate_instances(total_instances,ec2)
    print("Instances terminated")