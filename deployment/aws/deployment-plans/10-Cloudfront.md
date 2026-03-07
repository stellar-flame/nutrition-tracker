## Introduce Cloudfront

Create Cloudfront distribution for S3 bucket as origin
Generate ACM (Amazon Certificate Manager) Certificate for `www.nutritionapptracker.com`
Make bucket private and remove static website hosting

## Update CORS
Update CORS on FastAPI to accept origin: `www.nutritionapptracker.com`
Redeploy container

## Update API to use HTTPS
Generate ACM (Amazon Certificate Manager) Certificate for `api.nutritionapptracker.com`
Add Listener on ALB for HTTPS:443
Update HTTP:80 Listener to redirect to HTTPS:443
Update Security Group to allow inbound traffic on HTTPS:443
