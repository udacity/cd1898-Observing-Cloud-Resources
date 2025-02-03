resource "kubernetes_namespace" "udacity" {
   metadata {
     name = local.name
   }
   depends_on = [
     module.project_eks
   ]
 }