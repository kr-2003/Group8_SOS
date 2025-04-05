#!/bin/bash

# Morse code timing constants (in milliseconds)
DOT_DURATION=200
DASH_DURATION=$((DOT_DURATION * 3))
SYMBOL_SPACE=$DOT_DURATION
LETTER_SPACE=$((DOT_DURATION * 3))
WORD_SPACE=$((DOT_DURATION * 7))

# Function to vibrate for a specific duration
vibrate() {
    beep -l "$1" -f 800
}

# Function to play Morse code
play_morse_code() {
    local text="$1"
    
    # Convert text to Morse code using 'morse' tool
    morse_code=$(echo "$text" | morse)

    # Iterate through each character in the Morse code
    for char in $(echo "$morse_code" | sed 's/\(.\)/\1 /g'); do
        case "$char" in
            ".")
                vibrate $DOT_DURATION
                ;;
            "-")
                vibrate $DASH_DURATION
                ;;
            " ")
                sleep $((SYMBOL_SPACE / 1000))
                ;;
        esac
    done
}

# Example usage: SOS (... --- ...)
play_morse_code "SOS"
