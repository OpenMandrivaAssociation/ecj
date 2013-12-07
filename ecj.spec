%define debug_package	%nil
%define qualifier 200902111700
%bcond_with gcjbootstrap

Summary:	Eclipse Compiler for Java
Name:		ecj
Version:	4.3
# Sad, but eclipse-ecj Obsoletes: ecj < 2:3.4.2-0.2.7
Epoch:		2
Release:	5
Url:		http://www.eclipse.org
License:	EPL
Group:		Development/Java
Source0:	ftp://ftp.halifax.rwth-aachen.de/eclipse/eclipse/downloads/drops4/R-4.3-201306052000/ecjsrc-%{version}.jar
Source1:	ecj.sh.in
# Use ECJ for GCJ
# cvs -d:pserver:anonymous@sourceware.org:/cvs/rhug \
# export -r eclipse_r34_1 eclipse-gcj
# tar cjf ecj-gcj.tar.bz2 eclipse-gcj
Source2:	%{name}-gcj.tar.bz2
Source3:	http://repo2.maven.org/maven2/org/eclipse/jdt/core/3.3.0-v_771/core-3.3.0-v_771.pom
# Always generate debug info when building RPMs (Andrew Haley)
Patch0:		%{name}-rpmdebuginfo.patch
Patch1:		%{name}-defaultto1.5.patch
Patch2:		%{name}-generatedebuginfo.patch
Patch3:		ecj-4.2.1-compile.patch
Patch4:		ecj-4.2.2-java7.patch
Patch5:		ecj-4.3-compile.patch
BuildArch:	noarch

%if %{without gcjbootstrap}
BuildRequires:	ant
BuildRequires:	java-1.7.0-openjdk-devel
%else
BuildRequires:	gcc-java >= 4.0.0
%endif

Requires:	java-sdk
Obsoletes:	eclipse-ecj < 1:%{version}-%{release}
Provides:	eclipse-ecj = 1:%{version}-%{release}

%description
ECJ is the Java bytecode compiler of the Eclipse Platform.  It is also known as
the JDT Core batch compiler.

%prep
%setup -q -c
# Use ECJ for GCJ's bytecode compiler
tar jxf %{SOURCE2}
mv eclipse-gcj/org/eclipse/jdt/internal/compiler/batch/GCCMain.java \
  org/eclipse/jdt/internal/compiler/batch/
cat eclipse-gcj/gcc.properties >> \
  org/eclipse/jdt/internal/compiler/batch/messages.properties
rm -rf eclipse-gcj

%apply_patches

cp %{SOURCE3} pom.xml

# We could remove the parts below as they aren't required for ecj core
# functionality -- but e.g. forcing ant to use ecj over javac requires
# the JDTCompilerAdapter, so let's not save space at the cost of losing
# functionality...

# Remove bits of JDT Core we don't want to build
#rm -r org/eclipse/jdt/internal/compiler/tool
#rm -r org/eclipse/jdt/internal/compiler/apt

# JDTCompilerAdapter isn't used by the batch compiler
#rm -f org/eclipse/jdt/core/JDTCompilerAdapter.java

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

# poms
install -d -m 755 %{buildroot}%{_datadir}/maven2/poms
install -pm 644 pom.xml \
    %{buildroot}%{_datadir}/maven2/poms/JPP-%{name}.pom

%add_to_maven_depmap org.eclipse.jdt core %{version} JPP %{name}

%post
%update_maven_depmap

%postun
%update_maven_depmap

%files
%doc about.html
%{_datadir}/maven2/poms/JPP-%{name}.pom
%{_mavendepmapfragdir}/%{name}
%{_bindir}/%{name}
%{_javadir}/%{name}*.jar
%{_javadir}/eclipse-%{name}*.jar
%{_javadir}/jdtcore.jar

