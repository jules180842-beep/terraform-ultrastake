resource "aws_instance" "master" {
  ami           = "ami-0c02fb55956c7d316" # Ubuntu 22.04 (us-east-1)
  instance_type = var.instance_type
  key_name      = var.key_name

  security_groups = [aws_security_group.ultrastake_sg.name]

  user_data = file("${path.module}/user_data_master.sh")

  tags = {
    Name = "ultrastake-master"
    Role = "master"
  }
}