FROM nginx:1.19.0-alpine

RUN rm /etc/nginx/conf.d/default.conf
EXPOSE 443
COPY nginx.conf /etc/nginx/conf.d
