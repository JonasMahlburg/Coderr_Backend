git add .
git commit -m "$*"
git push
ssh paintingotter34@35.204.204.97 "cd projects/Coderr_Backend && sudo git pull && sudo supervisorctl restart coderr-gunicorn"
