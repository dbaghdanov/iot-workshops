source ./vars.env

aws iot detach-policy --policy-name $policy_name --target $certificate_arn 

aws iot update-certificate --certificate-id $certificate_id --new-status INACTIVE 

aws iot delete-certificate --certificate-id $certificate_id 

aws iot delete-policy --policy-name $policy_name

aws iot delete-thing --thing-name $thing_name

rm vars.env AmazonRootCA1.pem certificate.pem publicKey.pem privateKey.pem

aws iam detach-role-policy --role-name $iam_role_name --policy-arn $policy_arn
aws iam delete-role --role-name $iam_role_name
aws iam delete-policy --policy-arn $policy_arn
aws iot delete-role-alias --role-alias $iot_role_alias
