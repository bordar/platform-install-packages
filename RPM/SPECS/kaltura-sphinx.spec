%define sphinx_user kaltura
%define sphinx_group kaltura
%define prefix	/opt/kaltura/sphinx
# this isn't really a stand location for placing conf files but we wish to remain compatible with the current config dir tree used by Kaltura
%define confdir	/opt/kaltura/app/configurations/sphinx

Name:           kaltura-sphinx
Version:        2.2.1
Release:        4
Summary:        Sphinx full-text search server - for Kaltura

Group:          Applications/Text
License:        GPLv2
URL:            http://sphinxsearch.com
Vendor:         Sphinx Technologies Inc.
Packager:       Kaltura Inc.

Source0:       	%{name}-%{version}.tar.gz 
Source1: 	%{name}
Source2:	http://snowball.tartarus.org/dist/libstemmer_c.tgz
Source3:	re2.tar.gz
Source4:	kaltura.conf.template
Patch0:		config-main.patch
Patch1:		config.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-build

BuildRequires:  mysql-devel
BuildRequires:	expat-devel

Requires(post): chkconfig
Requires(preun): chkconfig
# This is for /sbin/service
Requires(preun): initscripts
Requires: mysql-libs zlib openssl expat libgcc krb5-libs, kaltura-base


%description
Sphinx is a full-text search server that adds many advanced features
on top of plain old text searching. Data can be fetched directly from
a database, or streamed in XML format. MySQL, PostgreSQL, SQL Server,
Oracle, and other databases are supported. Client programs can query
Sphinx either using native SphinxAPI library, or using regular MySQL
client programs and libraries via SQL-like SphinxQL interface.


%prep
%setup -n %{name}-%{version}
%patch0 -p1
%patch1 -p1
%setup -D -T -a 2 -n %{name}-%{version}
%setup -D -T -a 3 -n %{name}-%{version}

# Fix wrong-file-end-of-line-encoding
sed -i 's/\r//' api/ruby/spec/sphinx/sphinx_test.sql
sed -i 's/\r//' api/java/mk.cmd
sed -i 's/\r//' api/ruby/spec/fixtures/keywords.php
sed -i 's/\r//' api/ruby/lib/sphinx/response.rb


%build

%configure --sysconfdir=/opt/kaltura/app/configurations/sphinx  --with-mysql --with-libstemmer --with-unixodbc --with-iconv --enable-id64 --with-syslog --prefix=/opt/kaltura/sphinx --mandir=/opt/kaltura/sphinx/share/man --bindir=/opt/kaltura/sphinx/bin
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT INSTALL="%{__install} -p -c"
mkdir $RPM_BUILD_ROOT/opt/kaltura/sphinx/lib
#mv $RPM_BUILD_ROOT/usr/local/lib/libre2* $RPM_BUILD_ROOT/opt/kaltura/sphinx/lib
# Install sphinx initscript
install -p -D -m 0755 %{SOURCE1} $RPM_BUILD_ROOT%{_initrddir}/kaltura-sphinx

# Create /var/log/sphinx
mkdir -p $RPM_BUILD_ROOT%{prefix}/var/log/sphinx

# Create /var/run/sphinx
mkdir -p $RPM_BUILD_ROOT%{prefix}/var/run/sphinx



# Create /etc/logrotate.d/sphinx
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
cat > $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/sphinx << EOF
%{prefix}/log/sphinx/*.log {
       weekly
       rotate 10
       copytruncate
       delaycompress
       compress
       notifempty
       missingok
}
EOF

mkdir $RPM_BUILD_ROOT%{_sysconfdir}/profile.d
cat > $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/kaltura_sphinx.sh << EOF
PATH=$PATH:%{prefix}/bin
export PATH
EOF

%clean
rm -rf $RPM_BUILD_ROOT


%post
ldconfig
# register service
if [ "$1" = 1 ];then
    /sbin/chkconfig --add kaltura-sphinx
	echo "
	#####################################################################################################################################
	Installation of %{name} %{version} completed
	Please run 
	# %{prefix}/bin/%{name}-config.sh [/path/to/answer/file]
	To finalize the setup.
	#####################################################################################################################################
	"
fi

# create user/group, and update permissions
chown -R %{sphinx_user}:%{sphinx_group} %{prefix}/var/log/sphinx %{prefix}/var/run/sphinx




%preun
if [ "$1" = 0 ] ; then
    /sbin/service kaltura-sphinx stop >/dev/null 2>&1
    /sbin/chkconfig --del kaltura-sphinx
fi


%files
%defattr(-,root,root,-)
%{prefix}/share/man/man1/*
%doc COPYING doc/sphinx.html doc/sphinx.txt sphinx-min.conf.dist sphinx.conf.dist example.sql
%dir %{confdir}
#%config(missingok) %{confdir}/kaltura_sphinx.conf
%config %{_sysconfdir}/profile.d/kaltura_sphinx.sh
%exclude %{confdir}/*.conf.dist
%exclude %{confdir}/example.sql
%{_initrddir}/kaltura-sphinx
%config(noreplace) %{_sysconfdir}/logrotate.d/sphinx
%{prefix}/bin/*
%dir %{prefix}/var/log/sphinx
%dir %{prefix}/var/run/sphinx



%changelog
* Sun Jan 12 2014 Jess Portnoy <jess.portnoy@kaltura.com> 2.2.1.r4097-4
- Output post message only on first install.

* Sun Jan 12 2014 Jess Portnoy <jess.portnoy@kaltura.com> 2.2.1.r4097-2
- Prefix can be w/o version, we only have one Sphinx ver at a time [unlike Ffmpeg].
- No lib dir for Sphinx.
- No need for the usage output in %%post.

* Sun Jan 12 2014 Jess Portnoy <jess.portnoy@kaltura.com> 2.2.1.r4097-2
- Paths to log and run corrected.

* Tue Dec 24 2013 Jess Portnoy <jess.portnoy@kaltura.com> 2.2.1.r4097-1
First build.
