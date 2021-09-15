# Establish a Foundation in Observability

In this project, students will apply the skills they have acquired in the Establish a Foundation in Observability course to configure a monitoring software stack to collect and display a variety of metrics for commonly used Azure resources which include VM Scale Sets, Azure Kubernetes service and Azure VMs. Additionally, students will establish and configure rules for alerting and set parameters to be notified prior to the occurence of failures within the aformentioned cloud resources. 

Students will also have the opportunity to test and observe thier own implentation of the monitoring software stack to apply and showcase SRE methodologies and practices which can be transferred to real-world scenarios.  

## Getting Started

**Amazon Account Lab instructions go here**

### Dependencies
* [Python](https://www.python.org/downloads/)
* [kubectl](https://kubernetes.io/docs/tasks/tools/)
* [helm](https://helm.sh/docs/intro/install/)
* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
* [puTTY for Windows](https://www.chiark.greenend.org.uk/~sgtatham/putty/) ssh clients are native to Linux and Mac.

### Local Environment Setup
1. [Use your favorite text editor, for this I am using VS Code](https://code.visualstudio.com/Download). Install the VS Code extensions for Python (optional).
2. [Use Postman to test the example REST API program.](https://www.postman.com/downloads/). This can be downloaded or used within the browser.
3. **OPTIONAL** [Use Lens to manage your Kubernetes cluster.](https://k8slens.dev/)
4. Create a git repo.
5. Clone the git repo to your local environment using ``` git clone <repo url> ```.

### Installation
#### Provision the Cloud Resources
1. Use the terraform files to provision each of the resources in AWS; it will take a few minutes to complete. Once the script is complete, you can go to the AWS and look for the the newly created resources in the EKS and EC2 areas. 

2. SSH into the EC2 instance.

### Test Connectivity to Flask App & Install Node Exporter

1. Test that the API was successfully installed by opening Postman and [importing the collection, and enviroment files](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/#importing-postman-data) provided in the class resources.
2. Change the following variables: `public-ip, username, email` then open the collection runner, choose the collection and environment, then Run the project. You should see successful resposnses for each of the API endpoints in the collection.
3. Copy the value of the `token` variable, and paste it somewhere safe, you will need it later.

Here are two examples of successful responses for `/init` and `authorize/user` endpoints:
```
/init
{
    "dataset": {
        "created": "Day, DD MM YYYY HH:MM:SS TZD",
        "description": "initialize the DB",
        "id": 1,
        "location": "home",
        "name": "init db"
    },
    "status": {
        "message": "101: Created.",
        "records": 1,
        "success": true
    }
}

/authorize/user
{
    "dataset": {
        "created": "<date-time>",
        "email": "<email>",
        "id": 1,
        "role": 0,
        "token": "<token>",
        "username": "<username>"
    },
    "status": {
        "message": "101: Created.",
        "records": 1,
        "success": true
    }
}
``` 
From this point forward, you will not need to **Initialize the Database** or **Register a User**.

## Project Instructions
1. Prior to executing commands in EKS, you may need to update the `kube config file` by running:
```
aws eks --region <region>  update-kubeconfig --name <cluster-name>
e.g. aws eks --region us-east-2  update-kubeconfig --name udacity-cluster
```
2. Create a namespace called `monitoring`
3. Create the `prometheus-additional.yaml` file and set the `targets` accordingly for both prometheus, and blackbox.
4. Modify the `values.yaml` (near line 2310) so that it matches:
```
additionalScrapeConfigsSecret:
      enabled: true
      name: additional-scrape-configs
      key: prometheus-additional.yaml
```
5. Create the kubernetes secret which references the above yaml file. 
6. Execute the following commands:
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```
7. Install the monitoring stack in Kubernetes using helm. You will need to include `-f "path\to\values.yaml" --namespace monitoring`.
8. Then login to Grafana using the credentials`user: admin & password: prom-operator`.
9. Create dashboards for the CPU for the EC2 instance using `instance:node_cpu:rate:sum` query.
10. Call the dashboard ***CPU %***.
11. Make a dashboard for Available Memory in bytes. Use `node_memory_MemAvailable_bytes` in the prometheus query.
12. Make a for Disk I/O. Use `node_disk_io_now` in the prometheus query.
13. Make a for Network Received in bytes. Use `instance:node_network_receive_bytes:rate:sum` in the prometheus query.

### Blackbox Exporter
1. Make sure you have the token from earlier (obtained from the API), then in `blackbox-values.yaml` add the following starting at line 112:
```
 valid_status_codes:
        - 200
        # - 401
        # - 403
 bearer_token: <YOUR_TOKEN>
```
2. Save it, then install blackbox in the Kubernetes cluster. You will need to include `-f "path\to\blackbox-values.yaml" --namespace monitoring`

3. In Grafana, import dashboard 7587.

### Alerting
1. Set up a notification channel to Slack or other using a webhook.
2. Create a dashboard for an API health check to check if the flask endpoint is online. Use `probe_http_status_code` for the prometheus query.
2. Configure alerts for:
    * One of the host metrics from above (CPU/Memory/Disk/Network)
    * Showing if the the flask endpoint is offline.
3. Cause the host metrics alerts to trigger.
4. Cause the flask endpoint to go offline.

## Submissions
1. A zip file containing screenshots from Grafana which include:
    * The dashboard for EC2 CPU utilization.
    * The dashboard for EC2 Memory utilization.
    * The dashboard for EC2 Disk I/O.
    * The dashboard for EC2 Network utilization.
    * The imported dashboard for Blackbox Exporter.
    * The dashboard showing that an alert triggered (could be one of CPU/memory/disk/network utilization).
    * The message from the alert--this can be in slack, email or other.
    * The alert showing that the flask app is offline.
    * The alert showing that the flask app is back online.
    * The list of alerting rules.

## Built With
### Software
* [Python](https://www.python.org/downloads/) - Programming Language
* [VS Code](https://code.visualstudio.com/) - Integrated Development Environment

### Open-source 3rd-party
[Example_Flask_API](https://github.com/orme292/example_flask_api)
[Prometheus Stack](https://github.com/prometheus-community/helm-charts/blob/main/charts)

## License
[License](../LICENSE.md)
