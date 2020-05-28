Summary: Quantum Linear Tape File System
Name: qtmltfs
Version: 2.4.0.2
Release: 1
Group: Util
Vendor: Quantum
License: BSD
Source: %{name}-%{version}-%{release}.tar.gz
Requires: /sbin/ldconfig, /usr/bin/awk, /usr/bin/systemctl, /bin/bash
Conflicts: %{name} < 2.4
Requires:  fuse >= 2.7
Requires:  libxml2
Requires:  libicu
BuildRoot: /tmp/rpm/%{name}-%{version}

%define         _prefix  /opt/QUANTUM/ltfs
%define         _sysconf /etc
%define         _ulocal  /usr/local
%define		_mandir /usr/share/man

%if %{defined suse_version}
%debug_package
%endif

%description
Quantum Linear Tape File System (QTM LTFS)

%prep
%setup -q -n qtmltfs2.4

%build
rm -rf $RPM_BUILD_ROOT
./autogen.sh
./configure --prefix=%{_prefix} --libdir=%{_libdir} --sysconfdir=%{_sysconf} --mandir=%{_mandir} --disable-snmp --enable-fast
make

%pretrans
if [ -d /usr/local/lib/ltfs ]
then
    mv /usr/local/lib/ltfs /usr/local/lib/ltfs.rpmsave
    ln -s /usr/local/lib/ltfs.rpmsave /usr/local/lib/ltfs
fi

if [ -d /usr/local/lib64/ltfs ]
then
    mv /usr/local/lib64/ltfs /usr/local/lib64/ltfs.rpmsave
    ln -s /usr/local/lib64/ltfs.rpmsave /usr/local/lib64/ltfs
fi

%posttrans
if [ -s /usr/local/lib/ltfs.rpmnew ]
then
    rm -rf /usr/local/lib/ltfs
    mv /usr/local/lib/ltfs.rpmnew /usr/local/lib/ltfs
    /sbin/ldconfig
fi

if [ -s /usr/local/lib64/ltfs.rpmnew ]
then
    rm -rf /usr/local/lib64/ltfs
    mv /usr/local/lib64/ltfs.rpmnew /usr/local/lib64/ltfs
    /sbin/ldconfig
fi

%pre
if cat /proc/mounts | awk {'print $1'} | grep -q "^ltfs$"
then
    echo
    echo "Error: please unmount all LTFS instances before installing this RPM."
    echo
    exit 1
fi

%preun
if cat /proc/mounts | awk {'print $1'} | grep -q "^ltfs$"
then
    echo
    echo "Error: please unmount all LTFS instances before removing this RPM."
    echo
    exit 1
fi
/usr/bin/systemctl stop ltfs
/usr/bin/systemctl disable ltfs
/usr/bin/systemctl restart rsyslog

