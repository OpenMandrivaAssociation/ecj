%define qualifier 200902111700

%define debug_package	%nil

%bcond_with gcjbootstrap

Summary: Eclipse Compiler for Java
Name: ecj
Version: 3.4.2
Release: 3
URL: http://www.eclipse.org
License: EPL
Group: Development/Java
Source0: http://download.eclipse.org/eclipse/downloads/drops/R-%{version}-%{qualifier}/%{name}src-%{version}.zip
Source1: ecj.sh.in
# Use ECJ for GCJ
# cvs -d:pserver:anonymous@sourceware.org:/cvs/rhug \
# export -r eclipse_r34_1 eclipse-gcj
# tar cjf ecj-gcj.tar.bz2 eclipse-gcj
Source2: %{name}-gcj.tar.bz2
Source3: http://repo2.maven.org/maven2/org/eclipse/jdt/core/3.3.0-v_771/core-3.3.0-v_771.pom
# Always generate debug info when building RPMs (Andrew Haley)
Patch0: %{name}-rpmdebuginfo.patch
Patch1: %{name}-defaultto1.5.patch
Patch2: %{name}-generatedebuginfo.patch

BuildRequires: gcc-java >= 4.0.0
BuildRequires: java-1.5.0-gcj-devel

%if ! %{with gcjbootstrap}
BuildRequires: ant
%endif

Requires: libgcj >= 4.0.0
Requires(post): gcc-java
Requires(postun): gcc-java

Provides: eclipse-ecj = 1:%{version}-%{release}

%description
ECJ is the Java bytecode compiler of the Eclipse Platform.  It is also known as
the JDT Core batch compiler.

%prep
%setup -q -c
%patch0 -p1
%patch1 -p1
%patch2 -p1

cp %{SOURCE3} pom.xml
# Use ECJ for GCJ's bytecode compiler
tar jxf %{SOURCE2}
mv eclipse-gcj/org/eclipse/jdt/internal/compiler/batch/GCCMain.java \
  org/eclipse/jdt/internal/compiler/batch/
cat eclipse-gcj/gcc.properties >> \
  org/eclipse/jdt/internal/compiler/batch/messages.properties
rm -rf eclipse-gcj

# Remove bits of JDT Core we don't want to build
rm -r org/eclipse/jdt/internal/compiler/tool
rm -r org/eclipse/jdt/internal/compiler/apt

# JDTCompilerAdapter isn't used by the batch compiler
rm -f org/eclipse/jdt/core/JDTCompilerAdapter.java

%build
%if %{with gcjbootstrap}
  for f in `find -name '*.java' | cut -c 3- | LC_ALL=C sort`; do
    gcj -Wno-deprecated -C $f
  done

  find -name '*.class' -or -name '*.properties' -or -name '*.rsc' |\
    xargs fastjar cf %{name}-%{version}.jar
%else
   ant
%endif

%install
mkdir -p %{buildroot}%{_javadir}
cp -a *.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
pushd %{buildroot}%{_javadir}
ln -s %{name}-%{version}.jar %{name}.jar
ln -s %{name}-%{version}.jar eclipse-%{name}-%{version}.jar
ln -s eclipse-%{name}-%{version}.jar eclipse-%{name}.jar
ln -s %{name}-%{version}.jar jdtcore.jar
popd

# Install the ecj wrapper script
install -p -D -m0755 %{SOURCE1} %{buildroot}%{_bindir}/ecj
sed --in-place "s:@JAVADIR@:%{_javadir}:" %{buildroot}%{_bindir}/ecj

%if %{with gcjbootstrap}
aot-compile-rpm
%endif

# poms
install -d -m 755 %{buildroot}%{_datadir}/maven2/poms
install -pm 644 pom.xml \
    %{buildroot}%{_datadir}/maven2/poms/JPP-%{name}.pom

%add_to_maven_depmap org.eclipse.jdt core %{version} JPP %{name}

%post
%if %{with gcjbootstrap}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif
%update_maven_depmap

%if %{with gcjbootstrap}
%postun
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif
%update_maven_depmap

%files
%doc about.html
%{_datadir}/maven2/poms/JPP-%{name}.pom
%{_mavendepmapfragdir}/%{name}
%{_bindir}/%{name}
%{_javadir}/%{name}*.jar
%{_javadir}/eclipse-%{name}*.jar
%{_javadir}/jdtcore.jar
%if %{with gcjbootstrap}
%{_libdir}/gcj/%{name}
%endif

%changelog
* Sun May 22 2011 Paulo Andrade <pcpa@mandriva.com.br> 3.4.2-1
+ Revision: 676968
- Import fedora ecj 3.4.2 package
- Import ecj

