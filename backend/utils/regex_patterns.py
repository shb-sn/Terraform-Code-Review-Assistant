"""
Contains regular exression patterns used by the security validator 
to detect hardcoded secrets, credentials, API keys and insecure terraform configurations.
"""

#hardcoded password
PASSWORD_PATTERN = (
    r'(?i)(password|passwd|pwd|db_password)\s*=\s*["\']?[^"\n\' ]+["\']?'
)

#generic secret
SECRET_PATTERN = (
    r'(?i)(secret|client_secret|app_secret|secret_key)\s*=\s*["\']?[^"\n\' ]+["\']?'
)

#API key
API_KEY_PATTERN=(
    r'(?i)(api[_-]?key)\s*=\s*["\'][A-Za-z0-9_\-]{16,}["\']'
)

#AWS access key
AWS_ACCESS_KEY_PATTERN=(
    r'AKIA[0-9A-Z]{16}'
)

#AWS Secret access key
AWS_SECRET_ACCESS_KEY_PATTERN=(
    r'(?i)(aws[_-]?secret[_-]?access[_-]?key)\s*=\s*["\'][A-Za-z0-9/+=]{40}["\']'
)

#bearer token
BEARER_TOKEN_PATTERN=(
    r'Bearer\s+[A-Za-z0-9\-._~+/]+=*'
)

#generic token
TOKEN_PATTERN=(
    r'(?i)(token|access[_-]?token)\s*=\s*["\'][A-Za-z0-9_\-]{16,}["\']'
)

#github personal access token
GITHUB_TOKEN_PATTERN=(
    r'gh[pousr]_[A-Za-z0-9]{36,255}'
)

#google API key
GOOGLE_API_KEY_PATTERN=(
    r'AIza[0-9A-Za-z\\-_]{35}'
)

#azure storage account key
AZURE_STORAGE_ACCOUNT_KEY_PATTERN=(
    r'(?i)(azure[_-]?storage[_-]?account[_-]?key)\s*=\s*["\'][A-Za-z0-9+/=]{80,}["\']'
)

#jwt token
JWT_PATTERN=(
    r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'
)

#RSA private key
RSA_PRIVATE_KEY_PATTERN=(
    r'-----BEGIN (RSA|EC|DSA|OPENSSH)? ?PRIVATE KEY-----'
)

#SSH private key
SSH_PRIVATE_KEY_PATTERN=(
    r'-----BEGIN OPENSSH PRIVATE KEY-----'
)

#terraform sensitive variable
SENSITIVE_VARIABLE_PATTERN=(
    r'variable\s+"[^"]+"\s*{\s*[^}]*sensitive\s*=\s*true[^}]*}'
)

#open CIDR (0.0.0.0/0) in security group
OPEN_CIDR_PATTERN=(
    r'cidr_blocks\s*=\s*\[\s*"0\.0\.0\.0/0"\s*\]'
)   

#public resource
PUBLIC_RESOURCE_PATTERN=(
    r'public_accessible\s*=\s*true'
)

#IAM wildcard action
IAM_WILDCARD_ACTION_PATTERN=(
    r'Action\s*=\s*"\*"'
)

#IAM wildcard resource
IAM_WILDCARD_RESOURCE_PATTERN=(
    r'Resource\s*=\s*"\*"'
)

#missing encryption
ENCRYPTION_DISABLED_PATTERN=(
    r'encryption\s*=\s*false'
)

#insecure HTTP url
HTTP_URL_PATTERN=(
    r'http://[^\s]+'
)

#terraform version constraint
TERRAFORM_VERSION_PATTERN=(
    r'required_version\s*='
)

#provider version constraint
PROVIDER_VERSION_PATTERN=(
    r'version\s*='
)

#public s3 bucket ACL
S3_PUBLIC_ACL_PATTERN=(
    r'acl\s*="(public-read|public-read-write|website)"'
)

#public s3 bucket policy
S3_PUBLIC_POLICY_PATTERN=(
    r'"Principal"\s*:\s*"\*"'
)

#S3 bucket public access block disabled
S3_PUBLIC_ACCESS_BLOCK_PATTERN=(
    r'block_public_acls\s*=\s*false|'
    r'block_public_policy\s*=\s*false|'
    r'ignore_public_acls\s*=\s*false|'
    r'restrict_public_buckets\s*=\s*false'
)