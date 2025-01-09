let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    (pkgs.python312.withPackages (py-pkgs: [
      py-pkgs.pillow
    ]))
  ];
}
