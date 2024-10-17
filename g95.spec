%define	name			g95
%define binutils_version	2.16.91.0.2-2mdk
%define	gcc_version		4.0.4
%define gcc_major		4.0.4
%define g95_snapshot		20070301
%define snapshot		404_%{g95_snapshot}
%define	program_suffix		%{nil}
%define	program_suffix		%{nil}
%define arch			%(echo %{_target_cpu}|sed -e "s/i.86/i386/" -e "s/athlon/i386/" -e "s/amd64/x86_64/")
%define gcc_libdir		%{_prefix}/lib/g95
%define gcc_target_platform	%{_target_platform}
%define target_prefix		%{_prefix}
%define target_libdir		%{_libdir}
%define target_slibdir		/%{_lib}
%define	rel			%mkrel 4

# Use system gcc compiler?
%define use_syscomp		0
%{?_with_systemcompiler: %global use_syscomp 1}
%{?_without_systemcompiler: %global use_syscomp 0}

Summary:	Another Fortran 95 Compiler
Name:		%{name}
Version:	0.91
Release:	1.%{snapshot}.%{rel}
License:	GPL
Group:		Development/Other
Url:		https://www.g95.org
Source0:	http://www.g95.org/g95_source.tar.bz2
Source1:	gcc-%{gcc_version}.tar.bz2
Patch0:		g95-buildroot.patch
Patch1:		g95-f951-coexist.patch
Patch2:		g95-gcclibdir.patch
Patch3:		g95-g95libdir.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-root
BuildRequires:	binutils >= %{binutils_version}
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	gawk >= 3.1.4
BuildRequires:	gettext
BuildRequires:	libgmp-devel
BuildRequires:	texinfo >= 4.1
BuildRequires:	zlib-devel
Requires: gcc

%define _provides_exceptions libgcc_s.so.1

%description
This package adds support for compiling Fortran 95 programs with g95,
a compiler alternative to the official GNU compiler called gfortran.
For further differences between g95 and gfortran see
http://gcc.gnu.org/wiki/TheOtherGCCBasedFortranCompiler.

%prep
%setup -q -c -n %{name} -a 1
pwd
ln -s gcc-%{gcc_version} gcc
ln -s gcc gcc-4_0-branch
tar -zxvf g95-%{version}/libf95.a-%{version}.tar.gz -C g95-%{version}/
ln -s g95-%{version}/libf95.a-%{version} libf95.a-%{version}
%patch0 -p1 -b .buildroot
%if %use_syscomp
%patch1 -p1 -b .coexist
%patch2 -p1 -b .gcclibdir
%else
%patch3 -p1 -b .g95libdir
%endif

%build
OPT_FLAGS=`echo $RPM_OPT_FLAGS|sed -e 's/-fno-rtti//g' -e 's/-fno-exceptions//g' -e 's/-mcpu=pentiumpro//g'`
PROGRAM_SUFFIX="--program-suffix=%{program_suffix}"

(cd gcc
 mkdir g95
 cd g95
 %{?__cputoolize: %{__cputoolize} -c ..}
 CC="%{__cc}" \
 CFLAGS="$OPT_FLAGS" \
 CXXFLAGS="$OPT_FLAGS" \
 XCFLAGS="$OPT_FLAGS" \
 TCFLAGS="$OPT_FLAGS" \
 `pwd`/../configure \
	--enable-languages=c \
	--prefix=%{_prefix} \
	--libexecdir=%{_prefix}/lib \
	--with-slibdir=%{target_slibdir} \
	--mandir=%{_mandir} \
	--infodir=%{_infodir} \
	--enable-threads=posix \
	--disable-checking \
	$PROGRAM_SUFFIX \
	--host=%{_target_platform} \
	--with-system-zlib
 %make
)	

