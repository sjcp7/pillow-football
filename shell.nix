let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    pkgs.ffmpeg_7
    (pkgs.python312.withPackages (py-pkgs: [
      py-pkgs.pillow
    ]))
  ];
}
