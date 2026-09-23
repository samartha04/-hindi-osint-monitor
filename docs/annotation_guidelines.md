# Annotation guidelines — validation set

Write and freeze these rules **before** anyone labels a single example. This
document is what you cite in the report to defend the validation set against
"you just labeled it however you wanted."

## What we're labeling

Each unit is one **event cluster** (a group of related posts about the same
claim/event), not an individual post. Two labels per cluster:

1. **Credibility** — one of: `false`, `unverified`, `mostly-true`, `true`
2. **Priority** — one of: `high` (should have triggered an alert),
   `watch`, `low` (correctly ignorable)

## Credibility label definitions

- **false** — contradicted by at least one authoritative source (fact-checker,
  official statement, primary document) with no credible support elsewhere.
- **unverified** — no authoritative source confirms or denies it within our
  observation window. This is not "probably false" — it's genuinely unknown.
  Most real-time alerts will fall here; that's expected and fine.
- **mostly-true** — core claim is accurate; minor details may be exaggerated
  or wrong.
- **true** — confirmed by 2+ independent authoritative sources.

If you're unsure between two labels, pick the lower-confidence one
(`unverified` over `mostly-true`) and flag it in the notes column rather than
guessing — a flagged disagreement is useful data, a silent guess is noise.

## Priority label definitions (this is the actual research question — be careful here)

- **high** — low credibility AND high reach/velocity at time of posting.
  This is a case the system should have caught before broader spread.
- **watch** — either credibility or reach is ambiguous/moderate; worth a
  human look but not urgent.
- **low** — either high credibility, or low reach, or both — no real-world
  risk regardless of truth value.

Important: priority is about **risk at the time**, not about what turned out
to be true later. A false claim that never spread is `low` priority even
though it's `false` credibility. Don't let hindsight bias creep in — label
using only what was knowable in the observation window.

## Process

1. Two annotators label the same 50-100 example subset **independently**,
   with no discussion beforehand.
2. Compute Cohen's kappa on both label sets separately (credibility and
   priority). Report both in the writeup — don't average or cherry-pick.
3. Where the two disagree, discuss and resolve as a team; document the
   resolution rule you used (majority, senior-annotator tiebreak, etc.) since
   reviewers will ask.
4. Only after step 3 do you split the rest of the dataset across
   annotators individually (single-labeled is fine past this point — you've
   already established your agreement baseline).
5. If you can, cross-check 50+ examples against Alt News / Boom / Vishvas
   News published fact-checks. Note where your labels agree/disagree with
   theirs — this is your external validation, separate from your internal
   kappa score, and it's the strongest evidence in your writeup.

## What to record per example

| field | notes |
|---|---|
| cluster_id | |
| credibility_label | |
| priority_label | |
| annotator_id | |
| confidence (1-3) | how sure the annotator was |
| notes | free text — cite the source you used to decide, if any |
| external_factcheck_match | y/n/n-a, only for the cross-checked subset |

Keep annotator_id even after resolving disagreements — you'll want it for
the kappa calculation and it costs nothing to keep.
