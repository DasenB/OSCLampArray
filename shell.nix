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
  ];
  my-python = pkgs.python311.withPackages my-python-packages;
in my-python.env
