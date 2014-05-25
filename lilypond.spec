%define __noautoreq '/usr/bin/guile'
%define _disable_ld_no_undefined 1

Name:		lilypond
Version:	2.18.2
Release:	1
Summary:	A typesetting system for music notation
Group:		Publishing
License:	GPLv3
URL:		http://www.lilypond.org
Source0:	http://download.linuxaudio.org/lilypond/sources/v2.18/%{name}-%{version}.tar.gz
Patch0:		lilypond-2.21.2-gcc44-relocate.patch
Group:		Publishing
Requires:	ghostscript >= 8.15
Requires:	guile1.8
Obsoletes: 	lilypond-fonts <= 2.12.1-1
Requires:	lilypond-century-schoolbook-l-fonts = %{version}-%{release}
Requires:	lilypond-emmentaler-fonts = %{version}-%{release}

BuildRequires:  t1utils 
BuildRequires:  bison 
BuildRequires:  flex 
BuildRequires:  imagemagick 
BuildRequires:  gettext 
BuildRequires:  tetex
BuildRequires:  python-devel >= 2.4.0
BuildRequires:  mftrace >= 1.1.19
BuildRequires:  texinfo >= 4.8
BuildRequires:  pkgconfig(guile-1.8)
BuildRequires:  ghostscript >= 8.15
BuildRequires:  pango-devel >= 1.12.0
BuildRequires:  pkgconfig(pangoft2)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:	fontpackages-devel
BuildRequires:	dblatex
BuildRequires:	texi2html
BuildRequires:	rsync
BuildRequires:	texlive
BuildRequires:	flex-devel
BuildRequires:	netpbm
BuildRequires:	zip

%description
LilyPond is an automated music engraving system. It formats music
beautifully and automatically, and has a friendly syntax for its input
files.

%package century-schoolbook-l-fonts
Summary:        Lilypond Century Schoolbook L fonts

Requires:       fontpackages-filesystem
Requires:	lilypond-fonts-common = %{version}-%{release}
Obsoletes:	lilypond-centuryschl-fonts <= 2.12.1-3
BuildArch:	noarch

%description century-schoolbook-l-fonts 
LilyPond is an automated music engraving system. It formats music
beautifully and automatically, and has a friendly syntax for its input
files.

These are the Century Schoolbook L fonts included in the package.

%package emmentaler-fonts
Summary:        Lilypond emmentaler fonts

Requires:       fontpackages-filesystem
Requires:	lilypond-fonts-common = %{version}-%{release}
BuildArch:	noarch

%description emmentaler-fonts 
LilyPond is an automated music engraving system. It formats music
beautifully and automatically, and has a friendly syntax for its input
files.

These are the emmentaler fonts included in the package.


%package fonts-common
Summary:        Lilypond fonts common dir

Requires:       fontpackages-filesystem
Obsoletes:	lilypond-aybabtu-fonts <= 2.12.3-3
Obsoletes:	lilypond-feta-fonts <= 2.12.3-3
Obsoletes:	lilypond-feta-alphabet-fonts <= 2.12.3-3
Obsoletes:	lilypond-feta-braces-fonts <= 2.12.3-3
Obsoletes:	lilypond-parmesan-fonts <= 2.12.3-3
BuildArch:	noarch

%description fonts-common
LilyPond is an automated music engraving system. It formats music
beautifully and automatically, and has a friendly syntax for its input
files.

This contains the directory common to all lilypond fonts.

%prep
%setup -q

%patch0 -p0

%build
%configure --without-kpathsea --disable-checking \
	--with-ncsb-dir=%{_datadir}/fonts/default/Type1
# underlink
echo LIBS=-lpython2.7 >> python/GNUmakefile
make


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT package_infodir=%{_infodir} \
	vimdir=%{_datadir}/vim

chmod +x $RPM_BUILD_ROOT%{_libdir}/%{name}/%{version}/python/midi.so

# Symlink lilypond-init.el in emacs' site-start.d directory
pushd $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp
mkdir site-start.d
ln -s ../lilypond-init.el site-start.d
popd

# Change encoding to UTF8
pushd $RPM_BUILD_ROOT%{_infodir}
iconv -f iso-8859-1 -t utf-8 music-glossary.info > music-glossary.info.utf8
mv music-glossary.info.utf8 music-glossary.info
sed -e s,lilypond/,, -i *.info
popd

rm -f $RPM_BUILD_ROOT%{_infodir}/dir

%find_lang %{name}

mkdir -p $RPM_BUILD_ROOT%{_fontdir}
mv $RPM_BUILD_ROOT%{_datadir}/lilypond/%{version}/fonts/otf/*.otf $RPM_BUILD_ROOT%{_fontdir}
rmdir $RPM_BUILD_ROOT%{_datadir}/lilypond/%{version}/fonts/otf
ln -s %{_fontdir} $RPM_BUILD_ROOT%{_datadir}/lilypond/%{version}/fonts/otf



%files -f %{name}.lang
%defattr(-,root,root,-)
%doc AUTHORS.txt COPYING DEDICATION HACKING INSTALL.txt
%doc NEWS.txt README.txt ROADMAP VERSION
%{_bindir}/*
%{_libdir}/lilypond
%{_datadir}/lilypond
%{_datadir}/emacs/site-lisp
%{_datadir}/vim/*/*
%{_infodir}/*
%{_mandir}/man1/*

%_font_pkg -n century-schoolbook-l CenturySchL*otf

%_font_pkg -n emmentaler emmentaler*otf

%files fonts-common
%doc COPYING
%defattr(0644,root,root,0755)
%dir %{_fontdir}
