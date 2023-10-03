import boto3 
import matplotlib.pyplot as plt

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
    TargetGroups_Metrics[str(LoadBalancer_Name)+'/'+str(TargterGroup)]=metric_list,
    TargetGroups_Metrics['timestamps']=time_stamps

    return TargetGroups_Metrics

#Function to plot metric values of all target groups of an ALB in one graph and save it in a path
def plot_metric_per_cluster(values_timestamp_dict,MetricName,path):
   
   time=values_timestamp_dict['timestamps']
   del values_timestamp_dict['timestamps']
   LoadBalancerName=list(values_timestamp_dict.keys())[0].split('/')[0]
   plt.figure()
   for key in list(values_timestamp_dict.keys()):
      plt.plot(time,values_timestamp_dict[key],label=str(key))
   plt.xlabel('Time')
   plt.ylabel(str(MetricName))
   plt.title(str(MetricName)+' per cluster of '+str(LoadBalancerName))
   plt.legend()
   plt.tight_layout()
   plt.savefig(path+str(MetricName)+'_per_cluster_of_'+str(LoadBalancerName)+'.png')


#Function to get a dictionary of timestamps List and Cloudwatch metric List of an ALB in a specific time interval: 
def get_metric_load_balancer(Cloudwatch_client,Id,MetricName,LoadBalancer_Name,Start_Time, End_Time,Period,Stat):
   LB_Metrics={}
   LB_cloudwatch=Cloudwatch_client.get_metric_data(
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
                                
                            }
                        ]
                    },
                 'Stat':Stat,
                 'Label': str(MetricName+' metric for '+LoadBalancer_Name),
                 'Period':Period,
                 'ReturnData':True

                }
            },
        ],
        StartTime=Start_Time,
        EndTime=End_Time
    )
   metric_list=LB_cloudwatch['MetricDataResults'][0]['Values']
   time_stamps=LB_cloudwatch['MetricDataResults'][0]['Timestamps']
   LB_Metrics[str(LoadBalancer_Name)]=metric_list
   LB_Metrics['timestamps']=time_stamps

   return LB_Metrics
   

#Function to plot metric values of an ALB and save the graph in a path
def plot_metric_load_balancer(values_timestamp_dict,MetricName,path):
   
   time=values_timestamp_dict['timestamps']
   del values_timestamp_dict['timestamps']
   LoadBalancerName=list(values_timestamp_dict.keys())[0]
   metric=list(values_timestamp_dict.values())[0]
   plt.figure()
   plt.plot(time,metric,label=str(LoadBalancerName))
   plt.xlabel('Time')
   plt.ylabel(str(MetricName))
   plt.title(str(MetricName)+' of '+str(LoadBalancerName))
   plt.legend()
   plt.tight_layout()
   plt.savefig(path+str(MetricName)+'_of_'+str(LoadBalancerName)+'.png')

#Just test
dict1={'timestamps': [1,2,3,4],'ALB/Cluster1': [5,4,6,8],'ALB/Cluster2': [-5,-4,-6,-8]}
MetricName='Test'
path='Visualizations\\'
#plot_metric_per_cluster(dict1,MetricName,path)

dict2={'timestamps': [1,2,3,4],'ALB': [5,4,6,8]}

plot_metric_load_balancer(dict2,MetricName,path)
