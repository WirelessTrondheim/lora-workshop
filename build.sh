#!/bin/bash
set -eu

markdown README.md > index.html

tar --exclude-vcs -zcf /tmp/build.tar.gz .

scp /tmp/build.tar.gz web:/tmp/

ssh web "tar xzvf /tmp/build.tar.gz -C /var/www/tradlosetrondheim.no/www/lora-workshop/"
