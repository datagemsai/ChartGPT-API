terraform=$(terraform -chdir=infrastructure -var-file="variables/staging.tfvars")
terraform fmt  # formatting
terraform init # initializing terraform plugins
terraform plan # checking the plan 
terraform apply --auto-approve # Deploying resources
gcloud run services describe chartgpt-app --format 'value(uri)'
