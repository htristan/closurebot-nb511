#!/bin/bash

function_name=$(jq -r .function_name config.json)
echo "FUNCTION_NAME=$function_name" >> $GITHUB_ENV