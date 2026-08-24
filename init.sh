#!/bin/bash
[ ! -e ./.env ] && cp -p env.sample .env && echo "Created .env from env.sample! Please check"

. .env

if [ -z "$GITHUB_USER" ]; then
    pynoser_repo="git@github.com:Herrminator/pynoser-python3.git"
    ssh git@github.com 2>&1 | grep success > /dev/null ||\
      pynoser_repo="https://github.com/Herrminator/pynoser-python3.git"
else
    pynoser_repo="https://$GITHUB_USER@github.com/Herrminator/pynoser-python3.git"
fi
  
# create empty files if necessary to make docker file volumes work
touch ./data/logs/uwsgi.log
touch ./data/logs/cron.log
touch ./data/logs/nginx/error.log

# the weirdest symlink of all (creates /home/johler/develop/python/django/pynoser/data in container)
ln -sf /data ./data
# more no-existent symlinks ;)
# /opt/pynoser/pynoser/util/pywrap

# Retrieve required scripts from pynoser-python3
scripts="pynoser-admin pynoser-sh pynoser-cron-sh pynoser-errreset pynoser-randupd docker.compose.up docker.compose.down"

mkdir -p ./tmp

if [ "$1" == "-r" ]; then
    rm $scripts
    exit
fi

if [[ ! -L "pynoser-admin" || "$1" == "-f" ]]; then
    cd pynoser-scripts
    # not supported by github :(
    # git archive --remote="$pynoser_repo" HEAD $scripts | tar x0

    git clone $pynoser_repo pynoser.tmp || exit
    cd pynoser.tmp || exit
    cp -p $scripts ..
    cp -p doc/restore ../../tmp
    cat   doc/chown.sh | sed -r 's/uwsgi=102/uwsgi=1000/' > ../../data/chown.sh
    chmod +x ../../data/chown.sh
    cd ..
    rm -rf pynoser.tmp
    cd ..
    for s in $scripts; do
      ln -sf "pynoser-scripts/$s" .
    done
else
    echo "Script links seem to exist. Use '-f' to overwrite"
fi
