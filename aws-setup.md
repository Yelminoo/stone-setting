# AWS S3 + IAM setup for stone-setting (step-by-step)

This guide shows how to create an S3 bucket, a least-privilege IAM policy, an IAM user, and programmatic access keys you can set as environment variables in Render (or use locally).

-- Quick checklist
- Create an S3 bucket
- Create an IAM policy scoped to the bucket (`policy.json` provided)
- Create an IAM user and attach the policy
- Create access keys for the user (copy the secret now)
- Add keys as environment variables in Render (or locally)

---

## 1) Create an S3 bucket (console)
1. Open the S3 console: https://s3.console.aws.amazon.com/s3
2. Click **Create bucket**.
3. For **Bucket name** pick a globally-unique name, e.g. `my-stone-setting-outputs-yourhandle`.
4. Choose a Region (e.g. `us-east-1`).
5. Keep **Block public access** ON (recommended). We will use presigned URLs unless you explicitly want public objects.
6. Click **Create bucket**.

### Or create using AWS CLI (PowerShell)
```powershell
aws s3 mb s3://my-stone-setting-outputs-yourhandle --region us-east-1
```

---

## 2) Create an IAM policy (least privilege)
Use the `policy.json` file in this repo. Replace `YOUR_BUCKET_NAME` with the bucket name you created.

Console:
- IAM → Policies → Create policy → JSON tab → paste the contents of `policy.json` (with your bucket name) → Next → Name the policy (e.g. `stone-setting-s3-policy`) → Create.

CLI (PowerShell):
```powershell
# Ensure policy.json contains your bucket name
$policyArn = (aws iam create-policy --policy-name stone-setting-s3-policy --policy-document file://policy.json | ConvertFrom-Json).Arn
Write-Host "Created policy: $policyArn"
```

---

## 3) Create IAM user and attach policy
Console (recommended):
1. IAM → Users → Add users
2. User name: `stone-setting-bot` (or your preferred name)
3. Access type: **Programmatic access** (creates Access Key ID and Secret Access Key)
4. Next: Attach permissions -> choose **Attach existing policies directly** -> find `stone-setting-s3-policy` -> Next
5. Optional: On the Tags step add a tag: `Key=Description`, `Value=Render uploader for stone-setting` (helps later)
6. Create user and copy the Access Key ID and Secret Access Key (store secret safely)

CLI (PowerShell):
```powershell
# Create user with a Description tag
aws iam create-user --user-name stone-setting-bot --tags Key=Description,Value="Render uploader for stone-setting"

# Attach policy ARN (replace POLICY_ARN printed from previous step)
aws iam attach-user-policy --user-name stone-setting-bot --policy-arn arn:aws:iam::123456789012:policy/stone-setting-s3-policy

# Create access key
$ak = aws iam create-access-key --user-name stone-setting-bot | ConvertFrom-Json
$ak.AccessKey.AccessKeyId
$ak.AccessKey.SecretAccessKey

# Save the above two values securely now (SecretAccessKey is shown only once)
```

Notes on tags: tags make it easier to manage, filter and audit programmatic users.

---

## 4) Retrieve / rotate / delete access keys
- Each IAM user can have up to 2 active access keys — use that to rotate keys safely.

List keys:
```powershell
aws iam list-access-keys --user-name stone-setting-bot
```

Deactivate a key (safe step before deleting):
```powershell
aws iam update-access-key --user-name stone-setting-bot --access-key-id AKIA... --status Inactive
```

Delete a key:
```powershell
aws iam delete-access-key --user-name stone-setting-bot --access-key-id AKIA...
```

---

## 5) Add env vars to Render (or set locally for testing)
In Render Dashboard → your service → Settings → Environment → Add Env Var:

- `S3_BUCKET` = `my-stone-setting-outputs-yourhandle`
- `AWS_ACCESS_KEY_ID` = `<AccessKeyId from create-access-key>`
- `AWS_SECRET_ACCESS_KEY` = `<SecretAccessKey from create-access-key>`
- `AWS_REGION` = `us-east-1`

Save and redeploy if necessary.

Local testing (PowerShell):
```powershell
$env:S3_BUCKET = "my-stone-setting-outputs-yourhandle"
$env:AWS_ACCESS_KEY_ID = "AKIA..."
$env:AWS_SECRET_ACCESS_KEY = "..."
$env:AWS_REGION = "us-east-1"
python app.py
```

Local Docker run with env vars:
```powershell
docker run --rm -it -p 5000:5000 `
  -e AWS_ACCESS_KEY_ID="AKIA..." `
  -e AWS_SECRET_ACCESS_KEY="..." `
  -e AWS_REGION="us-east-1" `
  -e S3_BUCKET="my-stone-setting-outputs-yourhandle" `
  -v ${PWD}\\output:/app/output stone-setting:latest
```

---

## 6) Presigned URLs (recommended for private buckets)
Instead of making objects public, the app can upload them privately and return time-limited presigned URLs for download. Example (Python/boto3):

```python
import boto3
s3 = boto3.client('s3', region_name='us-east-1', aws_access_key_id=..., aws_secret_access_key=...)
url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=3600)
```

If you want, I can update `app.py` to return presigned URLs automatically.

---

## 7) Security best practices (summary)
- Use least-privilege IAM policies (scope to bucket and actions)
- Avoid embedding keys in code or repo
- Rotate keys regularly (create new, update services, delete old)
- Use presigned URLs to keep bucket private
- Use IAM roles (EC2/ECS/Lambda) or OIDC where possible instead of long-lived access keys
- Store secrets in the service secret store (Render env vars, AWS Secrets Manager)

---

If you'd like, I can:
- update `app.py` to return presigned URLs (recommended), or
- walk you through creating the user and keys in the console while you paste the values here (I won't store them), or
- add a `README_AWS_CLI.md` with additional automation scripts (CloudFormation or Terraform) to create the bucket & policy.
