#!/bin/bash

touch /etc/nginx/sites-available/Bluejay-SAAK && chmod 777 /etc/nginx/sites-available

cat engine.txt >> /etc/nginx/sites-available

ln -s /etc/nginx/sites-available/Bluejay-SAAK /etc/nginx/sites-enabled/

sudo nginx -t

sudo systemctl restart nginx

service nginx status

netstat -lntp
