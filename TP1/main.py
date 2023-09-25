import boto3

def create_instance_ec2(num_instances,ami_id,instance_type,key_pair_name,resource,count,security_group_id=None):
    instances=[]
    for i in range(num_instances):
        instances.append(resource.create_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_pair_name["KeyName"],
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[security_group_id] if security_group_id else [],
            TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'lab1-ec2-instance-' + str(i + 1)
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
    response=client.create_listener(
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
    return 

