#!/bin/sh

git submodule update --init
git rm --cached  _theme_packages/tom
git submodule update --init
