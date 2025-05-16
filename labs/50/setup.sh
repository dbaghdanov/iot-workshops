touch vars.env

random=$(cat /dev/urandom | tr -dc 'a-z0-9' | head -c 8)
thing_name="jobagent_$random"
policy_name="JobAgent_Policy_$random"
echo "export thing_name=$thing_name" >> vars.env
echo "export policy_name=$policy_name" >> vars.env

# create a thing
thing_arn=$(aws iot create-thing --thing-name $thing_name --query 'thingArn' --output text)
echo "export thing_arn=$thing_arn" >> vars.env

# create the cartificates and download the keys
read certificate_arn certificate_id < <(aws iot create-keys-and-certificate \
    --set-as-active \
    --certificate-pem-outfile certificate.pem \
    --public-key-outfile publicKey.pem \
    --private-key-outfile privateKey.pem \
    --query '[certificateArn,certificateId]' --output text)

echo "export certificate_arn=$certificate_arn" >> vars.env
echo "export certificate_id=$certificate_id" >> vars.env

# create an iot policy
aws iot create-policy --policy-name $policy_name --policy-document file://iot-policy.json

# attach the cert arn to our iot policy                   
aws iot attach-policy --policy-name $policy_name --target $certificate_arn

# download the amazon root CA
curl -Lo AmazonRootCA1.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem


## We can create a job by passing the job document directly, we don't HAVE to create a bucket, that that's an option too
# # create a bucket for our jobs documents
# bucket_name="iot-job-documents-$(cat /dev/urandom | tr -dc 'a-z0-9' | head -c 8)"
# echo "export bucket_name=$bucket_name" >> vars.env

# aws s3api create-bucket --bucket "$bucket_name"

# # and upload our job document
# aws s3 cp reboot-job.json s3://$bucket_name/

# create an iot job

