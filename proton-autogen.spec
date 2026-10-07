%define __python /usr/bin/python3

Name:           proton-autogen
Version:        3.3.9
Release:        1%{?dist}
Summary:        Automatic Proton/Wine launcher for Windows executables

License:        MIT
URL:            https://github.com/N3oRay/proton-autogen
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-build
BuildRequires:  python3-installer
BuildRequires:  python3-wheel
BuildRequires:  python3-gobject
BuildRequires:  gobject-introspection-devel
BuildRequires:  gtk4-devel

Requires:       python3
Requires:       python3-pyyaml
Requires:       python3-gobject
Requires:       python3-rich
Requires:       python3-requests
Requires:       python3-psutil
Requires:       python3-xlib
Requires:       gtk4
Requires:       gdk-pixbuf2
Requires:       graphene

Recommends:     steam
Recommends:     wine
Recommends:     mangohud
Recommends:     gamemode
Recommends:     gamescope
Recommends:     nautilus
Recommends:     nemo
Recommends:     dolphin

BuildArch:      noarch

%description
Proton-Autogen automatically creates and configures Proton environments
for Windows games and applications, applying optimized settings for
the best compatibility.

Simply right-click a .exe file, select "Open with Proton-Autogen",
and launch the application without manual Steam configuration.

%prep
%setup -q -n %{name}-%{version}

%build
python3 -m build --wheel --no-isolation

%install
# Install Python package and resources
python3 -m installer --destdir="%{buildroot}" dist/*.whl

# Install launcher binary
install -Dm755 usr/bin/%{name} "%{buildroot}%{_bindir}/%{name}"

# Install shared resources
install -dm755 "%{buildroot}%{_datadir}/%{name}"
cp -a usr/share/%{name}/. "%{buildroot}%{_datadir}/%{name}/"

# Install desktop file
install -Dm644 usr/share/applications/%{name}.desktop \
    "%{buildroot}%{_datadir}/applications/%{name}.desktop"

# Install icon
install -Dm644 usr/share/icons/hicolor/256x256/apps/%{name}.png \
    "%{buildroot}%{_datadir}/icons/hicolor/256x256/apps/%{name}.png"

install -Dm644 usr/share/icons/hicolor/256x256/apps/%{name}.png \
    "%{buildroot}%{_datadir}/icons/hicolor/256x256/apps/io.github.N3oRay.ProtonAutogen.png"

# Install man page (if exists)
if [ -f debian/%{name}.1.gz ]; then
    install -Dm644 debian/%{name}.1.gz \
        "%{buildroot}%{_mandir}/man1/%{name}.1.gz"
fi

# Install Nautilus and Nemo integration
install -Dm644 usr/share/nautilus-python/extensions/proton_autogen_nautilus.py \
    "%{buildroot}%{_datadir}/nautilus-python/extensions/proton_autogen_nautilus.py" || true

install -Dm644 usr/share/nemo/actions/%{name}.nemo_action \
    "%{buildroot}%{_datadir}/nemo/actions/%{name}.nemo_action" || true

# Install Dolphin/KDE integration
install -Dm644 usr/share/kio/servicemenus/%{name}.desktop \
    "%{buildroot}%{_datadir}/kio/servicemenus/%{name}.desktop" || true

# Install license
install -Dm644 LICENSE \
    "%{buildroot}%{_licensedir}/%{name}/LICENSE"

%check
# Test using Python import to verify the module can be imported
PYTHONPATH="%{buildroot}%{python3_sitelib}:$PYTHONPATH" python3 -c "from proton_autogen.config import VERSION; print(f'Module version: {VERSION}')"

# Test the installed binary with PYTHONPATH set
PYTHONPATH="%{buildroot}%{python3_sitelib}:$PYTHONPATH" %{buildroot}%{_bindir}/%{name} --version
PYTHONPATH="%{buildroot}%{python3_sitelib}:$PYTHONPATH" %{buildroot}%{_bindir}/%{name} --help

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{python3_sitelib}/proton_autogen/
%{python3_sitelib}/proton_autogen-*.dist-info/
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/256x256/apps/%{name}.png
%{_datadir}/icons/hicolor/256x256/apps/io.github.N3oRay.ProtonAutogen.png
%{_datadir}/nemo/actions/%{name}.nemo_action
%{_datadir}/kio/servicemenus/%{name}.desktop
%{_datadir}/nautilus-python/extensions/proton_autogen_nautilus.py
%{_mandir}/man1/%{name}.1.gz

%changelog
* Wed Oct 07 2026 N3oRay <n3oray77@gmail.com> - 3.3.9-1
- Initial RPM package for 3.3.9
