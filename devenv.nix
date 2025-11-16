{pkgs, ...}: {
  packages = with pkgs; [
    chromedriver
    chromium
    dbeaver-bin
    sqlite
    zlib
  ];

  # Set up TMPDIR before Python virtual environment creation
  tasks."setup:tmpdir" = {
    exec = ''
      mkdir -p .build
      export TMPDIR=$PWD/.build
    '';
    before = ["devenv:python:virtualenv"];
  };

  languages.python = {
    enable = true;
    venv = {
      enable = true;
      requirements = ./requirements.txt;
    };
  };
}
