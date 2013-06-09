#!/bin/sh

set -e 
mkdir -p ~/.local/share/gedit/plugins
cp *.plugin ~/.local/share/gedit/plugins/.
cp -R smartbox ~/.local/share/gedit/plugins/.
