#!/bin/bash

if [ "$#" -ne 4 ]
then
  echo "Usage: sudo sh $BASH_SOURCE ENVIRONMENT AWS_ACCOUNT_ID AWS_ACCESS_KEY AWS_SECRET_ACCESS_KEY"
  exit 1
fi

cd /home/ec2-user
sudo yum install -y docker
sudo service docker start

aws configure set aws_access_key_id $3
aws configure set aws_secret_access_key $4
aws configure set default.region us-west-2

sudo yum install -y awslogs
sudo systemctl start awslogsd

sudo docker login -u AWS -p $(aws ecr get-login-password --region us-west-2) $2.dkr.ecr.us-west-2.amazonaws.com


sudo docker pull $2.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-agi-$1
sudo docker pull $2.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-voip-$1

mkdir agi
mkdir asterisk

aws s3 cp s3://lsit-zoom-queue-env-vars/frontdesk-app-agi/$1.env agi/$1.env

aws s3 sync s3://lsit-zoom-queue-env-vars/frontdesk-app-voip/$1 asterisk

sudo docker stop $(sudo docker ps -q --filter name=front-desk-app-voip-$1 )
sudo docker stop $(sudo docker ps -q --filter name=front-desk-app-agi-$1 )

sudo docker rm front-desk-app-voip-$1
sudo docker rm front-desk-app-agi-$1

sudo docker run --net=host --mount type=bind,source="$(pwd)"/asterisk/sounds,target=/var/lib/asterisk/sounds --mount type=bind,source="$(pwd)"/asterisk/moh,target=/var/lib/asterisk/moh --mount type=bind,source="$(pwd)"/asterisk/conf,target=/etc/asterisk --log-driver=awslogs --log-opt awslogs-region=us-west-2 --log-opt awslogs-group=/ec2/frontdesk-app-voip-$1 --name front-desk-app-voip-$1 -d $2.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-voip-$1

sudo docker run --net=host --env-file=agi/$1.env --log-driver=awslogs --log-opt awslogs-region=us-west-2 --log-opt awslogs-group=/ec2/frontdesk-app-agi-$1 --name front-desk-app-agi-$1 -d $2.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-agi-$1