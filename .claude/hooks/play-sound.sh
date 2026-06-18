#!/bin/bash
# Play a notification sound when Claude Code finishes responding

if [[ "$OSTYPE" == "darwin"* ]]; then
  afplay /System/Library/Sounds/Glass.aiff &
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
  powershell -c "(New-Object Media.SoundPlayer 'C:\Windows\Media\chimes.wav').PlaySync()" &
elif command -v paplay &>/dev/null; then
  paplay /usr/share/sounds/freedesktop/stereo/complete.oga &
elif command -v aplay &>/dev/null; then
  aplay /usr/share/sounds/freedesktop/stereo/complete.oga &
fi
