from aws_cdk import core as cdk
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk.aws_logs import LogGroup
from aws_cdk.aws_s3 import Bucket
from aws_cdk import aws_events as events
from aws_cdk.aws_events_targets import EcsTask, ContainerOverride

class ScheudledTaskStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, vpc: ec2.Vpc, bucket: Bucket, cluster: ecs.Cluster, app_props: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Required props
        app_name = app_props["app_name"]
        app_env = app_props["app_env"]
        image_uri = app_props["image_uri"]
        
        # Calculated props
        app_prefix = app_name.capitalize() + app_env.capitalize()
        task_name = "{app_name}-{app_env}".format(app_name=app_name, app_env=app_env)
        env_bucket_arn = bucket.bucket_arn

        # Optional
        resource_multiplier = app_props.get("resource_multiplier", 1)
        is_private = app_props.get("is_private", False)
        command_override = app_props.get("command_override", [])
        schedule = app_props.get("schedule", {"minute": "0", "hour": "8"})

        role = iam.Role(
            self,
            "{app_prefix}Role".format(app_prefix=app_prefix),
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")],
            role_name="{app_prefix}ECSTaskExecutionRole".format(app_prefix=app_prefix),
            description="Allows {task_name} tasks to run in ECS and be able to read config files from the appropriate S3 bucket.".format(task_name=task_name)
        )

        policy = iam.Policy(
            self,
            "{app_prefix}Policy".format(app_prefix=app_prefix),
            force=True,
            policy_name="{app_prefix}ConfigRead".format(app_prefix=app_prefix),
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
            )
        )

        task = ecs.FargateTaskDefinition(
            self,
            "{app_prefix}Task".format(app_prefix=app_prefix),
            cpu=256,
            memory_limit_mib=512,
            family=task_name,
            execution_role=role,
            task_role=role
        )

        image = ecs.ContainerImage.from_registry(image_uri)

        task.add_container(
            task_name,
            image=image,
            cpu=256*resource_multiplier,
            memory_limit_mib=512*resource_multiplier,
            logging=ecs.LogDriver.aws_logs(
                stream_prefix=task_name,
                log_group=LogGroup(
                    scope=self,
                    id="{app_prefix}LogGroup".format(app_prefix=app_prefix),
                    log_group_name="/ecs/{task_name}".format(task_name=task_name),
                    removal_policy=cdk.RemovalPolicy.DESTROY
            )),
            environment_files=[
                ecs.S3EnvironmentFile(
                    Bucket.from_bucket_arn(
                        self,
                        "{app_prefix}Bucket".format(app_prefix=app_prefix),
                        env_bucket_arn
                    ),
                    key="{app_name}/{environment}.env".format(app_name=app_name, environment=app_env)
                )
            ],
            container_name=task_name
        )

        security_group = ec2.SecurityGroup(
            self,
            "{app_prefix}SecurityGroup".format(app_prefix=app_prefix),
            allow_all_outbound=True,
            security_group_name=task_name,
            vpc=vpc
        )
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.all_traffic()
        )

        event_role = iam.Role(
            self,
            "{app_prefix}EventRole".format(app_prefix=app_prefix),
            assumed_by=iam.ServicePrincipal("events.amazonaws.com"),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2ContainerServiceEventsRole")],
            role_name="{app_prefix}EventRole".format(app_prefix=app_prefix),
            description="Allows {task_name} scheduled tasks to run in ECS.".format(task_name=task_name)
        )

        if is_private:
            subnet_selection = ec2.SubnetSelection(
                subnets=vpc.private_subnets
            )
        else:
            subnet_selection = ec2.SubnetSelection(
                subnets=vpc.public_subnets
            )

        ecs_task_target = EcsTask(
            cluster=cluster,
            task_definition=task,
            role=event_role,
            platform_version=ecs.FargatePlatformVersion.LATEST,
            security_groups=[security_group],
            subnet_selection=subnet_selection,
            container_overrides=[ContainerOverride(
                container_name=task_name,
                command=command_override
            )]
        )
        scheduled_task = events.Rule(
            self,
             "{app_prefix}ScheduledTask".format(app_prefix=app_prefix),
            schedule=events.Schedule.cron(**schedule),
            targets=[ecs_task_target]
        )
        if not is_private:
            # DO NOT use public subnets out of development.  Instead setup VPC endpoints as needed
            scheduled_task.node.default_child.add_override(
                "Properties.Targets.0.EcsParameters.NetworkConfiguration.AwsVpcConfiguration.AssignPublicIp",
                "ENABLED"
            )