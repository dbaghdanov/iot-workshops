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

## Lab 5.1

This lab has us update a shadow document, which our client will listen for delta changes and take additional actions if the `MOTOR` is `ON`.

[Lab 5.1 - Thing Shadows with the AWS IoT Device SDK Python v2](https://catalog.workshops.aws/aws-iot-immersionday-workshop/en-US/aws-iot-core/device-sdk-v2/lab51-thingshadows)

**To setup**:
```
cd labs/5
chmod 744 setup.sh cleanup.sh
./setup.sh
```

This will:
- Create a `shadow-ratchet` IoT Thing
- Create an attach the IoT Policy
- Create and attach a certificate and download the keys
- Updates `shadow.py` with the Thing endpoint

**To run**:
You can then run `python3 shadow.py` to start it, which will start publishing to the `data/temperature` topic.  While it's running, update the AWS IoT > Manage > Things > shadow-ratchet > Classic Shadow > Device Shadow Document:
```json
{
  "state": {
    "desired": {
      "MOTOR": "ON"
    },
    "reported": {
      "MOTOR": "ON"
    }
  }
}
```

You will see the client updated by the document change, and start to publish the motor status to the `data/vibration` topic.

```
bash-5.2# python3 shadow.py 
Connecting to <target-endpoint>-ats.iot.us-east-1.amazonaws.com with client ID 'shadow-ratchet'...
{'session_present': False}
Connected!
Updating shadow with reported motor status
Device shadow reported properties updated
Temperature Message Published
Temperature Message Published
Temperature Message Published
Temperature Message Published
Device Shadow delta update received
Request received to start motor. Starting motor and vibration analysis.
Updating shadow with reported motor status
Device shadow reported properties updated
Temperature Message Published
Motor is running, Vibration Message Published
```

**To cleanup**:
```
./cleanup.sh
```

This clean up script will:
- Deactiveate, disassociate, and delete the certificates
- Delete the Policy
- Delete the Thing


## Lab 35

[Lab 35 - Setting up AWS IoT GreengrassV2](https://catalog.workshops.aws/aws-iot-immersionday-workshop/en-US/aws-greengrassv2/lab35-greengrassv2-basics)

Setup for this is a little more involved.


**To setup**:
```
cd labs/5
chmod 744 *.sh
./01_setup.sh
./02_setup_greengrass.sh
./03_setup_deployment.sh
```

`01_setup.sh` will setup:
- Create a IoT Thing
- Create a IoT Thing Group
- Create an attach the IoT Policy
- Create and attach a certificate and download the keys
- Create an IAM Role and Policy
- Create an IoT Role Alias to the IAM Role

`02_setup_greengrass.sh` will:
- Installs the latest greengrass-nucleus client
- Configures a `config.yaml`
- Starts a GreenGrass process

Open a new shell/terminal to continue:

`03_setup_deployment.sh` will:
- Create a Deployment which installs the aws.greengrass.cli on clients


```
bash-5.2# ./02_setup_greengrass.sh 
Archive:  greengrass-nucleus-latest.zip
  inflating: GreengrassCore/META-INF/MANIFEST.MF  
  inflating: GreengrassCore/META-INF/SIGNER.SF  
  inflating: GreengrassCore/META-INF/SIGNER.RSA  
  inflating: GreengrassCore/LICENSE  
  inflating: GreengrassCore/NOTICE   
  inflating: GreengrassCore/README.md  
  inflating: GreengrassCore/THIRD-PARTY-LICENSES  
  inflating: GreengrassCore/bin/greengrass.exe  
  inflating: GreengrassCore/bin/greengrass.service.procd.template  
  inflating: GreengrassCore/bin/greengrass.service.template  
  inflating: GreengrassCore/bin/greengrass.xml.template  
  inflating: GreengrassCore/bin/loader  
  inflating: GreengrassCore/bin/loader.cmd  
  inflating: GreengrassCore/conf/recipe.yaml  
  inflating: GreengrassCore/lib/Greengrass.jar  
AWS Greengrass v2.14.3
```

Which will start a Greengrass process:
```
bash-5.2# java -Droot="/greengrass/v2" -Dlog.store=FILE -jar ./GreengrassCore/lib/Greengrass.jar \
  --init-config ./config.yaml \
  --component-default-user ggc_user:ggc_group
Creating user ggc_user 
ggc_user created 
Creating group ggc_group 
ggc_group created 
Added ggc_user to ggc_group 
Launching Nucleus...
Launched Nucleus successfully.
```

Because this is running in a docker container, I chose to start GreenGrass as a process.  Open a new terminal and view the status of `tail -f /greengrass/v2/logs/greengrass.log`

After running `03_setup_deployment.sh` you should see this in the greengrass.log:
```
[INFO] (pool-3-thread-5) com.aws.greengrass.deployment.DeploymentService: deployment-task-execution. Starting deployment task. {Deployment service config={ComponentToGroups={aws.greengrass.Cli....
```


**To cleanup**:
```
./cleanup.sh
```

## Lab 50

[Lab 50 - Basic Device Management](https://catalog.workshops.aws/aws-iot-immersionday-workshop/en-US/aws-iot-device-management/lab50-basicdevicemanagement)

In this lab we run a python script which listens for jobs from IoT.

**To setup**:
```
cd labs/50
chmod 744 *.sh
./setup.sh
./run_lab.sh
```

`setup.sh` will setup:
- Create a IoT Thing
- Create an attach the IoT Policy
- Create and attach a certificate and download the keys

**To run**:

`run_lab.sh` will:
- Download the AWSIoTPythonSDK
- Run `job_agent.py` and await instructions
- Send a reboot job


```
bash-5.2# ./run_lab.sh 
Collecting AWSIoTPythonSDK
  Downloading AWSIoTPythonSDK-1.5.4-py2.py3-none-any.whl (80 kB)
     |████████████████████████████████| 80 kB 2.2 MB/s            
Installing collected packages: AWSIoTPythonSDK
Successfully installed AWSIoTPythonSDK-1.5.4
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv

      _       _                                _
     | |     | |         /\                   | |
     | | ___ | |__      /  \   __ _  ___ _ __ | |_
 _   | |/ _ \| '_ \    / /\ \ / _` |/ _ \ '_ \| __|
| |__| | (_) | |_) |  / ____ \ (_| |  __/ | | | |_
 \____/ \___/|_.__/  /_/    \_\__, |\___|_| |_|\__|
                               __/ |
                              |___/

Initializing...
Connecting to <target-endpoint>-ats.iot.us-east-1.amazonaws.com
Subscribing to $aws/things/jobagent/jobs/notify-next
Subscribing to $aws/things/jobagent/jobs/+/get/accepted
Subscribing to $aws/things/jobagent/jobs/+/get/rejected
Subscribing to $aws/things/jobagent/jobs/start-next/accepted
Subscribing to $aws/things/jobagent/jobs/start-next/rejected
Ready
Checking for new jobs...
Start-next saw no execution: {"clientToken":"469aa0cd-1234-5678-9012-abcdefg1234","timestamp":1747340774}

Received job iot-reboot-job-id-wi6yhgic with document {'command': 'reboot'}

> Press ENTER to execute it... Executing job ID, version, number: iot-reboot-job-id-wi6yhgic, 2, 1
With jobDocument: {"command": "reboot"}
Sending update to AWS IoT Jobs on $aws/things/jobagent/jobs/iot-reboot-job-id-wi6yhgic/update
Executing: reboot
Unsubscribing from $aws/things/jobagent/jobs/notify-next
Unsubscribing from $aws/things/jobagent/jobs/+/get/accepted
Unsubscribing from $aws/things/jobagent/jobs/+/get/rejected
Unsubscribing from $aws/things/jobagent/jobs/start-next/accepted
Unsubscribing from $aws/things/jobagent/jobs/start-next/rejected
JobAgent has rebooted

      _       _                                _
     | |     | |         /\                   | |
     | | ___ | |__      /  \   __ _  ___ _ __ | |_
 _   | |/ _ \| '_ \    / /\ \ / _` |/ _ \ '_ \| __|
| |__| | (_) | |_) |  / ____ \ (_| |  __/ | | | |_
 \____/ \___/|_.__/  /_/    \_\__, |\___|_| |_|\__|
                               __/ |
                              |___/

Initializing...
Connecting to a1bt8cjpr3x541-ats.iot.us-east-1.amazonaws.com
Subscribing to $aws/things/jobagent/jobs/notify-next
Subscribing to $aws/things/jobagent/jobs/+/get/accepted
Subscribing to $aws/things/jobagent/jobs/+/get/rejected
Subscribing to $aws/things/jobagent/jobs/start-next/accepted
Subscribing to $aws/things/jobagent/jobs/start-next/rejected
Ready
Checking for new jobs...
```


**To cleanup**:
```
./cleanup.sh
```

NOTES:

AWS has a list of managed job templates which include tasks such as:
- starting/stopping services
- downloading files
- running commands
- etc
