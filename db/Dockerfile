FROM mysql:latest

COPY 01-init.sql /docker-entrypoint-initdb.d/01-init.sql
COPY 02-setup-users.sh /docker-entrypoint-initdb.d/02-setup-users.sh

RUN chmod +x /docker-entrypoint-initdb.d/02-setup-users.sh
