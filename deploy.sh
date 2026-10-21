#!/bin/zsh
# Publish the site to GitHub Pages (m0sbee.com).
# Bumps ?v= on CSS/JS links so browsers skip their cached copies, then commits and pushes.
# Usage: ./deploy.sh "what changed"
set -e
cd "$(dirname "$0")"

v=$(date +%Y%m%d%H%M%S)
sed -E -i '' "s#(css/style\.css|js/(main|logo3d|tools3d)\.js)(\?v=[0-9]+)?\"#\1?v=$v\"#g" index.html ru/index.html

git add -A
git commit -q -m "${1:-Update site}"
git push -q origin main
echo "pushed $(git rev-parse --short HEAD), version $v"
