from __future__ import print_function

import json
import boto3

ecs = boto3.client('ecs', region_name='${AWS::Region}')


def lambda_handler(event, context):

    # event = {
    #     "wcu": 5,
    #     "rcu": 5,
    #     "tableRegion": "us-east-1",
    #     "tableName": "MyTable2",
    #     "hashKey": "MyKey",
    #     "duration": 420
    # }

    # Log the received event
    print("Received event: " + json.dumps(event, indent=2))

    # Check we have the required event properties to continue
    expected_fields = ["tableRegion", "tableName", "hashKey", "duration"]
    for f in expected_fields:
        if f not in event:
            print("Expecting field {} in event data. Exiting.".format(f))
            return {"success": False, "error": "Missing expected field."}

    read_stress_config = ""
    write_stress_config = ""

    if "rcu" in event and event["rcu"] > 0:
        read_stress_config = "-sr -rcu {}".format(event["rcu"])

    if "wcu" in event and event["wcu"] > 0:
        write_stress_config = "-sw -wcu {}".format(event["wcu"])

    if read_stress_config == "" and write_stress_config == "":
        return {"success": False, "error": "Task does not read or write to the table."}

    try:
        response = ecs.run_task(
            cluster='default',
            taskDefinition='${TaskDefinition}',
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
                        '${TaskSubnet}',
                    ],
                    'securityGroups': [
                        '${TaskSg}',
                    ],
                    'assignPublicIp': 'ENABLED'
                }
            }
        )
        print(response)
        return {"success": True, "error": None}
    except Exception as e:
        message = 'Error starting task: {}'.format(e)
        print(message)
        return {"success": False, "error": message}
