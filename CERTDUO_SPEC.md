# CertDuo — Product & Technical Specification

## Overview

CertDuo is a Progressive Web Application (PWA) that provides a Duolingo-style learning experience for Microsoft certification preparation. It combines structured learning paths mapped to Microsoft Learn documentation with quiz-based reinforcement using spaced repetition.

**Target Certifications (V1):** AZ-900, AZ-104, MD-102, MS-102

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Framework | Next.js 14+ (App Router) | Single codebase for frontend + API |
| Language | TypeScript | Strict mode enabled |
| Styling | Tailwind CSS | With shadcn/ui component library |
| PWA | next-pwa (or @ducanh2912/next-pwa) | Service worker, manifest, install prompt |
| Database | PostgreSQL | Hosted via Supabase or Neon |
| ORM | Prisma | Type-safe database access |
| Auth | Microsoft Entra ID (Azure AD) via MSAL.js | OAuth 2.0 / OpenID Connect |
| Push Notifications | Web Push API via Firebase Cloud Messaging (FCM) | Daily learning reminders |
| Deployment | Vercel | Native Next.js support |
| Scraping (tooling) | Python (Playwright + BeautifulSoup) | Separate from main app, used to seed DB |

---

## Authentication

### Microsoft Sign-In (MSAL.js)

- Use `@azure/msal-react` and `@azure/msal-browser` for authentication
- Register app in Azure Portal (Entra ID) → App Registrations
- Required scopes: `User.Read`, `openid`, `profile`, `email`
- On sign-in, store the Microsoft user ID, display name, and email in our Users table
- Use Next.js middleware to protect authenticated routes
- Store session via secure HTTP-only cookies (next-auth with Azure AD provider is also acceptable)

### Auth Flow

1. User clicks "Sign in with Microsoft"
2. MSAL redirects to Microsoft login
3. On callback, create or update user record in our DB
4. Issue session token / cookie
5. Redirect to dashboard

---

## Database Schema (Prisma)

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// ─── Certifications ───

model Certification {
  id          String   @id @default(cuid())
  code        String   @unique // e.g., "AZ-900"
  name        String   // e.g., "Azure Fundamentals"
  description String?
  iconUrl     String?
  totalModules Int     @default(0)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  modules     Module[]
  questions   Question[]
  userCerts   UserCertification[]
  exams       Exam[]
}

model Module {
  id              String   @id @default(cuid())
  certificationId String
  title           String
  description     String?
  orderIndex      Int      // determines learning path order
  msLearnUrl      String?  // link to Microsoft Learn module
  createdAt       DateTime @default(now())

  certification   Certification @relation(fields: [certificationId], references: [id])
  topics          Topic[]
  questions       Question[]
}

model Topic {
  id          String   @id @default(cuid())
  moduleId    String
  title       String
  content     String?  // bite-sized summary for in-app reading
  msLearnUrl  String   // direct link to MS Learn page for this topic
  orderIndex  Int
  createdAt   DateTime @default(now())

  module      Module @relation(fields: [moduleId], references: [id])
  questions   Question[]
  userDocs    UserDocumentation[]
}

// ─── Questions ───

enum QuestionSource {
  MICROSOFT    // from Microsoft Learn practice assessments
  EXAMTOPICS   // from ExamTopics
  COMMUNITY    // future: user-submitted
}

enum QuestionType {
  SINGLE_CHOICE
  MULTIPLE_CHOICE
  TRUE_FALSE
  DRAG_DROP       // future
}

