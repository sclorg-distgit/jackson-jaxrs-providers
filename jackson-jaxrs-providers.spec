%global pkg_name jackson-jaxrs-providers
%{?scl:%scl_package %{pkg_name}}
%{?java_common_find_provides_and_requires}
Name:          %{?scl_prefix}jackson-jaxrs-providers
Version:       2.5.0
Release:       2.3%{?dist}
Summary:       Jackson JAX-RS providers
License:       ASL 2.0
URL:           http://wiki.fasterxml.com/JacksonHome
Source0:       https://github.com/FasterXML/jackson-jaxrs-providers/archive/%{pkg_name}-%{version}.tar.gz


BuildRequires: %{?scl_prefix}mvn(com.fasterxml.jackson.core:jackson-core)
BuildRequires: %{?scl_prefix}mvn(com.fasterxml.jackson.core:jackson-databind)
BuildRequires: %{?scl_prefix}mvn(com.fasterxml.jackson.module:jackson-module-jaxb-annotations)
BuildRequires: %{?scl_prefix}mvn(javax.ws.rs:javax.ws.rs-api)

#BuildRequires: mvn(org.jboss.resteasy:resteasy-jackson2-provider)

BuildRequires: %{?scl_prefix_java_common}maven-local
BuildRequires: %{?scl_prefix_maven}maven-enforcer-plugin
BuildRequires: %{?scl_prefix_maven}maven-plugin-build-helper
BuildRequires: %{?scl_prefix_maven}maven-plugin-bundle
BuildRequires: %{?scl_prefix_maven}maven-site-plugin
BuildRequires: %{?scl_prefix_maven}maven-source-plugin
BuildRequires: %{?scl_prefix_maven}maven-surefire-provider-junit

BuildArch:     noarch

%description
This is a multi-module project that contains Jackson-based JAX-RS providers for
following data formats:

* JSON (https://github.com/FasterXML/jackson-core)

%package -n %{?scl_prefix}jackson-jaxrs-json-provider
Summary:       Jackson-JAXRS-JSON

%description -n %{?scl_prefix}jackson-jaxrs-json-provider
Functionality to handle JSON input/output for JAX-RS implementations
(like Jersey and RESTeasy) using standard Jackson data binding.

%package javadoc
Summary:       Javadoc for %{pkg_name}

%description javadoc
This package contains javadoc for %{pkg_name}.

%prep

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%setup -q -n %{pkg_name}-%{pkg_name}-%{version}

cp -p xml/src/main/resources/META-INF/LICENSE .
cp -p xml/src/main/resources/META-INF/NOTICE .
sed -i 's/\r//' LICENSE NOTICE

%pom_disable_module cbor
%pom_disable_module smile
%pom_disable_module xml

%pom_xpath_set "pom:properties/pom:version.jersey" 1.19

# Circular dep?
%pom_remove_dep org.jboss.resteasy:resteasy-jackson2-provider json
rm json/src/test/java/com/fasterxml/jackson/jaxrs/json/resteasy/RestEasyProviderLoadingTest.java

%mvn_package ":jackson-jaxrs-providers" %{pkg_name}
%mvn_package ":jackson-jaxrs-base" %{pkg_name}

%pom_remove_parent
%pom_xpath_remove "pom:dependency[pom:scope='test']"
%pom_remove_dep "javax.ws.rs:jsr311-api"
%pom_add_dep "javax.ws.rs:javax.ws.rs-api"

%pom_xpath_inject "pom:project" '
    <build>
      <plugins>
        <plugin>
          <groupId>org.apache.felix</groupId>
          <artifactId>maven-bundle-plugin</artifactId>
          <extensions>true</extensions>
          <version>1.0.0</version>
          <configuration>
            <instructions>
              <_nouses>true</_nouses>
              <_removeheaders>Include-Resource,JAVA_1_3_HOME,JAVA_1_4_HOME,JAVA_1_5_HOME,JAVA_1_6_HOME,JAVA_1_7_HOME</_removeheaders>
              <_versionpolicy>${osgi.versionpolicy}</_versionpolicy>
              <Bundle-Name>${project.name}</Bundle-Name>
              <Bundle-SymbolicName>${project.groupId}.${project.artifactId}</Bundle-SymbolicName>
              <Bundle-Description>${project.description}</Bundle-Description>
              <Export-Package>${osgi.export}</Export-Package>
              <Private-Package>${osgi.private}</Private-Package>
              <Import-Package>${osgi.import}</Import-Package>
              <DynamicImport-Package>${osgi.dynamicImport}</DynamicImport-Package>
              <Bundle-DocURL>${project.url}</Bundle-DocURL>
              <Bundle-RequiredExecutionEnvironment>${osgi.requiredExecutionEnvironment}</Bundle-RequiredExecutionEnvironment>

              <Implementation-Build-Date>${maven.build.timestamp}</Implementation-Build-Date>
              <X-Compile-Source-JDK>${javac.src.version}</X-Compile-Source-JDK>
              <X-Compile-Target-JDK>${javac.target.version}</X-Compile-Target-JDK>

              <Implementation-Title>${project.name}</Implementation-Title>
              <Implementation-Version>${project.version}</Implementation-Version>
              <Implementation-Vendor-Id>${project.groupId}</Implementation-Vendor-Id>
              <Implementation-Vendor>${project.organization.name}</Implementation-Vendor>

              <Specification-Title>${project.name}</Specification-Title>
              <Specification-Version>${project.version}</Specification-Version>
              <Specification-Vendor>${project.organization.name}</Specification-Vendor>
            </instructions>
          </configuration>
        </plugin>
      </plugins>
    </build>'

%pom_xpath_inject "pom:properties" '
<osgi.versionpolicy>${range;[===,=+);${@}}</osgi.versionpolicy>'

file=`find json -name PackageVersion.java.in`
gid=`grep "<groupId>" pom.xml | head -1 | sed 's/.*>\(.*\)<.*/\1/'`
aid=`grep "<artifactId>" pom.xml | head -1 | sed 's/.*>\(.*\)<.*/\1/'`
v=`grep "<version>" pom.xml | head -1 | sed 's/.*>\(.*\)<.*/\1/'`
pkg=`echo ${file} | cut -d/ -f5- | rev | cut -d/ -f2- | rev | tr '/' '\.'`

sed -i "s/@projectversion@/${v}/
        s/@projectgroupid@/${gid}/
        s/@package@/${pkg}/
        s/@projectartifactid@/${aid}/" ${file}

cp ${file} ${file%.in}


%{?scl:EOF}

%build

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}

