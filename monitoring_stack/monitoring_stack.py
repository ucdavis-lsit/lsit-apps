from aws_cdk import Stack
from constructs import Construct
import aws_cdk.aws_sns as sns
import aws_cdk.aws_sns_subscriptions as subscriptions
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as event_targets

class MonitoringStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.ecs_alerts_topic = sns.Topic(self, "ECSAlerts")
        self.ecs_alerts_topic.add_subscription(subscriptions.EmailSubscription("dssit-devs-exceptions@ucdavis.edu"))

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
                        "service:qualtrics-tools-production"
                    ],
                }
            )
        )
        task_stopped_rule.add_target(
            event_targets.SnsTopic(self.ecs_alerts_topic)
        )