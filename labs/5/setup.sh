touch vars.env

policy_name="shadow-ratchet-policy"
thing_name="shadow-ratchet"
echo "export policy_name=$policy_name" >> vars.env
echo "export thing_name=$thing_name" >> vars.env

# create a thing
aws iot create-thing --thing-name $thing_name

# create an iot policy
aws iot create-policy --policy-name $policy_name --policy-document file://ratchet-policy.json

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

target_ep=$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --output text)
sed -i "s|target_ep = '.*'|target_ep = \'$target_ep\'|" shadow.py

