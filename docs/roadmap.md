# Roadmap

## Status: Phase 0 (setup) — in progress

**Scope decision:** Reddit is deferred, not dropped. Reddit closed
self-service API access on 11 Nov 2025 — new credentials need manual
approval under a "Responsible Builder Policy" review (2-4 weeks), which
doesn't fit a semester-project critical path. MVP scope is now **news +
YouTube only**. Reddit collector code stays in the repo, fully built and
tested, ready to switch on if/when approval comes through — treat it as a
stretch goal for Phase 4-5, not a Phase 1 dependency. Say this plainly in
the report's scope section; it's a reasonable, documented decision, not a
gap to hide.

## Phase 0 — Setup (Week 1-2)
- [x] Finalize scope: Devanagari-first, text-native, news + YouTube for MVP
- [x] Literature + prior-art search (see docs/prior_art.md)
- [x] Repo skeleton, schema doc, annotation guidelines
- [x] News RSS collector built and tested
- [x] YouTube collector built and tested
- [x] Reddit collector built and tested (deferred — see scope decision above)
- [ ] Roles assigned (fill in README.md table)
- [ ] GitHub repo created, secrets added (YOUTUBE_API_KEY only for now),
      collect.yml running on schedule

## Phase 1 — Ingestion (Week 3-4)
- [x] News RSS running on schedule
- [x] YouTube running on schedule
- [ ] Verify data/raw/ is actually accumulating daily — check this weekly,
      don't assume the cron job is silently working
- [ ] (Stretch, if Reddit approval lands) switch Reddit collector on —
      zero code changes needed, just add the three secrets

## Phase 2 — Representation + Clustering (Week 5-7)
- [ ] MuRIL embeddings pipeline
- [ ] Near-duplicate de-dup pass (cosine similarity threshold), before HDBSCAN
- [ ] HDBSCAN tuning on real collected data
- [ ] Manually inspect clusters — check for wire-copy vs. real events
- [ ] Milestone: raw posts → clean event clusters demo

## Phase 3 — Scoring Engine (Week 8-10)
- [ ] Credibility sub-score: cross-source corroboration + source track record
- [ ] Influence sub-score: follower/subscriber count + baseline-relative
      engagement velocity
- [ ] Joint score as quadrant/matrix logic (not just a weighted average)
- [ ] Time-windowed spike detection
- [ ] Annotation in parallel: two people label independently, compute
      Cohen's kappa (see docs/annotation_guidelines.md)

## Phase 4 — Dashboard + Evaluation (Week 11-13)
- [ ] Dashboard: live topics, clusters, alert feed, priority quadrant
- [ ] Ablation table: joint score vs. credibility-only vs. influence-only
- [ ] Cross-check subset against Alt News / Boom / Vishvas News fact-checks
- [ ] Precision/recall against team-annotated set

## Phase 5 — Writeup + Buffer (Week 14-15)
- [ ] Report, patent-safety documentation (dated repo history)
- [ ] Buffer week
- [ ] Stretch: geo-tagging alerts, or switching Reddit on, if time remains

## Ordering rule

Don't start Phase 3 scoring until Phase 2 clustering is producing clean
clusters on real data. A scoring model built on noisy/duplicate clusters
will look broken even if the scoring logic is correct.
