%{?scl:%scl_package jackson-jaxrs-providers}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

%global baserelease 2

Name:          %{?scl_prefix}jackson-jaxrs-providers
Version:       2.6.3
Release:       2.%{baserelease}%{?dist}
Summary:       Jackson JAX-RS providers
License:       ASL 2.0
URL:           http://wiki.fasterxml.com/JacksonHome
Source0:       https://github.com/FasterXML/jackson-jaxrs-providers/archive/%{pkg_name}-%{version}.tar.gz

BuildRequires: %{?scl_prefix_maven}maven-local
BuildRequires: %{?scl_prefix}mvn(com.fasterxml.jackson:jackson-parent:pom:)
BuildRequires: %{?scl_prefix}mvn(com.fasterxml.jackson.core:jackson-core)
BuildRequires: %{?scl_prefix}mvn(com.fasterxml.jackson.core:jackson-databind)
BuildRequires: %{?scl_prefix}mvn(com.fasterxml.jackson.module:jackson-module-jaxb-annotations)
BuildRequires: %{?scl_prefix_maven}mvn(org.apache.maven.plugins:maven-antrun-plugin)
BuildRequires: %{?scl_prefix}mvn(javax.ws.rs:javax.ws.rs-api)
BuildRequires: %{?scl_prefix_java_common}mvn(junit:junit)
BuildRequires: %{?scl_prefix_maven}mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires: %{?scl_prefix_maven}mvn(org.apache.maven.plugins:maven-enforcer-plugin)
BuildRequires: %{?scl_prefix_maven}mvn(org.apache.maven.plugins:maven-site-plugin)
BuildRequires: %{?scl_prefix_maven}mvn(org.apache.maven.plugins:maven-source-plugin)
BuildRequires: %{?scl_prefix_maven}mvn(org.codehaus.mojo:build-helper-maven-plugin)
BuildRequires: %{?scl_prefix_maven}mvn(org.codehaus.woodstox:stax2-api)
BuildRequires: %{?scl_prefix_maven}mvn(org.codehaus.woodstox:woodstox-core-asl)
BuildRequires: %{?scl_prefix_java_common}mvn(org.eclipse.jetty:jetty-server)
BuildRequires: %{?scl_prefix_java_common}mvn(org.eclipse.jetty:jetty-servlet)

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
set -e -x
%setup -q -n %{pkg_name}-%{pkg_name}-%{version}

cp -p xml/src/main/resources/META-INF/LICENSE .
cp -p xml/src/main/resources/META-INF/NOTICE .
sed -i 's/\r//' LICENSE NOTICE

%pom_xpath_set "pom:properties/pom:version.jersey" 1

# Disable jar with no-meta-inf-services classifier, breaks build
%pom_remove_plugin :maven-jar-plugin cbor
%pom_remove_plugin :maven-jar-plugin json
%pom_remove_plugin :maven-jar-plugin smile
%pom_remove_plugin :maven-jar-plugin xml
%pom_remove_plugin :maven-jar-plugin yaml

# Circular dep?
%pom_remove_dep org.jboss.resteasy:resteasy-jackson2-provider json
rm json/src/test/java/com/fasterxml/jackson/jaxrs/json/resteasy/RestEasyProviderLoadingTest.java

%mvn_package ":jackson-jaxrs-providers" %{pkg_name}
%mvn_package ":jackson-jaxrs-base" %{pkg_name}

# Dep is unavailable
%pom_xpath_remove "pom:dependency[pom:groupId='com.sun.jersey']"

# Use glassfish API
%pom_change_dep javax.ws.rs:jsr311-api javax.ws.rs:javax.ws.rs-api

# Disable unneeded providers
%pom_disable_module cbor
%pom_disable_module smile
%pom_disable_module xml
%pom_disable_module yaml

%pom_remove_plugin com.google.code.maven-replacer-plugin:replacer json
%pom_add_plugin org.apache.maven.plugins:maven-antrun-plugin json \
  "<executions><execution><id>process-packageVersion</id><phase>generate-sources</phase></execution></executions>"
%{?scl:EOF}


%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x

%mvn_build -s -f
%{?scl:EOF}


%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%mvn_install
%{?scl:EOF}


%files -f .mfiles-%{pkg_name}
%doc README.md release-notes/*
%doc LICENSE NOTICE

%files -n %{?scl_prefix}jackson-jaxrs-json-provider -f .mfiles-jackson-jaxrs-json-provider
%doc LICENSE NOTICE

%files javadoc -f .mfiles-javadoc
%doc LICENSE NOTICE

%changelog
* Tue Jul 26 2016 Mat Booth <mat.booth@redhat.com> - 2.6.3-2.2
- Remove all unneeded providers, we only need json
- Switch to Glassfish javax.ws.rs API
- Remove deps on unavailable jersey 1.x libs and skip tests

* Tue Jul 26 2016 Mat Booth <mat.booth@redhat.com> - 2.6.3-2.1
- Auto SCL-ise package for rh-eclipse46 collection

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sun Oct 25 2015 gil cattaneo <puntogil@libero.it> 2.6.3-1
- update to 2.6.3

* Mon Sep 28 2015 gil cattaneo <puntogil@libero.it> 2.6.2-1
- update to 2.6.2

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
