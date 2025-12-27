#!/bin/bash

FILES=${*:-.}

# Use sed to remove trailing whitespace - works on both Linux and macOS
sed -i.sed 's/[[:space:]]*$//' $FILES && rm -f ${FILES}.sed

for FILE in $FILES; do
    if [[ "$FILE" == *.py ]]; then
        ruff format $FILE
        ruff check --fix $FILE
    elif [[ "$FILE" == *.md ]]; then
        mdformat $FILE
    fi
done
