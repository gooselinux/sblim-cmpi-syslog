%define provider_dir %{_libdir}/cmpi
%define tog_pegasus_version 2:2.5.1

Summary:        SBLIM syslog instrumentation
Name:           sblim-cmpi-syslog
Version:        0.8.0
Release:        1%{?dist}
License:        EPL
Group:          Applications/System
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
URL:            http://sourceforge.net/projects/sblim/
Source0:        http://downloads.sourceforge.net/sblim/%{name}-%{version}.tar.bz2

BuildRequires:  tog-pegasus-devel >= %{tog_pegasus_version}
BuildRequires:  sblim-cmpi-base-devel >= 1.5.4
BuildRequires:  sed
Requires:       tog-pegasus >= %{tog_pegasus_version}, sblim-cmpi-base
Requires:       sblim-cmpi-base >= 1.5.4
Requires:       /etc/ld.so.conf.d
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description
Standards Based Linux Instrumentation Syslog Providers

%package devel
# ^- currently a placeholder - no devel files shipped
Summary:        SBLIM Syslog Instrumentation Header Development Files
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       tog-pegasus

%description devel
SBLIM Base Syslog Development Package

%package test
Summary:        SBLIM Syslog Instrumentation Testcases
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}
Requires:       sblim-testsuite
Requires:       tog-pegasus

%description test
SBLIM Base Syslog Testcase Files for SBLIM Testsuite

%prep
%setup -q
# removing COPYING, because it's misleading
rm -f COPYING

%build
%ifarch s390 s390x ppc ppc64
export CFLAGS="$RPM_OPT_FLAGS -fsigned-char"
%else
export CFLAGS="$RPM_OPT_FLAGS" 
%endif
%configure \
        TESTSUITEDIR=%{_datadir}/sblim-testsuite \
        CIMSERVER=pegasus \
        PROVIDERDIR=%{provider_dir}
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
# remove unused libtool files
rm -f $RPM_BUILD_ROOT/%{_libdir}/*a
rm -f $RPM_BUILD_ROOT/%{provider_dir}/*a
# shared libraries
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d
echo "%{_libdir}/cmpi" > $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf
# move libraries to provider dir
mv $RPM_BUILD_ROOT/%{_libdir}/lib[Ss]yslog*.so* $RPM_BUILD_ROOT/%{provider_dir}
# add shebang to the scripts
sed -i -e '1i#!/bin/sh' $RPM_BUILD_ROOT/%{_bindir}/syslog-service.sh \
$RPM_BUILD_ROOT/%{_datadir}/sblim-testsuite/runtest_pegasus.sh \
$RPM_BUILD_ROOT/%{_datadir}/sblim-testsuite/runtest_wbemcli.sh \
$RPM_BUILD_ROOT/%{_datadir}/sblim-testsuite/system/linux/logrecord.sh \
$RPM_BUILD_ROOT/%{_datadir}/sblim-testsuite/system/linux/msglogtest.sh \
$RPM_BUILD_ROOT/%{_datadir}/sblim-testsuite/system/linux/messagelog.sh

%files
%defattr(-,root,root,0755)
%{_bindir}/syslog-service.sh
%{provider_dir}/lib[Ss]yslog*.so*
%{_datadir}/%{name}
%docdir %{_datadir}/doc/%{name}-%{version}
%{_datadir}/doc/%{name}-%{version}
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf

%files test
%defattr(-,root,root,0755)
%{_datadir}/sblim-testsuite/runtest*
%{_datadir}/sblim-testsuite/test-cmpi-syslog*
%{_datadir}/sblim-testsuite/cim/Syslog*
%{_datadir}/sblim-testsuite/system/linux/Syslog*
%{_datadir}/sblim-testsuite/system/linux/logrecord.sh
%{_datadir}/sblim-testsuite/system/linux/messagelog.sh
%{_datadir}/sblim-testsuite/system/linux/msglogtest.sh
%{_datadir}/sblim-testsuite/system/linux/setting

%define SYSLOG_SCHEMA %{_datadir}/sblim-cmpi-syslog/Syslog_Log.mof %{_datadir}/sblim-cmpi-syslog/Syslog_Service.mof  %{_datadir}/sblim-cmpi-syslog/Syslog_Configuration.mof
%define SYSLOG_REGISTRATION %{_datadir}/sblim-cmpi-syslog/Syslog_Configuration.registration  %{_datadir}/sblim-cmpi-syslog/Syslog_Log.registration %{_datadir}/sblim-cmpi-syslog/Syslog_Service.registration

%pre
# If upgrading, deregister old version
if [ $1 -gt 1 ]; then
  %{_datadir}/%{name}/provider-register.sh -d \
  -t pegasus -r %{SYSLOG_REGISTRATION} -m %{SYSLOG_SCHEMA} > /dev/null 2>&1 || :;
fi

%post
/sbin/ldconfig
if [ $1 -ge 1 ]; then
# Register Schema and Provider - this is higly provider specific
  %{_datadir}/%{name}/provider-register.sh \
  -t pegasus -r %{SYSLOG_REGISTRATION} -m %{SYSLOG_SCHEMA} > /dev/null 2>&1 || :;
fi;

%preun
# Deregister only if not upgrading
if [ $1 -eq 0 ]; then
  %{_datadir}/%{name}/provider-register.sh -d \
  -t pegasus -r %{SYSLOG_REGISTRATION} -m %{SYSLOG_SCHEMA} > /dev/null 2>&1 || :;
fi

%postun -p /sbin/ldconfig

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Wed Jun 30 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 0.8.0-1
- Update to sblim-cmpi-syslog-0.8.0

* Fri Oct 23 2009 Vitezslav Crhonek <vcrhonek@redhat.com> - 0.7.11-1
- Initial support
