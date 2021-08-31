# Establish a Foundation in Observability

In this project, students will apply the skills they have acquired in the Establish a Foundation in Observability course to configure a monitoring software stack to collect and display a variety of metrics for commonly used Azure resources which include VM Scale Sets, Azure Kubernetes service and Azure VMs. Additionally, students will establish and configure rules for alerting and set parameters to be notified prior to the occurence of failures within the aformentioned cloud resources. 

Students will also have the opportunity to test and observe thier own implentation of the monitoring software stack to apply and showcase SRE methodologies and practices which can be transferred to real-world scenarios.  

## Getting Started
1. [Create a disposable Outlook account](https://outlook.com)
2. [Create a free Azure Account. Use the Outlook email address.](https://azure.microsoft.com/en-us/free/)
(If needed, Click "start" free under user licenses)

### Dependencies
* [Python](https://www.python.org/downloads/)
* [kubectl](https://kubernetes.io/docs/tasks/tools/)
* [helm](https://helm.sh/docs/intro/install/)
* [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
* [puTTY for Windows](https://www.chiark.greenend.org.uk/~sgtatham/putty/) ssh clients are native to Linux and Mac.

### Azure DevOps Local Environment Setup
1. [Use your favorite text editor, for this I am using VS Code](https://code.visualstudio.com/Download). Install the VS Code extensions for Python (optional).
2. [Use Postman to test the example REST API program.](https://www.postman.com/downloads/). This can be downloaded or used within the browser.
3. **OPTIONAL** [Use Lens to manage your Kubernetes cluster.](https://k8slens.dev/)
4. Create a git repo.
5. Clone the git repo to your local environment using ``` git clone <repo url> ```.

### Installation
#### Provision the Cloud Resources
1. A bash script `setup-script.sh` has been provided to automate the creation of the Cloud Resources. You should not need to modify this script.
```
  # Log in to Azure using 
  az login
  chmod +x setup-script.sh
  ./setup-script.sh
```
The script above will take a few minutes to each of the resources. Once the script is complete, you can go to Azure portal and look for the **srend-c1-project** resource group. 

If you see the below message, answer `y`:
```
It is highly recommended to use USER assigned identity (option --assign-identity) when you want to bring your ownsubnet, which will have no latency for the role assignment to take effect. When using SYSTEM assigned identity, azure-cli will grant Network Contributor role to the system assigned identity after the cluster is created, and the role assignment will take some
time to take effect, see https://docs.microsoft.com/en-us/azure/aks/use-managed-identity, proceed to create cluster with system assigned identity? (y/N):
```

**NOTE:** If an error appears which states `--vnet-subnet-id is not a valid Azure resource ID` run `export MSYS_NO_PATHCONV=1`

2. To connect to the VM Scale Set with ssh/puTTY, go to the VM Scale Set in Azure Portal, then Instances and **click Connect**. Use the public IP of the VMSS and the corresponding port which will be 50000, 50001, 50002 etc. -- this is because the inbound NAT rule of the load balancer defaults to port 50000.

3. To connect to the Azure VM, go to Virtual Machines in Azure Portal, and **click Connect**. Use the public IP and port 22.

### Install Flask App & Node Exporter
1. Once connected to the Azure VM, use `sudo touch api-install.sh` to create a file, then `sudo nano api-install.sh` to open the file.
2. Paste in the **api-install.sh** file obtained from git.
3. Save and exit nano  by pressing `ctrl+x, y, ENTER`.
4. Execute the script `sudo sh api-install.sh`. This will take a few minutes to complete. Additionally, this will install mysql and prompt you for the version (***we will use v5.7***), as well as a root password. See the below screenshots.

![Configuring mysql](/screenshots/project-install-mysql-1.JPG)
![Select v5.7 for installation](/screenshots/project-install-mysql-2.JPG)
![Confirm v5.7 for installation](/screenshots/project-install-mysql-3.JPG)
![Enter root password](/screenshots/project-install-mysql-4.JPG)

5. Once the script finishes **Configure nginx** `sudo nano /etc/nginx/sites-enabled/default`
Replace the server {} block with:
```
server {
    listen 80;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```
6. Then save.
7. Be sure to check for errors, then reload nginx:
```
sudo nginx -t
sudo systemctl restart nginx
```
8. Test that the API was successfully installed by opening Postman and [importing the collection, and enviroment files](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/#importing-postman-data) provided in the class resources.
9. Change the following variables: `public-ip, username, email` then open the collection runner choose the collection and environment, then Run the project. You should see successful resposnses for each of the API endpoints in the collection.
10. Copy the value of the `token` variable, and paste it somewhere safe, you will need it later.

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

11. Install node-exporter on each of the VM and VMSS.

## Project Instructions
1. Prior to executing commands in AKS, you may need to run:
```
az account set --subscription "Azure Subscription 1"
az aks get-credentials --resource-group srend-c1-project --name udacity-aks
```
2. Create a namespace called `monitoring`
3. Create the `prometheus-additional.yaml` file and set the `targets` accordingly for both prometheus, and blackbox.
4. Modify the `values.yaml` (near line 2310):
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
9. Create dashboards for the CPU for each of VM & VMSS using `instance:node_cpu:rate:sum` query.
10. Combine these dashboards into 1 dashboard called ***CPU %***.
11. Make one combined dashboard for Available Memory in bytes. Use `node_memory_MemAvailable_bytes` in the prometheus query.
12. Make one combined dashboard for Disk I/O. Use `node_disk_io_now` in the prometheus query.
13. Make one combined dashboard for Network Received in bytes. Use `instance:node_network_receive_bytes:rate:sum` in the prometheus query.

### Blackbox Exporter
1. Make sure you have the token from earlier, then in `blackbox-values.yaml` add the following starting at line 112:
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
    * The dashboard for VM/VMSS CPU utilization.
    * The dashboard for VM/VMSS Memory utilization.
    * The dashboard for VM/VMSS Disk I/O.
    * The dashboard for VM/VMSS Network utilization.
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
