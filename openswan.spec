
Summary:	Open Source implementation of IPsec for the Linux operating system
Summary(pl):	Otwarta implementacja IPseca dla systemu operacyjnego Linux
Name:		openswan
Version:	2.3.0
Release:	1
Epoch:		0
License:	GPL/BSD
Group:		Networking/Daemons
Source0:	http://www.openswan.org/download/%{name}-%{version}.tar.gz
# Source0-md5:	709d2b1102ddf6e50620b2fb5038e62b
Source1:	%{name}.init
Patch0:		%{name}-prefix.patch
Patch1:		%{name}-bash.patch
URL:		http://www.openswan.org/
Obsoletes:	ipsec-tools
Obsoletes:	strongswan
Obsoletes:	freeswan
Provides:	freeswan
PreReq:		rc-scripts
Requires(post,preun):	/sbin/chkconfig
Requires:	bash
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	gmp-devel
BuildRequires:	htmldoc
BuildRequires:	man2html
BuildRequires:	sed >= 4.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Openswan is an Open Source implementation of IPsec for the Linux 2.6.x
operating system. Is it a code fork of the FreeS/WAN project, started
by a few of the developers who were growing frustrated with the
politics surrounding the FreeS/WAN project.

%description -l pl
Openswan to otwarta implementacja IPseca dla systemu operacyjnego
Linux 2.6.x. Jest to odga��zienie kodu z projektu FreeS/WAN,
rozpocz�te przez kilku programist�w coraz bardziej sfrustrowanych
polityk� otaczaj�c� projekt FreeS/WAN.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%{__sed} -i -e "s#/lib/ipsec#/%{_lib}/ipsec#g#" Makefile
%{__sed} -i -e "s#/lib/freeswan$#/%{_lib}/freeswan#g#" Makefile
%{__sed} -i -e "s#/lib/ipsec#/%{_lib}/ipsec#g#" Makefile.inc

%build
%{__make} programs

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ipsec
%{__sed} -i -e "s#/lib/ipsec#/%{_lib}/ipsec#g#" $RPM_BUILD_ROOT/etc/rc.d/init.d/ipsec

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add ipsec
if [ -f /var/lock/subsys/ipsec ]; then
        /etc/rc.d/init.d/ipsec restart >&2
else
        echo "Run \"/etc/rc.d/init.d/ipsec start\" to start IPSEC daemon."
fi

%preun
if [ "$1" = "0" ]; then
        if [ -f /var/lock/subsys/ipsec ]; then
    		/etc/rc.d/init.d/ipsec stop>&2
	fi
        /sbin/chkconfig --del ipsec
fi

%files
%defattr(644,root,root,755)
%doc BUGS CHANGES CREDITS LICENSE README
%attr(755,root,root) %{_sbindir}/*
%dir %{_libdir}/ipsec
%attr(755,root,root) %{_libdir}/ipsec/*
%attr(754,root,root) /etc/rc.d/init.d/ipsec
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/ipsec.conf
%dir %{_sysconfdir}/ipsec.d
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/ipsec.d/*
%{_docdir}/openswan
%{_mandir}/man3/*
%{_mandir}/man5/*
%{_mandir}/man8/*
