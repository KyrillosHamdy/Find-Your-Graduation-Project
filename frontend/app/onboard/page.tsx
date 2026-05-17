"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { getRecommendations, IntentProfile } from "@/lib/api";
import styles from "./onboard.module.css";

const DOMAINS = [
  "NLP", "Computer Vision", "Machine Learning", "Deep Learning",
  "Cybersecurity", "Web Development", "Mobile", "Cloud & DevOps",
  "Data Engineering", "Robotics", "IoT", "Blockchain",
  "Bioinformatics", "Distributed Systems", "AR/VR",
];

const STACKS = [
  "Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust",
  "React", "Next.js", "FastAPI", "Django", "Node.js",
  "PyTorch", "TensorFlow", "Hugging Face",
  "Docker", "Kubernetes", "AWS", "PostgreSQL", "MongoDB",
];

export default function OnboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [profile, setProfile] = useState<IntentProfile>({
    domains: [],
    skill_level: "intermediate",
    months_available: 6,
    team_size: 2,
    preferred_stack: [],
    interests_text: "",
    avoid_text: "",
  });

  function toggleDomain(d: string) {
    setProfile((p) => ({
      ...p,
      domains: p.domains.includes(d)
        ? p.domains.filter((x) => x !== d)
        : [...p.domains, d],
    }));
  }

  function toggleStack(s: string) {
    setProfile((p) => ({
      ...p,
      preferred_stack: p.preferred_stack.includes(s)
        ? p.preferred_stack.filter((x) => x !== s)
        : [...p.preferred_stack, s],
    }));
  }

  async function handleSubmit() {
    if (profile.domains.length === 0) {
      setError("Pick at least one domain.");
      return;
    }
    if (!profile.interests_text.trim()) {
      setError("Tell us what excites you.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const result = await getRecommendations(profile);
      router.push(`/board?session=${result.session_id}&data=${encodeURIComponent(JSON.stringify(result.cards))}`);
    } catch (e) {
      setError("Something went wrong. Check your backend is running.");
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        {/* Back */}
        <a href="/" className={styles.back}>
          ← Back
        </a>

        <div className={styles.heading}>
          <h1>Tell us about yourself</h1>
          <p className={styles.sub}>
            This is the only form. Your answers shape everything — the ideas, the papers, the blueprint.
          </p>
        </div>

        {/* Domains */}
        <section className={styles.section}>
          <label className={styles.label}>
            Domains of interest
            <span className={styles.required}>*</span>
          </label>
          <p className={styles.hint}>Pick all that apply.</p>
          <div className={styles.chips}>
            {DOMAINS.map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => toggleDomain(d)}
                className={`${styles.chip} ${profile.domains.includes(d) ? styles.chipActive : ""}`}
              >
                {d}
              </button>
            ))}
          </div>
        </section>

        {/* Skill level */}
        <section className={styles.section}>
          <label className={styles.label}>Skill level</label>
          <div className={styles.radioGroup}>
            {(["beginner", "intermediate", "advanced"] as const).map((lvl) => (
              <button
                key={lvl}
                type="button"
                onClick={() => setProfile((p) => ({ ...p, skill_level: lvl }))}
                className={`${styles.radioBtn} ${profile.skill_level === lvl ? styles.radioBtnActive : ""}`}
              >
                {lvl.charAt(0).toUpperCase() + lvl.slice(1)}
              </button>
            ))}
          </div>
        </section>

        {/* Timeline + Team */}
        <div className={styles.row}>
          <section className={styles.section}>
            <label className={styles.label}>Months available</label>
            <div className={styles.sliderRow}>
              <input
                type="range"
                min={1}
                max={24}
                value={profile.months_available}
                onChange={(e) =>
                  setProfile((p) => ({ ...p, months_available: +e.target.value }))
                }
                className={styles.slider}
              />
              <span className={`mono ${styles.sliderValue}`}>
                {profile.months_available}mo
              </span>
            </div>
          </section>

          <section className={styles.section}>
            <label className={styles.label}>Team size</label>
            <div className={styles.sliderRow}>
              <input
                type="range"
                min={1}
                max={10}
                value={profile.team_size}
                onChange={(e) =>
                  setProfile((p) => ({ ...p, team_size: +e.target.value }))
                }
                className={styles.slider}
              />
              <span className={`mono ${styles.sliderValue}`}>
                {profile.team_size === 1 ? "solo" : `${profile.team_size} people`}
              </span>
            </div>
          </section>
        </div>

        {/* Stack */}
        <section className={styles.section}>
          <label className={styles.label}>Preferred tech stack</label>
          <p className={styles.hint}>Optional — leave blank if you have no preference.</p>
          <div className={styles.chips}>
            {STACKS.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => toggleStack(s)}
                className={`${styles.chip} ${styles.chipMono} ${profile.preferred_stack.includes(s) ? styles.chipActive : ""}`}
              >
                {s}
              </button>
            ))}
          </div>
        </section>

        {/* Free text */}
        <section className={styles.section}>
          <label className={styles.label} htmlFor="interests">
            What excites you?
            <span className={styles.required}>*</span>
          </label>
          <p className={styles.hint}>
            Describe what you want to build, problems you care about, or research areas you've been reading about. The more specific, the better.
          </p>
          <textarea
            id="interests"
            rows={4}
            maxLength={500}
            value={profile.interests_text}
            onChange={(e) =>
              setProfile((p) => ({ ...p, interests_text: e.target.value }))
            }
            placeholder="e.g. I've been reading about RAG systems and want to build something that helps Arabic speakers find information in unstructured documents..."
            className={styles.textarea}
          />
          <span className={`mono ${styles.charCount}`}>
            {profile.interests_text.length}/500
          </span>
        </section>

        <section className={styles.section}>
          <label className={styles.label} htmlFor="avoid">
            Topics to avoid
          </label>
          <p className={styles.hint}>Optional. We'll exclude these from your results.</p>
          <textarea
            id="avoid"
            rows={2}
            maxLength={500}
            value={profile.avoid_text}
            onChange={(e) =>
              setProfile((p) => ({ ...p, avoid_text: e.target.value }))
            }
            placeholder="e.g. no blockchain, no mobile-only projects..."
            className={styles.textarea}
          />
        </section>

        {error && <p className={styles.error}>{error}</p>}

        <button
          type="button"
          onClick={handleSubmit}
          disabled={loading}
          className={styles.submit}
        >
          {loading ? (
            <>
              <span className={styles.spinner} />
              Finding your ideas — this takes ~15 seconds…
            </>
          ) : (
            <>
              Find my graduation project
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
