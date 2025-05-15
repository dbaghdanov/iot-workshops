source ./vars.env

curl -s https://d2s8p88vqu9w66.cloudfront.net/releases/greengrass-nucleus-latest.zip > greengrass-nucleus-latest.zip
unzip greengrass-nucleus-latest.zip -d GreengrassCore && rm greengrass-nucleus-latest.zip
version=$(java -jar ./GreengrassCore/lib/Greengrass.jar --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
echo "export version=$version" >> vars.env
echo "AWS Greengrass v$version"

sed -i "s|certificateFilePath: .*|certificateFilePath: \"$(realpath ./certificate.pem)\"|" config.yaml
sed -i "s|privateKeyPath: .*|privateKeyPath: \"$(realpath ./privateKey.pem)\"|" config.yaml
sed -i "s|rootCaPath: .*|rootCaPath: \"$(realpath ./AmazonRootCA1.pem)\"|" config.yaml
sed -i "s|thingName: .*|thingName: \"$thing_name\"|" config.yaml
sed -i "s|version: .*|version: \"$version\"|" config.yaml
sed -i "s|awsRegion: .*|awsRegion: \"$AWS_REGION\"|" config.yaml
sed -i "s|iotRoleAlias: .*|iotRoleAlias: \"$iot_role_alias\"|" config.yaml
sed -i "s|iotDataEndpoint: .*|iotDataEndpoint: \"$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --output text)\"|" config.yaml
sed -i "s|iotCredEndpoint: .*|iotCredEndpoint: \"$(aws iot describe-endpoint --endpoint-type iot:CredentialProvider --output text)\"|" config.yaml

java -Droot="/greengrass/v2" -Dlog.store=FILE -jar ./GreengrassCore/lib/Greengrass.jar \
  --init-config ./config.yaml \
  --component-default-user ggc_user:ggc_group