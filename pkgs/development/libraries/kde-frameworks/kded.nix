{
  mkDerivation, propagate, wrapGAppsHook,
  extra-cmake-modules, kdoctools,
  gsettings-desktop-schemas, kconfig, kcoreaddons, kcrash, kdbusaddons, kinit,
  kservice, qtbase,
}:

mkDerivation {
  name = "kded";
  nativeBuildInputs = [ extra-cmake-modules kdoctools wrapGAppsHook ];
  buildInputs = [
    gsettings-desktop-schemas kconfig kcoreaddons kcrash kdbusaddons kinit
    kservice qtbase
  ];
  outputs = [ "out" "dev" ];
  setupHook = propagate "out";
  dontWrapGApps = true;
  preFixup = ''
    qtWrapperArgs+=("''${gappsWrapperArgs[@]}")
  '';
}
