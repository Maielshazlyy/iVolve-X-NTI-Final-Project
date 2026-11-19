output "vpc_id" {
  description = "ID of the VPC."
  value       = aws_vpc.this.id
}

output "vpc_cidr" {
  description = "IPv4 CIDR range of the VPC."
  value       = aws_vpc.this.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets."
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets."
  value       = aws_subnet.private[*].id
}

output "availability_zones" {
  description = "Availability Zones used by the subnets."
  value       = local.availability_zones
}

output "nat_gateway_ids" {
  description = "IDs of the NAT Gateways providing outbound access to private subnets."
  value       = aws_nat_gateway.this[*].id
}

output "public_network_acl_id" {
  description = "Network ACL associated with the public subnets."
  value       = aws_network_acl.public.id
}

output "private_network_acl_id" {
  description = "Network ACL associated with the private subnets."
  value       = aws_network_acl.private.id
}
