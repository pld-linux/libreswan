# TODO:
# - libreswan.init needs update (since openswan 2.6.x)
# - warning: Installed (but unpackaged) file(s) found:
#   /usr/share/doc/libreswan/index.html
#   /usr/share/doc/libreswan/ipsec.conf-sample
#
# NOTE (TODO: check validity for current libreswan):
# - 32-bit tncfg and starter won't work on 64-bit kernels because of FUBAR
#   ioctls (only ifru_data pointer is supported in 32->64 conversion of
#   SIOCDEVPRIV ioctl, but openswan puts some static data in structure there)
#
Summary:	Open Source implementation of IPsec for the Linux operating system
Summary(pl.UTF-8):	Otwarta implementacja IPseca dla systemu operacyjnego Linux
Name:		libreswan
Version:	3.23
Release:	0.1
License:	GPL v2 with linking permission, BSD (DES and radij code)
Group:		Networking/Daemons
Source0:	https://download.libreswan.org/%{name}-%{version}.tar.gz
# Source0-md5:	ad6e6715cd01c143a4501f933c044a88
Source1:	%{name}.init
Patch0:		%{name}-gawk.patch
URL:		https://libreswan.org/
BuildRequires:	bison
BuildRequires:	curl-devel
BuildRequires:	docbook-dtd412-xml
BuildRequires:	flex
BuildRequires:	libcap-ng-devel
BuildRequires:	libevent-devel >= 2
BuildRequires:	libselinux-devel
BuildRequires:	nss-devel >= 3
BuildRequires:	nspr-devel >= 4
BuildRequires:	pam-devel
BuildRequires:	perl-tools-pod
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	sed >= 4.0
BuildRequires:	unbound-devel
BuildRequires:	which
BuildRequires:	xmlto
Requires(post,preun):	/sbin/chkconfig
Requires:	bash
Requires:	iproute2
Requires:	iptables
Requires:	rc-scripts
Provides:	freeswan
Provides:	openswan
Obsoletes:	freeswan
Obsoletes:	ipsec-tools
Obsoletes:	openswan
Obsoletes:	strongswan
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Libreswan is an IPsec implementation for Linux. It has support for
most of the extensions (RFC + IETF drafts) related to IPsec, including
IKEv2, X.509 Digital Certificates, NAT Traversal, and many others.
Libreswan uses the native Linux IPsec stack (NETKEY/XFRM) per default,
but may also use the alternative Libreswan kernel IPsec stack (KLIPS).

Libreswan was forked from Openswan 2.6.38, which was forked from
FreeS/WAN 2.04.

%description -l pl.UTF-8
Libreswan to implementacja standardu IPsec dla Linuksa. Obsługuje
większość rozszerzeń IPseca (RFC + szkice IETF), w tym IKEv2,
certyfikaty X.509, przechodzenie NAT i wiele innych. Libreswan
wykorzystuje domyślnie natywny stos IPsec Linuksa (NETKEY/XFRM),
ale może używać też alternatywnego (KLIPS).

Libreswan wywodzi się z projektu Openswan w wersji 2.6.38, który z
kolei wywodzi się z projektu FreeS/WAN w wersji 2.04.

%prep
%setup -q
%patch0 -p1

%build
USE_WEAKSTUFF=true \
USE_NOCRYPTO=true \
%{__make} -j1 programs \
	CC="%{__cc}" \
	INC_USRLOCAL=%{_prefix} \
	FINALLIBEXECDIR=%{_libexecdir}/ipsec \
	MANTREE=%{_mandir} \
	USERCOMPILE="%{rpmcflags}" \
	IPSECVERSION=%{version}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,/var/run/pluto}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	INC_USRLOCAL=%{_prefix} \
	FINALLIBEXECDIR=%{_libexecdir}/ipsec \
	MANTREE=$RPM_BUILD_ROOT%{_mandir} \
	IPSECVERSION=%{version}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ipsec
%{__sed} -i -e "s#/lib/ipsec#/%{_lib}/ipsec#g#" $RPM_BUILD_ROOT/etc/rc.d/init.d/ipsec

install -d $RPM_BUILD_ROOT%{systemdtmpfilesdir}
cat >$RPM_BUILD_ROOT%{systemdtmpfilesdir}/libreswan.conf <<EOF
d /var/run/pluto 0755 root root -
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add ipsec
%service ipsec restart "IPSEC daemon"

%preun
if [ "$1" = "0" ]; then
	%service ipsec stop
	/sbin/chkconfig --del ipsec
fi

%files
%defattr(644,root,root,755)
%doc CHANGES CREDITS LICENSE README* TRADEMARK
%attr(755,root,root) %{_sbindir}/ipsec
%dir %{_libexecdir}/ipsec
%attr(755,root,root) %{_libexecdir}/ipsec/*
%attr(754,root,root) /etc/rc.d/init.d/ipsec
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/pluto
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ipsec.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ipsec.secrets
%dir %{_sysconfdir}/ipsec.d
%dir %{_sysconfdir}/ipsec.d/policies
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ipsec.d/policies/block
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ipsec.d/policies/clear
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ipsec.d/policies/clear-or-private
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ipsec.d/policies/private
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ipsec.d/policies/private-or-clear
%config(noreplace) %verify(not md5 mtime size) /etc/pam.d/pluto
%dir /var/run/pluto
%{systemdtmpfilesdir}/libreswan.conf
%{_mandir}/man5/ipsec.conf.5*
%{_mandir}/man5/ipsec.secrets.5*
%{_mandir}/man5/ipsec_*.5*
%{_mandir}/man8/ipsec.8*
%{_mandir}/man8/ipsec_*.8*
%{_mandir}/man8/pluto.8*
