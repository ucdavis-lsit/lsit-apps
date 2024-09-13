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
        "prefix": "LSITZoomQueue",
        "app_name": "frontdesk",
        "aws_bucket_name": "lsit-zoom-queue-env-vars",
        "need_dev": True,
        "is_legacy": True,
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
            "stat.advisingfrontdesk.lsit.ucdavis.edu",
            "amha.advisingfrontdesk.lsit.ucdavis.edu",
            "bae.advisingfrontdesk.lsit.ucdavis.edu",
            "gsm.advisingfrontdesk.lsit.ucdavis.edu",
            "ece.advisingfrontdesk.lsit.ucdavis.edu",
            "bme.advisingfrontdesk.lsit.ucdavis.edu"
        ],
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/557bde58-1690-4c5b-98ed-834368940ed2", "arn:aws:acm:us-west-2:042277129213:certificate/fd32f426-b389-43c0-84a0-788dec47e244", "arn:aws:acm:us-west-2:042277129213:certificate/fe647e66-8606-48e9-8300-81e65df9b249"],
        "is_private": True,
        "additional_https_rule_priorities": [9,10,11,14,15,16],
        "additional_http_rule_priorities": [9,10,11,14,15,16],
        "resource_multiplier": 16,
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
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/f2df87ed-969e-46b1-9953-252eec50dda8"],
        "is_private": True,
        "resource_multiplier": 8,
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
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/785c2a8f-1dec-4f52-b3e9-e7d0bf533185"],
        "is_private": True,
        "resource_multiplier": 2,
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
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/57886965-4836-4c9d-91ae-96f198303398", "arn:aws:acm:us-west-2:042277129213:certificate/b75e325d-e22a-463d-b780-fcfaee3cf5f2"],
        "is_private": True,
        "additional_https_rule_priorities": [8],
        "additional_http_rule_priorities": [8],
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
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/ea04220f-8ffe-4497-9b11-ea6535b35f92"],
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
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/38b10da6-072d-4d00-86ee-c0bf1904e630"],
        "is_private": True,
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
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/7ba4d62f-36bd-481d-bcd2-a565d6b79d9b"],
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

ScheudledTaskStack(
    app,
    "QualtricsToolsAppSyncGroups",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    {
        "app_name": "qualtrics-tools-sync-groups",
        "app_env": "production",
        "image_uri": "curlimages/curl:latest",
        "command_override": ["sh","-c","curl -XGET https://qualtricstools.lsit.ucdavis.edu/api/cron/syncGroups?key=$API_KEY"],
        "is_private": True,
        "schedule": {"minute": "0"}
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
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/2fb5a776-989f-4e85-a8a5-3eaea5e676a3"],
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

ScheudledTaskStack(
    app,
    "QualtricsToolsAppStagingSyncGroups",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    {
        "app_name": "qualtrics-tools-sync-groups",
        "app_env": "staging",
        "image_uri": "curlimages/curl:latest",
        "command_override": ["sh","-c","curl -XGET https://stage.qualtricstools.lsit.ucdavis.edu/api/cron/syncGroups?key=$API_KEY"],
        "is_private": True,
        "schedule": {"minute": "0"}
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

# LSIT UCPath Audit Prod
"""qualtrics_tools_stack = LSITStack(
    app,
    "LSITUCPathAuditAppProdStack",
    network_stack.vpc,
    network_stack.bucket,
    network_stack.cluster,
    network_stack.load_balancer,
    {
        "app_name": "lsit-ucpath-audit",
        "app_env": "production",
        "task_port": 3000,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/lsit-ucpath-audit-production:latest",
        "https_listener": frontdesk_frontend_stack.https_listener,
        "http_listener": frontdesk_frontend_stack.http_listener,
        "health_check_path": "/api/health",
        "https_load_balancer_priority": 17,
        "http_load_balancer_priority": 17,
        "host_headers": [
            "ucpathaudit.lsit.ucdavis.edu",
        ],
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/62a81bbf-fd43-4dd7-b872-16b8537610ca"],
        "is_private": True,
        "monitoring_stack": monitoring_stack
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)"""

# DX Network Stack
dx_network_stack = NetworkStack(
    app,
    "DXNetworkStack",
    {
        "prefix": "DX",
        "aws_bucket_name": "lsit-dx-apps-env-vars",
        "ip_addresses": "172.29.117.0/25",
        "is_dx": True
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

# LSIT UCPath Audit Prod DX
ucpath_audit_stack = LSITStack(
    app,
    "LSITUCPathAuditDXAppProdStack",
    dx_network_stack.vpc,
    dx_network_stack.bucket,
    dx_network_stack.cluster,
    dx_network_stack.load_balancer,
    {
        "app_name": "lsit-ucpath-audit",
        "app_env": "production",
        "task_port": 3000,
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/lsit-ucpath-audit-production:latest",
        "health_check_path": "/api/health",
        "https_load_balancer_priority": 1,
        "http_load_balancer_priority": 1,
        "host_headers": [
            "ucpathaudit.lsit.ucdavis.edu",
        ],
        "certificate_arns": ["arn:aws:acm:us-west-2:042277129213:certificate/62a81bbf-fd43-4dd7-b872-16b8537610ca"],
        "is_private": True,
        "monitoring_stack": monitoring_stack
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

# LSIT UCPath Audit Take Snapshots Prod DX
ScheudledTaskStack(
    app,
    "LSITUCPathAuditDXAppProdTakeSnapshots",
    dx_network_stack.vpc,
    dx_network_stack.bucket,
    dx_network_stack.cluster,
    {
        "app_name": "lsit-ucpath-audit-take-snapshots",
        "app_env": "production",
        "image_uri": "042277129213.dkr.ecr.us-west-2.amazonaws.com/lsit-ucpath-audit-cron-production:latest",
        "is_private": True,
    },
    env=Environment(account=CDK_DEFAULT_ACCOUNT, region=CDK_DEFAULT_REGION),
)

app.synth()
