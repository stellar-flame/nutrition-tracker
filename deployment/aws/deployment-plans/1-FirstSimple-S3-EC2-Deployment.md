# First Deployment
I am using this project to learn about deployments in AWS

This is the first simple deployment on AWS using an EC2 container

## Setup VPC
I set up the VPC for all future development and production simulation of this app based on what I learnt in Cantrill's course.

This is the configuration
* 10.0.0.0/16 VPC and subnets /20
* 2 AZs with each AZ having
  * 1 public subnet
  * 2 private subnet 

## 
* **React app** → static files on Amazon Simple Storage Service (S3)
* **FastAPI backend** → single Amazon Elastic Compute Cloud (EC2) instance in a **public subnet** with a **public IP**


---

## 1. React app on S3 (static website)

1. **Build your React app**

   ```bash
   npm run build
   ```

   This creates a `build/` folder.

2. **Create an S3 bucket**

   * Name: something like `my-react-app-dev`
   * Region: same region as your backend (for sanity).
   * **Uncheck** “Block all public access” *only if* you’re doing classic static website hosting.
     (If you later use CloudFront, you can keep it private and use an origin access control.)

3. **Upload the `build/` folder**

   * Upload everything inside `build/` to the S3 bucket.

4. **Enable static website hosting (simple dev way)**

   * In the bucket → **Properties** tab → “Static website hosting”.
   * Enable → index document = `index.html`.

5. **Note the website endpoint URL**

   * S3 gives you something like:
     `http://my-react-app-dev.s3-website-us-west-2.amazonaws.com`

You can visit that URL and see your frontend.

---

## 2. EC2 instance in a public subnet

You can use your **default VPC** for dev to keep it easy.

### a) Make sure you have a public subnet

In the VPC console:

* Pick a subnet that:

  * Is in your default VPC.
  * Has a route table with `0.0.0.0/0 → Internet Gateway`.

That’s your **public subnet**.

### b) Launch an EC2 instance

1. Go to **EC2 → Launch instance**.
2. Choose:

   * Amazon Linux 2 or Ubuntu (whatever you prefer).
   * Instance type: something small like `t3.micro` or `t2.micro`.
3. **Network settings**:

   * VPC: your default (or custom) VPC.
   * Subnet: your **public subnet**.
   * **Enable** “Auto-assign public IP”.
4. **Security group** (firewall):

   * Allow **SSH** (port 22) from **your IP** only.
   * Allow **HTTP** (port 80) or your FastAPI port (for example, 8000) from `0.0.0.0/0` (for dev) or from your IP.

   Example rules:

   * Inbound:

     * TCP 22 → your IP
     * TCP 8000 → 0.0.0.0/0 (or your IP if you want tighter)
5. Launch the instance and wait until it’s **running**.

---

## 3. Install and run FastAPI on the EC2 box

SSH into the instance:

```bash
ssh -i your-key.pem ec2-user@<EC2_PUBLIC_IP>
```

Then:

1. **Install Python + pip + venv** (example for Amazon Linux 2):

   ```bash
   sudo yum update -y
   sudo yum install -y python3 git
   python3 -m venv venv
   source venv/bin/activate
   pip install fastapi uvicorn
   ```

2. **Put your FastAPI code on the server**

   * Either `git clone` your repo, or `scp` files up.

3. **Run FastAPI with uvicorn** binding to `0.0.0.0`:

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

   OR 

   nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > fastapi.log 2>&1 &

   Replace `main:app` with your actual module and app object.

   tail logs:
      tail -f fastapi.log
   
   find process:
      ps aux | grep uvicorn

4. From your laptop, test it in a browser:

   ```text
   http://<EC2_PUBLIC_IP>:8000/docs
   ```

   You should see the FastAPI docs UI.

(For dev, it’s okay to just run uvicorn in a screen/tmux session. For later, you’d use a process manager like `systemd` or `supervisord`.)

---

## 4. Hook the React app to the FastAPI API

In your React code, create a config for the API base URL, something like:

```ts
const API_BASE_URL = "http://<EC2_PUBLIC_IP>:8000";
```

Or use an environment variable:

```bash
REACT_APP_API_BASE_URL=http://<EC2_PUBLIC_IP>:8000
```

Then your frontend calls:

```ts
fetch(`${process.env.REACT_APP_API_BASE_URL}/api/whatever`)
```

Rebuild (`npm run build`) and re-upload to S3 when you change this.

---

## 5. Don’t forget CORS (Cross-Origin Resource Sharing)

React app (S3 URL) and FastAPI (EC2 URL) are on **different origins**, so you must configure CORS in FastAPI.

In `main.py` (or wherever you create the app):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://my-react-app-dev.s3-website-us-west-2.amazonaws.com",
    # add https://your-cloudfront-domain.com later if you use CloudFront
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Restart uvicorn and try calling the API from the React app.
---

## 6. Where this fits with the “big” VPC design

* ✅ **Simple**:

  * React → S3 static site
  * FastAPI → single EC2 with public IP in a public subnet

Next up:

* Move FastAPI into **private subnets**.
* Put an **Application Load Balancer (ALB)** in the public subnets.
* Add a **database** in private database subnets.
* (Optional) Put CloudFront in front of S3.

Things to learn: 
* **Nginx + reverse proxy** so you can serve FastAPI on port 80 instead of 8000.


## 7 Allocate an Elastic IP
* This prevents the public IP from changing on restart and having to update S3 static react files
