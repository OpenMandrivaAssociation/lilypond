#global	__requires_exclude guile1.8

Summary:	A typesetting system for music notation
Name:		lilypond
Version:	2.24.4
Release:	2
License:	GPLv3+
Group:		Publishing
Url:		https://www.lilypond.org
Source0:	https://lilypond.org/download/sources/v2.23/%{name}-%{version}.tar.gz
Patch0:		lilypond-2.21.2-gcc44-relocate.patch
BuildRequires:	bison >= 2.4.1
BuildRequires:	dblatex
# Not provided yet
# BuildRequires:	extractpdfmark
BuildRequires:	flex	>= 2.5.29
BuildRequires:	fontforge
BuildRequires:	gettext >= 0.17
BuildRequires:	ghostscript >= 9.03
BuildRequires:	imagemagick
BuildRequires:	locales-extra-charsets
BuildRequires:	mftrace >= 1.1.19
BuildRequires:	netpbm
BuildRequires:	perl >= 5.6.1
BuildRequires:	rsync
BuildRequires:	t1utils >= 1.33
BuildRequires:	texi2html >= 1.82
BuildRequires:	texinfo >= 6.1
BuildRequires:	texlive
BuildRequires:	texlive-bibtex
BuildRequires:	texlive-epsf
BuildRequires:	texlive-fontware.bin
BuildRequires:	texlive-metafont.bin
BuildRequires:	texlive-metapost
BuildRequires:	texlive-pdftex.bin
BuildRequires:	texlive-tex-gyre
BuildRequires:	texlive-xetex
BuildRequires:	texlive-collection-langcyrillic
BuildRequires:	tidy
BuildRequires:	zip
BuildRequires:	pkgconfig(freetype2)
BuildRequires:	pkgconfig(fontconfig) >= 2.4.0
BuildRequires:	pkgconfig(glib-2.0) >= 2.38
#BuildRequires:	pkgconfig(guile-2.2)
BuildRequires:	pkgconfig(guile-3.0)
BuildRequires:	pkgconfig(libfl)
BuildRequires:	pkgconfig(pango) >= 1.12.0
BuildRequires:	pkgconfig(pangoft2) >= 1.38.0
BuildRequires:	pkgconfig(python3) >= 3.6
Requires:	ghostscript >= 9.03
Requires:	guile >= 3.0.10
Requires:	lilypond-emmentaler-fonts = %{EVRD}
%rename	lilypond-fonts

%description
LilyPond is an automated music engraving system. It formats music
beautifully and automatically, and has a friendly syntax for its input
files.

%files -f %{name}.lang
%doc AUTHORS.txt COPYING DEDICATION
%doc NEWS.txt README.md ROADMAP VERSION
%{_bindir}/*
#%%{_libdir}/%%{name}
%{_datadir}/%{name}
%{_datadir}/emacs/site-lisp
%{_datadir}/vim/*/*
%{_infodir}/*
%{_mandir}/man1/*

#-----------------------------------------------------------------------------

%package emmentaler-fonts
Summary:	Lilypond emmentaler fonts
Requires:	lilypond-fonts-common = %{EVRD}
BuildArch:	noarch

%description emmentaler-fonts 
LilyPond is an automated music engraving system. It formats music
beautifully and automatically, and has a friendly syntax for its input
files.
These are the emmentaler fonts included in the package.

%files emmentaler-fonts
%doc COPYING
%{_datadir}/fonts/OTF/emmentaler-*.otf

#-----------------------------------------------------------------------------

%package fonts-common
Summary:	Lilypond fonts common dir
%rename	lilypond-aybabtu-fonts
%rename	lilypond-centuryschl-fonts
%rename	lilypond-century-schoolbook-l-fonts
%rename	lilypond-feta-fonts
%rename	lilypond-feta-alphabet-fonts
%rename	lilypond-feta-braces-fonts
%rename	lilypond-parmesan-fonts
BuildArch:	noarch

%description fonts-common
LilyPond is an automated music engraving system. It formats music
beautifully and automatically, and has a friendly syntax for its input
files.
This package contains the directory common to all lilypond fonts.

%files fonts-common
%doc COPYING
%dir %{_datadir}/fonts/OTF

#-----------------------------------------------------------------------------

%prep
%autosetup -p0


%build
export CC=gcc
export CXX=g++
export GUILE_FLAVOR=guile-3.0
# Needed only when building unstable
#./autogen.sh --noconfigure
%configure	--disable-checking

%make_build all


%install
%make_install package_infodir=%{_infodir} vimdir=%{_datadir}/vim

# Symlink lilypond-init.el in emacs' site-start.d directory
pushd %{buildroot}%{_datadir}/emacs/site-lisp
	mkdir site-start.d
	ln -s ../%{name}-init.el site-start.d
popd

# Change encoding to UTF8
pushd %{buildroot}%{_infodir}
	iconv -f iso-8859-1 -t utf-8 music-glossary.info > music-glossary.info.utf8
	mv music-glossary.info.utf8 music-glossary.info
	sed -e s,lilypond/,, -i *.info
popd

# Drop unused dir
rm -f %{buildroot}%{_infodir}/dir

# We would like to have all the provided .otf font files in %%{_datadir}/fonts/OTF
mkdir -p %{buildroot}%{_datadir}/fonts/OTF
mv %{buildroot}%{_datadir}/%{name}/%{version}/fonts/otf/*.otf %{buildroot}%{_datadir}/fonts/OTF/
rmdir %{buildroot}%{_datadir}/%{name}/%{version}/fonts/otf
ln -s %{_datadir}/fonts/OTF %{buildroot}%{_datadir}/%{name}/%{version}/fonts/otf

# Fix python shebangs
sed '1 s,^.*$,#!%{__python3},' -i %{buildroot}%{_bindir}/{lilypond-book,lilysong,midi2ly,lilymidi,abc2ly,etf2ly,musicxml2ly,convert-ly}


%find_lang %{name}