model Question {
  id              String         @id @default(cuid())
  certificationId String
  moduleId        String?
  topicId         String?
  questionText    String
  questionType    QuestionType   @default(SINGLE_CHOICE)
  answers         Json           // array of { id, text, isCorrect }
  explanation     String?        // why the correct answer is correct
  source          QuestionSource
  sourceUrl       String?        // original URL
  sourceIcon      String?        // icon identifier: "microsoft" | "examtopics"
  documentationLinks Json?       // array of { url, title } pointing to MS Learn docs
  difficulty      Int            @default(1) // 1-5
  communityScore  Float?         // ExamTopics community vote accuracy
  isActive        Boolean        @default(true)
  createdAt       DateTime       @default(now())
  updatedAt       DateTime       @updatedAt

  certification   Certification  @relation(fields: [certificationId], references: [id])
  module          Module?        @relation(fields: [moduleId], references: [id])
  topic           Topic?         @relation(fields: [topicId], references: [id])
  userProgress    UserQuestionProgress[]
}

// ─── Users ───

model User {
  id            String   @id @default(cuid())
  microsoftId   String   @unique
  email         String   @unique
  displayName   String
  avatarUrl     String?
  timezone      String?  @default("UTC")
  preferredTime String?  @default("08:00") // preferred notification time (HH:mm)
  tier          String   @default("free") // "free" | "pro" (future monetization)
  streakCount   Int      @default(0)
  lastActiveAt  DateTime?
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt

  certifications UserCertification[]
  questionProgress UserQuestionProgress[]
  documentation  UserDocumentation[]
  exams          Exam[]
  sessions       Session[]
  pushSubscriptions PushSubscription[]
}

model Session {
  id        String   @id @default(cuid())
  userId    String
  token     String   @unique
  expiresAt DateTime
  createdAt DateTime @default(now())

  user      User     @relation(fields: [userId], references: [id])
}

// ─── User Progress ───

model UserCertification {
  id              String   @id @default(cuid())
  userId          String
  certificationId String
  status          String   @default("active") // "active" | "completed" | "paused"
  currentModuleId String?
  percentComplete Float    @default(0)
  startedAt       DateTime @default(now())
  completedAt     DateTime?

  user            User          @relation(fields: [userId], references: [id])
  certification   Certification @relation(fields: [certificationId], references: [id])

  @@unique([userId, certificationId])
}

model UserQuestionProgress {
  id              String   @id @default(cuid())
  userId          String
  questionId      String

  // SM-2 Algorithm Fields
  status          String   @default("unseen") // "unseen" | "learning" | "review" | "mastered"
  easeFactor      Float    @default(2.5)
  interval        Int      @default(0) // days until next review
  repetitions     Int      @default(0)
  nextReviewDate  DateTime?
  lastAnsweredAt  DateTime?
  lastAnswerCorrect Boolean?
  timesAnswered   Int      @default(0)
  timesCorrect    Int      @default(0)

  user            User     @relation(fields: [userId], references: [id])
  question        Question @relation(fields: [questionId], references: [id])

  @@unique([userId, questionId])
}

model UserDocumentation {
  id        String   @id @default(cuid())
  userId    String
  topicId   String
  docUrl    String
  status    String   @default("unread") // "unread" | "read" | "confirmed"
  linkedQuestionId String? // the question that triggered this doc being added
  assignedAt DateTime @default(now())
  readAt     DateTime?
  confirmedAt DateTime?

  user      User  @relation(fields: [userId], references: [id])
  topic     Topic @relation(fields: [topicId], references: [id])

  @@unique([userId, topicId, docUrl])
}

// ─── Exams ───

model Exam {
  id              String   @id @default(cuid())
  userId          String
  certificationId String
  score           Float?   // percentage 0-100
  passed          Boolean? // score >= 70
  totalQuestions   Int
  correctAnswers  Int      @default(0)
  status          String   @default("in_progress") // "in_progress" | "completed"
  startedAt       DateTime @default(now())
  completedAt     DateTime?
  answers         Json?    // array of { questionId, selectedAnswer, isCorrect }

  user            User          @relation(fields: [userId], references: [id])
  certification   Certification @relation(fields: [certificationId], references: [id])
}

// ─── Push Notifications ───

