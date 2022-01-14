import os

from aws_cdk import core as cdk
from aws_cdk import core

from lsit_stack.lsit_stack import LSITStack
from network_stack.network_stack import NetworkStack

CDK_DEFAULT_ACCOUNT=os.environ["CDK_DEFAULT_ACCOUNT"]
CDK_DEFAULT_REGION=os.environ["CDK_DEFAULT_REGION"]

app = core.App()

network_stack = NetworkStack(
    app,
    "NetworkStack",
    {
        "aws_account_name": "LSITZoomQueue"
    },
    env=core.Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)
LSITStack(
    app,
    "ZoomQueueDevelopmentStack",
    network_stack.vpc,
    network_stack.bucket,
    {
        "app_name": "zoom-queue-websocket",
        "app_env": "development",
        "task_port": 8080,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/zoom-queue-websocket-dev:latest",
        "load_balancer_port": 8080
    },
    env=core.Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

app.synth()
