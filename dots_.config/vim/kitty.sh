#!/bin/bash

# Check if the terminal is Kitty using the KITTY_PID environment variable
if [[ -n "$KITTY_PID" ]]; then
  kitty @ set-spacing padding=0 margin=0
  vim "$@"
  kitty @ set-spacing padding=default margin=default
else
  # Do nothing if not Kitty
  vim "$@"
fi
