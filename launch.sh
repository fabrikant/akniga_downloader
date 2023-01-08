#!/bin/bash

if [ ! -d "node_modules" ]; then
    npm i
    echo
    node src/index.js
    echo
    read -p "Press enter to continue..."
else
    node src/index.js
    echo
    read -p "Press enter to continue..."
fi
