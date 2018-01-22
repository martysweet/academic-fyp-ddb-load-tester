from __future__ import print_function

import json
import boto3

ecs = boto3.client('ecs', region_name='us-east-1')

def lambda_handler(event, context):

    event = {
        "stressType": "read",
        "tableRegion": "us-east-1",
        "tableName": "MyTable2",
        "hashKey": "MyKey",
        "units": 10,
        "duration": 420
    }

    # Log the received event
    print("Received event: " + json.dumps(event, indent=2))

    try:
        response = ecs.run_task(
            cluster='default',
            taskDefinition='fargate-test-2-TaskDefinition-1XA0M2F4EOB22:1',
            overrides={
                'containerOverrides': [
                    {
                        'name': 'fyp-ddb-stress-test',
                        'environment': [
                            {
                                'name': 'STRESS_TYPE',
                                'value': str(event['stressType'])
                            },
                            {
                                'name': 'TABLE_REGION',
                                'value': str(event['tableRegion'])
                            },
                            {
                                'name': 'TABLE_NAME',
                                'value': str(event['tableName'])
                            },
                            {
                                'name': 'HASH_KEY',
                                'value': str(event['hashKey'])
                            },
                            {
                                'name': 'UNITS',
                                'value': str(event['units'])
                            },
                            {
                                'name': 'DURATION',
                                'value': str(event['duration'])
                            },
                        ]
                    },
                ]
            },
            launchType='FARGATE',
            platformVersion='LATEST',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': [
                        'subnet-e9bce68d',
                    ],
                    'securityGroups': [
                        'sg-b04549c4',
                    ],
                    'assignPublicIp': 'DISABLED'
                }
            }
        )
        print(response)
        return True
    except Exception as e:
        print(e)
        message = 'Error starting task'
        print(message)
        raise Exception(message)
