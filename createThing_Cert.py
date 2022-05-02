# Connecting to AWS
import json
import os
# Create random name for things
import random
import string

import boto3

# Parameters for Thing
howmany = 10
homeDir = 'D:/code/UIUC/437/lab4/certificates'
if not os.path.isdir(homeDir):
    os.mkdir(homeDir)
currenthave = len(os.listdir(homeDir))

defaultPolicyName = 'IOTPolicy'
thingGroupName = 'IOTgroup1'
thingGroupArn = 'arn:aws:iot:us-west-2:403483949402:thinggroup/IOTgroup1'

thingId = ''
thingArn = ''
thingName = ''


###################################################
def createThing(device_num):
    global thingClient
    global thingName, thingArn, thingId

    thingName = ''.join(
        [random.choice(string.ascii_letters + string.digits) for n in range(15)])
    thingResponse = thingClient.create_thing(
        thingName=thingName
    )
    print(f'Creating certificate for thing \t\"{thingName}\"\t under dir:../certificates/device_{device_num}')

    data = json.loads(json.dumps(thingResponse, sort_keys=False, indent=4))
    for element in data:
        if element == 'thingArn':
            thingArn = data['thingArn']
        elif element == 'thingId':
            thingId = data['thingId']
            createCertificate(device_num)


def createCertificate(device_num):
    global thingClient
    certResponse = thingClient.create_keys_and_certificate(
        setAsActive=True
    )
    data = json.loads(json.dumps(certResponse, sort_keys=False, indent=4))
    for element in data:
        if element == 'certificateArn':
            certificateArn = data['certificateArn']
        elif element == 'keyPair':
            PublicKey = data['keyPair']['PublicKey']
            PrivateKey = data['keyPair']['PrivateKey']
        elif element == 'certificatePem':
            certificatePem = data['certificatePem']
        elif element == 'certificateId':
            certificateId = data['certificateId']
    directory = "device_" + str(device_num)
    path = os.path.join(homeDir, directory)
    os.mkdir(path)
    with open(path + "/" + directory + '.public.pem', 'w') as outfile:
        outfile.write(PublicKey)
    with open(path + "/" + directory + '.private.pem', 'w') as outfile:
        outfile.write(PrivateKey)
    with open(path + "/" + directory + '.cert.pem', 'w') as outfile:
        outfile.write(certificatePem)

    response = thingClient.attach_policy(
        policyName=defaultPolicyName,
        target=certificateArn
    )
    response = thingClient.attach_thing_principal(
        thingName=thingName,
        principal=certificateArn
    )
    response = thingClient.add_thing_to_thing_group(
        thingGroupName=thingGroupName,
        thingGroupArn=thingGroupArn,
        thingName=thingName,
        thingArn=thingArn,
    )


thingClient = boto3.client('iot')
for i in range(howmany):
    createThing(currenthave + i)
