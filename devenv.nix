{
  pkgs,
  config,
  ...
}: {
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
  # Due to size restrictions of the /tmp folder, we need to modify the folder
  # pip uses to install "sentence-transformer", a dependency listed in
  # requirements.txt.
  env.TMPDIR = "${config.devenv.runtime}";
}