model PushSubscription {
  id        String   @id @default(cuid())
  userId    String
  endpoint  String
  p256dh    String
  auth      String
  createdAt DateTime @default(now())

  user      User @relation(fields: [userId], references: [id])
}
```

---

## Spaced Repetition Algorithm (SM-2)

Implement the SM-2 algorithm for question scheduling. This is the algorithm used by Anki.

### Implementation

```typescript
// lib/sm2.ts

interface SM2Result {
  easeFactor: number;
  interval: number;
  repetitions: number;
  nextReviewDate: Date;
  status: "learning" | "review" | "mastered";
}

/**
 * SM-2 Spaced Repetition Algorithm
 * @param quality - Answer quality: 0-2 = incorrect, 3 = correct with difficulty, 4 = correct, 5 = perfect
 * @param currentEaseFactor - Current ease factor (starts at 2.5)
 * @param currentInterval - Current interval in days
 * @param currentRepetitions - Number of successful repetitions
 */
export function calculateSM2(
  quality: number, // 0-5
  currentEaseFactor: number,
  currentInterval: number,
  currentRepetitions: number
): SM2Result {
  let easeFactor = currentEaseFactor;
  let interval: number;
  let repetitions: number;

  if (quality >= 3) {
    // Correct answer
    if (currentRepetitions === 0) {
      interval = 1;
    } else if (currentRepetitions === 1) {
      interval = 3;
    } else {
      interval = Math.round(currentInterval * easeFactor);
    }
    repetitions = currentRepetitions + 1;
  } else {
    // Incorrect answer — reset
    interval = 1;
    repetitions = 0;
  }

  // Update ease factor
  easeFactor = easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02));
  easeFactor = Math.max(1.3, easeFactor); // minimum 1.3

  const nextReviewDate = new Date();
  nextReviewDate.setDate(nextReviewDate.getDate() + interval);

  // Determine status
  let status: SM2Result["status"];
  if (repetitions >= 5 && easeFactor >= 2.0) {
    status = "mastered";
  } else if (repetitions >= 1) {
    status = "review";
  } else {
    status = "learning";
  }

  return { easeFactor, interval, repetitions, nextReviewDate, status };
}
```

### Quality Scoring Rules

| User Action | Quality Score |
|-------------|--------------|
| Wrong answer, no idea | 0 |
| Wrong answer, recognized correct after seeing it | 1 |
| Wrong answer, but answer seemed familiar | 2 |
| Correct answer, with significant difficulty | 3 |
| Correct answer, with some hesitation | 4 |
| Correct answer, instant recall | 5 |

**Simplified mapping for our UX:**
- User answers **wrong** → quality = 1
- User answers **correct** (took time) → quality = 3
- User answers **correct** (quick) → quality = 5

Measure "quick" as answering within 10 seconds of the question appearing.

---

## Application Pages & Routes

```
/                           → Landing page (unauthenticated)
/auth/signin                → Microsoft sign-in page
/auth/callback              → OAuth callback handler
/dashboard                  → Main dashboard (authenticated)
/certifications             → Browse available certifications
/certifications/[code]      → Certification detail (e.g., /certifications/az-900)
/learn/[certCode]           → Daily learning session for a certification
/learn/[certCode]/review    → Review incorrect answers + documentation
/exam/[certCode]            → Final exam mode
/exam/[certCode]/results    → Exam results page
/progress                   → Overall progress dashboard
/settings                   → User settings (notification time, timezone, etc.)
```

---

## Core User Flows

### Flow 1: Onboarding

1. User lands on `/` → sees hero section explaining CertDuo
2. Clicks "Sign in with Microsoft" → redirected to Microsoft login
3. On first sign-in, shown certification picker → selects one or more certs
4. Redirected to `/dashboard`
5. Prompted to enable push notifications + set preferred learning time
6. Prompted to install PWA (browser install prompt)

### Flow 2: Daily Learning Session

1. User receives push notification: "☁️ Let's learn: AZ-900 — Cloud Concepts"
2. Clicks notification → opens `/learn/az-900`
3. **Reading Phase:**
   - Shown a bite-sized topic summary (2-3 paragraphs from the current module/topic)
   - "Continue Reading on Microsoft Learn →" link to full MS Learn page
   - "I've read this, continue →" button
4. **Quiz Phase:**
   - 1-2 questions from the current topic
   - Each question shows source badge: Microsoft icon (M) or ExamTopics icon (🌐)
   - User selects answer → submits
5. **If Correct:**
   - ✅ "Correct!" animation
   - SM-2 updates: schedule next review
   - Progress bar advances
   - "Continue" → next question or end of session
6. **If Incorrect:**
   - ❌ "Not quite" — shows correct answer + explanation
   - Shows list of relevant Microsoft Learn documentation links
   - Each doc link has a checkbox: "I've read and understood this"
   - User must confirm at least the primary doc link to continue
   - Question goes back into the review queue (SM-2 resets interval)
   - Documentation entries are created in UserDocumentation table
7. **Session Complete:**
   - Shows session summary: questions answered, accuracy %, streak count
   - "See your progress →" link

### Flow 3: Documentation Review

1. User navigates to `/learn/[certCode]/review`
2. Sees list of documentation they need to read (status: unread/read/confirmed)
3. For each doc:
   - Title + link to Microsoft Learn page
   - Which question it was linked to (with the question text shown)
   - "Mark as Read" → status becomes "read"
   - "I understand this, confirm" → status becomes "confirmed"
4. Once confirmed, the linked documentation is removed from the pending list
5. The associated question will appear again in a future session (based on SM-2 scheduling)

### Flow 4: Final Exam

**Triggered when:** All topics in a certification have been covered and the user has no pending documentation to review.

1. User sees "You're ready for the final exam!" prompt on dashboard or certification page
2. Clicks "Start Exam" → `/exam/[certCode]`
3. Exam presents ALL questions for the certification in random order
4. Timed (optional — can be toggled in settings)
5. User answers all questions → clicks "Submit Exam"
6. Results page shows:
   - Score: X/100 (percentage)
   - Pass threshold: 70%
   - **If passed (≥70%):** 🎉 Celebration! Certification marked as completed. Badge awarded.
   - **If failed (<70%):** Shows all incorrect questions with documentation links. Same flow as daily learning — must read docs, confirm understanding. Failed questions re-enter the spaced repetition queue. User can retake exam once all review is complete.

### Flow 5: Progress Dashboard

1. `/progress` shows:
   - Per-certification progress rings (% complete)
   - Current streak count + calendar heatmap
   - Questions mastered / in review / unseen counts
   - Weak areas (topics with lowest accuracy)
   - Documentation pending review count
   - Exam readiness indicator

---

## Push Notification System

### Setup

1. Register a Firebase project → get FCM server key + config
2. Service worker handles push events and shows notifications
3. On user sign-in, request notification permission
4. Store push subscription in `PushSubscription` table

### Notification Schedule

- User sets preferred time in settings (default: 08:00 local time)
- Server-side cron job (Vercel Cron or external) runs every 15 minutes
- Checks for users whose preferred time falls within the current 15-minute window
- Sends push notification via FCM

### Notification Content

```
Title: "☁️ Let's learn: AZ-900"
Body: "Cloud Concepts — 3 questions waiting for review"
Action: Opens /learn/az-900
```

If user has reviews due (from SM-2 scheduling), prioritize those:
```
Title: "🔄 Review time: AZ-104"
Body: "You have 5 questions to review today"
```

---

## Content Scraping System (Separate Python Project)

This is a standalone Python project in `/scraper` that seeds the database. It is NOT part of the Next.js app.

### Directory Structure

```
/scraper
  /scrapers
    microsoft_learn.py    # Scrapes MS Learn practice assessments
    examtopics.py         # Scrapes ExamTopics questions
  /processors
    question_parser.py    # Normalizes questions into standard format
    doc_mapper.py         # Maps questions to MS Learn documentation URLs
  /output
    az-900.json           # Scraped + processed output per cert
    az-104.json
    md-102.json
    ms-102.json
  seed_database.py        # Reads JSON files and inserts into PostgreSQL
  requirements.txt        # playwright, beautifulsoup4, psycopg2, etc.
  README.md
