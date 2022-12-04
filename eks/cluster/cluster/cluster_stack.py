from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_eks as eks,
    aws_iam as iam
)
from constructs import Construct
import yaml

class ClusterStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Look up the default VPC
        vpc = ec2.Vpc.from_lookup(self, id="VPC", is_default=True)

        # Create the master role for EKS Cluster
        iam_role = iam.Role(self, id=f"{construct_id}-iam", role_name=f"{construct_id}-am", assumed_by=iam.AccountRootPrincipal())

        # Creating the Kubernetes cluster with EKS
        eks_cluster = eks.Cluster(self, 
            id=f"{construct_id}-cluster",
            cluster_name=f"{construct_id}-cluster",
            vpc=vpc,
            vpc_subnets=vpc.public_subnets,
            masters_role=iam_role,
            default_capacity_instance=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO), 
            version=eks.KubernetesVersion.V1_20
        )

        # Read deployment config YAML file and create deployment_yaml variable to pass to the cluster
        with open("../cdk8s/dist/cdk8s.k8s.yaml", 'r') as stream: 
            deployment_yaml = yaml.load(stream, Loader=yaml.FullLoader)

        # Read service config YAML file and create service_yaml variable to pass to the cluster
        with open("../cdk8s/dist/cdk8s-service.k8s.yaml") as stream: 
            service_yaml = yaml.load(stream, Loader=yaml.FullLoader)

        # Pass the YAML files to the cluster using the add_manifest method to apply the service and deployment Kubernetes manifests to the cluster

        eks_cluster.add_manifest(f"{construct_id}-app-deployment", deployment_yaml)
        eks_cluster.add_manifest(f"{construct_id}-app-service", service_yaml)