%install
[ -d $RPM_BUILD_ROOT ] && rm -rf $RPM_BUILD_ROOT;
make -e prefix=$RPM_BUILD_ROOT%{_prefix} libdir=$RPM_BUILD_ROOT%{_libdir} includedir=$RPM_BUILD_ROOT%{_includedir} sysconfdir=$RPM_BUILD_ROOT%{_sysconf} mandir=$RPM_BUILD_ROOT%{_mandir} install
mkdir $RPM_BUILD_ROOT%{_libdir}/ltfs
mv $RPM_BUILD_ROOT%{_libdir}/libtape-* $RPM_BUILD_ROOT%{_libdir}/ltfs
mv $RPM_BUILD_ROOT%{_libdir}/libiosched-* $RPM_BUILD_ROOT%{_libdir}/ltfs
mv $RPM_BUILD_ROOT%{_libdir}/libkmi-* $RPM_BUILD_ROOT%{_libdir}/ltfs
mkdir -p $RPM_BUILD_ROOT%{_sysconf}/logrotate.d
cp %{_builddir}/qtmltfs2.4/docs/ltfslog $RPM_BUILD_ROOT%{_sysconf}/logrotate.d
mkdir -p $RPM_BUILD_ROOT%{_sysconf}/rsyslog.d
cp %{_builddir}/qtmltfs2.4/docs/ltfs-log.conf $RPM_BUILD_ROOT%{_sysconf}/rsyslog.d
mkdir -p $RPM_BUILD_ROOT%{_sysconf}/systemd/system
cp %{_builddir}/qtmltfs2.4/docs/ltfs.service $RPM_BUILD_ROOT%{_sysconf}/systemd/system
mv $RPM_BUILD_ROOT%{_bindir}/ltfs $RPM_BUILD_ROOT%{_bindir}/ltfs-singledrive
mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp %{_builddir}/qtmltfs2.4/docs/INSTALL $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp %{_builddir}/qtmltfs2.4/LICENSE $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp %{_builddir}/qtmltfs2.4/NOTICES $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp %{_builddir}/qtmltfs2.4/docs/README $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp %{_builddir}/qtmltfs2.4/docs/ltfs-log.conf $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp %{_builddir}/qtmltfs2.4/docs/ltfs.conf.example $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
cp %{_builddir}/qtmltfs2.4/docs/ltfs.conf.local.example $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
# create symbolic links (Commands)
[ ! -d $RPM_BUILD_ROOT%{_ulocal}/bin ] && mkdir -p $RPM_BUILD_ROOT%{_ulocal}/bin
ln -s -f %{_bindir}/ltfs-singledrive $RPM_BUILD_ROOT%{_ulocal}/bin/ltfs
ln -s -f %{_bindir}/mkltfs $RPM_BUILD_ROOT%{_ulocal}/bin/mkltfs
ln -s -f %{_bindir}/ltfsck $RPM_BUILD_ROOT%{_ulocal}/bin/ltfsck