```

### Scraping Strategy

**Microsoft Learn Practice Assessments:**
- URL pattern: `https://learn.microsoft.com/en-us/credentials/certifications/[cert-name]/practice/assessment`
- Use Playwright (headless browser) — pages are JS-rendered
- Extract: question text, answer options, correct answer, explanation, related module links
- Mark source as `MICROSOFT`

**ExamTopics:**
- URL pattern: `https://www.examtopics.com/exams/microsoft/[cert-code]/view/`
- Use Playwright for pagination
- Extract: question text, answer options, most-voted correct answer, community vote percentage
- Mark source as `EXAMTOPICS`
- Store `communityScore` for confidence indication

### Output Format (JSON)

```json
{
  "certification": "AZ-900",
  "questions": [
    {
      "questionText": "Which cloud model uses shared infrastructure...",
      "questionType": "SINGLE_CHOICE",
      "answers": [
        { "id": "a", "text": "Public cloud", "isCorrect": true },
        { "id": "b", "text": "Private cloud", "isCorrect": false },
        { "id": "c", "text": "Hybrid cloud", "isCorrect": false },
        { "id": "d", "text": "Community cloud", "isCorrect": false }
      ],
      "explanation": "Public cloud uses shared infrastructure managed by a third-party provider...",
      "source": "MICROSOFT",
      "sourceUrl": "https://learn.microsoft.com/...",
      "documentationLinks": [
        {
          "url": "https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/...",
          "title": "Cloud deployment models"
        }
      ],
      "module": "Cloud Concepts",
      "topic": "Cloud Models",
      "difficulty": 1
    }
  ]
}
```

