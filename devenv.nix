{pkgs, ...}: {
  packages = with pkgs; [
    chromedriver
    chromium
    dbeaver-bin
    sqlite
    zlib
  ];

  languages.python = {
    enable = true;
    venv = {
      enable = true;
      requirements = ./requirements.txt;
    };
  };
}
