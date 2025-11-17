variable "repository_name" {
  description = "Name of the ECR repository"
  type        = string
}

variable "tags" {
  description = "Base tags to apply to resources"
  type        = map(string)
  default     = {}
}
