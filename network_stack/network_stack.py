import os
from typing import Protocol

from aws_cdk import core as cdk
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_rds as rds
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk.aws_elasticloadbalancing import LoadBalancer, LoadBalancerListener
from aws_cdk.aws_elasticloadbalancingv2 import ApplicationListener, ApplicationListenerAttributes, ApplicationLoadBalancer, ApplicationProtocol, ApplicationTargetGroup, ListenerAction, ListenerCertificate, ListenerCondition, TargetGroupBase, TargetType, ApplicationListenerRule
from aws_cdk.aws_logs import LogGroup
from aws_cdk.aws_s3 import Bucket

class NetworkStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, app_props: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Required props
        prefix = app_props["aws_account_name"]

        """
        Creates VPC with 2 public subnets and 2 private subnets, one of each in two availability zones (A and B)
        Creates 2 NAT gateways, one for each availability zone, which each have an Elastic IP address
        """
        self.vpc = ec2.Vpc(
            self,
            "{prefix}Vpc".format(prefix=prefix),
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="{prefix}PublicSubnet".format(prefix=prefix),
                    subnet_type=ec2.SubnetType.PUBLIC
                ),
                ec2.SubnetConfiguration(
                    name="{prefix}PrivateSubnet".format(prefix=prefix),
                    subnet_type=ec2.SubnetType.PRIVATE
                ),
                ec2.SubnetConfiguration(
                    name="{prefix}IsolatedSubnet".format(prefix=prefix),
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
            "{prefix}SecurityGroup".format(prefix=prefix),
            allow_all_outbound=True,
            security_group_name=prefix,
            vpc=self.vpc
        )
        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.all_traffic()
        )


        # Development cluster
        self.development_cluster = ecs.Cluster(
            self,
            "{prefix}DevelopmentCluster".format(prefix=prefix),
            vpc=self.vpc,
            cluster_name="{prefix}DevelopmentCluster".format(prefix=prefix),
        )

        # Development load balancer
        self.development_load_balancer = ApplicationLoadBalancer(
            self,
            "{prefix}DevPublicLB".format(prefix=prefix),
            vpc=self.vpc,
            security_group=security_group,
            internet_facing=True,
            load_balancer_name="{prefix}DevPublicLB".format(prefix=prefix),
        )


        # Create a postgres DB for Zoom Queue app
        database = rds.DatabaseInstance(
            self,
            "{prefix}DevelopmentPostgresDatabase".format(prefix=prefix),
            vpc=self.vpc,
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

        # Prod/Staging load balancer
        self.load_balancer = ApplicationLoadBalancer(
            self,
            "{prefix}PublicLB".format(prefix=prefix),
            vpc=self.vpc,
            security_group=security_group,
            internet_facing=True,
            load_balancer_name="{prefix}PublicLB".format(prefix=prefix),
        )

        # Create a postgres DB for prod/staging frontdesk app
        database = rds.DatabaseInstance(
            self,
            "{prefix}FrontdeskDatabase".format(prefix=prefix),
            vpc=self.vpc,
            vpc_subnets={
                "subnet_type": ec2.SubnetType.ISOLATED,
            },
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_13_1),
            credentials=rds.Credentials.from_generated_secret("frontdeskadmin",secret_name="frontdeskcredentials"),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.SMALL
            ),
            backup_retention=cdk.Duration.days(3),
            delete_automated_backups=True,
            removal_policy=cdk.RemovalPolicy.RETAIN,
            deletion_protection=True,
            database_name="frontdesk",
            publicly_accessible=True,
            instance_identifier="frontdeskapp"
        )
        database.connections.allow_from_any_ipv4(ec2.Port.tcp(5432))

        self.cluster = ecs.Cluster(
            self,
            "{prefix}Cluster".format(prefix=prefix),
            vpc=self.vpc,
            cluster_name="LSITFrontDeskCluster",
        )

        # VPC Endpoints for prod/staging
        ec2.InterfaceVpcEndpoint(
            self,
            "{prefix}ECRVPCEndpoint".format(prefix=prefix),
            vpc=self.vpc,
            service=ec2.InterfaceVpcEndpointAwsService.ECR,
            subnets=ec2.SubnetSelection(
                subnets=self.vpc.private_subnets
            ),
        )

        ec2.InterfaceVpcEndpoint(
            self,
            "{prefix}ECRDockerVPCEndpoint".format(prefix=prefix),
            vpc=self.vpc,
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            subnets=ec2.SubnetSelection(
                subnets=self.vpc.private_subnets
            ),
        )

        ec2.GatewayVpcEndpoint(
            self,
            "{prefix}S3VPCEndpoint".format(prefix=prefix),
            vpc=self.vpc,
            service=ec2.GatewayVpcEndpointAwsService.S3,
            subnets=self.vpc.private_subnets
        )

        # Environment Variable Bucket
        self.bucket = Bucket(
            self,
            "lsit-zoom-queue-env-vars",
            bucket_name="lsit-zoom-queue-env-vars"
        )