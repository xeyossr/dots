if command -v satty &>/dev/null; then
	export SCREENSHOT_ANNOTATION_TOOL="satty"
elif command -v swappy &>/dev/null; then
	export SCREENSHOT_ANNOTATION_TOOL="swappy"
else
	export SCREENSHOT_ANNOTATION_TOOL=""
fi
