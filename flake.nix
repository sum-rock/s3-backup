{
  description = "S3-Backups made easy";
  inputs = {
    flake-utils = { url = "github:numtide/flake-utils"; };
  };
  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        env = pkgs.poetry2nix.mkPoetryEnv {
          python = pkgs.python311;
          groups = [ "development" ];
          projectDir = ./.;
          pyproject = ./pyproject.toml;
          poetrylock = ./poetry.lock;
        };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            env
            pkgs.duplicity
          ];
        };
      }
    );
}

