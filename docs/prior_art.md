# Prior art / related work notes (Phase 0)

Living document — add to this as you find more. Cite these in the report's
related-work section and keep this as the evidence trail for the
patent-safety documentation mentioned in the roadmap.

## Closest architectural precedent

**TweetCred** (Gupta, Kumaraguru, Castillo, Meier — IIIT Delhi / QCRI,
arXiv:1405.5490) — real-time semi-supervised ranking model for tweet
credibility. Deployed to 717 users, scored 1.1M+ tweets, 84% of scores
returned within 6 seconds. Closest real-time-pipeline precedent. Gap: no
influence/reach weighting, no Hindi focus, credibility-only.

## Hindi-language misinformation work (static, not real-time)

- **Hostile Post Detection in Hindi** (Bhatnagar et al., IIT Bombay,
  arXiv:2101.07973) — two-level BERT + statistical classifier ensemble,
  multi-label classification (fake/hate/offensive/defamation/non-hostile) on
  static Twitter/Facebook data. No real-time, no influence weighting.
- **Stanceosaurus** (Zheng et al., Georgia Tech, arXiv:2210.15954) — 28,033
  tweet corpus (English/Hindi/Arabic) annotated for stance toward
  misinformation claims from 15 fact-checking sources. A dataset, not a
  monitoring system.
- **De-FactoX** (Bansal et al., TCS Research / IIT Patna, arXiv:2507.05179) —
  generates Hindi-language veracity explanations via preference optimization.
  Explanation generation, not detection or alerting.

## Credibility-only systems (no influence weighting)

- **CREDBANK** (Georgia Tech dissertation) — crowd + machine hybrid
  framework tracking newsworthy topics and crowd-sourced credibility scores
  over months on Twitter.
- **CrediBench** — web-scale graph dataset (45M nodes, 1B edges from Common
  Crawl) jointly modeling content + hyperlink structure for source
  credibility scoring. Structural, not real-time, not Hindi.

## Adjacent patents (credibility/alerting, not joint credibility×influence)

- US patent family on multi-factor validation for "common operational
  picture" systems — assigns an accuracy probability rating to a reported
  event from sensor + social media cross-checking, triggers alert above a
  threshold that can vary by event severity (e.g. lower threshold for
  active-shooter-type events). Closest patent-side precedent for
  threshold-based alerting logic — worth re-reading closely before finalizing
  the joint-score alert threshold design, to make sure ours is
  distinguishable.
- US12639507B2 (DigiCert, pub. 2026) — scores online-article credibility from
  publisher + content signals with provenance metadata. Single-axis
  credibility, no influence/reach component.

## Gap this project fills

No located prior work combines: (1) real-time ingestion, (2) Hindi-language
focus, (3) multi-format (text confirmed; image/video roadmapped), and
(4) a **joint** credibility × influence scoring function for alert
prioritization. TweetCred is the strongest single point of comparison to cite
and differentiate from directly.

## TODO before Phase 3

- [ ] Search Google Patents / USPTO full-text directly (this pass used web
      search only — do a proper patent database search before finalizing any
      patent-safety claims in the report)
- [ ] Check for any Indian-specific commercial OSINT/misinformation tools
      (state police social media monitoring cells, any Indian startups) not
      covered by this English-language academic search
- [ ] Re-check closer to Phase 3 — this is a fast-moving area, re-search
      before finalizing the related-work section
