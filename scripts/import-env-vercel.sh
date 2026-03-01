#!/usr/bin/env bash
# Reads .env.local and pushes every variable to Vercel (production + preview + development)
# Usage: bash scripts/import-env-vercel.sh

VERCEL=~/.npm-global/bin/vercel
ENV_FILE=".env.local"

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ $ENV_FILE not found. Run from project root."
  exit 1
fi

echo "📦 Importing $ENV_FILE → Vercel env vars..."
echo ""

while IFS= read -r line || [ -n "$line" ]; do
  # Skip blank lines and comments
  [[ "$line" =~ ^[[:space:]]*$ ]] && continue
  [[ "$line" =~ ^# ]] && continue

  KEY="${line%%=*}"
  VALUE="${line#*=}"

  # Skip if key is empty
  [ -z "$KEY" ] && continue

  echo "  Adding $KEY ..."
  # Add to all three environments
  printf '%s' "$VALUE" | $VERCEL env add "$KEY" production --yes 2>/dev/null
  printf '%s' "$VALUE" | $VERCEL env add "$KEY" preview --yes 2>/dev/null
  printf '%s' "$VALUE" | $VERCEL env add "$KEY" development --yes 2>/dev/null

done < "$ENV_FILE"

echo ""
echo "✅ Done! Check your Vercel dashboard → Settings → Environment Variables"
echo "   Then update MSAL_REDIRECT_URI, NEXT_PUBLIC_MSAL_REDIRECT_URI, and NEXT_PUBLIC_APP_URL to your production URL."
