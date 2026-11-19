# Network Module

This reusable module defines the development VPC and the network paths needed by EKS and other project services.

## Resources

- One VPC with DNS support and DNS hostnames enabled.
- An Internet Gateway and public route table.
- Public and private subnets distributed across the requested Availability Zones.
- Public subnet tags for internet-facing load balancer discovery and private subnet tags for internal load balancers and EKS discovery.
- Elastic IP address(es) and NAT Gateway(s) for outbound internet access from private subnets.
- Route table associations for every subnet.

By default, one NAT Gateway is shared by private subnets to reduce development cost. Setting `single_nat_gateway = false` creates one NAT Gateway per Availability Zone for AZ-local egress and improved availability, at higher cost.

The module only declares infrastructure. The development environment calls it from `terraform/environments/dev`; no AWS resources have been applied yet. Inputs, outputs, and implementation are in `variables.tf`, `outputs.tf`, and `main.tf`.
