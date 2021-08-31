#!/bin/bash

# Variables
subscriptionId="<subscription_id>"
resourceGroup="srend-c1-project"
location="eastus"
osType="UbuntuLTS"
adminUsername="udacity"
adminPassword="Udacity123456"
vmssName="udacity-vmss"
aksName="udacity-aks"
vmName="udacity-vm"
pubIpName="udacity-pubip"
adminName="udacityadmin"
storageAccount="udacitydiag$RANDOM"
bePoolName="udacity-bepool"
lbName="udacity-lb"
lbRule="$lbName-network-rule"
nsgName="udacity-nsg"
vnetName="udacity-vnet"
subnetName="udacity-subnet"
probeName="tcpProbe"
vmSize="Standard_B2s"
storageType="Standard_LRS"
subnetId="/subscriptions/$subscriptionId/resourceGroups/$resourceGroup/providers/Microsoft.Network/virtualNetworks/$vnetName/subnets/$subnetName"

# Create resource group. 
# This command will not work for the Cloud Lab users. 
# Cloud Lab users can comment this command and 
# use the existing Resource group name, such as, resourceGroup="cloud-demo-153430" 
echo "STEP 0 - Creating resource group $resourceGroup..."

az group create \
--name $resourceGroup \
--location $location \
--verbose

echo "Resource group created: $resourceGroup"

# Create Storage account
echo "STEP 1 - Creating storage account $storageAccount"

az storage account create \
--name $storageAccount \
--resource-group $resourceGroup \
--location $location \
--sku Standard_LRS

echo "Storage account created: $storageAccount"

# Create Vnet
echo "STEP 2 - Creating vnet $vnetName"

az network vnet create \
--resource-group $resourceGroup \
--name $vnetName \
--address-prefix 10.0.0.0/16 \
--subnet-name $subnetName \
--subnet-prefix 10.0.0.0/24

echo "Vnet created: $vnetName"

# Create Network Security Group
echo "STEP 3 - Creating network security group $nsgName"

az network nsg create \
--resource-group $resourceGroup \
--name $nsgName \
--verbose

echo "Network security group created: $nsgName"

# Create VM Scale Set
echo "STEP 4 - Creating VM scale set $vmssName"

az vmss create \
  --resource-group $resourceGroup \
  --name $vmssName \
  --image $osType \
  --vm-sku $vmSize \
  --nsg $nsgName \
  --subnet $subnetName \
  --vnet-name $vnetName \
  --backend-pool-name $bePoolName \
  --storage-sku $storageType \
  --load-balancer $lbName \
  --custom-data cloud-init.txt \
  --upgrade-policy-mode automatic \
  --admin-username $adminName \
  --generate-ssh-keys \
  --verbose 

echo "VM scale set created: $vmssName"

# Associate NSG with VMSS subnet
echo "STEP 5 - Associating NSG: $nsgName with subnet: $subnetName"

az network vnet subnet update \
--resource-group $resourceGroup \
--name $subnetName \
--vnet-name $vnetName \
--network-security-group $nsgName \
--verbose

echo "NSG: $nsgName associated with subnet: $subnetName"

# Create Health Probe
echo "STEP 6 - Creating health probe $probeName"

az network lb probe create \
  --resource-group $resourceGroup \
  --lb-name $lbName \
  --name $probeName \
  --protocol tcp \
  --port 80 \
  --interval 5 \
  --threshold 2 \
  --verbose

echo "Health probe created: $probeName"

# Create Network Load Balancer Rule
echo "STEP 7 - Creating network load balancer rule $lbRule"

az network lb rule create \
  --resource-group $resourceGroup \
  --name $lbRule \
  --lb-name $lbName \
  --probe-name $probeName \
  --backend-pool-name $bePoolName \
  --backend-port 80 \
  --frontend-ip-name loadBalancerFrontEnd \
  --frontend-port 80 \
  --protocol tcp \
  --verbose

echo "Network load balancer rule created: $lbRule"

# Add port 80 to inbound rule NSG
echo "STEP 8 - Adding port 80 to NSG $nsgName"

az network nsg rule create \
--resource-group $resourceGroup \
--nsg-name $nsgName \
--name Port_80 \
--destination-port-ranges 80 \
--direction Inbound \
--priority 100 \
--verbose

echo "Port 80 added to NSG: $nsgName"

# Add port 22 to inbound rule NSG
echo "STEP 9 - Adding port 22 to NSG $nsgName"

az network nsg rule create \
--resource-group $resourceGroup \
--nsg-name $nsgName \
--name Port_22 \
--destination-port-ranges 22 \
--direction Inbound \
--priority 110 \
--verbose

echo "Port 22 added to NSG: $nsgName"

# Add port 9100 to inbound rule NSG
echo "STEP 10 - Adding port 9100 to NSG $nsgName"
az network nsg rule create \
--resource-group $resourceGroup \
--nsg-name $nsgName \
--name Port_9100 \
--destination-port-ranges 9100 \
--direction Inbound \
--priority 120 \
--verbose

echo "Port 9100 added to NSG: $nsgName"

# Create Kubernetes Cluster
echo "STEP 11 - Creating Kubernetes Cluster $aksName"
az aks create \
--resource-group $resourceGroup \
 --name $aksName \
 --node-count 2 \
 --node-vm-size "Standard_DS2_v2" \
 --network-plugin "azure" \
 --dns-service-ip "10.1.0.10" \
 --service-cidr "10.1.0.0/24" \
 --vnet-subnet-id $subnetId

echo "Kubernetes cluster created: $aksName"

# Create Public IP
echo "STEP 12 - Creating Public Ip $pubIpName"
az network public-ip create \
--resource-group $resourceGroup \
--name $pubIpName \

echo "Azure Public IP created: $pubIpName"

# Create VM
echo "STEP 13 - Creating VM $vmName"
az vm create \
--resource-group $resourceGroup \
--admin-username $adminUsername \
--admin-password $adminPassword \
--name $vmName \
--image $osType \
--size $vmSize \
--nsg $nsgName \
--subnet $subnetName \
--vnet-name $vnetName \
--public-ip-sku "Standard" \
--public-ip-address $pubIpName

echo "Azure VM created: $vmName"

echo "Setup script completed!"
