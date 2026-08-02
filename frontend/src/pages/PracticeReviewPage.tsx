import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api, type PracticeItem, type PracticeReviewResult } from '../lib/api';
import { QuizShell } from '../components/QuizShell';
import { SentenceInput, ReferenceBlock, FeedbackBlock, GREEN_TINT } from '../components/SentenceQuiz';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

// Grammar practice (文法練習): generated one-shot items targeting specific grammar points.
// Unlike sentence reviews there is NO SRS — the server scores only the first attempt
// (origin='practice' point rows) and completes the item on any correct attempt. A miss
// requeues the SAME item as a retry card; retries hit the same endpoint but are judged
// display-only server-side. The escape hatch calls /complete (mark done, nothing logged).
interface Card {
  item: PracticeItem;
  retry: boolean;
}

// English prompt + the target grammar chips (cued production: the point is SHOWN — varied
// production is the goal here; uncued recall is the sentence SRS's job).
function PracticePromptHero({ item, retry }: { item: PracticeItem; retry: boolean }) {
  return (
    <div
      className="flex shrink-0 flex-col items-center gap-3 py-12 text-center"
      style={{ backgroundColor: GREEN_TINT }}
    >
      <span className="font-mono text-[10px] tracking-[0.2em] text-muted-foreground uppercase">
        {retry ? 'もう一度 — 文法練習' : '文法練習 — 英語 → 日本語'}
      </span>
      <span className="max-w-2xl px-4 text-2xl">{item.english}</span>
      <div className="flex flex-wrap items-center justify-center gap-2 px-4">
        {item.targets.map((t) => (
          <span
            key={t.grammar_point_id}
            className="inline-flex items-baseline gap-1.5 border border-wk-sentence/40 bg-wk-sentence/10 px-2 py-0.5"
          >
            <span lang="ja" className="font-[family-name:var(--font-mincho)] text-sm text-wk-sentence">
              {t.key}
            </span>
            <span className="text-[11px] text-muted-foreground">{t.meaning_en}</span>
          </span>
        ))}
      </div>
    </div>
  );
}

