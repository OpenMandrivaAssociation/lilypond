# Taken from pango spec
%define biarchs_32 %{ix86}
%define biarchs_64 x86_64
%define query_modules_suffix %{nil}
%ifarch %{biarchs_32}
%define query_modules_suffix -32
%endif
%ifarch %{biarchs_64}
%define query_modules_suffix -64
%endif
%define query_modules pango-querymodules%{query_modules_suffix}

# for python modules
%define _disable_ld_no_undefined 1

Name:		lilypond
Version:	2.16.0
Release:	2
Epoch:		0
Summary:	Program for printing sheet music
License:	GPL
Group:		Publishing
URL:		http://www.lilypond.org/
Source0:	http://lilypond.org/download/sources/v2.13/%{name}-%{version}.tar.gz
Source2:	http://download.linuxaudio.org/lilypond/binaries/documentation/%{name}-%{version}-1.documentation.tar.bz2
Source10:	%{name}.rpmlintrc
Suggests:	%{name}-doc = %{version}
Requires(post):	ec-fonts-mftraced
Requires(post):	texlive-kpathsea.bin
Requires(post):	mkfontdir
Requires(post):	rpm-helper
Requires(preun): rpm-helper
Requires(postun): texlive-kpathsea.bin
Requires(post):	findutils
# (Abel) bib2html or bibtex2html -- pick either one
BuildRequires:	bib2html
BuildRequires:	texi2html
BuildRequires:	bison
BuildRequires:	ec-fonts-mftraced
BuildRequires:	flex
BuildRequires:	fontconfig
BuildRequires:	fontforge >= 1.0-0.20110222
BuildRequires:	gettext-devel
BuildRequires:	ghostscript
BuildRequires:	groff-for-man
BuildRequires:	pkgconfig(gtk+-2.0)
BuildRequires:	pkgconfig(guile-1.8)
BuildRequires:	pango-modules
BuildRequires:	mftrace
BuildRequires:	python-devel
BuildRequires:	texinfo
BuildRequires:	netpbm
BuildRequires:	zip
BuildRequires:	imagemagick
BuildRequires:	dblatex
Requires:		guile1.8

%description
LilyPond is a music typesetter.  It produces beautiful sheet music using a
high level description file as input.  LilyPond is part of the GNU project.

LilyPond is split into two packages.  The package "lilypond" provides the
core package, containing the utilities for converting the music source
(.ly) files into printable output.  The package "lilypond-doc" 
provides the full documentation, example .ly files for various features and 
the Mutopia project files (musical equivalent of the Gutenberg project - see
http://www.mutopiaproject.org for details).

If you are new to lilypond, you will almost certainly want to install the
"lilypond-doc" package and take a look at tutorials under
%{_docdir}/lilypond-doc.

%package doc
Summary:	LilyPond documentation, examples and Mutopia files
Group:		Publishing
Provides:	%{name}-manual = %{EVRD}
BuildArch:	noarch

%description doc
The documentation of LilyPond, both in HTML and PostScript, along with
example input files and the files from the Mutopia project. If you
want to try the examples or score files from Mutopia project, please
also install LilyPond main package.


%prep
%setup -q

mkdir -p %{name}-documentation-%{version}
cd %{name}-documentation-%{version}
bunzip2 -dcq %{SOURCE2} | tar -xf -
cd -

%build
#
# build environment untrustworthy
#
%{_bindir}/%query_modules > pango.modules
echo "[Pango]" > pangorc
echo "ModuleFiles = `pwd`/pango.modules" >> pangorc
export PANGO_RC_FILE=`pwd`/pangorc

#
# build timestamp in HTML can be affected by locale
# (not necessary after applying date patch)
#
#export LC_TIME=C
%configure2_5x
# let's drop the macro for the time being as the program doesn't build otherwise on a dual-core
# %make
make all

# Doesn't work out of the box for this version.
# %make web

%install
%makeinstall_std

#
# web doc
#
# Doesn't work out of the box for this version.
# make out=www web-install DESTDIR=%{buildroot}

#
# move emacs file to our location
#
install -D -m 644 elisp/lilypond-init.el %{buildroot}%{_sysconfdir}/emacs/site-start.d/lilypond-init.el

#
# move vim stuff to our location
#
mv %{buildroot}%{_datadir}/lilypond/%{version}/vim %{buildroot}%{_datadir}/vim

#
# some more house cleaning
#
find %{buildroot} -path '*%{_datadir}/lilypond/%{version}/fonts' -prune -type f -o -name 'fonts.cache-1' -print0 | %{_bindir}/xargs -r -0 %{__rm}
find %{buildroot}%{_docdir} -name '*.png' -empty -print0 | %{_bindir}/xargs -r -0 %{__rm}
find %{buildroot}%{_datadir}/lilypond/%{version} -xtype l -print0 | %{_bindir}/xargs -r -0 %{__rm}

#
# Create symlinks to lilypond folder under TeX directory, so that TeX can
# use lilypond files natively, courtesy of Michael Brown's great hacks
# Necessary for tex backend to work, since startup profile is gone -- Abel
#
mkdir -p %{buildroot}%{_datadir}/texmf/dvips \
         %{buildroot}%{_datadir}/texmf/tex \
         %{buildroot}%{_datadir}/texmf/fonts/source \
         %{buildroot}%{_datadir}/texmf/fonts/tfm  \
         %{buildroot}%{_datadir}/lilypond/%{version}/fonts/type1
pushd %{buildroot}%{_datadir}/texmf > /dev/null
ln -s ../../lilypond/%{version}/ps dvips/lilypond
ln -s ../../lilypond/%{version}/tex tex/lilypond
ln -s ../../../lilypond/%{version}/fonts/source fonts/source/lilypond
ln -s ../../../lilypond/%{version}/fonts/tfm fonts/tfm/lilypond
popd > /dev/null

%find_lang %{name}

mkdir -p %{buildroot}%{_sysconfdir}/X11/fontpath.d/
ln -s ../../..%{_datadir}/lilypond/%{version}/fonts/type1 \
    %{buildroot}%{_sysconfdir}/X11/fontpath.d/lilypond:pri=50

%post
find /var/lib/texmf \( -name 'feta*.pk' -or -name 'feta*.tfm' -or -name 'parmesan*.pk' -or -name 'parmesan*.tfm' \) -print0 | xargs -r -0 rm -f
mktexlsr > /dev/null
mkfontdir %{_datadir}/lilypond/%{version}/fonts/type1

%preun
rm -f %{_datadir}/lilypond/%{version}/fonts/type1/fonts.dir

%postun
mktexlsr > /dev/null

%files -f %{name}.lang
%doc COPYING README.txt DEDICATION NEWS.txt AUTHORS.txt THANKS
%{_bindir}/*
%{_datadir}/emacs/site-lisp/lilypond*
%{_datadir}/%{name}
%{_datadir}/texmf/dvips/lilypond
%{_datadir}/texmf/fonts/source/lilypond
%{_datadir}/texmf/fonts/tfm/lilypond
%{_datadir}/texmf/tex/lilypond
%{_datadir}/vim/*/*
%{_libdir}/%{name}
%{_mandir}/man?/*
%{_infodir}/*.info*
%config(noreplace) %{_sysconfdir}/emacs/site-start.d/*
%{_sysconfdir}/X11/fontpath.d/lilypond:pri=50

%files doc
%doc %{name}-documentation-%{version}/*


