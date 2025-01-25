import json
import boto3

def lambda_handler(event, context):
    #print(event)
    action = event['action']
    auto_scaling_groups = []
    auto_scaling_groups_status = []
    overall_status = "READY"
    for asg_config in event['auto_scaling_groups']:
        tags = asg_config.get('tags', {})
        new_min_size = asg_config.get('min_size')
        new_max_size = asg_config.get('max_size')
        new_instance_type = asg_config.get('instance_type')
        asg_name = get_auto_scaling_group_name(tags)
        if asg_name:
            print(f"ASG Name: {asg_name}")
            update_asg(asg_name, new_min_size, new_max_size, new_instance_type, action)

def get_auto_scaling_group_name(tags):
    matching_asg = None
    asg_client = boto3.client('autoscaling')
    filters = [{'Name': 'tag:' + key, 'Values': [value]} for key, value in tags.items()]
    response = asg_client.describe_auto_scaling_groups(Filters=filters)
    matching_asg = response['AutoScalingGroups']
    if matching_asg:
        return matching_asg[0]['AutoScalingGroupName']


def update_asg(asg_name, new_min_size, new_max_size, new_instance_type, action):
    session = boto3.Session()
    asg_client = session.client('autoscaling')
    ec2_client = session.client('ec2')
    response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
    asgs = response['AutoScalingGroups'][0]
    ltid=response['AutoScalingGroups'][0]['LaunchTemplate']['LaunchTemplateId']
    ltversion=response['AutoScalingGroups'][0]['LaunchTemplate']['Version']
    ltresponse = ec2_client.describe_launch_template_versions(
        LaunchTemplateId=ltid,
        Versions=[ltversion]
    )
    launch_template_data=ltresponse['LaunchTemplateVersions'][0]['LaunchTemplateData']
    launch_template_data['InstanceType']=new_instance_type
    new_version_response=ec2_client.create_launch_template_version(
        LaunchTemplateId=ltid,
        LaunchTemplateData=launch_template_data
    )
    new_version=str(new_version_response['LaunchTemplateVersion']['VersionNumber'])
    print(f"New Version: {new_version}") 
    asg_client.update_auto_scaling_group(
    AutoScalingGroupName=asg_name,
    LaunchTemplate={
        'LaunchTemplateId': ltid,
        'Version': new_version  # Use the new version number here
    },
    MinSize=new_min_size,
    MaxSize=new_max_size
    ) 
    instances_to_terminate = [instance['InstanceId'] for instance in asgs['Instances'] if instance['InstanceType'] != new_instance_type]
    print(instances_to_terminate)
    if instances_to_terminate:
        ec2_client.terminate_instances(InstanceIds=instances_to_terminate)
        print(f"Terminating instances with old instance type")
    return response


