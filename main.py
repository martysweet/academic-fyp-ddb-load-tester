import time
import datetime
import random
import boto3
import argparse



def random_country():
    lines = open("countries.txt").read().splitlines()
    return random.choice(lines)


def get_current_time():
    return time.time() + datetime.timedelta(days=3).total_seconds()


def do_dynamo_write(client, table, hash_key):
    country = random_country()
    population = random.randint(500, 200000000)
    city_count = random.randint(5, 1000)

    resp = client.put_item(
        TableName=table,
        Item={
            hash_key: {
                'S': country,
            },
            'population': {
                'N': str(population)
            },
            'cityCount': {
                'N': str(city_count)
            }
        },
        ReturnValues='NONE',
        ReturnConsumedCapacity="TOTAL"
    )

    units_used = resp['ConsumedCapacity']['CapacityUnits']
    print("Wrote: {} with {:d} cities and a population of {:d}. Consumed Units: {}.".format(country, city_count,
                                                                                            population, units_used))


def do_dynamo_read(client, table, hash_key):
    country = random_country()

    resp = client.get_item(
        TableName=table,
        Key={
            hash_key: {
                'S': country,
            }
        },
        ConsistentRead=True,    # Enforce 1 WRU
        ReturnConsumedCapacity="TOTAL"
    )

    city_count = population = "?"
    if 'Item' in resp:
        if 'cityCount' in resp['Item']:
            city_count = resp['Item']['cityCount']['N']
        if 'population' in resp['Item']:
            population = resp['Item']['population']['N']

    units_used = resp['ConsumedCapacity']['CapacityUnits']
    print("Read: {} with {} cities and a population of {}. Consumed Units: {}.".format(country, city_count, population,
                                                                                       units_used))


def main(args):

    # Input CLI parameters
    stress_type = args.stress_type
    region = args.table_region
    table = args.table_name
    hash_key = args.hash_key
    units_per_second = args.units_per_second
    test_duration = args.test_duration

    # Connect to the DynamoDB Service
    if args.aws_profile:
        session = boto3.Session(profile_name=args.aws_profile)
        ddb_client = session.client('dynamodb', region_name=region)
    else:
        ddb_client = boto3.client('dynamodb', region_name=region)

    # Start the requested test
    if stress_type == "write":
        stress_test(units_per_second, test_duration, do_dynamo_write, 'writes', ddb_client, table, hash_key)
    elif stress_type == "read":
        stress_test(units_per_second, test_duration, do_dynamo_read, 'reads', ddb_client, table, hash_key)
    else:
        print("Unknown stress type, use 'read' or 'write'.")


def stress_test(count_per_interval, duration, func, stress_type, ddb_client, table, hash_key):
    # Set parameters for the stress loop
    count = 0
    time_interval = 1
    last_operation_time = get_current_time()
    interval_start_time = get_current_time()
    stress_end_time = get_current_time() + duration

    # Loop for specified duration
    while get_current_time() < stress_end_time:
        current_time = get_current_time()
        time_diff = current_time - last_operation_time
        interval_time_diff = current_time - interval_start_time

        if count < count_per_interval and time_diff < time_interval and interval_time_diff < time_interval:
            func(ddb_client, table, hash_key)
            last_operation_time = get_current_time()
            count += 1
        elif time_diff > time_interval:
            print("Completed {} {} in {} seconds. Target is {}.\n".format(count, stress_type, time_interval, count_per_interval))
            last_operation_time = interval_start_time = get_current_time()
            count = 0
        else:
            time.sleep(0.1)

    print("Stress test ended at {} after {} seconds".format(get_current_time(), duration))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Runs a stress tests against a DynamoDB table at a specified unit consumption rate.",
    )
    parser.add_argument("--stress-type", "-t", required=True, help="Type of stress test to perform, either 'read' or 'write'.")
    parser.add_argument("--table-region", "-r", required=True, help="Region where the table is located.")
    parser.add_argument("--table-name", "-n", required=True, help="Table name to write or read data from.")
    parser.add_argument("--hash-key", "-k", required=True, help="Hash Key of the table, only compatible with type 'S'.")
    parser.add_argument("--units-per-second", "-u", type=int, default=5, help="Amount of units per second that we should attempt to consume.")
    parser.add_argument("--test-duration", "-d", type=int, default=60, help="Duration the test should go on for.")
    parser.add_argument("--aws-profile", help="Profile name to use for the boto3 client.")
    args = parser.parse_args()

    main(args)
