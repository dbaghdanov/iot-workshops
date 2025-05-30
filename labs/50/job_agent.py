from __future__ import print_function
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from uuid import uuid4
import json
import argparse
import time
import signal
import sys
from threading import Thread

parser = argparse.ArgumentParser(description='An AWS IoT Device Management Jobs agent implementation')
parser.add_argument('-e', '--endpoint', required=True)
parser.add_argument('-c', '--cert', required=True)
parser.add_argument('-k', '--key', required=True)
parser.add_argument('-r', '--rootca', required=False, default='certs/rootCA.pem')

banner = """
      _       _                                _
     | |     | |         /\                   | |
     | | ___ | |__      /  \   __ _  ___ _ __ | |_
 _   | |/ _ \| '_ \    / /\ \ / _` |/ _ \ '_ \| __|
| |__| | (_) | |_) |  / ____ \ (_| |  __/ | | | |_
 \____/ \___/|_.__/  /_/    \_\__, |\___|_| |_|\__|
                               __/ |
                              |___/
"""

THING_NAME = 'jobagent'
JOBS_TOPIC_BASE = "$aws/things/{}/jobs"

class DeviceJobAgent:
    def __init__(self, name, endpoint, cert, key, rootca):
        self.jobsSucceeded = 0
        self.updatesRejected = 0
        self._thingName = name
        self._jobTopicBase = JOBS_TOPIC_BASE.format(name)
        self._endpoint = endpoint
        self._cert = cert
        self._key = key
        self._rootca = rootca
        self._rebooting = False

    def isRebooting(self):
        return self._rebooting

    # Since the MQTT client runs on his own thread, a publish in a subscriptions call back that uses QoS1 
    # needs his own separate thread to succeed
    def threadedQoS1Publish(self, topic, payload):
        Thread(target=self._iotClient.publish, kwargs={'topic':topic, 'payload':payload, 'QoS':1}).start()

    def executeJob(self, execution):
        print('Executing job ID, version, number: {}, {}, {}'.format(execution['jobId'], execution['versionNumber'], execution['executionNumber']))
        print('With jobDocument: ' + json.dumps(execution['jobDocument']))
        statusDetails = {
            "handledBy": "jobagent",
            "at": int(time.time())
        }
        self.updateJobStatus(statusDetails, execution['jobId'], execution['versionNumber'], execution['executionNumber'])
        print('Executing: {}'.format(execution['jobDocument']['command']))
        self._rebooting = True


    def updateJobStatus(self, statusDetails, jobId, versionNumber, executionNumber):
        status = 'SUCCEEDED'
        updateDocument = {
            'jobId': jobId, 
            'status': status,
            'statusDetails': statusDetails,
            'expectedVersion': versionNumber,
            'executionNumber': executionNumber
        }
        print('Sending update to AWS IoT Jobs on {}'.format(self._jobTopicBase + '/{}/update'.format(jobId)))
        self.threadedQoS1Publish(self._jobTopicBase + '/{}/update'.format(jobId), json.dumps(updateDocument))

    def newJobReceived(self, client, userdata, message):
        if self._rebooting:
            return
        print(message.payload)
        print('Job execution changed -> start next job')
        token = str(uuid4())
        self.threadedQoS1Publish(self._jobTopicBase+'/start-next', payload=json.dumps({'clientToken': token}))

    def startNextJob(self, client, userdata, message):
        job = json.loads(message.payload.decode('utf-8'))
        if 'execution' in job:
            execution = job['execution']
            print('Received job {} with document {}'.format(execution['jobId'], execution['jobDocument']))
            print('\n> Press ENTER to execute it... ', end='')
            sys.stdin.readline()
            self.executeJob(execution)
        else:
            print('Start-next saw no execution: ' + message.payload.decode('utf-8'))

    def updateJobSuccessful(self, client, userdata, message):
        print('Update job successful')
        print(message.payload)

    def updateJobRejected(self, client, userdata, message):
        print('Update job rejected')
        print(message.payload)

    def startNextRejected(self, client, userdata, message):
        print('Start next rejected')
        print(message.payload)

    def addSubscription(self, topic, callback):
        print('Subscribing to ' + topic)
        self._iotClient.subscribe(topic, 0, callback)

    def removeSubscription(self, topic):
        print('Unsubscribing from ' + topic)
        self._iotClient.unsubscribe(topic)

    def setupJobsSubscriptions(self):
        # Sets up subscriptions to the AWS IoT Jobs topics: https://docs.aws.amazon.com/iot/latest/developerguide/jobs-devices.html
        self.addSubscription(self._jobTopicBase + '/notify-next', self.newJobReceived)
        self.addSubscription(self._jobTopicBase + '/+/get/accepted', self.updateJobSuccessful)
        self.addSubscription(self._jobTopicBase + '/+/get/rejected', self.updateJobRejected)
        self.addSubscription(self._jobTopicBase + '/start-next/accepted', self.startNextJob)
        self.addSubscription(self._jobTopicBase + '/start-next/rejected', self.startNextRejected)

    def unsubscribe(self):
        self.removeSubscription(self._jobTopicBase + '/notify-next')
        self.removeSubscription(self._jobTopicBase + '/+/get/accepted')
        self.removeSubscription(self._jobTopicBase + '/+/get/rejected')
        self.removeSubscription(self._jobTopicBase + '/start-next/accepted')
        self.removeSubscription(self._jobTopicBase + '/start-next/rejected')

    def disconnect(self):
        self.unsubscribe()

    def init(self):
        if self._rebooting: 
            print('JobAgent has rebooted')
            self._rebooting = False
        print(banner)
        self._iotClient = AWSIoTMQTTClient(self._thingName)
        self._iotClient.configureEndpoint(self._endpoint, 8883)
        self._iotClient.configureCredentials(self._rootca, self._key, self._cert)
        self._iotClient.configureConnectDisconnectTimeout(10)  # Time to wait until CONNACK is recevied
        self._iotClient.configureMQTTOperationTimeout(5)  # Time to wait for a comfirmation of an MQTT message
        print('Initializing...')
        print('Connecting to {}'.format(self._endpoint))
        self._iotClient.connect()
        # Create the subscriptions
        self.setupJobsSubscriptions()
        print('Ready')

        # Check if there are any jobs to execute
        print('Checking for new jobs...')
        token = str(uuid4())
        # Send a message to start the next pending job (if any)
        # This first call is ok, since it is not inside a subscribe callback
        self._iotClient.publish(self._jobTopicBase+'/start-next', payload=json.dumps({'clientToken': token}), QoS=1)

if __name__ == '__main__':
    args = parser.parse_args()
    agent = DeviceJobAgent(THING_NAME, args.endpoint, args.cert, args.key, args.rootca)
    while True:
        agent.init()
        while not agent.isRebooting():
            time.sleep(1)
        agent.disconnect()

