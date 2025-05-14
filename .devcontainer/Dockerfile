# Start from an official Python image (Debian-based)
FROM amazonlinux:2023

RUN dnf upgrade --refresh \
 && dnf update \
 && dnf install -y \
 python3.9-pip \
 java-17-amazon-corretto \
 unzip \
 shadow-utils \
 less \
 && dnf clean all \
 && rm -rf /var/cache/dnf /tmp/*

# # Install AWS CLI v2
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        CLI_URL="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        CLI_URL="https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    curl "$CLI_URL" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

RUN python3 -m pip install awsiotsdk 

# Set default workdir
WORKDIR /workspace

# # # Install Greengrass CLI (replace version as needed)
# RUN mkdir -p /greengrass && \
#     curl -s https://d2s8p88vqu9w66.cloudfront.net/releases/greengrass-nucleus-latest.zip > greengrass-nucleus-latest.zip && \
#     unzip greengrass-nucleus-latest.zip -d GreengrassInstaller && rm greengrass-nucleus-latest.zip


# #Notes:
# - cannot start up the greengrass service as there is no access to systemd.
# - you can run greengrass as a process
# - it will not be able to run lambda containers because they depend on cgroups v1
