# Network Module

This reusable module defines the development VPC and the network paths needed by EKS and other project services.

## Resources

- One VPC with DNS support and DNS hostnames enabled.
- An Internet Gateway and public route table.
- Public and private subnets distributed across the requested Availability Zones.
- Public subnet tags for internet-facing load balancer discovery and private subnet tags for internal load balancers and EKS discovery.
- Elastic IP address(es) and NAT Gateway(s) for outbound internet access from private subnets.
- Route table associations for every subnet.
- Separate public and private Network ACLs associated with their respective subnets. The public ACL allows HTTP for the ALB, trusted admin CIDRs for Jenkins SSH/UI, VPC traffic, web egress, and ephemeral return ports. The private ACL allows VPC traffic and HTTP/HTTPS egress through NAT.

By default, one NAT Gateway is shared by private subnets to reduce development cost. Setting `single_nat_gateway = false` creates one NAT Gateway per Availability Zone for AZ-local egress and improved availability, at higher cost.

The Network ACLs are stateless and explicitly allow return traffic. EKS and Jenkins security groups remain the primary workload-level controls. Review the Terraform plan before applying ACL associations to live subnets because an incomplete rule set can interrupt access. Inputs, outputs, and implementation are in `variables.tf`, `outputs.tf`, and `main.tf`.