(cd g95-%{version}
 %{?__cputoolize: %{__cputoolize} -c ..}
 ./autogen.sh
 CC="%{__cc}" \
 CFLAGS="$OPT_FLAGS" \
 CXXFLAGS="$OPT_FLAGS" \
 XCFLAGS="$OPT_FLAGS" \
 TCFLAGS="$OPT_FLAGS" \
 ./configure \
	--prefix=%{_prefix} \
	--libexecdir=%{_prefix}/lib \
	--with-slibdir=%{target_slibdir} \
	--mandir=%{_mandir} \
	--infodir=%{_infodir} \
	--with-gcc-dir=`pwd`/../gcc \
	$PROGRAM_SUFFIX \
	--host=%{_target_platform} \
	--with-system-zlib
 %make
)

(cd g95-%{version}/libf95.a-%{version}
 perl -pi -e 's@\$prefix/lib/gcc-lib/\$host/\$gcc_version@%{gcc_libdir}/\$host/%{gcc_major}@g' configure.in configure
 CC="%{__cc}" \
 CFLAGS="$OPT_FLAGS" \
 CXXFLAGS="$OPT_FLAGS" \
 XCFLAGS="$OPT_FLAGS" \
 TCFLAGS="$OPT_FLAGS" \
 ./configure \
	--prefix=%{_prefix} \
	--libexecdir=%{_prefix}/lib \
	--with-slibdir=%{target_slibdir} \
	--mandir=%{_mandir} \
	--infodir=%{_infodir} \
	--with-gcc-dir=`pwd`/../../gcc \
	$PROGRAM_SUFFIX \
	--host=%{_target_platform} \
	--with-system-zlib
 make
)


%install
rm -rf %{buildroot}
mkdir -p %{buildroot}

(cd g95-%{version}
%makeinstall_std)

(cd g95-%{version}/libf95.a-%{version}
%makeinstall_std)

rm -f %{buildroot}%{_prefix}/G95Manual.pdf %{buildroot}%{_prefix}/INSTALL

%if %use_syscomp
# Fix path of libf95.a to the same one of gcc
mv %{buildroot}%{_prefix}/lib/gcc-lib/%{_target_platform}/%{gcc_major}/libf95.a \
	%{buildroot}%{gcc_libdir}/%{gcc_target_platform}/%{gcc_version}/libf95.a
rm -rf %{buildroot}%{_prefix}/lib/gcc-lib

# remove files which are already provided by gcc
(cd %{buildroot}%{gcc_libdir}/%{gcc_target_platform}/%{gcc_version}
 rm -f cc1 crtbegin.o crtbeginS.o crtbeginT.o crtend.o crtendS.o \
 libgcc.a libgcc_s.so libgcc_s.so.1)
%endif
ln -sf %{_bindir}/%{_target_platform}-g95 %{buildroot}%{_bindir}/g95

%clean
rm -rf %{buildroot}%

%files
%defattr(-,root,root)
%doc g95-%{version}/G95Manual.pdf g95-%{version}/COPYING
%doc g95-%{version}/AUTHORS g95-%{version}/BUGS g95-%{version}/INSTALL
%doc g95-%{version}/README
%{_bindir}/*
%{gcc_libdir}/%{gcc_target_platform}/%{gcc_major}/libf95.a
%if %use_syscomp
%{gcc_libdir}/%{gcc_target_platform}/%{gcc_major}/g951
%else
%{gcc_libdir}/%{gcc_target_platform}/%{gcc_major}/f951
%{gcc_libdir}/%{gcc_target_platform}/%{gcc_major}/cc1
%{gcc_libdir}/%{gcc_target_platform}/%{gcc_major}/crtbegin.o
%{gcc_libdir}/%{gcc_target_platform}/%{gcc_major}/crtbeginS.o
%{gcc_libdir}/%{gcc_target_platform}/%{gcc_major}/crtbeginT.o
%{gcc_libdir}/%{gcc_target_platform}/%{gcc_major}/crtend.o
%{gcc_libdir}/%{gcc_target_platform}/%{gcc_major}/crtendS.o
%{gcc_libdir}/%{gcc_target_platform}/%{gcc_major}/libgcc.a
%{gcc_libdir}/%{gcc_target_platform}/%{gcc_major}/libgcc_s.so
%{gcc_libdir}/%{gcc_target_platform}/%{gcc_major}/libgcc_s.so.1
%{gcc_libdir}/%{gcc_target_platform}/%{gcc_major}/libgcc_eh.a
%endif


