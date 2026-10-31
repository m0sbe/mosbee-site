#!/bin/zsh
# One-time server setup for mosbee.ru on the FirstVDS server (ispmanager panel, nginx).
# Creates the site in the panel (owner "oil", no PHP, alias www.mosbee.ru) and checks the nginx config.
# Run from the Mac:  ./server-setup.sh
# HTTPS is a separate step, after the domain's DNS points to the server:  ./server-setup.sh https
set -e
SERVER=oil-server
M=/usr/local/mgr5/sbin/mgrctl

if [[ "$1" == "https" ]]; then
  ssh "$SERVER" "
    $M -m ispmgr webdomain.edit sok=ok elid=mosbee.ru secure=on ssl_cert=letsencrypt
    $M -m ispmgr letsencrypt.generate sok=ok elid=mosbee.ru
    $M -m ispmgr webdomain.edit sok=ok elid=mosbee.ru redirect_http=on
    nginx -t && systemctl reload nginx
    echo; echo '--- certificate:'
    openssl s_client -connect 188.120.248.52:443 -servername mosbee.ru </dev/null 2>/dev/null | openssl x509 -noout -issuer -enddate
  "
  exit
fi

ssh "$SERVER" "
  $M -m ispmgr webdomain.edit sok=ok name=mosbee.ru owner=oil email=webmaster@mosbee.ru ipaddr=188.120.248.52 php=off secure=off aliases=www.mosbee.ru
  echo '--- site in the panel:'
  $M -m ispmgr webdomain | grep 'name=mosbee.ru'
  echo '--- nginx listen (must be 188.120.248.52, not the docker bridge):'
  grep -n listen /etc/nginx/vhosts/oil/mosbee.ru.conf
  nginx -t
"
echo; echo "site created; now run  ./deploy.sh \"first upload to the server\""