%mvn_build -s -- -Dmaven.test.skip=true

%{?scl:EOF}

%install

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_install

%{?scl:EOF}

%files -f .mfiles-%{pkg_name}
%doc README.md release-notes/* LICENSE NOTICE

%files -n %{?scl_prefix}jackson-jaxrs-json-provider -f .mfiles-jackson-jaxrs-json-provider
%doc LICENSE NOTICE

%files javadoc -f .mfiles-javadoc
%doc LICENSE NOTICE

%changelog
* Thu Jul 30 2015 Roland Grunberg <rgrunber@redhat.com> - 2.5.0-2.3
- Add missing osgi.versionpolicy property.

* Tue Jul 28 2015 Alexander Kurtakov <akurtako@redhat.com> 2.5.0-2.2
- Drop provides/obsoletes outside of dts namespace.

* Thu Jul 02 2015 Roland Grunberg <rgrunber@redhat.com> - 2.5.0-2.1
- SCL-ize.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Jan 31 2015 gil cattaneo <puntogil@libero.it> 2.5.0-1
- update to 2.5.0

* Sat Sep 20 2014 gil cattaneo <puntogil@libero.it> 2.4.2-1
- update to 2.4.2

* Wed Jul 09 2014 gil cattaneo <puntogil@libero.it> 2.4.1-2
- enable jackson-jaxrs-cbor-provider

* Fri Jul 04 2014 gil cattaneo <puntogil@libero.it> 2.4.1-1
- update to 2.4.1

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Mar 28 2014 Michael Simacek <msimacek@redhat.com> - 2.2.2-2
- Use Requires: java-headless rebuild (#1067528)

* Wed Jul 17 2013 gil cattaneo <puntogil@libero.it> 2.2.2-1
- update to 2.2.2
- renamed jackson-jaxrs-providers

* Tue Jul 16 2013 gil cattaneo <puntogil@libero.it> 2.1.5-1
- update to 2.1.5

* Wed Oct 24 2012 gil cattaneo <puntogil@libero.it> 2.1.0-1
- update to 2.1.0
- renamed jackson2-jaxrs-json-provider

* Thu Sep 13 2012 gil cattaneo <puntogil@libero.it> 2.0.5-1
- initial rpm
