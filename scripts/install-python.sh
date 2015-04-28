#!/usr/bin/env bash

cd `dirname $BASH_SOURCE` && cd ..

echo "Installing Python requirements..."
pip install -q -r requirements/dev.txt

echo "Installing the Reverification XBlock..."
cat <<EOF | python -
import pkg_resources
import sys
try:
    pkg_resources.require('edx-reverification-block')
except pkg_resources.DistributionNotFound:
    sys.exit(1)
EOF
REVERIFICATION_MISSING=$?
if [[ $REVERIFICATION_MISSING -eq 1 ]]; then
    pip install -q -e .
    echo "Installed."
else
    echo "Already installed."
fi
