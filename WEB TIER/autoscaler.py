import boto3
import time
# import threading

ec2 = boto3.resource('ec2', region_name='us-east-1')
sqs = boto3.client('sqs', region_name='us-east-1')

REQUEST_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/<AWS-ACCOUNT-ID>/<QUEUE_ID>-req-queue'
AMI_ID = 'AMI_ID'
INSTANCE_TYPE = 't2.micro'
SECURITY_GROUP_IDS = ['SECURITY_GROUPS']
KEY_NAME = 'KEY_NAME'
MAX_INSTANCES = 20
INSTANCE_PREFIX = 'app-tier-instance'
IAM_ROLE_SQS_S3_FULL_ACCESS_ARN = 'arn:aws:iam::<AWS_ACCOUNT_ID>:instance-profile/<IAM_ROLE_S3_SQS_FULL_ACCESS>'

def scale_instances():
    while True:
        response = sqs.get_queue_attributes(QueueUrl=REQUEST_QUEUE_URL, AttributeNames=['ApproximateNumberOfMessages'])
        message_count = int(response['Attributes']['ApproximateNumberOfMessages'])

        print("MESSAGES IN REQUEST QUEUE: ", message_count)
        
        desired_instance_count = min(MAX_INSTANCES, message_count)
        
        print("DESIRED INSTANCES COUNT", desired_instance_count)

        instances = list(ec2.instances.filter(Filters=[
            {'Name': 'tag:Name', 'Values': [f'{INSTANCE_PREFIX}-*']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]))
        current_instance_count = len(instances)
        
        if desired_instance_count > current_instance_count:
            for i in range(desired_instance_count - current_instance_count):
                instance_number = current_instance_count + i + 1
                ec2.create_instances(
                    ImageId=AMI_ID,
                    MinCount=1,
                    MaxCount=1,
                    InstanceType=INSTANCE_TYPE,
                    SecurityGroupIds=SECURITY_GROUP_IDS,
                    KeyName=KEY_NAME,
                    IamInstanceProfile={'Arn': IAM_ROLE_SQS_S3_FULL_ACCESS_ARN},
                    TagSpecifications=[{
                        'ResourceType': 'instance',
                        'Tags': [{'Key': 'Name', 'Value': f'{INSTANCE_PREFIX}-{instance_number}'}]
                    }]
                )
        elif desired_instance_count < current_instance_count:
            instances_to_terminate = instances[desired_instance_count:]
            for instance in instances_to_terminate:
                instance.terminate()

        time.sleep(15)

if __name__ == "__main__":
    scale_instances()
