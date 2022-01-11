import os

from aws_cdk import core as cdk
from aws_cdk import core

from network_stack.network_stack import NetworkStack

CDK_DEFAULT_ACCOUNT=os.environ["CDK_DEFAULT_ACCOUNT"]
CDK_DEFAULT_REGION=os.environ["CDK_DEFAULT_REGION"]

app = core.App()

NetworkStack(
    app,
    "NetworkStack",
    {
        "aws_account_name": "LSITZoomQueue"
    }
)

app.synth()
