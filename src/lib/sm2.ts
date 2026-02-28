export interface SM2Result {
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
  quality: number,
  currentEaseFactor: number,
  currentInterval: number,
  currentRepetitions: number
): SM2Result {
  let easeFactor = currentEaseFactor;
  let interval: number;
  let repetitions: number;

  if (quality >= 3) {
    if (currentRepetitions === 0) {
      interval = 1;
    } else if (currentRepetitions === 1) {
      interval = 3;
    } else {
      interval = Math.round(currentInterval * easeFactor);
    }
    repetitions = currentRepetitions + 1;
  } else {
    interval = 1;
    repetitions = 0;
  }

  easeFactor = easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02));
  easeFactor = Math.max(1.3, easeFactor);

  const nextReviewDate = new Date();
  nextReviewDate.setDate(nextReviewDate.getDate() + interval);

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

/**
 * Map simple user actions to SM-2 quality scores
 * "quick" = answered within 10 seconds
 */
export function getQualityScore(correct: boolean, quick: boolean): number {
  if (!correct) return 1;
  if (quick) return 5;
  return 3;
}
