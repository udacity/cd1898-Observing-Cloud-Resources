provider "kubernetes" {
   config_path            = "~/.kube/config"
   host                   = data.aws_eks_cluster.cluster.endpoint
   cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
   token                  = data.aws_eks_cluster_auth.cluster.token
 }

 data "aws_eks_cluster" "cluster" {
   name = module.project_eks.cluster_id
 }

 data "aws_eks_cluster_auth" "cluster" {
   name = module.project_eks.cluster_id
 }

 module "project_eks" {
   source             = "./modules/eks"
   name               = local.name
   account            = data.aws_caller_identity.current.account_id
   private_subnet_ids = module.vpc.private_subnet_ids
   vpc_id             = module.vpc.vpc_id
 }