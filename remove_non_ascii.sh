#!/bin/bash

LC_ALL=C tr -dc '\0-\177' <"$1" >"$2" && mv "$2" "$1"