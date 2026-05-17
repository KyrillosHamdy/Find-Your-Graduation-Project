"use client";
import Link from "next/link";
import styles from "./page.module.css";

export default function Home() {
  return (
    <main className={styles.main}>
      {/* Header */}
      <header className={styles.header}>
        <span className={`${styles.logo} mono`}>GP_ADVISOR</span>
        <span className={styles.badge}>Powered by Gemini Flash</span>
      </header>

      {/* Hero */}
      <section className={styles.hero}>
        <div className={styles.heroEyebrow}>
          <span className={styles.dot} />
          <span className="mono">For CS Students</span>
        </div>

        <h1 className={styles.heroTitle}>
          Find your <span className="serif">graduation</span>
          <br />
          project in minutes.
        </h1>

        <p className={styles.heroSubtitle}>
          One form. Five grounded ideas. Each backed by a real research paper.
          No fabrication. No "coming soon." No shallow suggestions.
        </p>

        <Link href="/onboard" className={styles.cta}>
          Start — it's free
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </Link>
      </section>

      {/* Feature grid */}
      <section className={styles.features}>
        {FEATURES.map((f, i) => (
          <div key={i} className={styles.featureCard} style={{ animationDelay: `${i * 0.1}s` }}>
            <span className={styles.featureIcon}>{f.icon}</span>
            <h3 className={styles.featureTitle}>{f.title}</h3>
            <p className={styles.featureDesc}>{f.desc}</p>
          </div>
        ))}
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <span className="mono" style={{ color: "var(--text-muted)", fontSize: 12 }}>
          Session data is ephemeral — nothing is stored permanently.
        </span>
      </footer>
    </main>
  );
}

const FEATURES = [
  {
    icon: "◈",
    title: "Two-step reasoning",
    desc: "Gemini first shortlists 10 candidates, then expands the best 5 — not a random top-5.",
  },
  {
    icon: "◉",
    title: "Real paper grounding",
    desc: "Every idea cites a real paper. arXiv validates each title and author before you see it.",
  },
  {
    icon: "◫",
    title: "Blueprint on demand",
    desc: "Click any idea to expand: What the project is, Why it matters, How to build it.",
  },
  {
    icon: "◌",
    title: "Tailored to you",
    desc: "Skill level, timeline, stack, and interests shape every result — not just a generic list.",
  },
];
