# CertDuo

Duolingo-style Microsoft Certification Preparation PWA. Learn, quiz, and certify for AZ-900, AZ-104, MD-102, and MS-102.

## Features

- **Spaced Repetition (SM-2)**: Questions are scheduled at optimal review intervals
- **Microsoft Learn Integration**: Bite-sized topic summaries with links to official docs
- **Dual Question Sources**: Microsoft Learn practice assessments + ExamTopics community questions
- **Source Badges**: Visual indicators for Microsoft (M) and ExamTopics (🌐) questions
- **Documentation Review**: Failed questions generate required reading lists
- **Final Exam Mode**: Full exam simulation with pass/fail threshold (70%)
- **Daily Streaks**: Learning habit tracking with push notification reminders
- **PWA**: Installable as a home screen app
- **Microsoft Sign-In**: Entra ID / Azure AD OAuth authentication

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16 (App Router) |
| Language | TypeScript (strict) |
| Styling | Tailwind CSS v4 |
| Database | PostgreSQL + Prisma 5 |
| Auth | Microsoft MSAL v5 |
| PWA | @ducanh2912/next-pwa |
| Push | Web Push API (VAPID) |
| Deployment | Vercel |

## Getting Started

### 1. Install dependencies

```bash
npm install
```

### 2. Set up environment variables

Edit `.env.local` with your values:

Required variables:
- `DATABASE_URL` — PostgreSQL connection string
- `MSAL_CLIENT_ID` / `NEXT_PUBLIC_MSAL_CLIENT_ID` — Azure app registration client ID
- `MSAL_CLIENT_SECRET` — Azure app client secret
- `SESSION_SECRET` — Random 32+ char secret (`openssl rand -base64 32`)
- VAPID keys (`npx web-push generate-vapid-keys`)

### 3. Set up Azure App Registration

1. Go to Azure Portal → Entra ID → App Registrations
2. Create a new registration
3. Add redirect URI: `http://localhost:3000/auth/callback` (Web platform)
4. Copy client ID and create a client secret
5. Add API permissions: `User.Read`, `openid`, `profile`, `email`

### 4. Set up database

```bash
npm run db:push      # Push schema (development)
# or
npm run db:migrate   # Create migration files
```

### 5. Seed questions (requires scraper)

```bash
cd scraper
pip install -r requirements.txt
playwright install chromium
python run_scraper.py --cert az-900
python seed_database.py --cert AZ-900 --input output/az-900.json
```

See `scraper/README.md` for full documentation.

### 6. Run development server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Database Scripts

```bash
npm run db:generate    # Regenerate Prisma client
npm run db:migrate     # Create and run migrations
npm run db:push        # Push schema (dev only)
npm run db:studio      # Open Prisma Studio GUI
```

## PWA Icons

Place icons in `public/icons/`: `icon-192.png`, `icon-512.png`, `icon-maskable-512.png`

## Deployment (Vercel)

1. Push to GitHub and import to Vercel
2. Set all environment variables in Vercel dashboard
3. Add production redirect URI to Azure app registration
4. `vercel.json` cron runs notification scheduler every 15 minutes

## Legal

Not affiliated with or endorsed by Microsoft Corporation. See `CERTDUO_SPEC.md` for legal notes.
