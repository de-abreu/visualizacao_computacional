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
        # Base
        pip
        jupyter
        python-lsp-server
        sqlalchemy

        # Data/Viz
        pandas
        pandas-stubs
        numpy
        tqdm
        seaborn
        networkx
        dash
        gunicorn
        plotly
        kaggle
        matplotlib

        # Webscrapper
        attrs
        certifi
        charset-normalizer
        dill
        exceptiongroup
        h11
        idna
        outcome
        packaging
        pysocks
        python-dateutil
        python-dotenv
        pytz
        requests
        selenium
        six
        sniffio
        sortedcontainers
        trio
        trio-websocket
        typing-extensions
        tzdata
        urllib3
        webdriver-manager
        websocket-client
        wsproto
      ]);
  in {
    # For `nix develop`
    devShells.${system}.default = pkgs.mkShell {
      packages = with pkgs; [
        pythonEnv
        chromium
        chromedriver
        sqlite
        dbeaver-bin
      ];
    };
  };
}
