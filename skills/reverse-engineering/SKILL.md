---
name: reverse-engineering
description: Maps an existing/legacy codebase into a hierarchical design (App to Feature to Service to Scenario) so a new developer understands it fast. Crawls the repo to draft a hypothesis, then interviews the developer to confirm, correct, and fill in what code can't say -- the "why," gotchas, deprecated-but-load-bearing parts. Claims tagged confirmed/inferred/unclear and anchored to file paths. Produces markdown docs (feature map, submaps, blueprints, scenario flows, start-here index) for humans and other Claude agents. Use when the user inherits or needs to understand an existing codebase; wants to document or reverse-engineer a legacy system; asks "how does this codebase work"; is onboarding to an unfamiliar repo; wants a design doc generated FROM existing code. Trigger on "help me get up to speed on this repo", "I just inherited this project", "document what's already built". For a NEW app with no existing code, use green-field-design instead.
---

# Reverse Engineering

The legacy-codebase counterpart to `green-field-design`. Same output hierarchy and doc formats, opposite posture: **the code is the primary source of truth; the developer is there to correct inferences and supply what the code structurally cannot say.**

## The hierarchy (unchanged from green-field-design)

```
App
 └── Feature      (a capability area -- passes the "the ___ feature" test)
      └── Service  (a bounded grouping; scenarios inside share backstage/purpose)
           └── Scenario  (smallest indivisible unit -- one trigger, one path, start to finish)
```

Same disambiguation tests apply when the boundaries are ambiguous in the code:
1. Purpose change vs. just a different entry point -> entry-point-only is a scenario, not a new service.
2. Does the backstage converge after the first step or two? Converges -> scenario. Diverges and stays diverged -> separate service/feature.
3. Would a PM schedule it as its own roadmap line item? Yes -> feature.
4. Deleting it: does it remove a capability, or just one way into it?

Legacy code adds a fifth signal worth checking: **does the code's own structure already draw this boundary** (separate modules, separate services/repos, separate route prefixes, separate database schemas)? If the code disagrees with what the boundary "should" be, document the disagreement (see Contradictions below) rather than silently picking one.

## Process overview

Unlike `green-field-design`, this skill runs **discovery before interview**, and defaults to **breadth-first** rather than depth-first, because a new developer usually needs the 30,000-foot map before picking a branch to go deep on.

### Level 0 -- Discovery pass (do this first, before asking the developer anything)

Crawl the repo for everything that's plausibly discoverable without help:
- Top-level directory/module structure, package boundaries, separate services/repos if it's a monorepo
- Entry points: routes, handlers, CLI commands, cron/scheduled jobs, message queue consumers, webhooks
- Existing tests -- they're often the best record of intended scenarios, including edge cases
- README files, inline comments, CHANGELOG, ADRs (architecture decision records) if present
- Git history: commit message patterns, recent activity concentration (what's actively touched vs. untouched -- a signal for active vs. frozen), authorship spread
- Config/feature flags -- often reveal scenarios or services that are partially built, disabled, or being migrated away from

From this, draft a **hypothesis tree**: candidate features, services within each, and scenarios within each service, each with a one-line rationale for why you inferred that boundary from the code. Do not treat this as final -- it's the opening move of the interview, not a substitute for it.

### Levels 1-4 -- Interview, confirm-or-correct style

At every level (App / Feature / Service / Scenario), the shape of each turn is:
1. Present your hypothesis for this node, with the code evidence that produced it (file paths, key symbols).
2. Ask the developer to confirm, correct, or say "unclear, nobody currently knows" -- that's a valid and important answer to capture, not a gap to keep pressing on.
3. At the Scenario level specifically, ask the questions the code cannot answer (see "Why and gotchas" below) even when the mechanical steps were fully inferable.

**Default traversal is breadth-first**: produce the full App feature map and every feature's submap before going deep into any single service's scenarios, so the developer gets the full picture early. Switch to `green-field-design`'s depth-first branch-by-branch mode only if the developer explicitly asks to go deep on one area immediately.

**Scenario-level questions, in addition to the mechanical ones (trigger, steps, systems touched, end state):**
- Why is this built this way -- is there a reason it doesn't follow the pattern used elsewhere in the codebase?
- Is this deprecated, actively maintained, or "deprecated but still load-bearing" (nobody's supposed to use it, but something still depends on it)?
- Is there anything here that's broken before, is fragile, or that you'd warn a new hire about before they touch it?
- Is there tribal knowledge here that isn't written down anywhere in the repo?

## Confidence tagging (required on every claim)

Every factual statement in every output doc must carry one of:
- `[confirmed]` -- the developer explicitly verified this
- `[inferred]` -- drawn from code, not yet confirmed by the developer
- `[unclear]` -- code and developer both couldn't resolve it; flagged as an open question

Do not silently upgrade an `[inferred]` claim to `[confirmed]` without the developer actually confirming it in the conversation. A docs set full of confident-sounding but unverified claims is worse than one that's honest about its gaps -- the whole point is that a new developer can trust the `[confirmed]` tags completely.

## Source anchoring (required on every service and scenario doc)

Every service and scenario doc must include a `## Source` section listing the file paths, key function/class/module names, and (where feasible) line ranges that back up the doc. This is what keeps the docs from rotting the moment the code changes again -- a stale doc with no source pointer is undiscoverable as stale; one with source pointers can be diffed against.

## Contradictions (surface, don't resolve away)

When two parts of the codebase appear to implement the same scenario differently, or a service's actual behavior contradicts its name/docs/comments, this is a **finding**, not noise to smooth over. Log it explicitly in the relevant doc under a `## Contradictions / tech debt` section rather than picking one interpretation and moving on silently -- this is often exactly the kind of thing a new developer most needs flagged.

## Output format

Same file layout as `green-field-design`, plus one new top-level file:

```
<app-name>/
├── start-here.md                      # NEW -- onboarding index, see below
├── app-feature-map.md
└── <feature-name>/
    ├── feature-submap.md              # only if the feature has 3+ services
    └── <service-name>/
        ├── service-notes.md           # NEW -- service-level source anchors + contradictions
        └── <scenario-name>/
            ├── scenario-flow.md
            └── service-blueprint.md
```

`app-feature-map.md`, `feature-submap.md`, `scenario-flow.md`, and `service-blueprint.md` follow the same structure as in `green-field-design`, with confidence tags added to every line and a `## Source` section added to `scenario-flow.md` and `service-blueprint.md`.

### start-here.md (new)
The recommended reading order for a new developer, not just a list of everything that exists:
- A 3-5 sentence plain-language summary of what the app does
- Which features are actively developed vs. legacy/frozen (from the git-activity signal in discovery)
- A suggested order to read the feature docs in, with a one-line reason for the ordering (e.g. "start with X, everything else depends on it")
- A short "known gaps" list -- anything still tagged `[unclear]` anywhere in the tree, so a new developer knows where the map is thin

### service-notes.md (new)
One level up from individual scenario docs -- captures anything true of the *whole* service that doesn't belong to one scenario specifically: its overall source anchors, its contradictions/tech-debt log, and any `[unclear]` items still open at the service level.

## Tone

Same interview posture as `green-field-design` -- one focused question or tight cluster at a time, react to what's said -- but the default utterance shape flips from "tell me about X" to "I found X, is that right?" Treat "I don't know, nobody does" as a legitimate, useful answer worth recording as `[unclear]` rather than something to keep probing.
