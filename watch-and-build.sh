#!/bin/bash
# Watch frontend files and auto-rebuild for production (port 8000)

echo "🔄 Starting frontend watch & build for production..."
echo "📦 Port 8000 will serve the latest built version"
echo ""

cd "$(dirname "$0")/frontend"

# Initial build
echo "🏗️  Initial build..."
npm run build

# Watch for changes and rebuild
echo ""
echo "👀 Watching for changes in src/..."
echo "Press Ctrl+C to stop"
echo ""

while true; do
  # Use inotifywait if available, otherwise fall back to simple loop
  if command -v inotifywait &> /dev/null; then
    inotifywait -r -e modify,create,delete ./src ./public 2>/dev/null
  else
    sleep 5
  fi

  echo "🔄 Change detected, rebuilding..."
  npm run build
  echo "✅ Build complete at $(date '+%H:%M:%S')"
  echo ""
done
