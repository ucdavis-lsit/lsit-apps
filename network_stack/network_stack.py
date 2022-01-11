import os
from typing import Protocol

from aws_cdk import core as cdk
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_rds as rds
from aws_cdk.aws_elasticloadbalancing import LoadBalancer, LoadBalancerListener
from aws_cdk.aws_elasticloadbalancingv2 import ApplicationListener, ApplicationListenerAttributes, ApplicationLoadBalancer, ApplicationProtocol, ApplicationTargetGroup, ListenerAction, ListenerCertificate, ListenerCondition, TargetGroupBase, TargetType, ApplicationListenerRule
from aws_cdk.aws_logs import LogGroup
from aws_cdk.aws_s3 import Bucket

class NetworkStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, app_props: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Required props
        app_name = app_props["app_name"]
        app_env = app_props["app_env"]

        # Calculated props
        app_prefix = app_name.capitalize() + app_env.capitalize()

        """
        Creates VPC with 2 public subnets and 2 private subnets, one of each in two availability zones (A and B)
        Creates 2 NAT gateways, one for each availability zone, which each have an Elastic IP address
        """
        vpc = ec2.Vpc(
            self,
            "{app_prefix}Vpc".format(app_prefix=app_prefix),
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="{app_prefix}PublicSubnet".format(app_prefix=app_prefix),
                    subnet_type=ec2.SubnetType.PUBLIC
                ),
                ec2.SubnetConfiguration(
                    name="{app_prefix}PrivateSubnet".format(app_prefix=app_prefix),
                    subnet_type=ec2.SubnetType.PRIVATE
                ),
                ec2.SubnetConfiguration(
                    name="{app_prefix}IsolatedSubnet".format(app_prefix=app_prefix),
                    cidr_mask=27,
                    subnet_type=ec2.SubnetType.ISOLATED
                )
            ]
        )

        """
        Creates a security group that allows all traffic
        Creates an application load balancer on the public subnets, since "internet_facing" is True that user the security group created
        """
        security_group = ec2.SecurityGroup(
            self,
            "{app_prefix}SecurityGroup".format(app_prefix=app_prefix),
            allow_all_outbound=True,
            security_group_name=app_prefix,
            vpc=vpc
        )
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.all_traffic()
        )
        public_load_balancer = ApplicationLoadBalancer(
            self,
            "{app_prefix}PublicLoadBalancer".format(app_prefix=app_prefix),
            vpc=vpc,
            security_group=security_group,
            internet_facing=True,
        )


        # Create a postgres DB in the isolated subnets
        database = rds.DatabaseInstance(
            self,
            "{app_prefix}PostgresDatabase".format(app_prefix=app_prefix),
            vpc=vpc,
            vpc_subnets={
                "subnet_type": ec2.SubnetType.PUBLIC,
            },
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_13_1),
            credentials=rds.Credentials.from_generated_secret("postgres"),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO
            ),
            backup_retention=cdk.Duration.days(0),
            delete_automated_backups=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            deletion_protection=False,
            database_name="postgres",
            publicly_accessible=True
        )
        database.connections.allow_from_any_ipv4(ec2.Port.tcp(5432))

        cdk.CfnOutput(
            self,
            "{app_prefix}DBEndpoint".format(app_prefix=app_prefix),
            value=database.instance_endpoint.hostname
        )
        cdk.CfnOutput(
            self,
            "{app_prefix}DBSecretName".format(app_prefix=app_prefix),
            value=database.secret.secret_name
        )