#!/bin/zsh
# Publish the site to GitHub Pages (m0sbee.com).
# Builds src/ into docs/ (new ?v= on CSS/JS links so browsers skip cached copies), then commits and pushes.
# Usage: ./deploy.sh "what changed"
set -e
cd "$(dirname "$0")"

python3 build.py

git add -A
git commit -q -m "${1:-Update site}"
git push -q origin main
echo "pushed $(git rev-parse --short HEAD)"
