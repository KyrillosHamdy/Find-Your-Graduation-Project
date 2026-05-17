"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { Card, Blueprint, expandCard } from "@/lib/api";
import styles from "./board.module.css";

function DifficultyBadge({ level }: { level: string }) {
  return (
    <span className={`${styles.diffBadge} ${styles[`diff_${level}`]} mono`}>
      {level}
    </span>
  );
}


function PaperBadge({ paper }: { paper: Card["paper"] }) {
  const content = (
    <span className={styles.paperInfo}>
      <span className={`${styles.paperLabel} mono`}>
        {paper.verified ? "verified paper" : "suggested paper"}
      </span>
      <span className={styles.paperTitle}>{paper.title}</span>
      <span className={styles.paperMeta}>
        {paper.first_author_lastname}, {paper.year}
      </span>
    </span>
  );

  if (paper.verified && paper.arxiv_url) {
    return (
      <a href={paper.arxiv_url} target="_blank" rel="noopener noreferrer" className={styles.paperLink}>
        {content}
      </a>
    );
  }
  return content;
}

function BlueprintView({ blueprint }: { blueprint: Blueprint }) {
  return (
    <div className={styles.blueprint}>
      {/* WHAT */}
      <div className={styles.bpSection}>
        <h4 className={styles.bpLabel}>◈ WHAT</h4>
        <p className={styles.bpText}>{blueprint.what.description}</p>
        <p className={styles.bpProblem}>{blueprint.what.problem_statement}</p>
        <div className={styles.scopeGrid}>
          <div>
            <span className={styles.scopeHead}>In scope</span>
            <ul className={styles.scopeList}>
              {blueprint.what.in_scope.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
          <div>
            <span className={styles.scopeHead}>Out of scope</span>
            <ul className={`${styles.scopeList} ${styles.outScope}`}>
              {blueprint.what.out_of_scope.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* WHY */}
      <div className={styles.bpSection}>
        <h4 className={styles.bpLabel}>◉ WHY</h4>
        <p className={styles.bpText}>{blueprint.why.importance}</p>
        <p className={styles.bpText}>{blueprint.why.paper_relevance}</p>
        <div className={styles.fitBox}>
          <span className={styles.fitLabel}>Your fit</span>
          <p>{blueprint.why.student_fit}</p>
        </div>
      </div>

      {/* HOW */}
      <div className={styles.bpSection}>
        <h4 className={styles.bpLabel}>◫ HOW</h4>
        <p className={styles.bpText}>{blueprint.how.architecture_overview}</p>

        <span className={styles.scopeHead}>Tech stack</span>
        <div className={styles.stackGrid}>
          {blueprint.how.stack.map((s, i) => (
            <div key={i} className={styles.stackItem}>
              <span className={`${styles.stackTool} mono`}>{s.tool}</span>
              <span className={styles.stackReason}>{s.reason}</span>
            </div>
          ))}
        </div>

        <span className={styles.scopeHead}>Phases</span>
        <div className={styles.phases}>
          {blueprint.how.phases.map((ph) => (
            <div key={ph.phase} className={styles.phase}>
              <span className={`${styles.phaseNum} mono`}>{String(ph.phase).padStart(2, "0")}</span>
              <div>
                <span className={styles.phaseName}>{ph.name}</span>
                <p className={styles.phaseDesc}>{ph.description}</p>
              </div>
            </div>
          ))}
        </div>

        <span className={styles.scopeHead}>Risks</span>
        <div className={styles.risks}>
          {blueprint.how.risks.map((r, i) => (
            <div key={i} className={styles.risk}>
              <p className={styles.riskText}>⚠ {r.risk}</p>
              <p className={styles.mitigation}>{r.mitigation}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function IdeaCard({
  card,
  index,
  sessionId,
}: {
  card: Card;
  index: number;
  sessionId: string;
}) {
  const [blueprint, setBlueprint] = useState<Blueprint | null>(null);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);

  async function handleExpand() {
    if (open && blueprint) {
      setOpen(false);
      return;
    }
    if (blueprint) {
      setOpen(true);
      return;
    }
    setLoading(true);
    try {
      const res = await expandCard(sessionId, card.id);
      setBlueprint(res.blueprint);
      setOpen(true);
    } finally {
      setLoading(false);
    }
  }

  return (
    <article
      className={styles.card}
      style={{ animationDelay: `${index * 0.08}s` }}
    >
      {/* Card header */}
      <div className={styles.cardTop}>
        <div className={styles.cardMeta}>
          <span className={`mono ${styles.cardNum}`}>
            {String(index + 1).padStart(2, "0")}
          </span>
          <span className={`mono ${styles.researchArea}`}>
            {card.research_area}
          </span>
        </div>
        <DifficultyBadge level={card.difficulty} />
      </div>

      {/* Title + tagline */}
      <h2 className={styles.cardTitle}>{card.title}</h2>
      <p className={styles.tagline}>{card.tagline}</p>

      {/* Description */}
      <p className={styles.description}>{card.description}</p>

      {/* Stack pills */}
      <div className={styles.stackPills}>
        {card.stack.map((s) => (
          <span key={s} className={`mono ${styles.stackPill}`}>{s}</span>
        ))}
      </div>

      {/* Footer */}
      <div className={styles.cardFooter}>
        <div className={styles.cardFooterLeft}>
          <PaperBadge paper={card.paper} />
          <span className={styles.timelineInfo}>
            <span className={`${styles.timelineLabel} mono`}>timeline</span>
            <span className={styles.timelineValue}>
              About {card.estimated_weeks} weeks
            </span>
          </span>
        </div>
        <button onClick={handleExpand} className={styles.expandBtn} disabled={loading}>
          {loading ? (
            <span className={styles.miniSpinner} />
          ) : open ? (
            "↑ Close"
          ) : (
            "Expand →"
          )}
        </button>
      </div>

      {/* Fit reason */}
      <p className={styles.fitReason}>✦ {card.fit_reason}</p>

      {/* Blueprint */}
      {open && blueprint && <BlueprintView blueprint={blueprint} />}
    </article>
  );
}

function BoardContent() {
  const params = useSearchParams();
  const sessionId = params.get("session") ?? "";
  const rawData = params.get("data") ?? "[]";

  let cards: Card[] = [];
  try {
    cards = JSON.parse(decodeURIComponent(rawData));
  } catch {}

  if (!cards.length) {
    return (
      <div className={styles.empty}>
        <p>No results found. <a href="/onboard">Go back</a> and try again.</p>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <a href="/" className={`mono ${styles.back}`}>← GP_ADVISOR</a>
        <div className={styles.headerRight}>
          <span className={styles.resultCount}>5 ideas found</span>
          <a href="/onboard" className={styles.newSearch}>New search</a>
        </div>
      </header>

      <div className={styles.intro}>
        <h1>Your graduation project ideas</h1>
        <p>Click <strong>Expand</strong> on any card to get the full What / Why / How blueprint.</p>
      </div>

      <div className={styles.board}>
        {cards.map((card, i) => (
          <IdeaCard key={card.id} card={card} index={i} sessionId={sessionId} />
        ))}
      </div>
    </div>
  );
}

export default function BoardPage() {
  return (
    <Suspense fallback={<div className={styles.loading}>Loading…</div>}>
      <BoardContent />
    </Suspense>
  );
}
