{
  description = "Crab";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    nixgl.url = "github:nix-community/nixGL";
  };

  outputs =
    { nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let pkgs = import nixpkgs { inherit system; };
          apple = pkgs.apple-sdk;
      in
        {

        devShells = {
          default =
            pkgs.mkShell.override { }
            {
              name = "holomoprhic";
              packages = with pkgs; [
                cmake
                uv
                python3
                cairo
                manim 
                ffmpeg 
                apple
              ];

              buildInputs = with pkgs; [ 
                kdePackages.qtmultimedia
                apple
              ];

              nativeBuildInputs = with pkgs; [ 
                pkg-config 
                kdePackages.qtmultimedia
                texliveFull
              ];

              env = {
                NIX_LDFLAGS = "-F/System/Library/Frameworks -framework OpenGL -framework Cocoa -framework IOKit";
                PYOPENGL_PLATFORM="darwin";
                # DYLD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (
                #   with pkgs;
                #   [
                #     cairo
                #     ffmpeg
                #     kdePackages.qtmultimedia
                #     texliveFull
                #     apple
                #   ]
                # );
              };
              
              shellHook = ''
              # 1. Force the dynamic linker to look at the REAL system frameworks first
              export DYLD_FALLBACK_FRAMEWORK_PATH="/System/Library/Frameworks:$DYLD_FALLBACK_FRAMEWORK_PATH"
              export DYLD_FALLBACK_LIBRARY_PATH="/usr/lib:/System/Library/Frameworks/OpenGL.framework/Versions/Current:$DYLD_FALLBACK_LIBRARY_PATH"

              # 2. Tell PyOpenGL to use the Darwin-specific loader logic
              export PYOPENGL_PLATFORM="darwin"

              # 3. If Manim still fails, it may be trying to use a Nix-packaged 'moderngl'.
              # Try setting this to force it to find the system's GL context:
              export LIBGL_DIAGNOSTIC=1 

              echo "Nix-Darwin OpenGL Bridge Active."
              '';
            };
        };
      }
    );
}
