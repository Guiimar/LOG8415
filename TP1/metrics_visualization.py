import boto3 

#Function to create Cloudwatch client:
def client_cloudwatch(aws_access_key_id, aws_secret_access_key, aws_session_token):
    cloudwatch_client =  boto3.client('cloudwatch',
                       'us-east-1',
                       aws_access_key_id= aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key ,
                      aws_session_token= aws_session_token) 
   
    
    return(cloudwatch_client)

#Function to get a dictionary of timestamps List and Cloudwatch metric Lists of target groups of an ALB in a specific time interval: 
def get_metric_clusters(Cloudwatch_client,Id,MetricName,LoadBalancer_Name,TargetGroups_Names_list,Start_Time, End_Time,Period,Stat):
   TargetGroups_Metrics={}
   for TargterGroup in  TargetGroups_Names_list:

    Target_cloudwatch=Cloudwatch_client.get_metric_data(
        MetricDataQueries=[
            {
                'Id':Id,
                'MetricStat':{
                    'Metric':{
                        'Namespace': 'AWS/ApplicationELB',
                        'MetricName':MetricName,
                        'Dimensions':[
                            {'Name':'LoadBalancer',
                                'Value': LoadBalancer_Name
                                
                            },
                            {
                                'Name':'TargetGroup',
                                'Value':TargterGroup

                            }
                        ]
                    },
                 'Stat':Stat,
                 'Label': str(MetricName+' metric for '+TargterGroup+' Of '+LoadBalancer_Name),
                 'Period':Period,
                 'ReturnData':True

                }
            },
        ],
        StartTime=Start_Time,
        EndTime=End_Time
    )
    metric_list=Target_cloudwatch['MetricDataResults'][0]['Values'],
    time_stamps=Target_cloudwatch['MetricDataResults'][0]['Timestamps']
    TargetGroups_Metrics[str(TargterGroup)+str(MetricName)]=metric_list,
    TargetGroups_Metrics['timestamps']=time_stamps

    return TargetGroups_Metrics


def get_metric_load_balancer():

def get_metric_ec2():
   
def plot_metric_clusters():

def plot_metric_load_balncer():
   
def plot_metric_ec2():



