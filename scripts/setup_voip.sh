#!/bin/bash

cd /home/ec2-user 
sudo yum install -y docker
sudo service docker start

aws configure set aws_access_key_id $3
aws configure set aws_secret_access_key $4
aws configure set default.region us-west-2

sudo docker login -u AWS -p $(aws ecr get-login-password --region us-west-2) $2.dkr.ecr.us-west-2.amazonaws.com


sudo docker pull $2.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-agi-$1
sudo docker pull $2.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-voip-$1

mkdir agi
mkdir asterisk

aws s3 cp s3://lsit-zoom-queue-env-vars/frontdesk-app-agi/$1.env agi/$1.env

aws s3 sync s3://lsit-zoom-queue-env-vars/frontdesk-app-voip/$1 asterisk

sudo docker stop $(sudo docker ps -q --filter ancestor=042277129213.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-voip-$1 )
sudo docker stop $(sudo docker ps -q --filter ancestor=042277129213.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-agi-$1 )

sudo docker run --net=host --mount type=bind,source="$(pwd)"/asterisk/sounds,target=/var/lib/asterisk/sounds --mount type=bind,source="$(pwd)"/asterisk/moh,target=/var/lib/asterisk/moh --mount type=bind,source="$(pwd)"/asterisk/conf,target=/etc/asterisk -d $2.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-voip-$1

sudo docker run --net=host --env-file=agi/$1.env -d $2.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-agi-$1