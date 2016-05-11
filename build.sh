#!/bin/bash
set -eu

markdown index.md > index.html

tar -zcf /tmp/build.tar.gz .

scp /tmp/build.tar.gz web:/tmp/

ssh web "tar xzvf /tmp/build.tar.gz -C /var/www/tradlosetrondheim.no/www/lora-workshop/"
