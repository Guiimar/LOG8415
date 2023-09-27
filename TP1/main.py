import boto3

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
        instances.append(resource.create_instances(
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
        ))
        print(f'{instances[i]} is starting')
    return instances

def create_target_group(group_name,vpc_id):
    tg_response=client.create_target_group(
        Name=group_name,
        Protocol='HTTP',
        Port=80,
        VpcId=vpc_id
    )
    target_group_arn = tg_response["TargetGroups"][0]["TargetGroupArn"]
    #Register target?
    
    return target_group_arn

def register_targets(instances_ids):
    targets=[]
    for instance_id in instances_ids:
        targets.append({"Id":instance_id,"Port":80})

    tg_registered=client.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=targets
    )

    returntg_registered



def create_load_balancer(security_group_id):
    response = client.create_load_balancer(
        Name="my-load-balancer",
        Subnets=["subnet-id1", "subnet-id2"],  
        SecurityGroups=[security_group_id],
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

# Here is the main program :
if __name__ == '__main__':
    key_id="ASIAZWRC4RAEAGX6KGFH"
    access_key="EHoHpJirh5FU/KZA8ZcIaydZq+rsTh8791MBkDvC"
    session_token="FwoGZXIvYXdzEJ3//////////wEaDGk0yV3u3CA5uqDnpiLKAUSQY+lwfobIBiYYi8KpayUJh2lHLZTVaZoIwOhtSXtAPmPENLdqjzlW/xbn53FayrP4R86S/OsD3ArolCK3kGZYtkgqUXzHt33B6Cf1zSyMCfcHh1oDR0O7Ixj3/BLPjGx0cvVBmbA33wWWAFuUFrcpz+Uas03F2d6LppaNDXlrTzhR01HaISC6skdZOnOK7codTd6ctQzh/1++45M/LriPh0p+5LIE3qPbYmcZB6XEuzCCMtvbXH1UXzkEVd7XqldEa63V7HHgtlAoqNDOqAYyLfwPAUTLSgPfUtMaTexUDsY+l4I50uzfleLzRmBTvMUnPdG6xaKiWLgYElpMYA=="
    ami_id = "ami-08bf0e5db5b302e19"

    # Connection created : 
    ec2 = create_connection_ec2(key_id, access_key, session_token)
    print("\n\n Connection made succefuly \n\n")

    key_pair_name = "vockey"
    security_group_id = "sg-0512a04b7ff12441a"

    # Create 4 instances with t2.large as intance type: 
    instance_type = "t2.large"
    print("\n\n creating instances, type : t2.large\n\n")
    instances = create_instance_ec2(4,ami_id, instance_type,key_pair_name,ec2,security_group_id)
    print(instances)
    print("\n\n instances created succefuly instance type : t2.large")

    # Create 4 instances with m4.large as instance type:
    instance_type = "m4.large"
    print("\n\n creating instances, type : m4.large\n\n")
    instances = create_instance_ec2(4,ami_id, instance_type,key_pair_name,ec2,security_group_id)
    print(instances)
    print("\n\n instances created succefuly instance type  : m4.large")
