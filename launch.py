from __future__ import print_function

import json
import boto3

ecs = boto3.client('ecs', region_name='us-east-1')

def lambda_handler(event, context):

    event = {
        "stressRead": True,
        "stressWrite": True,
        "wcu": 5,
        "rcu": 5,
        "tableRegion": "us-east-1",
        "tableName": "MyTable2",
        "hashKey": "MyKey",
        "duration": 420
    }

    # Log the received event
    print("Received event: " + json.dumps(event, indent=2))

    # Check we have the required event properties to continue
    expected_fields = ["tableRegion", "tableName", "hashKey", "duration"]
    for f in expected_fields:
        if f not in event:
            print("Expecting field {} in event data. Exiting.".format(f))
            exit(1)

    read_stress_config = ""
    write_stress_config = ""

    if "stressRead" in event and event["stressRead"] is True:
        if "rcu" not in event:
            print("Expecting rcu in event data. Exiting.".format(f))
            exit(1)
        read_stress_config = "-sr -rcu {}".format(event["rcu"])

    if "stressWrite" in event and event["stressWrite"] is True:
        if "rcu" not in event:
            print("Expecting wcu in event data. Exiting.".format(f))
            exit(1)
        write_stress_config = "-sw -wcu {}".format(event["wcu"])

    if read_stress_config == "" and write_stress_config == "":
        print("No stressRead or stressWrite flags given")
        exit(1)

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
                                'name': 'WRITE_STRESS_CONFIG',
                                'value': str(write_stress_config)
                            },
                            {
                                'name': 'READ_STRESS_CONFIG',
                                'value': str(read_stress_config)
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
                    'assignPublicIp': 'ENABLED'
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
