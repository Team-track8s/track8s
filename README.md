# kube8

This project utilizes Kubernetes to deploy a containerized web app with Amazon EKS and AWS CloudFormation. 

Link to Medium.com article that I published a tutorial based on this project: how-to-deploy-a-containerized-web-app-in-a-kubernetes-cluster-using-amazon-eks-cff46b41b8ef

Note to self: After finished creating app and EKS cluster and your AWS enviroment and CDK infrastructure has been fully set up:

1. Run to deploy:
```
cdk deploy
```

2. Get pod status:
```
kubectl get all
```

3. To see app in browser: grab LoadBalancer external-ip and open in browser.

4. Destroy AWS environment:
```
cdk destroy
```

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

7. Now you are read to deploy the cluster by running the command:
```
cdk deploy
```

8. CDK will prompt before creating the infrastructure because it is creating infrastructure that changes security configuration (in this case I created IAM roles and security groups). Press y, hit enter to deploy and then wait for the deployment to finish.

9. When cluster is successfully deployed, should get a green checkmark next to your output and 2 commands:
- ClusterStack.ClusterStackclusterConfigCommand 
- ClusterStack.ClusterStackclusterGetTokenCommand

10. Copy the ClusterStack.ClusterStackclusterConfigCommand and run the command. The command should start with `aws eks update-kubeconfig - name…`
- allows device to connect to and operate  cluster by updating  Kubernetes configuration (kubeconfig) to point to cluster so that the kubectl command will work.

- output should be something similar to the following:
```
Added ew context arn:aws:eks:eu-west-1:0123456789012:cluster/ClusterStack-cluster to /home/ubuntu/.kube/config
```

11. To confirm that everything is configured correctly, run the command:
```
kubectl get all
```
If everything was configured correctly, you should get NAME, TYPE, CLUSTER-IP, etc outputs.

---

# Install cdk8s-CLI
The following instructions are to set up AWS CDK for Kubernetes (cdk8s). cdk8s is a framework for defining Kubernetes apps and reusable abstractions. cdk8s is a separate tool which you will need to install in addition to CDK. cdk8s-CLI is the main tool that you will use to define service and deployment for the application you will deploy. The AWS cdk8s outputs a YAML file, a Kubernetes configuration file, that you can use to deploy applications using kubectl or AWS CDK.
Check out the cdk8s CLI Guide

---

## Install cdk8s:

1. Install cdk8s-cli
```brew install cdk8s```
or use npm ```npm install -g cdk8s-cli```

2. If you are using Python, install pipenv. 
```pip3 install pip3```

3. Navigate to your eks/cdk8s project folder and create a CDK8s application to generate a project skeleton that includes a Python env and base libraries by running the command:
```cdk8s init python-app```

Once the files and folder structure is finished being created, you are now ready to define your app config in order to to deploy your app to the EKS cluster

# Create Service & Deployment Configurations For Your App and Deploy Your App Into Your EKS Cluster
- use cdk8s constructs to define Kubernetes API Objects. These constructs can be used to create services and deployments configurations for your app and use the Kubernetes config file (a YAML file) that is generated to integrate it with the AWS CDK code from the previous steps to deploy your application.

## There are 4 steps necessary to deploy app:
1. Import the k8s library to generate the strings for the YAML Kubernetes config file.

2. In the service lookup, define the label set to apply to the pods.
- Labels are key/value pairs attached to Kubernetes objects.
- You will be tagging the pods to run them as part of the deployment and then the ReplicationController will use the labels to select the pods when in step 4, it is creating the service to expose them to the load balancer.
- The label you will use is : {"app": "cdk8s"}

3. Define a deployment to spin up the container on the cluster but do not configure it to receive traffic from the load balancer.

4. Expose the deployment to the load balancer by defining a service.

--

1. Navigate to the file eks/cdk8/main.py, add the following code to main.py:

```
# main.py

#!/usr/bin/env python
from constructs import Construct
from cdk8s import App, Chart
from imports import k8s

# super() is called 2x because it creates the YAML file with the specified name
# and appends any config generated after that point by calling the parent class 
# constructor that this class inherits from
class MyChart(Chart):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id) # generates a file for the service config

        # define resources here

        # Label that will be used to tag pods
        label = {"app": "cdk8s"}

        k8s.KubeDeployment(self, 'deployment',
            spec = k8s.DeploymentSpec(
                replicas = 2,
                selector = k8s.LabelSelector(match_labels = label),
                template = k8s.PodTemplateSpec(
                metadata = k8s.ObjectMeta(labels = label),
                spec = k8s.PodSpec(containers = [
                    k8s.Container(
                    name = 'cdk8s',
                    image = 'public.ecr.aws/s9u7u6x1/sample_app_001:no-db',
                    ports = [k8s.ContainerPort(container_port = 80)])]))))

        # Create the service to expose the pods to traffic from teh load balancer
        super().__init__(scope, f"{id}-service") # generates a 2nd file for the deployment

        k8s.KubeService(self, 'service',
            spec = k8s.ServiceSpec(
            type = 'LoadBalancer',
            ports = [k8s.ServicePort(port = 80, target_port = k8s.IntOrString.from_number(80))],
            selector = label))

app = App()
MyChart(app, "cdk8s")

app.synth()
```

2. Run the command to generate the config files:
```cdk8s synth```

- It should create 2 config files in cdk8s/dist folder, the service and deployment config files

3. Navigate to eks/cluster/cluster/cluster_stack.py and install pyyaml
```pip install pyyaml```

4. Then  add the following code to cluster_stack.py file:
```
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
        eks_cluster = eks.Cluster(
            self, 
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
```

5. After adding this code, to make sure you have no errors in your codebase thus far, run the command and make sure stack is outputted correctly:
```cdk ls```

6. Make sure in eks/cluster directory and deploy app by running the command:
```cdk deploy```

7. Once app has been successfully deployed by AWS CDK, you can use the following command to make sure you're using the correct context before using kubectl:
```kubectl config current-context```

8. Check the status of the app in the pods by running the command:
```kubectl get all```

9. In terminal after running the command kubectl get all , copy the EXTERNAL-IP address that corresponds with the LoadBalancer value and open it in browser. It should be a mix of numbers and letters and look something like the following:
```xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx–xxxxxxxxx.us-east-x.elb.amazonaws.com```

# Cleaning Up AWS Environment to Not Get Charged
- $75.00 USD / month to run this app or 10c USD per hour.
To remove all the infrastructure you created during this tutorial, use the command and press y when prompted:
```cdk destroy```


# Resources
- Upgrading to CDKv2: https://oblcc.com/blog/upgrading-cdk-from-cdkv1-to-cdkv2-in-an-existing-project/
- https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet
= Pass the YAML files to the cluster using the add_manifest method to apply the service and deployment Kubernetes manifests to the cluster
