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
  in {
    # For `nix develop`
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = [pythonEnv pkgs.chromium];
      shellHook = ''
        export BROWSER=chromium  # Set browser path
        jupyter notebook         # Launch Jupyter
      '';
    };
  };
}
