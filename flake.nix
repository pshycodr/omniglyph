{
  description = "OmniGlyph — fast emoji and Unicode symbol picker (GTK4 + Python)";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python313;
        pythonEnv = python.withPackages (
          ps: with ps; [
            pygobject3
            rapidfuzz
            tomli-w
            nuitka
          ]
        );
        omniglyph = pkgs.stdenv.mkDerivation {
          pname = "omniglyph";
          version = "1.1.0";
          src = pkgs.fetchFromGitHub {
            owner = "pshycodr";
            repo = "omniglyph";
            rev = "v1.1.0";
            hash = "sha256-R6i72CiNOj8dMhYf9rMX49je8WOG1OZp2MenacHzTEU=";
          };
          nativeBuildInputs = with pkgs; [
            gobject-introspection
            autoPatchelfHook
            gcc
            makeWrapper
          ];
          buildInputs = with pkgs; [
            gtk4
            libadwaita
            gtk4-layer-shell
            glib
            cairo
            pango
            harfbuzz
            graphene
            gdk-pixbuf
            pythonEnv
          ];
          dontConfigure = true;
          buildPhase = ''
            runHook preBuild
            export HOME=$TMPDIR
            export PYTHONPATH=${pythonEnv}/${python.sitePackages}
            ${pythonEnv}/bin/python3 -m nuitka \
              --standalone \
              --enable-plugin=implicit-imports \
              --include-package=gi \
              --include-package=gi.repository \
              --include-data-dir=glyph/db/collections=db/collections \
              --include-data-dir=glyph/styles=styles \
              --output-dir=out \
              glyph/main.py
            runHook postBuild
          '';
          installPhase = ''
            runHook preInstall
            mkdir -p $out/lib/omniglyph $out/bin
            cp -r out/main.dist/. $out/lib/omniglyph/
            makeWrapper $out/lib/omniglyph/main.bin $out/bin/omniglyph \
              --prefix GI_TYPELIB_PATH : "${pkgs.gtk4}/lib/girepository-1.0" \
              --prefix GI_TYPELIB_PATH : "${pkgs.libadwaita}/lib/girepository-1.0" \
              --prefix GI_TYPELIB_PATH : "${pkgs.gtk4-layer-shell}/lib/girepository-1.0" \
              --prefix GI_TYPELIB_PATH : "${pkgs.gobject-introspection}/lib/girepository-1.0" \
              --prefix GI_TYPELIB_PATH : "${pkgs.glib.out}/lib/girepository-1.0" \
              --prefix GI_TYPELIB_PATH : "${pkgs.pango.out}/lib/girepository-1.0" \
              --prefix GI_TYPELIB_PATH : "${pkgs.gdk-pixbuf}/lib/girepository-1.0" \
              --prefix GI_TYPELIB_PATH : "${pkgs.harfbuzz}/lib/girepository-1.0" \
              --prefix GI_TYPELIB_PATH : "${pkgs.graphene}/lib/girepository-1.0"
            runHook postInstall
          '';
          meta = {
            description = "Fast emoji and Unicode symbol picker for Linux (GTK4 + Libadwaita)";
            homepage = "https://github.com/pshycodr/omniglyph";
            license = pkgs.lib.licenses.gpl3Only;
            mainProgram = "omniglyph";
          };
        };
      in
      {
        packages.default = omniglyph;
        packages.omniglyph = omniglyph;
        apps.default = flake-utils.lib.mkApp { drv = omniglyph; };
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            pythonEnv
            gtk4
            libadwaita
            gtk4-layer-shell
            gobject-introspection
            pango
            harfbuzz
            graphene
            gdk-pixbuf
            cairo
          ];
        };
      }
    );
}