### Database Seeding

`seed_database.py` reads the JSON output files and:
1. Creates/updates Certification records
2. Creates/updates Module and Topic records
3. Upserts Question records (deduplicates by question text hash)
4. Links questions to modules and topics
5. Stores documentation links

Run with: `python seed_database.py --cert az-900 --input output/az-900.json`

---

## Question Source Badges

Questions must visually indicate their source:

- **Microsoft (M):** Blue square badge with white "M" — represents official Microsoft Learn content. High trust.
- **ExamTopics (🌐):** Globe icon badge — represents community-sourced content. Show community confidence score if available (e.g., "87% agree").
- **Community (future):** Different icon for user-submitted questions.

---

## PWA Configuration

### manifest.json

```json
{
  "name": "CertDuo",
  "short_name": "CertDuo",
  "description": "Duolingo-style Microsoft Certification Prep",
  "start_url": "/dashboard",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#0078D4",
  "orientation": "portrait",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

### Service Worker

- Cache app shell (HTML, CSS, JS) for fast loading
- Do NOT cache API responses (no offline mode in V1)
- Handle push notification events
- Handle notification click → open correct URL

---

## UI/UX Design Direction

### Visual Style

- Clean, modern, Microsoft Fluent-inspired design
- Primary color: Microsoft Blue (#0078D4)
- Accent color for correct: Green (#107C10)
- Accent color for incorrect: Red (#D13438)
- Card-based UI for questions and topics
- Progress rings/bars inspired by Duolingo
- Gamification: streak counter with fire emoji, XP points (future)

### Key Components to Build

1. **CertificationCard** — shows cert name, icon, progress ring, "Continue" button
2. **QuestionCard** — question text, answer options (radio/checkbox), source badge, submit button
3. **AnswerFeedback** — correct/incorrect animation, explanation, doc links
4. **ProgressRing** — circular progress indicator with percentage
5. **StreakBanner** — shows current streak count, last active date
6. **DocumentationList** — list of docs with read/confirmed status toggles
7. **ExamResults** — score display, pass/fail indicator, question breakdown
8. **NotificationPrompt** — asks user to enable notifications + set time
9. **InstallPrompt** — PWA install CTA

### Mobile-First

- All layouts designed mobile-first (primary use case is phone)
- Responsive breakpoints for tablet and desktop
- Touch-friendly tap targets (minimum 44x44px)
- Swipe gestures for navigating between questions (nice-to-have)

---

## API Routes

All API routes live under `/app/api/` in the Next.js app router.

### Auth
- `POST /api/auth/signin` — Initiate Microsoft OAuth
- `GET /api/auth/callback` — Handle OAuth callback
- `POST /api/auth/signout` — Clear session
- `GET /api/auth/me` — Get current user

### Certifications
- `GET /api/certifications` — List all certifications
- `GET /api/certifications/[code]` — Get certification detail with modules
- `POST /api/certifications/[code]/enroll` — Enroll user in certification
- `DELETE /api/certifications/[code]/enroll` — Unenroll

### Learning
- `GET /api/learn/[certCode]/session` — Get next learning session (topic + questions based on SM-2 scheduling)
- `POST /api/learn/[certCode]/answer` — Submit answer for a question. Body: `{ questionId, selectedAnswerId }`. Returns: correct/incorrect, explanation, doc links, updated SM-2 values.
- `GET /api/learn/[certCode]/review` — Get pending documentation to review
- `POST /api/learn/[certCode]/review/confirm` — Confirm documentation as read. Body: `{ docId }`

### Progress
- `GET /api/progress` — Get overall progress across all certs
- `GET /api/progress/[certCode]` — Get detailed progress for a certification
- `GET /api/progress/streak` — Get streak info

### Exams
- `POST /api/exam/[certCode]/start` — Start a final exam. Returns all questions.
- `POST /api/exam/[certCode]/submit` — Submit exam answers. Body: `{ answers: [{ questionId, selectedAnswerId }] }`. Returns: score, pass/fail, incorrect question details.
- `GET /api/exam/[certCode]/results/[examId]` — Get exam results

### Settings
- `GET /api/settings` — Get user settings
- `PATCH /api/settings` — Update settings (timezone, notification time, etc.)

### Push
- `POST /api/push/subscribe` — Save push subscription
- `DELETE /api/push/unsubscribe` — Remove push subscription

---

## Monetization Hooks (Build Now, Activate Later)

### User Tier System

The `tier` field on the User model supports future monetization:

- **Free tier:**
  - 1 active certification at a time
  - Maximum 10 questions per day
  - Basic progress tracking
  
- **Pro tier (future):**
  - All certifications simultaneously
  - Unlimited daily questions
  - Detailed analytics (accuracy trends, time-per-question, weak area breakdown)
  - Priority access to new question banks
  - Ad-free (if ads are ever added to free tier)

### Implementation Notes

- Add a `checkTierLimit()` middleware that gates features based on `user.tier`
- Store tier check results in the session to avoid DB lookups on every request
- Add Stripe integration placeholder: `/api/billing/checkout`, `/api/billing/webhook`
- Track daily question count per user (can be computed from `UserQuestionProgress.lastAnsweredAt`)

---

## Folder Structure (Next.js App)

```
/certduo
  /prisma
    schema.prisma
    /migrations
  /public
    manifest.json
    sw.js
    /icons
  /src
    /app
      layout.tsx              # Root layout with providers
      page.tsx                # Landing page
      /auth
        /signin/page.tsx
        /callback/page.tsx
      /dashboard/page.tsx
      /certifications
        page.tsx
        /[code]/page.tsx
      /learn
        /[certCode]
          page.tsx            # Daily learning session
          /review/page.tsx    # Documentation review
      /exam
        /[certCode]
          page.tsx            # Exam mode
          /results/[examId]/page.tsx
      /progress/page.tsx
      /settings/page.tsx
      /api
        /auth/[...]/route.ts
        /certifications/[...]/route.ts
        /learn/[...]/route.ts
        /progress/[...]/route.ts
        /exam/[...]/route.ts
        /settings/route.ts
        /push/[...]/route.ts
    /components
      /ui                    # shadcn/ui components
      /certification         # CertificationCard, CertificationList
      /question              # QuestionCard, AnswerFeedback, SourceBadge
      /progress              # ProgressRing, StreakBanner, Heatmap
      /documentation         # DocumentationList, DocCard
      /exam                  # ExamResults, ExamQuestion
      /layout                # Navbar, Sidebar, MobileNav
      /notifications         # NotificationPrompt, InstallPrompt
    /lib
      prisma.ts              # Prisma client singleton
      auth.ts                # MSAL configuration + helpers
      sm2.ts                 # SM-2 algorithm implementation
      push.ts                # Push notification helpers
      utils.ts               # General utilities
    /hooks
      useAuth.ts
      useLearningSession.ts
      useProgress.ts
    /types
      index.ts               # Shared TypeScript types
  /scraper                   # Python scraping project (see above)
  next.config.js
  tailwind.config.ts
  tsconfig.json
  package.json
  .env.local                 # DATABASE_URL, MSAL_CLIENT_ID, etc.
  README.md
