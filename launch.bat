@echo off

if not exist "node_modules" (
    npm i
    echo:
    node src/index.js
    echo:
    @pause
)

node src/index.js
echo:
@pause
