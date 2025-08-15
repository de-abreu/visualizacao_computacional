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
        kaggle
        matplotlib
        pandas
        plotly
        scikit-learn
        seaborn
      ]);

    dependencies = [pythonEnv pkgs.chromium];

    runScript = pkgs.writeShellApplication {
      name = "launch-jupyter";
      runtimeInputs = dependencies;
      text = ''
        cd ${self}              # Move to the project's working directory
        export BROWSER=chromium # Set browser path
        jupyter notebook        # Launch Jupyter
      '';
    };
  in {
    # For `nix develop`
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = dependencies;
    };

    # For `nix run`
    packages.${system}.default = runScript;
  };
}
