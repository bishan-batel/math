{
  description = "Crab";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
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
                just
              ] ++ pkgs.lib.optional pkgs.stdenv.isDarwin [ apple ];

              buildInputs = with pkgs; [ 
                kdePackages.qtmultimedia
              ] ++ pkgs.lib.optional pkgs.stdenv.isDarwin [ apple ];

              nativeBuildInputs = with pkgs; [ 
                pkg-config 
                pango
                texliveFull
                ffmpeg 
                manim-slides
                qt6.qtmultimedia 
                qt6.qtbase 
                gst_all_1.gstreamer
                gst_all_1.gst-plugins-base
                gst_all_1.gst-plugins-good
                gst_all_1.gst-plugins-bad
                gst_all_1.gst-libav
              ] ++ pkgs.lib.optional pkgs.stdenv.isLinux (with pkgs; [
                  qt6.qtwayland
                  gst_all_1.gstreamer
                  gst_all_1.gst-plugins-base
                  gst_all_1.gst-plugins-good
                  gst_all_1.gst-plugins-bad
                  gst_all_1.gst-libav
                ]);

              env = if pkgs.stdenv.isDarwin then {
                NIX_LDFLAGS = "-F/System/Library/Frameworks -framework OpenGL -framework Cocoa -framework IOKit";
                PYOPENGL_PLATFORM="darwin";
              } else { 
                LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (with pkgs; [ ffmpeg pango qt6.qtwayland qt6.qtmultimedia qt6.qtbase ]);
              };
              
              shellHook = if pkgs.stdenv.isDarwin then  /*bash*/ ''
              # 1. Force the dynamic linker to look at the REAL system frameworks first
              export DYLD_FALLBACK_FRAMEWORK_PATH="/System/Library/Frameworks:$DYLD_FALLBACK_FRAMEWORK_PATH"
              export DYLD_FALLBACK_LIBRARY_PATH="/usr/lib:/System/Library/Frameworks/OpenGL.framework/Versions/Current:$DYLD_FALLBACK_LIBRARY_PATH"

              # 2. Tell PyOpenGL to use the Darwin-specific loader logic
              export PYOPENGL_PLATFORM="darwin"

              # 3. If Manim still fails, it may be trying to use a Nix-packaged 'moderngl'.
              # Try setting this to force it to find the system's GL context:
              export LIBGL_DIAGNOSTIC=1 
              export QT_PLUGIN_PATH="${pkgs.qt6.qtbase}/${pkgs.qt6.qtbase.qtPluginPrefix}:${pkgs.qt6.qtmultimedia}/${pkgs.qt6.qtbase.qtPluginPrefix}"
              export GST_PLUGIN_SYSTEM_PATH_1_0="${pkgs.gst_all_1.gstreamer.out}/lib/gstreamer-1.0:${pkgs.gst_all_1.gst-plugins-base}/lib/gstreamer-1.0:${pkgs.gst_all_1.gst-plugins-good}/lib/gstreamer-1.0:${pkgs.gst_all_1.gst-plugins-bad}/lib/gstreamer-1.0:${pkgs.gst_all_1.gst-libav}/lib/gstreamer-1.0"

              echo "Nix-Darwin OpenGL Bridge Active."
              '' else /*bash*/ ''
                  export QT_PLUGIN_PATH="${pkgs.qt6.qtbase}/${pkgs.qt6.qtbase.qtPluginPrefix}:${pkgs.qt6.qtmultimedia}/${pkgs.qt6.qtbase.qtPluginPrefix}"
                  export GST_PLUGIN_SYSTEM_PATH_1_0="${pkgs.gst_all_1.gstreamer.out}/lib/gstreamer-1.0:${pkgs.gst_all_1.gst-plugins-base}/lib/gstreamer-1.0:${pkgs.gst_all_1.gst-plugins-good}/lib/gstreamer-1.0:${pkgs.gst_all_1.gst-plugins-bad}/lib/gstreamer-1.0:${pkgs.gst_all_1.gst-libav}/lib/gstreamer-1.0"
              '';
            };
        };
      }
    );
}
