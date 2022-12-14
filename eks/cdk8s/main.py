#!/usr/bin/env python
from constructs import Construct
from cdk8s import App, Chart
from imports import k8s

# super() is called 2x because it creates the YAML file with the name specified and appends any config generated after that point by calling the parent class constructor that this class inherits from
class MyChart(Chart):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id) # generates a file for the service config

        # Label that will be used to tag pods
        label = {"app": "cdk8s"}

        k8s.KubeDeployment(
            self, 
            'deployment',
            spec = k8s.DeploymentSpec(
                replicas = 2,
                selector = k8s.LabelSelector(match_labels = label),
                template = k8s.PodTemplateSpec(
                    metadata = k8s.ObjectMeta(labels = label),
                    spec = k8s.PodSpec(containers = [
                        k8s.Container(
                            name = 'cdk8s',
                            image = 'public.ecr.aws/s9u7u6x1/sample_app_001:no-db',
                            ports = [k8s.ContainerPort(container_port = 80)]
                        )
                    ])
                )
            )
        )

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
