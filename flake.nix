{
  description = "Data visualization development environment";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-25.05";

  outputs = {
    self,
    nixpkgs,
  }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};

    # Custom Python environment
    pythonEnv = pkgs.python3.withPackages (ps:
      with ps; [
        jupyter
        pandas
        plotly
        kaggle
      ]);

    # Script to run the Python app with arguments
    runScript = pkgs.writeShellApplication {
      name = "jupiter-scrapper";
      runtimeInputs = [pythonEnv];
      text = ''
        ${pythonEnv}/bin/python src/main.py "$@"
      '';
    };
  in {
    # For `nix develop`
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = [pythonEnv];
      shellHook = ''
        echo "📊 Welcome to the data visualizarion development environment"
      '';
    };

    # For `nix run`
    packages.${system}.default = runScript;
  };
}
