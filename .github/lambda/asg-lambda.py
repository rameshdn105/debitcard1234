import json
import boto3

def lambda_handler(event, context):
    # Initialize the Auto Scaling client
    client = boto3.client('autoscaling')

    # Define your Auto Scaling Group name
    asg_name = 'demo-asg-lambda'
    
    # Extract the action (increase or decrease) and the desired change in capacity from the event
    action = event.get('action')
    change_capacity = event.get('capacity_change', 0)  # Default to 0 if not provided

    # Get the current desired capacity of the ASG
    response = client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
    current_capacity = response['AutoScalingGroups'][0]['DesiredCapacity']

    # Calculate the new desired capacity
    if action == 'increase':
        new_capacity = current_capacity + change_capacity
    elif action == 'decrease':
        new_capacity = current_capacity - change_capacity
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid action. Please use "increase" or "decrease".')
        }

    # Update the ASG's desired capacity
    client.update_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        DesiredCapacity=new_capacity
    )

    return {
        'statusCode': 200,
        'body': json.dumps(f'Auto Scaling Group capacity updated to {new_capacity}.')
    }
