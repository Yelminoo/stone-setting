Render deployment steps (Docker)

This project can be deployed to Render using the provided `Dockerfile`.

Quick manual deploy (recommended):

1. Push your code to GitHub (main branch):

```powershell
git add Dockerfile .dockerignore requirements.txt app.py
git commit -m "Prepare for Render: Dockerfile, S3 support"
git push origin main
```

2. Log in to Render (https://dashboard.render.com) and connect your GitHub repo.

3. Create a new Web Service:
   - Type: Web Service
   - Environment: Docker
   - Branch: main
   - Dockerfile Path: `./Dockerfile`
   - Plan: Starter (or higher if you expect heavy CPU/memory usage)
   - Health Check Path: `/health`
   - Add Environment Variables (if using S3):
     - `S3_BUCKET` — your bucket name
     - `AWS_ACCESS_KEY_ID` — IAM user key
     - `AWS_SECRET_ACCESS_KEY` — IAM user secret
     - `AWS_REGION` — region (e.g., us-east-1)

4. Create the service and wait for the build and deploy logs to complete.

Notes
- The container runs `gunicorn` binding to `$PORT`. Render will set `PORT` for you.
- Files written to `/app/output` are ephemeral unless you configure a persistent disk or upload outputs to S3 (recommended). This code will upload to S3 when `S3_BUCKET` is set.

Troubleshooting
- If builds fail due to missing system packages, check the Dockerfile `apt-get` step and add the missing package.
- If generation times out or fails on high-complexity meshes, increase the service plan (more memory/CPU).
