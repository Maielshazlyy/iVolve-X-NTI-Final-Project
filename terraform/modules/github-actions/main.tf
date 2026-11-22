data "aws_iam_user" "ci" {
  user_name = var.ci_user_name
}

data "aws_iam_policy_document" "ecr_push" {
  statement {
    sid       = "EcrAuthorizationToken"
    effect    = "Allow"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    sid    = "PublishImagesToProjectRepositories"
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]
    resources = var.ecr_repository_arns
  }
}

resource "aws_iam_user_policy" "ecr_push" {
  name   = "${var.project_name}-${var.environment}-github-actions-ecr-push"
  user   = data.aws_iam_user.ci.user_name
  policy = data.aws_iam_policy_document.ecr_push.json
}
