import os

from aws_cdk import App, Environment

from lsit_stack.lsit_stack import LSITStack
from network_stack.network_stack import NetworkStack
from queue_stack.queue_stack import QueueStack
from scheduled_task_stack.scheduled_task_stack import ScheudledTaskStack    
from monitoring_stack.monitoring_stack import MonitoringStack
from getvfd_stack.getvfd_stack import GetVFDStack
from queue_stack.queue_stack import QueueStack
from voip_stack.voip_stack import VOIPStack


CDK_DEFAULT_ACCOUNT=os.environ["CDK_DEFAULT_ACCOUNT"]
CDK_DEFAULT_REGION=os.environ["CDK_DEFAULT_REGION"]

app = App()

network_stack = NetworkStack(
    app,
    "NetworkStack",
    {
        "aws_account_name": "LSITZoomQueue"
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
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
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/d18674bd-6a83-41aa-b10f-e379c2f8a1fa"]
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
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
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/2e50e559-3efd-444e-8937-8feadec6003b"]
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
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
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/697571d7-e696-4c3c-9c42-d47f538fea7a"]
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
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
        "command_override": ["sh","-c","curl -XDELETE https://dev.api.frontdesk.lsit.ucdavis.edu/api/guest?key=$API_KEY"]
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

ScheudledTaskStack(
    app,
    "ZoomQueueDevelopmentCleanupAnnouncements",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.development_cluster,
    {
        "app_name": "zoom-queue-cleanup-announcements",
        "app_env": "development",
        "image_uri": "curlimages/curl:latest",
        "command_override": ["sh","-c",'curl -XDELETE "https://dev.api.frontdesk.lsit.ucdavis.edu/api/announcement?key=$API_KEY&domain=$DOMAIN"']
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
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
        "health_check_path": "/api/health",
        "https_load_balancer_priority": 1,
        "http_load_balancer_priority": 1,
        "host_headers": [
            "advisingfrontdesk.lsit.ucdavis.edu",
            "uea.advisingfrontdesk.lsit.ucdavis.edu",
            "lsit.advisingfrontdesk.lsit.ucdavis.edu",
            "grad.advisingfrontdesk.lsit.ucdavis.edu",
            "physics.advisingfrontdesk.lsit.ucdavis.edu",
            "eps.advisingfrontdesk.lsit.ucdavis.edu",
            "yellowcluster.advisingfrontdesk.lsit.ucdavis.edu",
            "ehe.advisingfrontdesk.lsit.ucdavis.edu",
            "langlit.advisingfrontdesk.lsit.ucdavis.edu",
            "antsocmsa.advisingfrontdesk.lsit.ucdavis.edu",
            "caes.advisingfrontdesk.lsit.ucdavis.edu",
            "cs.advisingfrontdesk.lsit.ucdavis.edu",
            "mae.advisingfrontdesk.lsit.ucdavis.edu"
        ],
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/a9930618-8c81-482e-b43c-0e9d1f06b616", "arn:aws:acm:us-west-2:042277129213:certificate/22c71dbb-f075-456a-b9e7-c6c08df51837"],
        "is_private": True,
        "additional_https_rule_priorities": [9,10],
        "additional_http_rule_priorities": [9,10]
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
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
        "https_listener": frontdesk_frontend_stack.https_listener,
        "http_listener": frontdesk_frontend_stack.http_listener,
        "https_load_balancer_priority": 2,
        "http_load_balancer_priority": 2,
        "host_headers": ["api.frontdesk.lsit.ucdavis.edu"],
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/4c608488-49d4-4fb8-9310-982170d9a394"],
        "is_private": True
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
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
        "https_listener": frontdesk_frontend_stack.https_listener,
        "http_listener": frontdesk_frontend_stack.http_listener,
        "https_load_balancer_priority": 3,
        "http_load_balancer_priority": 3,
        "host_headers": ["websocket.frontdesk.lsit.ucdavis.edu"],
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/9ee190dd-6d07-4bfd-a293-dc3048c56c6b"],
        "is_private": True
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

ScheudledTaskStack(
    app,
    "FrontDeskAppProdCleanupGuests",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    {
        "app_name": "frontdesk-app-cleanup-guests",
        "app_env": "production",
        "image_uri": "curlimages/curl:latest",
        "command_override": ["sh","-c","curl -XDELETE https://api.frontdesk.lsit.ucdavis.edu/api/guest?key=$API_KEY"],
        "is_private": True
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

ScheudledTaskStack(
    app,
    "FrontDeskAppProdCleanupAnnouncements",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    {
        "app_name": "frontdesk-app-cleanup-announcements",
        "app_env": "production",
        "image_uri": "curlimages/curl:latest",
        "command_override": ["sh","-c",'curl -XDELETE "https://api.frontdesk.lsit.ucdavis.edu/api/announcement?key=$API_KEY&domain=$DOMAIN"'],
        "is_private": True
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

ScheudledTaskStack(
    app,
    "FrontDeskAppProdCleanupExpiredGuests",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    {
        "app_name": "frontdesk-app-cleanup-expired-guests",
        "app_env": "production",
        "image_uri": "curlimages/curl:latest",
        "command_override": ["sh","-c","curl -XDELETE https://api.frontdesk.lsit.ucdavis.edu/api/expiredGuests?key=$API_KEY"],
        "is_private": True,
        "schedule": {"minute": "*"}
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

ScheudledTaskStack(
    app,
    "FrontDeskAppProductionProcessGuestEvents",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    {
        "app_name": "frontdesk-app-process-guest-events",
        "app_env": "production",
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-server-prod:latest",
        "command_override": ["npm","run","processGuestEvents"],
        "is_private": True,
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

LSITStack(
    app,
    "FrontDeskAppSessionWorkerProductionStack",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    network_stack.load_balancer,
    {
        "app_name": "frontdesk-app-session-worker",
        "app_env": "production",
        "task_port": 3002,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-server-prod:latest",
        "is_private": True,
        "command": ["npm","run","sessionWorker"],
        "is_public_facing": False
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

VOIPStack(
    app,
    "FrontDeskAppVOIPProductionStack",
    network_stack.vpc,
    network_stack.bucket,
    {
        "app_name": "frontdesk-app-voip",
        "app_env": "production",
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

# Staging
LSITStack(
    app,
    "FrontDeskAppClientStagingStack",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    network_stack.load_balancer,
    {
        "app_name": "frontdesk-app-client",
        "app_env": "staging",
        "task_port": 3000,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-client-staging:latest",
        "health_check_path": "/api/health",
        "https_listener": frontdesk_frontend_stack.https_listener,
        "http_listener": frontdesk_frontend_stack.http_listener,
        "https_load_balancer_priority": 4,
        "http_load_balancer_priority": 4,
        "host_headers": [
            "stage.advisingfrontdesk.lsit.ucdavis.edu",
            "uea.stage.advisingfrontdesk.lsit.ucdavis.edu",
            "lsit.stage.advisingfrontdesk.lsit.ucdavis.edu",
            "grad.stage.advisingfrontdesk.lsit.ucdavis.edu",
            "antsocmsa.stage.advisingfrontdesk.lsit.ucdavis.edu",
            "cs.stage.advisingfrontdesk.lsit.ucdavis.edu",
            "langlit.stage.advisingfrontdesk.lsit.ucdavis.edu",
            "orangecluster.stage.advisingfrontdesk.lsit.ucdavis.edu",
        ],
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/42f3fc26-59c4-495f-9166-9e8180d95e6b", "arn:aws:acm:us-west-2:042277129213:certificate/c49d425c-7018-4e7e-92e8-efa15017bfdc"],
        "is_private": True,
        "additional_https_rule_priorities": [8],
        "additional_http_rule_priorities": [8]
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

LSITStack(
    app,
    "FrontDeskAppServerStagingStack",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    network_stack.load_balancer,
    {
        "app_name": "frontdesk-app-server",
        "app_env": "staging",
        "task_port": 3001,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-server-staging:latest",
        "https_listener": frontdesk_frontend_stack.https_listener,
        "http_listener": frontdesk_frontend_stack.http_listener,
        "https_load_balancer_priority": 5,
        "http_load_balancer_priority": 5,
        "host_headers": ["stage.api.frontdesk.lsit.ucdavis.edu"],
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/1ae579ad-54ac-4a6e-bcb7-3e4a547b3a08"],
        "is_private": True
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

LSITStack(
    app,
    "FrontDeskAppWebsocketStagingStack",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    network_stack.load_balancer,
    {
        "app_name": "frontdesk-app-websocket",
        "app_env": "staging",
        "task_port": 80,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-websocket-staging:latest",
        "https_listener": frontdesk_frontend_stack.https_listener,
        "http_listener": frontdesk_frontend_stack.http_listener,
        "https_load_balancer_priority": 6,
        "http_load_balancer_priority": 6,
        "host_headers": ["stage.websocket.frontdesk.lsit.ucdavis.edu"],
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/3e9d0032-9e87-4210-853d-31bec7f931cd"],
        "is_private": True
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

ScheudledTaskStack(
    app,
    "FrontDeskAppStagingCleanupGuests",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    {
        "app_name": "frontdesk-app-cleanup-guests",
        "app_env": "staging",
        "image_uri": "curlimages/curl:latest",
        "command_override": ["sh","-c","curl -XDELETE https://stage.api.frontdesk.lsit.ucdavis.edu/api/guest?key=$API_KEY"],
        "is_private": True
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

ScheudledTaskStack(
    app,
    "FrontDeskAppStagingCleanupAnnouncements",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    {
        "app_name": "frontdesk-app-cleanup-announcements",
        "app_env": "staging",
        "image_uri": "curlimages/curl:latest",
        "command_override": ["sh","-c",'curl -XDELETE "https://stage.api.frontdesk.lsit.ucdavis.edu/api/announcement?key=$API_KEY&domain=$DOMAIN"'],
        "is_private": True
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

ScheudledTaskStack(
    app,
    "FrontDeskAppStagingCleanupExpiredGuests",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    {
        "app_name": "frontdesk-app-cleanup-expired-guests",
        "app_env": "staging",
        "image_uri": "curlimages/curl:latest",
        "command_override": ["sh","-c","curl -XDELETE https://stage.api.frontdesk.lsit.ucdavis.edu/api/expiredGuests?key=$API_KEY"],
        "is_private": True,
        "schedule": {"minute": "*"}
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

ScheudledTaskStack(
    app,
    "FrontDeskAppStagingProcessGuestEvents",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    {
        "app_name": "frontdesk-app-process-guest-events",
        "app_env": "staging",
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-server-staging:latest",
        "command_override": ["npm","run","processGuestEvents"],
        "is_private": True
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

LSITStack(
    app,
    "FrontDeskAppSessionWorkerStagingStack",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    network_stack.load_balancer,
    {
        "app_name": "frontdesk-app-session-worker",
        "app_env": "staging",
        "task_port": 3002,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-server-staging:latest",
        "is_private": True,
        "command": ["npm","run","sessionWorker"],
        "is_public_facing": False
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

# Monitoring
MonitoringStack(
    app,
    "ECSMonitoringStack",
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

# Get VFD
GetVFDStack(
    app,
    "GetVFDStack",
    {
        "app_name": "frontdesk-app-getvfd",
        "app_env": "production",
        "https_listener": frontdesk_frontend_stack.https_listener,
        "http_listener": frontdesk_frontend_stack.http_listener,
        "https_load_balancer_priority": 7,
        "http_load_balancer_priority": 7,
        "host_headers": ["getvfd.ucdavis.edu"],
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/a4fdc45f-ed12-41ec-aadc-f7367c8edd02"],
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION)
)

# Queue Stack
QueueStack(
    app,
    "QueueStack",
    {
        "queue_name": "GuestEventsQueue",
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION)
)

QueueStack(
    app,
    "QueueStagingStack",
    {
        "queue_name": "GuestEventsStagingQueue",
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION)
)

QueueStack(
    app,
    "QueueDevelopmentStack",
    {
        "queue_name": "GuestEventsDevelopmentQueue",
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION)
)



app.synth()
