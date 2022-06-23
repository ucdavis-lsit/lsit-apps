from aws_cdk import Stack, Duration
from constructs import Construct
import aws_cdk.aws_sqs as sqs

class QueueStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, queue_props: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Required props
        queue_name = queue_props["queue_name"]

        # Optional props
        wait_time = queue_props.get("wait_time", 20)

        sqs.Queue(
            self,
            construct_id,
            queue_name=queue_name,
            receive_message_wait_time=Duration.seconds(wait_time),
        )
