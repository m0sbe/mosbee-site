#!/bin/zsh
# Publish the site to the FirstVDS server (mosbee.ru, nginx of the ispmanager panel).
# Builds src/ into docs/ (new ?v= on CSS/JS links so browsers skip cached copies),
# then uploads docs/ to the site folder on the server and saves the sources to GitHub as a backup.
# Usage: ./deploy.sh "what changed"
set -e
cd "$(dirname "$0")"

SERVER=oil-server                               # alias from ~/.ssh/config (188.120.248.52)
DOCROOT=/var/www/oil/data/www/mosbee.ru         # site folder created in ispmanager, owner "oil"

python3 build.py
rsync -az --delete docs/ "$SERVER:$DOCROOT/"
ssh "$SERVER" "chown -R oil:oil $DOCROOT"
echo "uploaded to $SERVER:$DOCROOT"

# Backup: keep the sources on GitHub (the site itself is served only from the server).
git add -A
git commit -q -m "${1:-Update site}" || true
git push -q origin main && echo "backup pushed to GitHub ($(git rev-parse --short HEAD))"
