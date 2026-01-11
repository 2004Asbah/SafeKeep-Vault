🛡️ SafeKeep VaultProduction-Grade, Cost-Optimized Cloud Archiving for NGOs.📌 The ProblemMany NGOs operating in low-bandwidth or high-risk zones struggle with two major issues:High Costs: Commercial cloud storage is expensive for long-term legal archiving.

Connectivity Issues: Large files fail to upload in remote areas, and unoptimized data wastes expensive satellite/mobile credits.🚀 The SolutionSafeKeep Vault is a DevOps-driven solution that provides a secure, automated pipeline for document preservation.

Auto-Optimization: Compresses files locally before upload to save bandwidth.

Smart Archiving: Uses AWS Lifecycle Policies to move old data to Glacier Deep Archive, reducing storage costs by up to 90%.

Enterprise Security: AES-256 encryption-at-rest and strict IAM policies.

🛠️ Tech StackCategoryTechnologyCloud ProviderAWS (S3, IAM, CloudWatch)InfrastructureTerraform (IaC)ContainerizationDockerAutomationGitHub Actions (CI/CD)FrontendStreamlit (Python)SecurityAES-256 Encryption, Checkov Scans🏗️ ArchitectureUser uploads a document via the Streamlit Web Portal.Python Backend optimizes the file (PDF/Image compression).

Terraform-managed S3 Bucket receives the encrypted file.Lifecycle Rules automatically transition data to low-cost storage tiers after 30 days.GitHub Actions handles the deployment of infrastructure and code updates.

⚡ Quick Start (For Developers)

1. Clone the RepoBashgit clone https://github.com/2004Asbah/safekeep-vault.git
cd safekeep-vault

2. Deploy InfrastructureBashcd terraform
terraform init
terraform apply -auto-approve

4. Run Locally (Docker)Bashdocker build -t safekeep-vault .
docker run -p 8501:8501 --env-file .env safekeep-vault

📈 Impact & Cost AnalysisBy implementing Intelligent Tiering, SafeKeep Vault reduces costs for a typical NGO from $0.023 per GB to $0.00099 per GB for long-term storage.🤝 ContributingThis project is built to help humanitarian organizations. Feel free to open an issue or submit a pull request!
