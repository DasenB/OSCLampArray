# shell.nix
{ pkgs ? import <nixpkgs> {} }:
let
  my-python-packages = ps: with ps; [
    pysimplegui
    python-osc
    tkinter
    sounddevice
    numpy
    scipy
    pyserial
    mido
    # ( buildPythonPackage {
    #   pname = "py-midi";
    #   version = "20.01";
    #   doCheck = false;
    #   propagatedBuildInputs = [
    #     pyserial
    #   ];
    #   src = pkgs.fetchFromGitHub {
    #     owner = "edthrn";
    #     repo = "py-midi";
    #     rev = "60ba0e8b418ef5e28357be71e81a6b9e1ca5fc99";
    #     sha256 = "sha256-dGmuu7ZG+xe60WkaSt4+d7Ek1txRhsUtzeSrv1GxXNk=";
    #  };})
  ];
  my-python = pkgs.python310.withPackages my-python-packages;
  # in my-python.env
in pkgs.mkShell {
  packages = [
    pkgs.usbutils
    (my-python.withPackages my-python-packages) # we have defined this in the installation section
  ];
}
