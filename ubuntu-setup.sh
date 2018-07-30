#!/bin/sh

# sudo apt install nvidia-driver-390

# basic stuff
sudo apt install git screen wget zlib1g-dev curl build-essential net-tools openssh-server
sudo apt install vim emacs xclip
sudo apt install net-tools
sudo apt install freeglut3 freeglut3-dev libxi-dev libxmu-dev
sudo apt install python3.7 python3.7-venv python3.7-doc binfmt-support
sudo apt install virtualenv

# sane desktop
sudo apt install xfce4 xfwm4-themes xfce4-power-manager xscreensaver-gl-extra  gconf-defaults-service xfce4-goodies
sudo apt install lightdm unity ubuntu-unity-desktop
sudo apt install qtile

# needed for xmonad stuff
sudo apt install libx11-dev libxinerama-dev libxrandr-dev libiw-dev
sudo apt install pkg-config libasound2-dev
sudo apt install libxft-dev libxml2-dev libxpm-dev libxpm4
sudo apt install scrot suckless-tools


# sudo ln -s "$(pwd)/usr/share/xsessions/xmonad.desktop" /usr/share/xsessions/
# sudo ln -s "$(pwd)/usr/local/bin/xmonad-session" /usr/local/bin/
# ln -s "$(pwd)/.xkb" $HOME
# ln -s "$(pwd)/xmonad-session-rc" ~/.xmonad
# ln -s "$(pwd)/xmonad.hs" ~/.xmonad
