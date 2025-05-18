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
          buildInputs = with pkgs; [
            python312 /* 3.12.10 */
            poetry /* 2.1.3 */
            pre-commit /* 4.0.1 */
            /* shouldn't put docker in this, use docker on your host os */
          ];
        };
      };
    };
  };
}