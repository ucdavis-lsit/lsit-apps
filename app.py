import os

from aws_cdk import core as cdk
from aws_cdk import core

from lsit_stack.lsit_stack import LSITStack
from network_stack.network_stack import NetworkStack
from scheduled_task_stack.scheduled_task_stack import ScheudledTaskStack    

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

# Development
dev_frontdesk_frontend_stack = LSITStack(
    app,
    "ZoomQueueFrontendDevelopmentStack",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.development_cluster,
    network_stack.development_load_balancer,
    {
        "app_name": "zoom-queue-frontend",
        "app_env": "development",
        "task_port": 3000,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/zoom-queue-frontend-development:latest",
        "load_balancer_port": 3000,
        "health_check_path": "/api/health",
        "https_load_balancer_priority": 1,
        "http_load_balancer_priority": 1,
        "host_headers": ["dev.advisingfrontdesk.lsit.ucdavis.edu"],
        "certificate_arn": "arn:aws:acm:us-west-2:042277129213:certificate/d18674bd-6a83-41aa-b10f-e379c2f8a1fa"
    },
    env=core.Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

LSITStack(
    app,
    "ZoomQueueBackendDevelopmentStack",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.development_cluster,
    network_stack.development_load_balancer,
    {
        "app_name": "zoom-queue-backend",
        "app_env": "development",
        "task_port": 3001,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/zoom-queue-backend-dev:latest",
        "load_balancer_port": 3001,
        "https_listener": dev_frontdesk_frontend_stack.https_listener,
        "http_listener": dev_frontdesk_frontend_stack.http_listener,
        "https_load_balancer_priority": 2,
        "http_load_balancer_priority": 2,
        "host_headers": ["dev.api.frontdesk.lsit.ucdavis.edu"],
        "certificate_arn": "arn:aws:acm:us-west-2:042277129213:certificate/2e50e559-3efd-444e-8937-8feadec6003b"
    },
    env=core.Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

LSITStack(
    app,
    "ZoomQueueWebsocketDevelopmentStack",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.development_cluster,
    network_stack.development_load_balancer,
    {
        "app_name": "zoom-queue-websocket",
        "app_env": "development",
        "task_port": 80,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/zoom-queue-websocket-dev:latest",
        "load_balancer_port": 8080,
        "https_listener": dev_frontdesk_frontend_stack.https_listener,
        "http_listener": dev_frontdesk_frontend_stack.http_listener,
        "https_load_balancer_priority": 3,
        "http_load_balancer_priority": 3,
        "host_headers": ["dev.websocket.frontdesk.lsit.ucdavis.edu"],
        "certificate_arn": "arn:aws:acm:us-west-2:042277129213:certificate/697571d7-e696-4c3c-9c42-d47f538fea7a"
    },
    env=core.Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

ScheudledTaskStack(
    app,
    "ZoomQueueDevelopmentCleanupCron",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.development_cluster,
    {
        "app_name": "zoom-queue-cleanup-cron",
        "app_env": "development",
        "image_uri": "curlimages/curl:latest",
    },
    env=core.Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)


# Prod
frontdesk_frontend_stack = LSITStack(
    app,
    "FrontDeskAppClientProdStack",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    network_stack.load_balancer,
    {
        "app_name": "frontdesk-app-client",
        "app_env": "production",
        "task_port": 3000,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-client-prod:latest",
        "load_balancer_port": 3000,
        "health_check_path": "/api/health",
        "https_load_balancer_priority": 1,
        "http_load_balancer_priority": 1,
        "host_headers": ["advisingfrontdesk.lsit.ucdavis.edu"],
        "certificate_arn": "arn:aws:acm:us-west-2:042277129213:certificate/a9930618-8c81-482e-b43c-0e9d1f06b616",
        "is_private": True
    },
    env=core.Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

LSITStack(
    app,
    "FrontDeskAppServerProdStack",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    network_stack.load_balancer,
    {
        "app_name": "frontdesk-app-server",
        "app_env": "production",
        "task_port": 3001,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-server-prod:latest",
        "load_balancer_port": 3001,
        "https_listener": frontdesk_frontend_stack.https_listener,
        "http_listener": frontdesk_frontend_stack.http_listener,
        "https_load_balancer_priority": 2,
        "http_load_balancer_priority": 2,
        "host_headers": ["api.frontdesk.lsit.ucdavis.edu"],
        "certificate_arn": "arn:aws:acm:us-west-2:042277129213:certificate/4c608488-49d4-4fb8-9310-982170d9a394",
        "is_private": True
    },
    env=core.Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

LSITStack(
    app,
    "FrontDeskAppWebsocketProdStack",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    network_stack.load_balancer,
    {
        "app_name": "frontdesk-app-websocket",
        "app_env": "production",
        "task_port": 80,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-websocket-prod:latest",
        "load_balancer_port": 8080,
        "https_listener": frontdesk_frontend_stack.https_listener,
        "http_listener": frontdesk_frontend_stack.http_listener,
        "https_load_balancer_priority": 3,
        "http_load_balancer_priority": 3,
        "host_headers": ["websocket.frontdesk.lsit.ucdavis.edu"],
        "certificate_arn": "arn:aws:acm:us-west-2:042277129213:certificate/9ee190dd-6d07-4bfd-a293-dc3048c56c6b",
        "is_private": True
    },
    env=core.Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)


app.synth()
