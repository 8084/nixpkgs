{ stdenv, pkgs, fetchurl }:

stdenv.mkDerivation rec {
  name    = "purescript-${version}";
  version = "0.12.1";
  meta = with stdenv.lib; {
    homepage = https://github.com/purescript/purescript;
    description = "A strongly-typed language that compiles to Javascript";
    platforms = platforms.linux;
    maintainers = [  ];
  };

  src = fetchurl {
    url    = "https://github.com/purescript/purescript/releases/download/v${version}/linux64.tar.gz";
    sha256 = "28e48ac0ce35fe1ab3de0da72062614e881453a179de2db5fd579e7744285f05";
  };

  unpackPhase = ''
    mkdir -p $out/bin
    tar -xvzf ${src}
    cp purescript/purs $out/bin/purs
    chmod +x $out/bin/purs
  '';

  dontStrip = true;

  installPhase = let
    libPath = stdenv.lib.makeLibraryPath [
      stdenv.cc.cc
      stdenv.cc.libc
      pkgs.glibc
      pkgs.zlibStatic
      pkgs.ncurses5
      pkgs.gmp5
    ];
  in ''
    patchelf \
      --set-interpreter "$(cat $NIX_CC/nix-support/dynamic-linker)" \
      --set-rpath ${libPath} \
       $out/bin/purs
  '';
}
