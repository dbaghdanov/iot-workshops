source ./vars.env

aws iot detach-policy --policy-name $policy_name --target $certificate_arn 

aws iot update-certificate --certificate-id $certificate_id --new-status INACTIVE 

aws iot delete-certificate --certificate-id $certificate_id 

aws iot delete-policy --policy-name $policy_name

aws iot delete-thing --thing-name $thing_name

rm vars.env AmazonRootCA1.pem certificate.pem publicKey.pem privateKey.pem