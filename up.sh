git add .
git commit -m "$*"
git push
ssh paintingotter34@34.13.212.51 "cd projects/Coderr_Backend && sudo git pull && sudo supervisorctl restart coderr-gunicorn"

