source ./vars.env

sed -i "s|\$thing_group_arn|$thing_group_arn|" iot-deployment.json 
sed -i "s|\$version|$version|" iot-deployment.json

deployment_id=$(aws greengrassv2 create-deployment --cli-input-json file://iot-deployment.json --query 'deploymentId' --output text)
echo "export deployment_id=$deployment_id" >> vars.env