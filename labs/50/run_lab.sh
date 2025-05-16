source ./vars.env

# Install the Python SDK if not already installed
python3 -m pip show AWSIoTPythonSDK >/dev/null 2>&1 || python3 -m pip install AWSIoTPythonSDK

# create a random job id name
job_id="iot-reboot-job-id-$(cat /dev/urandom | tr -dc 'a-z0-9' | head -c 8)"
echo "export job_id=$job_id" >> vars.env

# send the job to aws
aws iot create-job --job-id $job_id --targets $thing_arn --document file://reboot-job.json --target-selection SNAPSHOT


# update the thing_name in the agent py script.
sed -i "s|THING_NAME =.*|THING_NAME = \'$thing_name\'|" job_agent.py

# run the job agent
python3 job_agent.py \
  -e $(aws iot describe-endpoint --endpoint-type iot:Data-ATS  --output text) \
  -c certificate.pem \
  -k privateKey.pem \
  -r AmazonRootCA1.pem 



