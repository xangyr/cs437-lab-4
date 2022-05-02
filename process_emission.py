#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#

# greengrassHelloWorldCounter.py
# Demonstrates a simple publish to a topic using Greengrass core sdk
# This lambda function will retrieve underlying platform information and send a hello world message along with the
# platform information to the topic 'hello/world/counter' along with a counter to keep track of invocations.
#
# This Lambda function requires the AWS Greengrass SDK to run on Greengrass devices.
# This can be found on the AWS IoT Console.

import json
import logging
import platform
import sys
import time

import greengrasssdk

# Setup logging to stdout
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Creating a greengrass core sdk client
client = greengrasssdk.client("iot-data")

# Retrieving platform information to send from Greengrass Core
my_platform = platform.platform()

# Counter to keep track of invocations of the function_handler
my_counter = 0
max_emission = [ 0.0 for i in range(5) ]

def function_handler(event, context):
    global my_counter
    global max_emission
    
    car = event["car"]
    emission = event["emission"]
    max_emission[int(car)] = max( float(max_emission[int(car)]), float(emission) )
    try:
        if not my_platform:
            client.publish(
                topic="emission/car/{}".format(car),
                queueFullPolicy="AllOrException",
                payload=json.dumps(
                    {"message": "Car {} has max emission CO2 {}".format(car, str(max_emission[int(car)])) }
                ),
            )
        else:
            client.publish(
                topic="emission/car/{}".format(car),
                queueFullPolicy="AllOrException",
                payload=json.dumps(
                    {
                       "message": "Car {} has max emission CO2 {}".format(car, str(max_emission[int(car)]))
                    }
                ),
            )
    except Exception as e:
        logger.error("Failed to publish message: " + repr(e))
    
    return
