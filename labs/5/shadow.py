#!/usr/bin/python

# Lab 5.1 - Device Shadows with AWS IoT SDK
# Make sure your host and region are correct.

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
from awsiot import iotshadow
import sys
import time
import signal
from random import randint
import json

# Setup our MQTT client and security certificates
# Make sure your certificate names match what you downloaded from AWS IoT
target_ep = '<target-endpoint>-ats.iot.us-east-1.amazonaws.com'
thing_name = 'shadow-ratchet'
cert_filepath = './certificate.pem'
private_key_filepath = './privateKey.pem'
ca_filepath = './AmazonRootCA1.pem'

# Variables referenced in the program are shown below
# Our motor is not currently running.
MOTOR_STATUS = "OFF"
pub_topic_1 = 'data/temperature'
pub_topic_2 = 'data/vibration'

# Callback when connection is accidentally lost
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. Error: {}".format(error))

# Callback when an interrupted connection is re-established
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if (return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present):
        print("Session did not persist Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread
        # Evaluate result with a callback instead
        resubscribe_future.add_done_callback(on_resubscribe_complete)

# Callback to resubscribe to previously subscribed topics upon lost session
def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))

# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

proxy_options = None

mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=target_ep,
    port=8883,
    cert_filepath=cert_filepath,
    pri_key_filepath=private_key_filepath,
    client_bootstrap=client_bootstrap,
    ca_filepath=ca_filepath,
    on_connection_interrupted=on_connection_interrupted,
    on_connection_resumed=on_connection_resumed,
    client_id=thing_name,
    clean_session=True,
    keep_alive_secs=30,
    http_proxy_options=proxy_options
)

print("Connecting to {} with client ID '{}'...".format(target_ep, thing_name))

# Connect to the gateway
while True:
    try:
        connect_future = mqtt_connection.connect()
        # Future.result() waits until a result is available
        connect_result = connect_future.result()
    except:
        print("Connection to IoT Core failed... retrying in 5s.")
        time.sleep(5)
        continue
    else:
        print(connect_result)
        print("Connected!")
        break

# Set up the Classic Shadow handler
shadowClient = iotshadow.IotShadowClient(mqtt_connection)

# Function to update the Classic Shadow
def updateDeviceShadow():
    global shadowClient
    global MOTOR_STATUS
    
    # Set the Classic Shadow with the current motor status and check if it was successful
    print("Updating shadow with reported motor status")
    payload = {"MOTOR": MOTOR_STATUS}
    shadowMessage = iotshadow.ShadowState(reported=payload)
    update_shadow_request = iotshadow.UpdateShadowRequest(state=shadowMessage, thing_name=thing_name)
    update_shadow_future = shadowClient.publish_update_shadow(request=update_shadow_request, qos=mqtt.QoS.AT_LEAST_ONCE)
    update_shadow_future.add_done_callback(on_classic_shadow_update_complete)

# Callback to update the Classic Shadow
def on_classic_shadow_update_complete(update_shadow_future):
    update_shadow_result = update_shadow_future.result()
    print("Device shadow reported properties updated")

    if update_shadow_result is not None:
        sys.exit("Server rejected Classic Shadow update request")

# Callback to get the Classic Shadow delta changes
# Add your custom logic to react to these delta changes, like turning ON the motor
def on_classic_shadow_update_event(shadowDeltaUpdatedEvent):
    global MOTOR_STATUS
    print("Device Shadow delta update received")
    desiredState = shadowDeltaUpdatedEvent.state
    
    # Get the desired motor status, act on it, and then update device shadow with new reported state
    status = desiredState["MOTOR"]
    if status == "ON":
        print("Request received to start motor. Starting motor and vibration analysis.")
        MOTOR_STATUS = status
        updateDeviceShadow()
    elif status == "OFF":
        print("Stopping motor and vibraiton analysis.")
        MOTOR_STATUS = status
        updateDeviceShadow()
    else:
        print("Invalid motor action, motor can only be 'ON' or 'OFF'")

def publishMessage(message, topic):
    message_json = json.dumps(message)
    publish_future, _ = mqtt_connection.publish(
        topic=topic,
        payload=message_json,
        qos=mqtt.QoS.AT_LEAST_ONCE
    )
    publish_result = publish_future.result()
    return publish_result

# This sends a random temperature message to the topic pub_topic_1
# and random vibration message to the topic pub_topic_2, if the motor is ON
def send():
    temp = randint(0, 100)
    message = {
        'temp': temp,
        'unit': 'F'
    }
    publish_result = publishMessage(message, topic=pub_topic_1)
    print("Temperature Message Published")
    
    # Only send motor vibration data if the motor is on.
    if MOTOR_STATUS == "ON":
        vibration = randint(-500, 500)
        message = {
            'vibration' : vibration
        }
        publish_result = publishMessage(message, topic=pub_topic_2)
        print ("Motor is running, Vibration Message Published")

# Set the initial motor status in the device shadow
updateDeviceShadow()

# Listen for delta changes
shadow_delta_updated_subscription = iotshadow.ShadowDeltaUpdatedSubscriptionRequest(thing_name=thing_name)
shadowClient.subscribe_to_shadow_delta_updated_events(
    request=shadow_delta_updated_subscription,
    qos=mqtt.QoS.AT_LEAST_ONCE,
    callback=on_classic_shadow_update_event
)

while True:
    send()
    time.sleep(5)

#To check and see if your message was published to the message broker go to the MQTT Client and subscribe to the iot topic and you should see your JSON Payload