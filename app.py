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

# Monitoring
monitoring_stack = MonitoringStack(
    app,
    "ECSMonitoringStack",
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
            "mae.advisingfrontdesk.lsit.ucdavis.edu",
            "orangecluster.advisingfrontdesk.lsit.ucdavis.edu",
            "cee.advisingfrontdesk.lsit.ucdavis.edu",
            "communication.advisingfrontdesk.lsit.ucdavis.edu",
            "intrel.advisingfrontdesk.lsit.ucdavis.edu",
            "linguistics.advisingfrontdesk.lsit.ucdavis.edu",
            "polisci.advisingfrontdesk.lsit.ucdavis.edu",
            "engineering.advisingfrontdesk.lsit.ucdavis.edu",
            "acbnc.advisingfrontdesk.lsit.ucdavis.edu",
            "oeoes.advisingfrontdesk.lsit.ucdavis.edu",
            "lgbtqia.advisingfrontdesk.lsit.ucdavis.edu",
            "menasa.advisingfrontdesk.lsit.ucdavis.edu",
            "our.advisingfrontdesk.lsit.ucdavis.edu",
            "english.advisingfrontdesk.lsit.ucdavis.edu",
            "fas.advisingfrontdesk.lsit.ucdavis.edu",
        ],
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/692cfbeb-e216-4319-890d-47d2283b1429", "arn:aws:acm:us-west-2:042277129213:certificate/22c71dbb-f075-456a-b9e7-c6c08df51837","arn:aws:acm:us-west-2:042277129213:certificate/fd32f426-b389-43c0-84a0-788dec47e244"],
        "is_private": True,
        "additional_https_rule_priorities": [9,10,11,14,15],
        "additional_http_rule_priorities": [9,10,11,14,15],
        "resource_multiplier": 2,
        "monitoring_stack": monitoring_stack
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
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/6955e8b8-66d6-40a5-a3dc-a8e8aff8a6d0"],
        "is_private": True,
        "resource_multiplier": 4,
        "monitoring_stack": monitoring_stack
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
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/0e1bccce-2efd-43d1-a78e-b42150f85c0f"],
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
        "command_override": ["sh","-c",'curl -XDELETE "https://api.frontdesk.lsit.ucdavis.edu/api/announcement?key=$API_KEY"'],
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

ScheudledTaskStack(
    app,
    "FrontDeskAppProductionVoipHealthCheck",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    {
        "app_name": "frontdesk-app-voip-health-check",
        "app_env": "production",
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-server-prod:latest",
        "command_override": ["npm","run","voipHealthCheck"],
        "is_private": True,
        "schedule": {"minute": "/10"}
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
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/57886965-4836-4c9d-91ae-96f198303398", "arn:aws:acm:us-west-2:042277129213:certificate/c49d425c-7018-4e7e-92e8-efa15017bfdc"],
        "is_private": True,
        "additional_https_rule_priorities": [8],
        "additional_http_rule_priorities": [8],
        "auto_scaling": True
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
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/8c266d3f-7717-4c18-bd74-c5af664f9816"],
        "is_private": True,
        "monitoring_stack": monitoring_stack
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
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/da6272ec-7b04-4350-85f1-f24d021da555"],
        "is_private": True,
        "auto_scaling": True
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

VOIPStack(
    app,
    "FrontDeskAppVOIPStagingStack",
    network_stack.vpc,
    network_stack.bucket,
    {
        "app_name": "frontdesk-app-voip",
        "app_env": "staging",
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

ScheudledTaskStack(
    app,
    "FrontDeskAppStagingVoipHealthCheck",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    {
        "app_name": "frontdesk-app-voip-health-check",
        "app_env": "staging",
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/frontdesk-app-server-staging:latest",
        "command_override": ["npm","run","voipHealthCheck"],
        "is_private": True,
        "schedule": {"minute": "/5"}
    },
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

# Qualtrics Tools Prod
qualtrics_tools_stack = LSITStack(
    app,
    "QualtricsToolsAppProdStack",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    network_stack.load_balancer,
    {
        "app_name": "qualtrics-tools",
        "app_env": "production",
        "task_port": 3000,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/qualtrics-tools-production:latest",
        "https_listener": frontdesk_frontend_stack.https_listener,
        "http_listener": frontdesk_frontend_stack.http_listener,
        "health_check_path": "/api/hello",
        "https_load_balancer_priority": 12,
        "http_load_balancer_priority": 12,
        "host_headers": [
            "qualtricstools.lsit.ucdavis.edu",
        ],
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/25e204ac-b682-493a-be0c-06dccfd59297"],
        "is_private": True,
        "monitoring_stack": monitoring_stack
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

ScheudledTaskStack(
    app,
    "QualtricsToolsAppTransferSurverys",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    {
        "app_name": "qualtrics-tools-transfer-surveys",
        "app_env": "production",
        "image_uri": "curlimages/curl:latest",
        "command_override": ["sh","-c","curl -XGET https://qualtricstools.lsit.ucdavis.edu/api/cron/transferSurveys?key=$API_KEY"],
        "is_private": True,
        "schedule": {"minute": "/5"}
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

# Qualtrics Tools Stage
qualtrics_tools_staging_stack = LSITStack(
    app,
    "QualtricsToolsAppStagingStack",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    network_stack.load_balancer,
    {
        "app_name": "qualtrics-tools",
        "app_env": "staging",
        "task_port": 3000,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/qualtrics-tools-staging:latest",
        "https_listener": frontdesk_frontend_stack.https_listener,
        "http_listener": frontdesk_frontend_stack.http_listener,
        "health_check_path": "/api/hello",
        "https_load_balancer_priority": 13,
        "http_load_balancer_priority": 13,
        "host_headers": [
            "stage.qualtricstools.lsit.ucdavis.edu",
        ],
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/daa02917-807c-453e-9a33-7a578e2d7281"],
        "is_private": True
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

ScheudledTaskStack(
    app,
    "QualtricsToolsAppStagingTransferSurverys",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    {
        "app_name": "qualtrics-tools-transfer-surveys",
        "app_env": "staging",
        "image_uri": "curlimages/curl:latest",
        "command_override": ["sh","-c","curl -XGET https://stage.qualtricstools.lsit.ucdavis.edu/api/cron/transferSurveys?key=$API_KEY"],
        "is_private": True,
        "schedule": {"minute": "/5"}
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

app.synth()
