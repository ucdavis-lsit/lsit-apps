from aws_cdk import core as cdk
import aws_cdk.aws_sqs as sqs

class QueueStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, queue_props: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Required props
        queue_name = queue_props["queue_name"]
        sqs.Queue(
            self,
            construct_id,
            queue_name=queue_name,
            receive_message_wait_time=cdk.Duration.seconds(20),
            )
            # TODO fifo=True)
