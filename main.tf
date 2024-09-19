provider "aws" {
  region = "us-east-1"
}

# Criar bucket S3
resource "aws_s3_bucket" "bucket" {
  bucket = "meu-bucket-de-armazenamento"
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

# Criar tarefa ECS
resource "aws_ecs_task_definition" "ecs_task" {
  family                   = "minha-tarefa"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name  = "minha-app"
      image = var.image_url
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
    subnets         = ["subnet-12345"]
    security_groups = ["sg-12345"]
    assign_public_ip = true
  }
}
