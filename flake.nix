{
  description = "Dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }: {
    devShells = {
      x86_64-linux = let
        system = "x86_64-linux";
        pkgs = import nixpkgs { inherit system; };
      in {
        default = pkgs.mkShell {
          NIX_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc
          ];
          NIX_LD = pkgs.lib.fileContents "${pkgs.stdenv.cc}/nix-support/dynamic-linker";
          shellHook = ''
            # fixing the Path issue for libstdc.so.6 https://discourse.nixos.org/t/sqlalchemy-python-fails-to-find-libstdc-so-6-in-virtualenv/38153
            export LD_LIBRARY_PATH=$NIX_LD_LIBRARY_PATH

            # do not write __pycache__ and .pyc
            export PYTHONDONTWRITEBYTECODE=1

            # necessary to not crash
            export JWT_SECRET_KEY=OSEF
            export RESET_PASSWORD_TOKEN_SECRET=OSEF
            export VERIFICATION_TOKEN_SECRET=OSEF
          '';
          buildInputs = with pkgs; [
            python312 /* 3.12.10 */
            poetry /* 2.1.3 */
            pre-commit /* 4.0.1 */
            libgcc
            postgresql_17.pg_config
            python312Packages.invoke
            nodejs
            /* shouldn't put docker in this, use docker on your host os */
          ];
        };
      };
    };
  };
}