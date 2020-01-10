server {
        server_name www.wolfinch.com;
        root /home/jork/www;
        index index.html;

            # Media: images, icons, video, audio, HTC
            location ~* \.(?:jpg|jpeg|gif|png|ico|cur|gz|svg|mp4|ogg|ogv|webm|htc)$ {
              access_log off;
              add_header Cache-Control "max-age=2592000";
            }
            # CSS and Javascript
#            location ~* \.(?:css|js)$ {
#              add_header Cache-Control "max-age=31536000";
#              access_log off;
#            }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/www.wolfinch.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/www.wolfinch.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
      
        location ~* ((/([0-9]+/wolfinch).*$)|/api/.*) {
        
           proxy_pass http://localhost:8080;
        }

}
server {
    if ($host = www.wolfinch.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


        listen 80;
        server_name www.wolfinch.com;
    return 404; # managed by Certbot


}
