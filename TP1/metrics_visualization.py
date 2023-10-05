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
def get_metric_clusters(Cloudwatch_client,Id,MetricName,LoadBalancerarn,TargetGroups_arns_list,Start_Time, End_Time,Period,Stat):
        arn_lb=LoadBalancerarn.split('/')
        arn_lb=arn_lb[1]+'/'+arn_lb[2]+'/'+arn_lb[3]
        TargetGroups_Metrics={}
        for TargterGroup in  TargetGroups_arns_list:
            arn_tg=TargterGroup.split(':')
            arn_tg=arn_tg[5]
            Target_cloudwatch=Cloudwatch_client.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id':Id,
                        'MetricStat':{
                            'Metric':{
                                'Namespace': 'AWS/ApplicationELB',
                                'MetricName':MetricName,
                                'Dimensions':[
                                    {
                                        'Name':'LoadBalancer',
                                        'Value': arn_lb
                                        
                                    },
                                    {
                                        'Name':'TargetGroup',
                                        'Value':arn_tg

                                    }
                                ],

                            },
                        'Stat':Stat,
                        'Period':Period,

                        },
                        'ReturnData':True
                    },
                ],
                StartTime=Start_Time,
                EndTime=End_Time,
            )
            metric_list=Target_cloudwatch['MetricDataResults'][0]['Values'][::-1]
            time_stamps=[t.strftime('%H:%M') for t in Target_cloudwatch['MetricDataResults'][0]['Timestamps']][::-1]
            TargetGroups_Metrics[arn_tg]=metric_list
            TargetGroups_Metrics['timestamps']=time_stamps

        return TargetGroups_Metrics

#Function to plot metric values of all target groups of an ALB in one graph and save it in a path
def plot_metric_per_cluster(values_timestamp_dict,MetricName,path):
    
        time=values_timestamp_dict['timestamps']
        del values_timestamp_dict['timestamps']
        plt.figure(figsize=(12,9))
        for key in list(values_timestamp_dict.keys()):
            plt.plot(time,values_timestamp_dict[key],label=str(key))
        plt.xlabel('Time')
        plt.ylabel(str(MetricName))
        plt.title(str(MetricName)+' per cluster')
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.savefig(path+str(MetricName)+'_per_cluster.png')


#Function to get average of a metric of EC2 instances per cluster: 
def get_average_Instances_metrics_per_cluster(Cloudwatch_client,Id,MetricName,Instances_Ids,Start_Time, End_Time,Period,Stat):
        EC2_Metrics={}
        for EC2_Id in Instances_Ids:
            EC2_Cloudwatch=Cloudwatch_client.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id':Id,
                        'MetricStat':{
                            'Metric':{
                                'Namespace': 'AWS/EC2',
                                'MetricName':MetricName,
                                'Dimensions':[{'Name':'InstanceId',
                                        'Value': EC2_Id
                                        
                                    }
                                ]
                            },
                        'Stat':Stat,
                        'Period':Period,

                        },
                        'ReturnData':True,
                    },
                ],
                StartTime=Start_Time,
                EndTime=End_Time
                )
            EC2_Metrics[EC2_Id]=EC2_Cloudwatch['MetricDataResults'][0]['Values'][::-1]
        
        Average_metric=[sum(i)/len(i) for i in zip(*EC2_Metrics.values())]
        time_stamps=[t.strftime('%H:%M') for t in EC2_Cloudwatch['MetricDataResults'][0]['Timestamps']][::-1]
        
        EC2_Metrics[str(MetricName)]=Average_metric
        EC2_Metrics['timestamps']=time_stamps

        return EC2_Metrics
   

#Function to get average of a metric of EC2 instances per cluster and save the graph in a path
def plot_average_Instances_metrics_per_cluster(values_timestamp_TG1,values_timestamp_TG2,TargetGroup_1arn,TargetGroup_2arn,MetricName,path):
        arn_tg1=TargetGroup_1arn.split(':')
        arn_tg1=arn_tg1[5]
        arn_tg2=TargetGroup_2arn.split(':')
        arn_tg2=arn_tg2[5]
        time=values_timestamp_TG1['timestamps']
        Average_metric_TG1=values_timestamp_TG1[str(MetricName)]
        Average_metric_TG2=values_timestamp_TG2[str(MetricName)]
        plt.figure(figsize=(12,9))
        plt.plot(time,Average_metric_TG1,label=arn_tg1)
        plt.plot(time,Average_metric_TG2,label=arn_tg2)
        plt.xlabel('Time')
        plt.ylabel(str(MetricName)+' Average per Cluster')
        plt.title('EC2 Instances '+str(MetricName)+' average per cluster')
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.savefig(path+'EC2_Instances_'+str(MetricName)+'_average_per_cluster'+'.png')
