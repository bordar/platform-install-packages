#!/usr/bin/env bash
# exit on errors
set -e
source borhan-install-config.sh
# flush, stop and disable iptables from init. This for testing purposes ONLY. Make sure to replace with proper FW settings
iptables -F
service iptables stop
chkconfig iptables off
if [ `getenforce` = 'Enforcing' ] ;then
        setenforce permissive
fi
yum -y clean all
rpm -ihv --force http://installrepo.borhan.org/releases/borhan-release.noarch.rpm
yum -y install mysql-server borhan-server borhan-red5 postfix
service mysqld start
# this might fail if we already set the root password previously
set +e
mysqladmin -u root password "$MYSQL_ROOT_PASSWORD"
set -e
mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "update mysql.user set password=PASSWORD('$MYSQL_ROOT_PASSWORD') where user='root'"
mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e ""
mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1')"
mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "DELETE FROM mysql.user WHERE User=''"
mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%'"
mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "FLUSH PRIVILEGES"
chkconfig mysqld on
service postfix restart
/opt/borhan/bin/borhan-mysql-settings.sh
service memcached restart
service ntpd restart
chkconfig memcached on
chkconfig ntpd on
echo "USER_CONSENT=1" > /opt/borhan/bin/contact.rc
echo "127.0.0.1 $BORHAN_DOMAIN" >> /etc/hosts
echo "TIME_ZONE=\"UTC\"
BORHAN_FULL_VIRTUAL_HOST_NAME=\"$BORHAN_DOMAIN:80\"
BORHAN_VIRTUAL_HOST_NAME=\"$BORHAN_DOMAIN\"
DB1_HOST=\"127.0.0.1\"
DB1_PORT=\"3306\"
DB1_PASS=\"$MYSQL_ROOT_PASSWORD\"
DB1_NAME=\"borhan\"
DB1_USER=\"borhan\"
SERVICE_URL=\"http://$BORHAN_DOMAIN:80\"
SPHINX_SERVER1=\"127.0.0.1\"
SPHINX_SERVER2=\" \"
DWH_HOST=\"127.0.0.1\"
DWH_PORT=\"3306\"
SPHINX_DB_HOST=\"127.0.0.1\"
SPHINX_DB_PORT=\"3306\"
ADMIN_CONSOLE_ADMIN_MAIL=\"$BORHAN_ADMIN_EMAIL\"
ADMIN_CONSOLE_PASSWORD=\"$BORHAN_ADMIN_PASSWORD\"
CDN_HOST=\"$BORHAN_DOMAIN\"
BORHAN_VIRTUAL_HOST_PORT=\"80\"
SUPER_USER=\"root\"
SUPER_USER_PASSWD=\"$MYSQL_ROOT_PASSWORD\"
ENVIRONMENT_NAME=\"$BORHAN_ENVIRONMENT_NAME\"
DWH_PASS=\"$MYSQL_ROOT_PASSWORD\"
PROTOCOL=\"http\"
RED5_HOST=\"$BORHAN_DOMAIN\"
USER_CONSENT=\"0\"
CONFIG_CHOICE=\"0\"
CONTACT_MAIL=\"$BORHAN_ADMIN_EMAIL\"

#for SSL - change:
#IS_SSL=Y
#and uncomment and set correct paths for the following directives
#SSL cert path
#CRT_FILE=/etc/ssl/certs/localhost.crt
#SSL key path
#KEY_FILE=/etc/pki/tls/private/localhost.key
#if such exists enter path here, otherwise leave as is.
#CHAIN_FILE=NONE

IS_SSL=\"N\"
IS_NGINX_SSL=\"N\"
VOD_PACKAGER_HOST=\"$BORHAN_DOMAIN\"
VOD_PACKAGER_PORT=\"88\"
WWW_HOST=\"$BORHAN_DOMAIN\"
IP_RANGE=\"0.0.0.0-255.255.255.255\"
" > borhan.ans
/opt/borhan/bin/borhan-config-all.sh borhan.ans
unzip oflaDemo-r4472-java6.war -d/usr/lib/red5/webapps/oflaDemo
service red5 restart
/opt/borhan/bin/borhan-red5-config.sh
