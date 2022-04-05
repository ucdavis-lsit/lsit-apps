from aws_cdk import core as cdk
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ec2 as ec2
import aws_cdk.aws_sns as sns
import aws_cdk.aws_sns_subscriptions as subscriptions
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as event_targets

class MonitoringStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ecs_alerts_topic = sns.Topic(self, "ECSAlerts")
        ecs_alerts_topic.add_subscription(subscriptions.EmailSubscription("dssit-devs-exceptions@ucdavis.edu"))

        task_stopped_rule = events.Rule(
            self,
            "ECSTaskStoppedRule",
            event_pattern=events.EventPattern(
                source=["aws.ecs"],
                detail_type=[
                    "ECS Task State Change"
                ],
                detail={
                    "lastStatus":[
                        "STOPPED",
                    ],
                    "group": [
                        "service:frontdesk-app-websocket-production",
                        "service:frontdesk-app-server-production",
                        "service:frontdesk-app-client-production",
                    ],
                }
            )
        )
        task_stopped_rule.add_target(
            event_targets.SnsTopic(ecs_alerts_topic)
        )