terraform {
    required_version = "~> 1.4"

    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "~> 5.0"
        }
        docker = {
            source = "kreuzwerker/docker"
            version = "~> 3.0"
        }
    }
}

locals {
    container_name = "physgpt_container"
    container_port = 80
    cluster_name   = "physgpt_cluster"
}

provider "aws" {
    region = "us-east-1"

    default_tags {
        tags = { cluster = local.cluster_name }
    }
}

data "aws_caller_identity" "this" {}
data "aws_ecr_authorization_token" "this" {}
data "aws_region" "this" {}

locals {
    ecr_address = format(
        "%v.dkr.ecr.%v.amazon.com",
        data.aws_caller_identity.this.account_id,
        data.aws_region.this.name
    )
}

provider "docker" {
    registry_auth {
        address = local.ecr_address
        password = data.aws_ecr_authorization_token.this.password
        username = data.aws_ecr_authorization_token.this.user_name
    }
}


module "ecr" {
    source = "terraform-aws-modules/ecr/aws"
    version = "~> 1.6.0"

    repository_force_delete = true
    repository_name = local.container_name
    repository_lifecycle_policy = jsonencode({
        rules = [{
            action = { type = "expire" }
            description = "Purge old images"
            rulePriority = 1
            selection = {
                countNumber = 2
                countType = "imageCountMoreThan"
                tagStatus = "any"
            }
        }]
    })
}

// Docker images
resource "docker_image" "web_image" {
    name = format(
        "%v_%v.%v",
        local.container_name,
        module.ecr.repository_url,
        formatdate("YYYY-MM-DD'T'hh-mm-ss", timestamp())
    )

    build { context = "." }
}

resource "docker_registry_image" "web_reg_image" {
    keep_remotely = true
    name = resource.docker_image.web_image.name
}






// Networking
data "aws_availability_zones" "available" { state = "available" }

module "vpc" {
    source = "terraform-aws-modules/vpc/aws"
    version = "~> 5.1.0"

    azs = slice(data.aws_availability_zones.available.names, 0, 2)
    cidr = "10.0.0.0/24"
    create_igw = true
    enable_nat_gateway = true
    private_subnets = ["10.0.0.0/26", "10.0.0.64/26"]
    public_subnets = ["10.0.0.128/26", "10.0.0.192/26"]
    single_nat_gateway = true
}

module "alb" {
    source = "terraform-aws-modules/alb/aws"
    version = "~> 8.7.0"

    load_balancer_type = "application"
    security_groups = [module.vpc.default_security_group_id]
    subnets = module.vpc.public_subnets
    vpc_id = module.vpc.vpc_id

    security_group_rules = {
        ingress_all_http = {
            type        = "ingress"
            from_port   = 80
            to_port     = 80
            protocol    = "TCP"
            description = "Allow HTTP traffic"
            cidr_blocks = ["0.0.0.0/0"]
        }
        egress_all = {
            type        = "egress"
            from_port   = 0
            to_port     = 0
            protocol    = "-1"
            description = "Allow outgoing requests"
            cidr_blocks = ["0.0.0.0/0"]
        }
    }

    http_tcp_listeners = [{
        port               = 80
        protocol           = "HTTP"
        target_group_index = 0
    }]

    target_groups = [{
        backend_port        = local.container_port
        background_protocol = "HTTP"
        target_type         = "ip"
    }]
}


// Fargate
module "ecs" {
   source = "terraform-aws-modules/ecs/aws"
   version = "~> 5.2.0"

   cluster_name = local.cluster_name

   fargate_capacity_providers = {
       FARGATE = {
           default_capacity_provider_strategy = {
               base   = 20
               weight = 50
           }
       }
       FARGATE_SPOT = {
           default_capacity_provider_strategy = {
               weight = 50
           }
       }
   }
}


// Tasks
data "aws_iam_role" "ecs_task_execution_role" {
    name = "ecsTaskExecutionRole"
}

resource "aws_ecs_task_definition" "this" {
    container_definitions = jsonencode([{
        environment: [
            { name = "NODE_ENV", value = "production" }
        ],
        essential = true,
        image = resource.docker_registry_image.web_reg_image.name,
        name = local.container_name,
        portMappings = [{ containerPort = local.container_port }]
    }])
    cpu = 256
    execution_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
    family = format("%v-tasks", local.cluster_name)
    memory = 512
    network_mode = "awsvpc"
    requires_compatibilities = ["FARGATE"]
}


