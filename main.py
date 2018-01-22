import time
import datetime
import random
import boto3


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


def main():

    # Input CLI parameters
    region = "eu-west-1"
    table = "MyTable2"
    hash_key = "MyKey"
    wps = 5
    thread_count = 2 # TODO: Implement CSP
    duration = 10

    # Connect to the DynamoDB Service
    ddb_client = boto3.client('dynamodb', region_name=region)

    for i in range(0, 999): # TODO: Implement into threads?
        stress_test(wps, duration, do_dynamo_write, 'writes', ddb_client, table, hash_key)
        stress_test(wps, duration, do_dynamo_read, 'reads', ddb_client, table, hash_key)


def stress_test(count_per_interval, duration, func, type, ddb_client, table, hash_key):
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
            print("Completed {} {} in {} seconds. Target is {}.\n".format(count, type, time_interval, count_per_interval))
            last_operation_time = interval_start_time = get_current_time()
            count = 0
        else:
            time.sleep(0.1)

    print("Stress test ended at {}".format(get_current_time()))

if __name__ == '__main__':
    main()