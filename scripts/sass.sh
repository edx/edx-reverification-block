#!/usr/bin/env bash

# Left-to-right sass
./node_modules/node-sass/bin/node-sass ./edx_reverification_block/xblock/static/sass/reverification-ltr.scss ./edx_reverification_block/xblock/static/reverification-ltr.min.css --output-style compressed

# Right-to-left sass
./node_modules/node-sass/bin/node-sass ./edx_reverification_block/xblock/static/sass/reverification-rtl.scss ./edx_reverification_block/xblock/static/reverification-rtl.min.css --output-style compressed
