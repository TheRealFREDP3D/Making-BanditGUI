#!/bin/bash
# Install npm dependencies
npm install
# Create directories for node_modules if they don't exist
mkdir -p static/js/xterm
# Copy xterm.js files to static directory
cp -r node_modules/xterm/css/xterm.css static/
cp -r node_modules/xterm/lib/xterm.js static/js/
cp -r node_modules/xterm-addon-fit/lib/xterm-addon-fit.js static/js/
cp -r node_modules/xterm-addon-web-links/lib/xterm-addon-web-links.js static/js/