# create symbolic links (Libraries)
[ ! -d $RPM_BUILD_ROOT%{_ulocal}/%{_lib} ] && mkdir -p $RPM_BUILD_ROOT%{_ulocal}/%{_lib}
for FN in $RPM_BUILD_ROOT%{_libdir}/*
do
    b=`basename ${FN}`
    [ -f ${FN} ] && ln -s -f %{_libdir}/${b} $RPM_BUILD_ROOT%{_ulocal}/%{_lib}/${b}
done

# create symbolic links (Backends)
ln -s -f  %{_libdir}/ltfs $RPM_BUILD_ROOT%{_ulocal}/%{_lib}/ltfs

# create symbolic links (Doc)
[ ! -d $RPM_BUILD_ROOT%{_ulocal}/share/doc ] && mkdir -p $RPM_BUILD_ROOT%{_ulocal}/share/doc
ln -s -f %{_docdir} $RPM_BUILD_ROOT%{_ulocal}/share/doc/%{name}-%{version}

%post
/sbin/ldconfig
/usr/bin/systemctl enable ltfs
/usr/bin/systemctl start ltfs
/usr/bin/systemctl restart rsyslog

if [ -d /usr/local/lib/ltfs.rpmsave ]
then
    mv /usr/local/lib/ltfs /usr/local/lib/ltfs.rpmnew
    mv /usr/local/lib/ltfs.rpmsave /usr/local/lib/ltfs
fi

if [ -d /usr/local/lib64/ltfs.rpmsave ]
then
    mv /usr/local/lib64/ltfs /usr/local/lib64/ltfs.rpmnew
    mv /usr/local/lib64/ltfs.rpmsave /usr/local/lib64/ltfs
fi

%postun
/sbin/ldconfig

%clean
[ -d $RPM_BUILD_ROOT ] && rm -rf $RPM_BUILD_ROOT;

%files
%config %attr(0644, root, root) %{_sysconfdir}/logrotate.d/ltfslog
%config %attr(0644, root, root) %{_sysconfdir}/ltfs.conf
%config %attr(0644, root, root) %{_sysconfdir}/ltfs.conf.local
%config %attr(0644, root, root) %{_sysconfdir}/rsyslog.d/ltfs-log.conf
%config %attr(0644, root, root) %{_sysconfdir}/systemd/system/ltfs.service
%attr(0755, root, root) %{_prefix}/bin/ltfs-singledrive
%attr(0755, root, root) %{_prefix}/bin/ltfsck
%attr(0755, root, root) %{_prefix}/bin/mkltfs
%attr(0644, root, root) %{_libdir}/libltfs.a
%attr(0755, root, root) %{_libdir}/libltfs.la
%{_libdir}/libltfs.so
%{_libdir}/libltfs.so.0
%attr(0755, root, root) %{_libdir}/libltfs.so.0.0.0
%attr(0755, root, root) %{_libdir}/ltfs/libiosched-fcfs.so
%attr(0755, root, root) %{_libdir}/ltfs/libiosched-unified.so
%attr(0755, root, root) %{_libdir}/ltfs/libkmi-flatfile.so
%attr(0755, root, root) %{_libdir}/ltfs/libkmi-simple.so
%attr(0755, root, root) %{_libdir}/ltfs/libtape-file.so
%attr(0755, root, root) %{_libdir}/ltfs/libtape-itdtimg.so
%attr(0755, root, root) %{_libdir}/ltfs/libtape-sg-ibmtape.so
%attr(0644, root, root) %{_libdir}/pkgconfig/ltfs.pc
%dir %attr(0755, root, root) %{_includedir}/ltfs
%attr(0644, root, root) %{_includedir}/ltfs/config.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/arch/arch_info.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/arch/signal_internal.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/arch/time_internal.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/dcache_ops.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/iosched_ops.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/kmi_ops.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/ltfs.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/ltfs_error.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/ltfs_fsops.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/ltfs_locking.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/ltfs_thread.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/ltfs_types.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/ltfslogging.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/ltfstrace.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/plugin.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/queue.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/tape.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/tape_ops.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/uthash.h
%attr(0644, root, root) %{_includedir}/ltfs/libltfs/uthash_ext.h
%docdir %{_defaultdocdir}/%{name}-%{version}
%dir %attr(0755, root, root) %{_defaultdocdir}
%dir %attr(0755, root, root) %{_defaultdocdir}/%{name}-%{version}
%doc %attr(0644, root, root) %{_defaultdocdir}/%{name}-%{version}/INSTALL
%doc %attr(0644, root, root) %{_defaultdocdir}/%{name}-%{version}/LICENSE
%doc %attr(0644, root, root) %{_defaultdocdir}/%{name}-%{version}/NOTICES
%doc %attr(0644, root, root) %{_defaultdocdir}/%{name}-%{version}/README
%doc %attr(0644, root, root) %{_defaultdocdir}/%{name}-%{version}/ltfs-log.conf
%doc %attr(0644, root, root) %{_defaultdocdir}/%{name}-%{version}/ltfs.conf.example
%doc %attr(0644, root, root) %{_defaultdocdir}/%{name}-%{version}/ltfs.conf.local.example
%dir %attr(0755, root, root) %{_datarootdir}/ltfs
%attr(0755, root, root) %{_datarootdir}/ltfs/ltfs
%dir %attr(0755, root, root) %{_mandir}
%dir %attr(0755, root, root) %{_mandir}/man8
%doc %attr(0644, root, root) %{_mandir}/man8/ltfs-sde.8.gz
%doc %attr(0644, root, root) %{_mandir}/man8/ltfsck.8.gz
%doc %attr(0644, root, root) %{_mandir}/man8/mkltfs.8.gz
%dir %attr(0755, root, root) %{_ulocal}/bin
%{_ulocal}/bin/ltfs
%{_ulocal}/bin/ltfsck
%{_ulocal}/bin/mkltfs
%dir %attr(0755, root, root) %{_ulocal}/lib64
%{_ulocal}/lib64/libltfs.a
%{_ulocal}/lib64/libltfs.la
%{_ulocal}/lib64/libltfs.so
%{_ulocal}/lib64/libltfs.so.0
%{_ulocal}/lib64/libltfs.so.0.0.0
%{_ulocal}/lib64/ltfs
%dir %attr(0755, root, root) %{_ulocal}/share
%dir %attr(0755, root, root) %{_ulocal}/share/doc
%{_ulocal}/share/doc/qtmltfs-%{version}

