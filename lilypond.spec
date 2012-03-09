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

Name:           lilypond
Version:        2.15.32
Release:        %mkrel 1
Epoch:          0
Summary:        Program for printing sheet music
License:        GPL
Group:          Publishing
URL:            http://www.lilypond.org/
Source0:        http://lilypond.org/download/sources/v2.13/%{name}-%{version}.tar.gz
Source2:	http://download.linuxaudio.org/lilypond/binaries/documentation/%{name}-%{version}-1.documentation.tar.bz2
Suggests:	%{name}-doc = %{version}
Requires(post): ec-fonts-mftraced
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(post): findutils
Requires(post): texlive
Requires(postun): texlive
BuildRequires:	texlive
# (Abel) bib2html or bibtex2html -- pick either one
BuildRequires:  bib2html
BuildRequires:  texi2html
BuildRequires:  bison
BuildRequires:  ec-fonts-mftraced
BuildRequires:  flex
BuildRequires:  fontforge >= 1.0-0.20110222
BuildRequires:  urw-fonts
BuildRequires:  gettext-devel
BuildRequires:  ghostscript
BuildRequires:  groff-for-man
BuildRequires:  gtk2-devel
BuildRequires:  guile-devel >= 1.8.1
BuildRequires:  mftrace
BuildRequires:  python-devel
BuildRequires:  texinfo
BuildRequires:  netpbm
BuildRequires:  info-install
BuildRequires:  zip
BuildRequires:  imagemagick
BuildRequires:  dblatex
BuildRequires:  pango
BuildRequires:  texlive-collection-music

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

%package	doc
Summary:        LilyPond documentation, examples and Mutopia files
Group:          Publishing
Obsoletes:      %{name}-manual
Provides:       %{name}-manual
BuildArch:	noarch

%description	doc
The documentation of LilyPond, both in HTML and PostScript, along with
example input files and the files from the Mutopia project. If you
want to try the examples or score files from Mutopia project, please
also install LilyPond main package.


%prep
%setup -q

mkdir -p %{name}-documentation-%{version}
cd %{name}-documentation-%{version}
bunzip2 -dcq %SOURCE2 | tar -xf -
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
%{configure2_5x} --with-ncsb-dir=%{_datadir}/fonts/default/Type1
# let's drop the macro for the time being as the program doesn't build otherwise on a dual-core
# %{make}
make all

# Doesn't work out of the box for this version.
#%{make} web

%install
%{__rm} -rf %{buildroot}
%{makeinstall_std}

#
# web doc
#
# Doesn't work out of the box for this version.
#%{__make} out=www web-install DESTDIR=%{buildroot}

#
# move emacs file to our location
#
%{__install} -D -m 644 elisp/lilypond-init.el %{buildroot}%{_sysconfdir}/emacs/site-start.d/lilypond-init.el

#
# move vim stuff to our location
#
%{__mv} %{buildroot}%{_datadir}/lilypond/%{version}/vim %{buildroot}%{_datadir}/vim

#
# some more house cleaning
#
%{_bindir}/find %{buildroot} -path '*%{_datadir}/lilypond/%{version}/fonts' -prune -type f -o -name 'fonts.cache-1' -print0 | %{_bindir}/xargs -r -0 %{__rm}
%{_bindir}/find %{buildroot}%{_docdir} -name '*.png' -empty -print0 | %{_bindir}/xargs -r -0 %{__rm}
%{_bindir}/find %{buildroot}%{_datadir}/lilypond/%{version} -xtype l -print0 | %{_bindir}/xargs -r -0 %{__rm}

#
# Create symlinks to lilypond folder under TeX directory, so that TeX can
# use lilypond files natively, courtesy of Michael Brown's great hacks
# Necessary for tex backend to work, since startup profile is gone -- Abel
#
%{__mkdir_p} %{buildroot}%{_datadir}/texmf/dvips \
         %{buildroot}%{_datadir}/texmf/tex \
         %{buildroot}%{_datadir}/texmf/fonts/source \
         %{buildroot}%{_datadir}/texmf/fonts/tfm  \
         %{buildroot}%{_datadir}/lilypond/%{version}/fonts/type1
pushd %{buildroot}%{_datadir}/texmf > /dev/null
%{__ln_s} ../../lilypond/%{version}/ps dvips/lilypond
%{__ln_s} ../../lilypond/%{version}/tex tex/lilypond
%{__ln_s} ../../../lilypond/%{version}/fonts/source fonts/source/lilypond
%{__ln_s} ../../../lilypond/%{version}/fonts/tfm fonts/tfm/lilypond
popd > /dev/null

%{find_lang} %{name}

mkdir -p %{buildroot}%_sysconfdir/X11/fontpath.d/
ln -s ../../..%_datadir/lilypond/%{version}/fonts/type1 \
    %{buildroot}%_sysconfdir/X11/fontpath.d/lilypond:pri=50


%clean
%{__rm} -rf %{buildroot}

%post
%_install_info lilypond.info
%_install_info lilypond-internals.info
%_install_info lilypond-learning.info
%_install_info lilypond-program.info
%_install_info music-glossary.info

%{_bindir}/find /var/lib/texmf \( -name 'feta*.pk' -or -name 'feta*.tfm' -or -name 'parmesan*.pk' -or -name 'parmesan*.tfm' \) -print0 | %{_bindir}/xargs -r -0 %{__rm} -f

%{_sbindir}/texlove.post

%{_bindir}/mkfontdir %{_datadir}/lilypond/%{version}/fonts/type1

%preun
%_remove_install_info lilypond.info
%_remove_install_info lilypond-learning.info
%_remove_install_info lilypond-internals.info
%_remove_install_info lilypond-program.info
%_remove_install_info music-glossary.info

%{__rm} -f %{_datadir}/lilypond/%{version}/fonts/type1/fonts.dir

%postun
%{_bindir}/mktexlsr > /dev/null

%files -f %{name}.lang
%defattr(-, root, root)
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
%defattr(-, root, root)
%doc %{name}-documentation-%{version}/*


