from typing import Protocol
from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_efs as efs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk.aws_s3 import Bucket

class VOIPStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, bucket: Bucket, app_props: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Required props
        app_name = app_props["app_name"]
        app_env = app_props["app_env"]

        # Calculated props
        app_prefix = app_name.capitalize() + app_env.capitalize()
        service_name = "{app_name}-{app_env}".format(app_name=app_name, app_env=app_env)
        env_bucket_arn = bucket.bucket_arn

        security_group = ec2.SecurityGroup(
            self,
            "{app_prefix}SecurityGroup".format(app_prefix=app_prefix),
            vpc=vpc,
            allow_all_outbound=True,
            security_group_name=service_name,
        )

        # SSH access
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description='Allow SSH access from anywhere'
        )

        # VOIP MS SIP Traffic
        security_group.add_ingress_rule(
             peer=ec2.Peer.ipv4('208.100.60.40/32'),
            connection=ec2.Port.tcp_range(5060,5080),
            description='VOIP MS'
        )

        security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4('208.100.60.40/32'),
            connection=ec2.Port.udp_range(5060,5080),
            description='VOIP MS'
        )

        # AMI Access
        security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4('100.20.51.51/32'),
            connection=ec2.Port.tcp(5038),
            description='Elastic IP Subnet 1 for AMI'
        )

        security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4('54.68.131.240/32'),
            connection=ec2.Port.tcp(5038),
            description='Elastic IP Subnet 2 for AMI'
        )

        # TODO Remove 
        security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4('73.151.105.106/32'),
            connection=ec2.Port.tcp(5038),
            description="Edgar Macbook"
        )        

        role = iam.Role(
            self,
            "{app_prefix}Role".format(app_prefix=app_prefix),
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMFullAccess")],
            role_name="{app_prefix}EC2Role".format(app_prefix=app_prefix),
            description="Allows {service_name} access to read config files from the appropriate S3 bucket.".format(service_name=service_name)
        )

        policy = iam.Policy(
            self,
            "{app_prefix}Policy".format(app_prefix=app_prefix),
            force=True,
            policy_name="{app_prefix}Policy".format(app_prefix=app_prefix),
            roles=[role]
        )

        policy.add_statements(
            iam.PolicyStatement(
                actions=["s3:GetBucketLocation"],
                resources=[env_bucket_arn]
            ),
            iam.PolicyStatement(
                actions=["s3:GetObject"],
                resources=["{bucket}/{app_name}/*".format(app_name=app_name,bucket=env_bucket_arn)]
            ),
            iam.PolicyStatement(
                actions=["s3:GetObject"],
                resources=["{bucket}/frontdesk-app-agi/*".format(bucket=env_bucket_arn)]
            ),
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogStreams"
                ],
                resources=["*"]
            )
        )

        ec2_instance = ec2.Instance(
            self,
            "{app_prefix}EC2Instance".format(app_prefix=app_prefix),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnets=vpc.public_subnets
            ),
            security_group=security_group,
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.BURSTABLE2,
                instance_size=ec2.InstanceSize.MEDIUM
            ),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            ),
            key_name='ec2_dev',
            instance_name=service_name,
            role=role
        )

        log_group = logs.LogGroup(
            self,
            "{app_prefix}LogGroup".format(app_prefix=app_prefix),
            log_group_name="/ec2/{service_name}".format(service_name=service_name)
        )
        log_group_agi = logs.LogGroup(
            self,
            "{app_prefix}LogGroupAGI".format(app_prefix=app_prefix),
            log_group_name="/ec2/frontdesk-app-agi-{app_env}".format(app_env=app_env)
        )