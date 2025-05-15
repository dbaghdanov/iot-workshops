# set the region and account id in the iot policy
sed -i "s|\[region\]|$AWS_REGION|" iot-policy.json
sed -i "s|\[account_id\]|$(aws sts get-caller-identity --query Account --output text)|" iot-policy.json

touch vars.env

policy_name="RatchetWorkshopPolicy_db"
thing_name="RatchetWorkshop_Core_db"
thing_group="RatchetWorkshop_db"
iam_policy_name="RatchetWorkshopTokenExchangeRoleAccess_db"
iam_role_name="RatchetWorkshopTokenExchangeRole_db"
iot_role_alias="RatchetWorkshopRoleAlias_db"

echo "export policy_name=$policy_name" >> vars.env
echo "export thing_name=$thing_name" >> vars.env
echo "export thing_group=$thing_group" >> vars.env
echo "export iam_policy_name=$iam_policy_name" >> vars.env
echo "export iam_role_name=$iam_role_name" >> vars.env
echo "export iot_role_alias=$iot_role_alias" >> vars.env

thing_group_arn=$(aws iot create-thing-group --thing-group-name $thing_group --query 'thingGroupArn' --output text)
echo "export thing_group_arn=$thing_group_arn" >> vars.env

aws iot create-thing --thing-name $thing_name
aws iot add-thing-to-thing-group --thing-group-name $thing_group --thing-name $thing_name
aws iot create-policy --policy-name $policy_name --policy-document file://iot-policy.json
# download iot certs and capture the arn
read certificate_arn certificate_id < <(aws iot create-keys-and-certificate \
    --set-as-active \
    --certificate-pem-outfile certificate.pem \
    --public-key-outfile publicKey.pem \
    --private-key-outfile privateKey.pem \
    --query '[certificateArn,certificateId]' --output text)

echo "export certificate_arn=$certificate_arn" >> vars.env
echo "export certificate_id=$certificate_id" >> vars.env

# attach the cert arn to our iot policy                   
aws iot attach-policy --policy-name $policy_name --target $certificate_arn

# download the amazon root CA
curl -Lo AmazonRootCA1.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem

# create an iam policy
policy_arn=$(aws iam create-policy --policy-name $iam_policy_name --policy-document file://iam-policy.json --query 'Policy.Arn' --output text)
echo "export policy_arn=$policy_arn" >> vars.env
role_arn=$(aws iam create-role --role-name $iam_role_name --assume-role-policy-document file://iam-role-trust-policy.json --query 'Role.Arn' --output text)
echo "export role_arn=$role_arn" >> vars.env
aws iam attach-role-policy --role-name $iam_role_name --policy-arn $policy_arn

aws iot create-role-alias --role-alias $iot_role_alias --role-arn $role_arn



