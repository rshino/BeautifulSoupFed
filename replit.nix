{ pkgs }: {
    deps = [
        pkgs.bashInteractive
        (pkgs.python38.withPackages (p: [p.pandas]))
    ];
}