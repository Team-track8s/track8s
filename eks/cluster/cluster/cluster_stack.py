from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_eks as eks,
    aws_iam as iam
)

from constructs import Construct

class ClusterStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # Look up the default VPC
        vpc = ec2.Vpc.from_lookup(self, id="VPC", is_default=True)

        # Create the master role for EKS Cluster
        iam_role = iam.Role(self, id=f"{construct_id}-iam", role_name=f"{construct_id}-am", assumed_by=iam.AccountRootPrincipal())

        # Creating cluster with EKS
        eks_cluster = eks.Cluster(
            self, id=f"{construct_id}-cluster",
            cluster_name=f"{construct_id}-cluster",
            vpc=vpc,
            vpc_subnets=vpc.public_subnets,
            masters_role=iam_role,
            default_capacity_instance=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO), 
            version=eks.KubernetesVersion.V1_20
        )