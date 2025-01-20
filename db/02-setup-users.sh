#!/bin/bash
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" <<EOF
CREATE USER "scraper"@"%" IDENTIFIED BY "${SCRAPER_PASSWORD}";
CREATE USER "backend"@"%" IDENTIFIED BY "${BACKEND_PASSWORD}";

GRANT SELECT, INSERT, UPDATE ON ogloszenia_trojmiasto.* TO "scraper"@"%";
GRANT SELECT ON ogloszenia_trojmiasto.* TO "backend"@"%";
FLUSH PRIVILEGES;
EOF
