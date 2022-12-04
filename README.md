# kube8

This project utilizes Kubernetes to deploy a containerized web app with Amazon EKS and AWS CloudFormation.

Useful commands:
 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

# Deploying a Containerized Web App on Amazon EKS:
Kubernetes is an open-source system that automates the deployment, scaling, and management of containerized applications and Amazon Elastic Kubernetes Service (EKS) is a service that you can use to run Kubernetes on AWS. You can integrate EKS with Amazon ECR to use container images.

## Get Started with EKS
Install kubectl, eksctl, and set up an IAM user. 
- kubectl is the command line tool used to communicate with the Kubernetes API server and 
- eksctl is the command line tool used to create and manage Kubernetes clusters on Amazon EKS.

- Create an IAM User and give the user the necessary permissions (IAM User Guide instructions).  -- AdministratorAccess

1. Create your directories with the following structure:
```
- project
  - eks
  - cluster
  - cdk8s
```

2. Install kubectl: Follow Amazon EKS's User Guide instructions.
3. Install eksctl: Follow Amazon EKS's User Guide instructions.

## Build AWS CDK Application, Create Your Cluster, and Deploy CDK Stack
Use aws-cdk-lib>=2.0.0.

1. Navigate to eks/cluster project folder and use the following command to create skeleton CDK app (replace python with language of choice):

```
cdk init app --language=python
```

2. Then, if using Python, create a virtual environment:
```
python3 -m venv .venv
```

After the init process completes and the virtual env is created, use the following command to activate your virtual env and install the AWS CDK core dependencies:
```
source .venv/bin/activate
python -m pip install -r reqirements.txt
```

Note: to deactivate your virtual environment `deactivate`

3. To verify that everything worked thus far, list the stacks in app by running the following command and making sure that the output is ClusterStack:
```
cdk ls
```

4. Navigate to eks/cluster/app.py and uncomment line 23 to configure CDK to so that it knows which Account ID and region to use in order to deploy the CDK stack:

⋅⋅⋅Change: 
```
env=cdk.Environment(account='1234234234', region='region'),
```

⋅⋅⋅to
```
env=core.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
```

⋅⋅⋅Re-verify that everything is still working by making sure ClusterStack is still listed:
```
cdk ls
```

5. Navigate to eks/cluster/cluster_stack.py and add the following code to look up the default VPN, define the IAM role, and create an EKS cluster:
```
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
```

6. Before you can use CDK, it needs to be bootstrapped, which will create the necessary infrastructure for CDK to manage infrastructure in your account. Run the following command:
```
cdk bootstrap
```

Should eventually output that says Environment was bootstrapped:

7. Now you are read to deploy the cluster by running the command:
```
cdk deploy
```

⋅⋅⋅Wait for cluster to deploy successfully.

8. CDK will prompt before creating the infrastructure because it is creating infrastructure that changes security configuration (in this case I created IAM roles and security groups). Press y, hit enter to deploy and then wait for the deployment to finish.

9. When cluster is successfully deployed, should get a green checkmark next to your output and 2 commands:
- ClusterStack.ClusterStackclusterConfigCommand 
- ClusterStack.ClusterStackclusterGetTokenCommand

10. Copy the ClusterStack.ClusterStackclusterConfigCommand and run the command. The command should start with `aws eks update-kubeconfig - name…`
This allows device to connect to and operate  cluster by updating  Kubernetes configuration (kubeconfig) to point to cluster so that the kubectl command will work.

Your output should be something similar to the following:
```
Added ew context arn:aws:eks:eu-west-1:0123456789012:cluster/ClusterStack-cluster to /home/ubuntu/.kube/config
```

11. To confirm that everything is configured correctly, run the command:
```
kubectl get all
```
If everything was configured correctly, you should get NAME, TYPE, CLUSTER-IP, etc outputs.



# Resources
- Upgrading to CDKv2: https://oblcc.com/blog/upgrading-cdk-from-cdkv1-to-cdkv2-in-an-existing-project/
- https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet
