Name:           zeromouse-cursor-theme
Version:        %{theme_version}
Release:        1%{?dist}
Summary:        High-visibility neon cursor theme for people with low vision
License:        AGPL-3.0-or-later
BuildArch:      noarch
Source0:        zeromouse.tar.gz

%description
ZeroMouse is a high-visibility XCursor theme designed with low-vision users
in mind. It uses neon lime and yellow-green artwork and includes animated
busy and launch feedback cursors with sizes from 24 through 512 pixels.

%prep
%setup -q -n zeromouse

%build

%install
install -d %{buildroot}%{_datadir}/icons/ZeroMouse
cp -a cursors index.theme %{buildroot}%{_datadir}/icons/ZeroMouse/

%files
%license LICENSE
%doc README.md preview
%{_datadir}/icons/ZeroMouse/

%changelog
* Thu Nov 12 2026 ZeroMouse contributors - %{theme_version}-1
- Initial cross-distribution RPM package