export function PracticeReviewPage() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const [cards, setCards] = useState<Card[]>([]);
  const [index, setIndex] = useState(0);
  const [input, setInput] = useState('');
  const [result, setResult] = useState<PracticeReviewResult | null>(null);
  const [shake, setShake] = useState(false);
  const [correctCount, setCorrectCount] = useState(0);
  const [wrongCount, setWrongCount] = useState(0);
  const [adoptedIds, setAdoptedIds] = useState<Set<number>>(new Set());
  const [rejectOpen, setRejectOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const judgedAt = useRef(0); // guards the submit-Enter from also advancing

  const queueQuery = useQuery({ queryKey: ['practiceQueue'], queryFn: api.getPracticeQueue });

  const card = cards[index];

  // Same endpoint for first attempts and retries — the server decides what scores.
  const submitMutation = useMutation({
    mutationFn: (submitted: string) => api.submitPracticeReview(card.item.practice_id, submitted),
    onSuccess: (res) => {
      setResult(res);
      judgedAt.current = Date.now();
      if (res.scored) {
        queryClient.invalidateQueries({ queryKey: ['grammarPoints'] });
      }
    },
  });

  // Escape hatch on a retry miss: mark done server-side and move on.
  const completeMutation = useMutation({
    mutationFn: () => api.completePractice(card.item.practice_id),
    onSuccess: () => {
      reset();
      setIndex((i) => i + 1);
    },
  });

  // Adopt a generated sentence into the 1-1 SRS bank: plain create flow (validated,
  // grammar-extracted, enters as a pending lesson) — a tricky generated sentence becomes
  // permanent practice material, while dynamic practice keeps generating fresh variants.
  const adoptMutation = useMutation({
    mutationFn: () => api.createProductionSentence(card.item.english, result!.reference),
    onSuccess: () => {
      setAdoptedIds((prev) => new Set(prev).add(card.item.practice_id));
      queryClient.invalidateQueries({ queryKey: ['sentences'] });
      queryClient.invalidateQueries({ queryKey: ['sentenceLessons'] });
      queryClient.invalidateQueries({ queryKey: ['grammarPoints'] });
    },
  });

  // Reject a bad generated sentence with a why — the reason steers future generations.
  // Instant (no replacement is generated); all cards for the rejected id (incl. queued
  // retries) are dropped and the session continues with the rest.
  const rejectMutation = useMutation({
    mutationFn: () => api.rejectPractice(card.item.practice_id, rejectReason.trim()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['practiceQueue'] });
      const id = card.item.practice_id;
      // Removing already-passed cards with this id (an answered first attempt) shifts the
      // current position — compensate so no card is skipped.
      const removedBefore = cards.slice(0, index).filter((c) => c.item.practice_id === id).length;
      setCards((prev) => prev.filter((c) => c.item.practice_id !== id));
      setIndex((i) => i - removedBefore);
      reset();
    },
  });

  // Empty queue → the user can request one bonus item.
  const bonusMutation = useMutation({
    mutationFn: api.bonusPractice,
    onSuccess: (res) => {
      queryClient.setQueryData(['practiceQueue'], res);
      setCards(res.items.map((item) => ({ item, retry: false })));
      setIndex(0);
    },
  });

  // Build the queue once loaded.
  useEffect(() => {
    if (cards.length === 0 && queueQuery.data && queueQuery.data.items.length > 0) {
      setCards(queueQuery.data.items.map((item) => ({ item, retry: false })));
    }
  }, [cards.length, queueQuery.data]);

  const judged = result !== null;
  const judging = submitMutation.isPending;

  useEffect(() => {
    if (!judged) setTimeout(() => inputRef.current?.focus(), 50);
  }, [index, judged]);

  const reset = () => {
    setResult(null);
    setInput('');
    setRejectOpen(false);
    setRejectReason('');
    adoptMutation.reset(); // don't leak an adopt error/pending state onto the next card
    rejectMutation.reset();
  };

  const requeueRetry = () => {
    setCards((prev) => {
      const next = [...prev];
      next.splice(index + 1, 0, { item: card.item, retry: true });
      return next;
    });
  };

  // First attempt: tally + (on miss) requeue a retry. Retry: pass moves on, a miss
  // requeues again (escape = the /complete button, handled separately).
  const advance = () => {
    if (!result) return;
    if (card.retry) {
      if (!result.correct) requeueRetry();
    } else if (result.correct) {
      setCorrectCount((c) => c + 1);
    } else {
      setWrongCount((c) => c + 1);
      requeueRetry();
    }
    reset();
    setIndex((i) => i + 1);
  };

  // When a card is judged, Enter advances (outside the textarea).
  useEffect(() => {
    if (!judged) return;
    const handler = (e: KeyboardEvent) => {
      if (
        e.key === 'Enter' &&
        !(e.target instanceof HTMLTextAreaElement) &&
        !(e.target instanceof HTMLInputElement) &&
        Date.now() - judgedAt.current > 250
      ) {
        advance();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  });

  const loading = queueQuery.isLoading;
  const queueItems = queueQuery.data?.items ?? [];
  const gradedTotal = cards.filter((c) => !c.retry).length || queueItems.length;
  const done = correctCount + wrongCount;

  const finish = () => {
    queryClient.invalidateQueries({ queryKey: ['practiceQueue'] });
    queryClient.invalidateQueries({ queryKey: ['grammarPoints'] });
    navigate('/');
  };

  if (!loading && queueItems.length === 0 && cards.length === 0) {
    return (
      <QuizShell exitTo="/">
        <div className="flex flex-1 flex-col items-center justify-center space-y-4 text-center">
          <h2 className="text-2xl font-bold">練習項目はありません</h2>
          <p className="text-muted-foreground">数時間ごとに新しい練習文が用意されます。</p>
          {queueQuery.data?.bonus_available && (
            <Button size="lg" onClick={() => bonusMutation.mutate()} disabled={bonusMutation.isPending}>
              {bonusMutation.isPending ? '生成中…' : 'ボーナス練習を生成'}
            </Button>
          )}
          {bonusMutation.isError && (
            <p className="text-sm text-destructive">{(bonusMutation.error as Error).message}</p>
          )}
        </div>
      </QuizShell>
    );
  }

  if (loading || cards.length === 0) {
    return (
      <QuizShell exitTo="/">
        <div className="flex flex-1 animate-pulse items-center justify-center text-lg text-muted-foreground">
          練習を読み込み中...（生成に少し時間がかかることがあります）
        </div>
      </QuizShell>
    );
  }

  if (index >= cards.length) {
    return (
      <QuizShell exitTo="/">
        <div className="flex flex-1 flex-col items-center justify-center space-y-6">
          <div className="text-6xl">&#10003;</div>
          <h2 className="text-2xl font-bold">練習完了！</h2>
          <p className="text-muted-foreground">正解 {correctCount}件、不正解 {wrongCount}件</p>
          <Button size="lg" onClick={finish}>
            ダッシュボードへ
          </Button>
        </div>
      </QuizShell>
    );
  }

  return (
    <QuizShell
      exitTo="/"
      right={
        <span className="flex items-center gap-3">
          <span>{done} / {gradedTotal}</span>
          <span className="text-success">{correctCount}✓</span>
          {wrongCount > 0 && <span className="text-destructive">{wrongCount}✗</span>}
        </span>
      }
    >
      {/* Progress bar (first attempts only) */}
      <div className="flex h-2 shrink-0 overflow-hidden bg-secondary">
        {correctCount > 0 && (
          <div className="h-full bg-success/75 transition-all" style={{ width: `${(correctCount / gradedTotal) * 100}%` }} />
        )}
        {wrongCount > 0 && (
          <div className="h-full bg-destructive/75 transition-all" style={{ width: `${(wrongCount / gradedTotal) * 100}%` }} />
        )}
      </div>

      <PracticePromptHero item={card.item} retry={card.retry} />

      <div className="mx-auto w-full max-w-2xl flex-1 p-4">
        <SentenceInput
          ref={inputRef}
          value={input}
          onChange={setInput}
          onEnter={() => !judged && submit()}
          disabled={judged || judging}
          shake={shake}
          onAnimationEnd={() => setShake(false)}
        />

        {!judged && (
          <div className="flex justify-center pt-4">
            <Button size="lg" onClick={submit} disabled={!input.trim() || judging}>
              {judging ? '判定中…' : '提出'}
              {!judging && (
                <kbd className="ml-2 bg-primary-foreground/20 px-1.5 py-0.5 font-mono text-[10px]">Enter</kbd>
              )}
            </Button>
          </div>
        )}

        {judged && result && (
          <div className="space-y-4 pt-5">
            <div className="text-center">
              <span className={cn('text-xl font-bold', result.correct ? 'text-success' : 'text-destructive/80')}>
                {result.correct ? '正解！' : '不正解'}
              </span>
            </div>

            <ReferenceBlock reference={result.reference} tone={result.correct ? 'correct' : 'wrong'} />

            {/* Adopt into the 1-1 bank — a sentence that threw you off is prime SRS material. */}
            <div className="flex justify-end">
              {adoptedIds.has(card.item.practice_id) ? (
                <span className="font-mono text-[10px] uppercase tracking-wider text-wk-sentence">
                  1-1練習に追加済み ✓
                </span>
              ) : (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => adoptMutation.mutate()}
                  disabled={adoptMutation.isPending}
                  className="text-muted-foreground"
                >
                  {adoptMutation.isPending ? '追加中…' : '＋ この文を1-1練習に追加'}
                </Button>
              )}
            </div>
            {adoptMutation.isError && (
              <p className="text-right text-xs text-destructive">
                {(adoptMutation.error as Error).message}
              </p>
            )}

            <FeedbackBlock feedback={result.feedback} />

            {/* Target-point verdicts — includes "required but not used" when a target was dodged. */}
            {result.point_results.some((p) => !p.ok) && (
              <div className="space-y-1">
                <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                  文法ミス
                </span>
                {result.point_results
                  .filter((p) => !p.ok)
                  .map((p) => (
                    <div
                      key={p.key}
                      className="flex items-baseline gap-2 border-l-2 border-destructive/50 bg-destructive/5 px-3 py-1.5"
                    >
                      <span
                        lang="ja"
                        className="shrink-0 font-[family-name:var(--font-mincho)] text-sm text-destructive"
                      >
                        {p.key}
                      </span>
                      {p.feedback && (
                        <span className="min-w-0 text-xs text-muted-foreground">
                          {p.feedback}
                        </span>
                      )}
                    </div>
                  ))}
              </div>
            )}

            <div className="flex items-center justify-center gap-2 pt-1">
              <Button size="lg" onClick={() => advance()}>
                {result.correct ? '続ける' : '続ける（もう一度）'}
                <kbd className="ml-2 bg-primary-foreground/20 px-1.5 py-0.5 font-mono text-[10px]">Enter</kbd>
              </Button>
              {/* Retry-miss escape: mark the item done server-side (nothing more is logged —
                  the first attempt already scored) and stop the requeue loop. */}
              {card.retry && !result.correct && (
                <Button
                  size="lg"
                  variant="outline"
                  onClick={() => completeMutation.mutate()}
                  disabled={completeMutation.isPending}
                >
                  正解として進む
                </Button>
              )}
            </div>
          </div>
        )}

        {submitMutation.isError && !judged && (
          <p className="pt-3 text-center text-sm text-destructive">
            {(submitMutation.error as Error).message}
          </p>
        )}

        {/* Reject a bad generated sentence (unknown vocab, loanword soup, unnatural...) —
            the reason is fed to future generations; a replacement arrives immediately. */}
        <div className="pt-8">
          {rejectOpen ? (
            <div className="space-y-2">
              <Input
                autoFocus
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="なぜダメ？（例：知らない単語が多すぎる）— 次回の生成に反映されます"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && rejectReason.trim() && !rejectMutation.isPending) {
                    e.stopPropagation();
                    rejectMutation.mutate();
                  }
                }}
              />
              <div className="flex justify-end gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setRejectOpen(false)}
                  disabled={rejectMutation.isPending}
                >
                  キャンセル
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => rejectMutation.mutate()}
                  disabled={!rejectReason.trim() || rejectMutation.isPending}
                >
                  {rejectMutation.isPending ? '却下中…' : '却下する'}
                </Button>
              </div>
              {rejectMutation.isError && (
                <p className="text-right text-xs text-destructive">
                  {(rejectMutation.error as Error).message}
                </p>
              )}
            </div>
          ) : (
            <div className="flex justify-end">
              <Button
                variant="ghost"
                size="sm"
                className="text-muted-foreground/60"
                onClick={() => setRejectOpen(true)}
              >
                この文を却下
              </Button>
            </div>
          )}
        </div>
      </div>
    </QuizShell>
  );

  function submit() {
    if (!input.trim() || judging || judged) return;
    submitMutation.mutate(input.trim());
  }
}
