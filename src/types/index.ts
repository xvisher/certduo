// ─── Enums ───

export type QuestionSource = "MICROSOFT" | "EXAMTOPICS" | "COMMUNITY";
export type QuestionType = "SINGLE_CHOICE" | "MULTIPLE_CHOICE" | "TRUE_FALSE" | "DRAG_DROP";
export type QuestionStatus = "unseen" | "learning" | "review" | "mastered";
export type DocStatus = "unread" | "read" | "confirmed";
export type CertStatus = "active" | "completed" | "paused";
export type ExamStatus = "in_progress" | "completed";
export type UserTier = "free" | "pro";

// ─── Answer ───

export interface Answer {
  id: string;
  text: string;
  isCorrect: boolean;
}

// ─── Documentation Link ───

export interface DocLink {
  url: string;
  title: string;
}

// ─── Certification ───

export interface Certification {
  id: string;
  code: string;
  name: string;
  description?: string;
  iconUrl?: string;
  totalModules: number;
  createdAt: string;
  updatedAt: string;
}

// ─── Module ───

export interface Module {
  id: string;
  certificationId: string;
  title: string;
  description?: string;
  orderIndex: number;
  msLearnUrl?: string;
  topics?: Topic[];
}

// ─── Topic ───

export interface Topic {
  id: string;
  moduleId: string;
  title: string;
  content?: string;
  msLearnUrl: string;
  orderIndex: number;
}

// ─── Question ───

export interface Question {
  id: string;
  certificationId: string;
  moduleId?: string;
  topicId?: string;
  questionText: string;
  questionType: QuestionType;
  answers: Answer[];
  explanation?: string;
  source: QuestionSource;
  sourceUrl?: string;
  sourceIcon?: string;
  documentationLinks?: DocLink[];
  difficulty: number;
  communityScore?: number;
  isActive: boolean;
}

// ─── User ───

export interface User {
  id: string;
  microsoftId: string;
  email: string;
  displayName: string;
  avatarUrl?: string;
  timezone: string;
  preferredTime: string;
  tier: UserTier;
  streakCount: number;
  lastActiveAt?: string;
  createdAt: string;
}

// ─── User Progress ───

export interface UserCertification {
  id: string;
  userId: string;
  certificationId: string;
  status: CertStatus;
  currentModuleId?: string;
  percentComplete: number;
  startedAt: string;
  completedAt?: string;
  certification?: Certification;
}

export interface UserQuestionProgress {
  id: string;
  userId: string;
  questionId: string;
  status: QuestionStatus;
  easeFactor: number;
  interval: number;
  repetitions: number;
  nextReviewDate?: string;
  lastAnsweredAt?: string;
  lastAnswerCorrect?: boolean;
  timesAnswered: number;
  timesCorrect: number;
}

export interface UserDocumentation {
  id: string;
  userId: string;
  topicId: string;
  docUrl: string;
  status: DocStatus;
  linkedQuestionId?: string;
  assignedAt: string;
  readAt?: string;
  confirmedAt?: string;
  topic?: Topic;
}

// ─── Session ───

export interface LearningSession {
  topic: Topic;
  questions: Question[];
  reviewCount: number;
}

export interface AnswerResult {
  correct: boolean;
  correctAnswerIds: string[];
  explanation?: string;
  documentationLinks?: DocLink[];
  sm2Update: {
    status: QuestionStatus;
    nextReviewDate: string;
    interval: number;
  };
}

// ─── Exam ───

export interface ExamAnswer {
  questionId: string;
  selectedAnswerIds: string[];
  isCorrect: boolean;
}

export interface ExamResult {
  id: string;
  score: number;
  passed: boolean;
  totalQuestions: number;
  correctAnswers: number;
  incorrectQuestions: Array<{
    question: Question;
    selectedAnswerIds: string[];
    documentationLinks?: DocLink[];
  }>;
  completedAt: string;
}

// ─── Progress ───

export interface ProgressStats {
  certification: Certification;
  userCert?: UserCertification;
  totalQuestions: number;
  mastered: number;
  reviewing: number;
  learning: number;
  unseen: number;
  pendingDocs: number;
  examReady: boolean;
}

// ─── API Responses ───

export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

// ─── Notification ───

export interface PushSubscriptionData {
  endpoint: string;
  p256dh: string;
  auth: string;
}