```

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/certduo

# Microsoft Auth (Entra ID)
MSAL_CLIENT_ID=your-azure-app-client-id
MSAL_CLIENT_SECRET=your-azure-app-client-secret
MSAL_TENANT_ID=common
MSAL_REDIRECT_URI=http://localhost:3000/auth/callback

# Firebase (Push Notifications)
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
FIREBASE_SERVER_KEY=

# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
NODE_ENV=development
```

---

## Implementation Order (Suggested)

### Phase 1: Foundation
1. Initialize Next.js project with TypeScript, Tailwind, shadcn/ui
2. Set up Prisma + PostgreSQL database
3. Implement database schema + run migrations
4. Set up Microsoft authentication (MSAL)
5. Create basic layout, navigation, and route structure
6. Build landing page + auth flow

### Phase 2: Content
7. Build Python scraper for Microsoft Learn practice assessments
8. Build Python scraper for ExamTopics
9. Process and normalize scraped data into JSON
10. Build database seeding script
11. Seed database with AZ-900, AZ-104, MD-102, MS-102 content

### Phase 3: Core Learning
12. Build certification selection + enrollment
13. Implement SM-2 algorithm
14. Build daily learning session (topic reading + quiz)
15. Build answer feedback with documentation links
16. Build documentation review page
17. Build progress tracking API + dashboard

