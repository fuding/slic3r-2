Summary:	G-code generator for 3D printers (RepRap, Makerbot, Ultimaker etc.)
Name:		slic3r
Version:	1.2.6
Release:	0.1
License:	AGPLv3 and CC-BY
# Images are CC-BY, code is AGPLv3
Group:		Applications/Engineering
URL:		http://slic3r.org/
Source0:	https://github.com/alexrj/Slic3r/archive/%{version}.tar.gz
# Source0-md5:	85c27cdc16c7efabfd6a34755b7881c9
Source1:        %{name}.desktop
Source2:        %{name}.appdata.xml
# Modify Build.PL so we are able to build this on Fedora
Patch0:		%{name}-buildpl.patch
# Don't warn for Perl >= 5.16
# Use /usr/share/slic3r as datadir
# Those two are located at the same place at the code, so the patch is merged
Patch1:		%{name}-nowarn-datadir.patch
Patch2:		%{name}-english-locale.patch
Patch3:		%{name}-linker.patch
Patch4:		%{name}-clear-error.patch
Patch5:		%{name}-test-out-of-memory.patch
Patch6:		%{name}-clipper.patch
BuildRequires:	perl(Class::XSAccessor)
BuildRequires:	perl(Encode::Locale)
BuildRequires:	perl(ExtUtils::MakeMaker) >= 6.80
BuildRequires:	perl(ExtUtils::ParseXS) >= 3.22
BuildRequires:	perl(ExtUtils::Typemap)
BuildRequires:	perl(ExtUtils::Typemaps::Default) >= 1.05
BuildRequires:	perl(File::Basename)
BuildRequires:	perl(File::Spec)
BuildRequires:	perl(Getopt::Long)
BuildRequires:	perl(Growl::GNTP) >= 0.15
BuildRequires:	perl(IO::Scalar)
BuildRequires:	perl(List::Util)
BuildRequires:	perl(Math::ConvexHull) >= 1.0.4
BuildRequires:	perl(Math::ConvexHull::MonotoneChain)
BuildRequires:	perl(Math::Geometry::Voronoi) >= 1.3
BuildRequires:	perl(Math::PlanePath) >= 53
BuildRequires:	perl(Module::Build::WithXSpp) >= 0.14
BuildRequires:	perl(Moo) >= 1.003001
BuildRequires:	perl(SVG)
BuildRequires:	perl(Scalar::Util)
BuildRequires:	perl(Storable)
BuildRequires:	perl(Test::Harness)
BuildRequires:	perl(Test::More)
BuildRequires:	perl(Time::HiRes)
BuildRequires:	perl(Wx)
BuildRequires:	perl(XML::SAX)
BuildRequires:	perl(XML::SAX::ExpatXS)
BuildRequires:	perl(parent)

BuildRequires:	ImageMagick
BuildRequires:	admesh-devel >= 0.98.1
BuildRequires:	boost-devel
BuildRequires:	desktop-file-utils
BuildRequires:	poly2tri-devel
BuildRequires:	polyclipping-devel >= 6.2.0

Requires:	admesh-libs >= 0.97.5
Requires:	perl(:MODULE_COMPAT_%(eval "`perl -V:version`"; echo $version))
Requires:	perl(XML::SAX)

%description
Slic3r is a G-code generator for 3D printers. It's compatible with
RepRaps, Makerbots, Ultimakers and many more machines. See the project
homepage at slic3r.org and the documentation on the Slic3r wiki for
more information.

%prep
%setup -qn Slic3r-%{version}

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
#%patch4 -p1
#%patch5 -p1
%patch6 -p1

# Remove bundled admesh, clipper, poly2tri and boost
rm -rf xs/src/admesh
rm xs/src/clipper.*pp
rm -rf xs/src/poly2tri
rm -rf xs/src/boost

%build
cd xs
perl ./Build.PL installdirs=vendor optimize="$RPM_OPT_FLAGS"
./Build
cd -
# Building non XS part only runs test, so skip it and run it in tests

# prepare pngs in mutliple sizes
for res in 16 32 48 128 256; do
  mkdir -p hicolor/${res}x${res}/apps
done
cd hicolor
convert ../var/Slic3r.ico %{name}.png
cp %{name}-0.png 256x256/apps/%{name}.png
cp %{name}-1.png 128x128/apps/%{name}.png
cp %{name}-2.png 48x48/apps/%{name}.png
cp %{name}-3.png 32x32/apps/%{name}.png
cp %{name}-4.png 16x16/apps/%{name}.png
rm %{name}-*.png
cd -

# To avoid "iCCP: Not recognized known sRGB profile that has been edited"
cd var
find . -type f -name "*.png" -exec convert {} -strip {} \;
cd -

%install
rm -rf $RPM_BUILD_ROOT
cd xs
./Build install destdir=$RPM_BUILD_ROOT create_packlist=0
cd -
find $RPM_BUILD_ROOT -type f -name '*.bs' -size 0 -exec rm -f {} \;

# I see no way of installing slic3r with it's build script
# So I copy the files around manually
install -d $RPM_BUILD_ROOT%{_bindir}
install -d $RPM_BUILD_ROOT%{perl_vendorlib}
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}
install -d $RPM_BUILD_ROOT%{_datadir}/icons
install -d $RPM_BUILD_ROOT%{_datadir}/appdata

cp -a %{name}.pl $RPM_BUILD_ROOT%{_bindir}/%{name}
cp -a lib/* $RPM_BUILD_ROOT%{perl_vendorlib}

cp -a var/* $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -r hicolor $RPM_BUILD_ROOT%{_datadir}/icons
desktop-file-install --dir=$RPM_BUILD_ROOT%{_desktopdir} %{SOURCE1}

cp %{SOURCE2} $RPM_BUILD_ROOT%{_datadir}/appdata/%{name}.appdata.xml

%{_fixperms} $RPM_BUILD_ROOT*

%check
cd xs
./Build test verbose=1
cd -
SLIC3R_NO_AUTO=1 perl Build.PL installdirs=vendor
# the --gui runs no tests, it only checks requires

%post
/sbin/ldconfig
/bin/%update_icon_cache_post hicolor &>/dev/null || :

%postun
/sbin/ldconfig
if [ $1 -eq 0 ] ; then
    /bin/%update_icon_cache_post hicolor &>/dev/null
    %{_bindir}/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
%{_bindir}/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md
%attr(755,root,root) %{_bindir}/%{name}
%{perl_vendorlib}/Slic3r*
%{perl_vendorarch}/Slic3r*
%{perl_vendorarch}/auto/Slic3r*
%{_iconsdir}/hicolor/*/apps/%{name}.png
%{_desktopdir}/%{name}.desktop
%{_datadir}/appdata/%{name}.appdata.xml
%{_datadir}/%{name}
