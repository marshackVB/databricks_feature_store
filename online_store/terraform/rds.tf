# Deploy the Aurora instance in the default VPC
data "aws_vpc" "default" {
  default = true
}


# Create a security group in the VPC that allow inbound traffic from the internet to Aurora
resource "aws_security_group" "aurora-public-access" {
    vpc_id                  = data.aws_vpc.default.id
    name                    = "aurora-public-access"
    description             = "allow public access to Aurora db"

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port   = 3306
        to_port     = 3306
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
        ipv6_cidr_blocks = ["::/0"]
    }
    
}


# Generate a random database password
resource "random_password" "db_master_pass" {
  length            = 20
  special           = true
  min_special       = 4
  override_special  = "!@#$"
}


/*
# Provision the Aurora cluster and a single instance
resource "aws_rds_cluster" "feature-store-cluster" {
    cluster_identifier          = "feature-store-cluster"
    engine                      = "aurora-mysql"
    engine_mode                 = "provisioned"
    engine_version              = "5.7.mysql_aurora.2.10.2"
    database_name               = "feature_store"
    master_username             = "feature_store_admin"
    master_password             = random_password.db_master_pass.result
    port                        = 3306
    vpc_security_group_ids =    [aws_security_group.aurora-public-access.id]
    skip_final_snapshot =       true
    backup_retention_period =   1
    apply_immediately =         true
    
}


resource "aws_rds_cluster_instance" "feature-store-instance" {
    count = 1
    identifier = "feature-store-cluster-${count.index}"
    cluster_identifier = aws_rds_cluster.feature-store-cluster.id
    instance_class = "db.r6g.large"
    engine = aws_rds_cluster.feature-store-cluster.engine
    engine_version = aws_rds_cluster.feature-store-cluster.engine_version
    publicly_accessible = true
}

output "endpoint" {
    value = aws_rds_cluster.feature-store-cluster.endpoint
}

output "database_user" {
    value = aws_rds_cluster.feature-store-cluster.master_username
}

output "database_pw" {
    value = aws_rds_cluster.feature-store-cluster.master_password
    sensitive = true
}

*/


# Provision an RDS instance
resource "aws_db_instance" "feature-store-db" {
    identifier                      = "feature-store"
    allocated_storage               = 20
    storage_type                    = "gp2"
    max_allocated_storage           = 0
    engine                          = "mysql"
    engine_version                  = "8.0.28"
    instance_class                  = "db.t3.micro"
    multi_az                        = false
    performance_insights_enabled    = false
    username                        = "feature_store_admin"
    password                        = random_password.db_master_pass.result
    db_name                         = "feature_store"
    vpc_security_group_ids          = [aws_security_group.aurora-public-access.id]
    publicly_accessible             = true
    skip_final_snapshot             = true
    backup_retention_period         = 1
    apply_immediately               = true
    
}


output "endpoint" {
    value = aws_db_instance.feature-store-db.endpoint
}

output "database_user" {
    value = aws_db_instance.feature-store-db.username
}

output "database_pw" {
    value = aws_db_instance.feature-store-db.password
    sensitive = true
}

