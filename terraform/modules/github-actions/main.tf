data "aws_iam_user" "deploy" {
  user_name = var.deploy_user_name
}

data "aws_iam_policy_document" "describe_cluster" {
  statement {
    effect    = "Allow"
    actions   = ["eks:DescribeCluster"]
    resources = [var.cluster_arn]
  }
}

resource "aws_iam_user_policy" "describe_cluster" {
  name   = "${var.project_name}-${var.environment}-github-deploy-describe-cluster"
  user   = data.aws_iam_user.deploy.user_name
  policy = data.aws_iam_policy_document.describe_cluster.json
}

resource "aws_eks_access_entry" "deploy" {
  cluster_name  = var.cluster_name
  principal_arn = data.aws_iam_user.deploy.arn
  type          = "STANDARD"
  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_eks_access_policy_association" "deploy" {
  cluster_name  = var.cluster_name
  principal_arn = data.aws_iam_user.deploy.arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSAdminPolicy"

  access_scope {
    type       = "namespace"
    namespaces = [var.namespace]
  }
}
