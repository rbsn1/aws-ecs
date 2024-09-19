provider "aws" {
  region = "us-east-1"
}

# Declarar variável para a URL da imagem
variable "image_url" {
  description = "URL da imagem Docker no ECR"
  type        = string
}

# Declarar variável para o ID da VPC
variable "vpc_id" {
  description = "ID da VPC onde os recursos serão provisionados"
  type        = string
  default     = "vpc-0d47ba13f56c2e7ef"  # Coloque o ID da sua VPC aqui
}

# Data sources para obter subnets e security groups da VPC fornecida
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }
}

data "aws_security_groups" "default" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }
}

# Criar bucket S3 com nome único
resource "random_id" "bucket_id" {
  byte_length = 4
}

resource "aws_s3_bucket" "bucket" {
  bucket = "meu-bucket-${random_id.bucket_id.hex}"
  acl    = "private"
}

# Armazenar segredos no Secrets Manager
resource "aws_secretsmanager_secret" "db_secret" {
  name        = "db-password"
  description = "Senha do banco de dados"
}

resource "aws_secretsmanager_secret_version" "db_secret_version" {
  secret_id     = aws_secretsmanager_secret.db_secret.id
  secret_string = "supersecreta123"
}

# Criar Cluster ECS
resource "aws_ecs_cluster" "ecs_cluster" {
  name = "meu-cluster"
}

# Criar IAM Role para o ECS Task Execution
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

# Anexar políticas à role
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Criar definição de tarefa ECS
resource "aws_ecs_task_definition" "ecs_task" {
  family                   = "minha-tarefa"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "minha-app"
      image     = var.image_url
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        }
      ]
    }
  ])
}

# Criar Serviço ECS
resource "aws_ecs_service" "ecs_service" {
  name            = "meu-servico"
  cluster         = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.ecs_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = data.aws_subnets.default.ids
    security_groups = tolist(slice(data.aws_security_groups.default.ids, 0, 5))  # Limitar a 5 grupos de segurança
    assign_public_ip = true
  }

  depends_on = [aws_iam_role_policy_attachment.ecs_task_execution_role_policy]
}