### Phase 4: Exam & Gamification
18. Build final exam mode
19. Build exam results page with review flow
20. Add streak tracking
21. Build progress rings and stats

### Phase 5: PWA & Notifications
22. Configure PWA (manifest, service worker, install prompt)
23. Set up Firebase Cloud Messaging
24. Build notification permission flow
25. Build server-side notification scheduler (cron)

### Phase 6: Polish
26. Mobile responsiveness pass
27. Loading states, error handling, edge cases
28. Performance optimization
29. Add monetization tier checks (gates only, no Stripe yet)
30. Testing + bug fixes

---

## Legal Considerations

- **Microsoft Learn content:** Practice assessments are publicly accessible. Questions may be subject to Microsoft's terms. Consider paraphrasing rather than verbatim copying. Link back to Microsoft Learn as the source.
- **ExamTopics:** Content is crowd-sourced and exists in a legal gray area. Microsoft has historically taken action against exam dump sites. Mitigate by:
  - Paraphrasing questions rather than copying verbatim
  - Always linking back to ExamTopics as the source
  - Making it clear these are "community practice questions"
  - Having a DMCA/takedown process ready
- **User data:** Comply with GDPR basics — allow data export and account deletion
- **Microsoft trademarks:** Don't imply official Microsoft endorsement. Add disclaimer.

---

## Key Metrics to Track (Future Analytics)

- Daily active users (DAU)
- Questions answered per day
- Average accuracy per certification
- Streak length distribution
- Exam pass rate
- Time to certification completion
- Retention (D1, D7, D30)
- Push notification open rate
