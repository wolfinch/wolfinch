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


        location ~* ((/([0-9]+/wolfinch).*$)|/api/.*) {

           proxy_pass http://localhost:8080;
        }

}