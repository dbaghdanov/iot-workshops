# AWS IoT Immersion Day workshops

## Getting Started:

Quickest:

To run AWS CLI commands against one of your accounts/regions, you will need to fetch Access Keys from your AWS SSO Landing Page

Select a sandbox account and copy/paste the access keys into your bash shell.

You should set your region manually with:
```
export AWS_REGION=us-west-2
```

## Lab 1

Automates the [Lab 1.1 - Getting Setup with the AWS IoT Device SDK Python v2](https://catalog.workshops.aws/aws-iot-immersionday-workshop/en-US/aws-iot-core/device-sdk-v2/lab11-gettingstarted2)

**To Setup**:
```
cd labs/1
chmod 744 setup.sh cleanup.sh
./setup.sh
```

This will:
- Create a `ratchet` IoT Thing
- Create an attach the IoT Policy
- Create and attach a certificate and download the keys
- Updates `ratchet.py` with the Thing endpoint

**To run**:
You can then run `python3 ratchet.py` to start it, which will start publishing to the `device/ratchet/data` topic.
```
bash-5.2# python3 ratchet.py 
Connecting to <target-endpoint>-ats.iot.us-east-1.amazonaws.com with client ID 'ratchet'...
Connected!
Subscribing to topic app/data
Subscribed with QoS.AT_LEAST_ONCE
Publishing message on topic device/ratchet/data
Publishing message on topic device/ratchet/data
Publishing message on topic device/ratchet/data
```

**To cleanup**:
```
./cleanup.sh
```

This clean up script will:
- Deactiveate, disassociate, and delete the certificates
- Delete the Policy
- Delete the Thing

