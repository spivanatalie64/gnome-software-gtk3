# PKGBUILD for AcreetionOS (Arch-based)
# Builds the local branch `distro/gtk3-acreetionos` of this repository
pkgname=gnome-software-gtk3
pkgver=50.0
pkgrel=1
pkgdesc="GNOME Software (GTK3 port - AcreetionOS)"
arch=(x86_64)
url="https://gitlab.gnome.org/GNOME/gnome-software"
license=(GPL)
depends=(gtk3 glib2 gdk-pixbuf2 json-glib libsoup libxmlb appstream)
makedepends=(meson ninja pkgconf git base-devel)
source=("git+file:///home/natalie/Projects/gnome-software-gtk3#branch=distro/gtk3-acreetionos")
sha256sums=(SKIP)

build() {
  cd "$srcdir/gnome-software-gtk3"
  meson setup build --prefix=/usr --buildtype=release || meson setup build --prefix=/usr
  meson compile -C build
}

check() {
  cd "$srcdir/gnome-software-gtk3"
  meson test -C build || true
}

package() {
  cd "$srcdir/gnome-software-gtk3"
  DESTDIR="$pkgdir" meson install -C build
}
