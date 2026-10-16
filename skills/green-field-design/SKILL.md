---
name: green-field-design
description: Relentlessly interviews the user to build a complete, shared understanding of a software project's design, then produces a multi-tier set of markdown design docs. Walks the hierarchy App to Feature to Service to Scenario one branch at a time, resolving every dependency in a branch before moving to the next, exploring the codebase instead of asking when the answer is discoverable (but always confirming findings with the user before proceeding). Use this skill whenever the user wants to plan, scope, or document a new app, feature, service, or scenario; wants to break a project down into features/services/scenarios; asks for a design doc, design interview, architecture breakdown, or requirements doc; or wants output that other Claude agents/sub-agents can pick up and build from. Trigger even if they don't use these exact words -- phrases like "help me plan out X", "let's figure out the design for Y", "I need to scope Z before building it", or "interview me about this project" should also trigger this skill.
---

# Green Field Design

Turns a fuzzy project idea into a fully interviewed, hierarchical design -- captured as a set of markdown files a human can review and other Claude agents can build from directly.

## The hierarchy (fixed vocabulary -- do not rename these terms)

```
App
 └── Feature      (a capability area a PM would put on a roadmap as its own line item)
      └── Service  (a bounded piece of a feature; groups scenarios that share backstage/purpose)
           └── Scenario  (the smallest indivisible unit -- one trigger, one path, start to finish)
```

- **App**: the whole product.
- **Feature**: answers "what capability is this." Passes the "the ___ feature" test (e.g. "the remediation feature"). Named as a noun.
- **Service**: a bounded grouping within a feature. Two things belong in the same service if their backstage/purpose converges; they're different services if the backstage diverges and stays diverged.
- **Scenario**: one circumstance under which a service gets exercised, distinguished by trigger, starting state, or path (success/failure, manual/automatic, first-attempt/retry). If two candidate scenarios differ only in the first step and converge immediately after, they're the same scenario's edge case, not two scenarios. Scenarios read naturally as verb phrases or trigger descriptions ("manually triggered from dashboard"), not as capability names.

When it's ambiguous whether something is a feature, a service, or a scenario, apply these tests in order:
1. Does the *purpose* change, or just the *entry point*? Entry-point-only change -> scenario.
2. Does the backstage converge after the first step or two? Converges -> scenario. Diverges and stays diverged -> separate service or feature.
3. Would a PM schedule it as its own roadmap line item? Yes -> feature. No, it only makes sense as a qualifier on an existing name -> scenario.
4. Does removing it delete the capability, or just remove one way into it? Removes a capability -> feature/service. Removes an entry point only -> scenario.

Watch for two anti-patterns: over-splitting by trigger name (manual/scheduled/retry variants of the same thing are usually one service with three scenarios, not three services), and hiding real complexity by calling genuinely divergent backstage paths "just a scenario" of one shared name.

## The interview process

**Walk the tree depth-first, one branch at a time.** Do not survey every feature shallowly before going deep on any of them -- fully resolve a branch (down to every scenario within it) before moving to the next sibling, unless the user explicitly asks for a breadth-first pass first. Dependencies between decisions get resolved in order: you cannot meaningfully interview a service's scenarios until the service's boundaries are settled, and you cannot settle a service's boundaries until the feature it lives in is settled.

At each level, prefer **codebase exploration over asking**, whenever a codebase is available and the answer is plausibly discoverable there (directory structure, entry points, existing route/handler names, existing tests). But never treat exploration as a substitute for the user's confirmation: state what you found and your interpretation of it, then explicitly ask the user to confirm or correct it before writing anything down or moving to the next node. Do not silently assume; a wrong assumption two levels up corrupts everything interviewed underneath it.

### Level 1 -- App
Ask (or infer from the codebase and confirm):
- What is the app, in one sentence -- who uses it and what problem does it solve?
- What are its features? If the user doesn't have a clean list, explore the codebase's top-level structure (directories, module names, top-level routes) and propose a candidate feature list, explicitly flagging where you're guessing.
Confirm the full feature list before proceeding. Write `app/app-feature-map.md` (see Output Format).

### Level 2 -- Feature (for each feature, in turn)
- What is this feature's purpose, in one sentence?
- What services make it up? Apply the feature/service disambiguation tests above to anything the user proposes that might actually be a scenario or a separate feature in disguise.
- If the feature has enough services to warrant it (roughly 3+, or if a flat list would be hard to scan), produce a submap; if it only has one or two services, skip the submap and note that explicitly rather than forcing one.
Confirm the service list for this feature before descending into any of them. Write `app/<feature>/feature-submap.md` if applicable.

### Level 3 -- Service (for each service, in turn)
- What is this service's purpose and backstage boundary -- what does it own, and what does it hand off to other services?
- What scenarios exercise it? For each candidate scenario, run the disambiguation tests -- confirm it isn't actually a different service, and isn't actually the same scenario as one already listed with just a different trigger name.
Confirm the scenario list for this service before descending into any of them.

### Level 4 -- Scenario (for each scenario, in turn -- this is where the real interview depth goes)
Interview until every one of these is answered, confirmed, and free of contradictions with sibling scenarios:
- **Trigger**: what starts this scenario -- a person, a schedule, an alert, another system?
- **Starting state**: what must be true beforehand for this scenario to make sense?
- **Frontstage**: is there a UI/interface a person sees at any point? If none, say so explicitly (fully automated scenarios have no frontstage row).
- **Steps in order**: the plain-language sequence of what happens, start to finish.
- **Backstage**: what internal processing happens at each step, invisible to any user?
- **Systems touched**: what services, datastores, queues, or external systems does each step call into? (Explore the codebase for this where possible -- imports, API calls, config -- then confirm with the user.)
- **End state / outcome**: what's true when the scenario completes successfully?
- **Failure/edge paths**: what can go wrong, and what happens then? (Only capture these as part of *this* scenario if they don't diverge into what should really be a separate scenario -- apply the disambiguation test.)

Once a scenario is fully confirmed, write its two output files (see below) before moving to the next scenario.

## Output format

Create one directory tree mirroring the hierarchy, all markdown, all suitable for another Claude agent to read and build from directly:

```
<app-name>/
├── app-feature-map.md
└── <feature-name>/
    ├── feature-submap.md              # only if the feature has 3+ services, or the user asked for one
    └── <service-name>/
        └── <scenario-name>/
            ├── scenario-flow.md
            └── service-blueprint.md
```

Do not produce state diagrams or sequence diagrams at any level -- this skill deliberately limits itself to feature maps, submaps, service blueprints, and scenario flows, per the audience-first principle: journey-style and blueprint-style artifacts read by both technical and non-technical stakeholders; UML-style notation does not.

### app-feature-map.md
A short intro paragraph (what the app is, one sentence), then a list of features, each with a one-line description. Include a simple markdown tree or table -- this is the top-level map, kept shallow on purpose. Link to each feature's directory.

### feature-submap.md
Same shape as the app map, one level down: intro paragraph for the feature, then a list of its services with one-line descriptions. Only write this file if the feature actually has enough services to warrant it -- if it has one or two, skip the submap and put the service list directly in a short note instead.

### scenario-flow.md
The plain-language, single-audience journey version -- no actors, no lanes, just the ordered steps a reader would need to understand what happens when this scenario runs. Format as an ordered list or a simple `Step -> Step -> Step` chain, each step in one short phrase, followed by a couple of sentences of context. This is the artifact for someone who wants to understand the scenario without needing the implementation-level detail below.

### service-blueprint.md
The layered, multi-audience version of the same scenario. Structure as a markdown table with one column per step and one row per lane:

| | Step 1 | Step 2 | Step 3 | ... |
|---|---|---|---|---|
| **User** | ... | ... | ... | |
| **Frontstage** | ... | ... | ... | |
| **Backstage** | ... | ... | ... | |
| **Systems** | ... | ... | ... | |

Omit the User and Frontstage rows entirely (with a note why) for scenarios that have no human-facing side. Below the table, list the trigger, starting state, end state, and any failure paths captured during the interview.

## Rendering visuals alongside the docs

While interviewing, it's good practice to render the corresponding visual inline (feature map, submap, journey-style flow, or blueprint table) using the visualization tool as each level is confirmed, so the user can sanity-check the shape of the design before you write the markdown and move deeper. The markdown files are the durable, agent-consumable artifact; the inline visual is the human-facing checkpoint. Don't skip straight to writing files without showing the user something to react to first, especially at the App and Feature levels where a wrong assumption is expensive to unwind later.

## Tone

This is meant to feel like an actual interview, not a form. Ask one focused question (or a tight cluster of related ones) at a time, react to what the user says, and don't hesitate to push back gently when an answer sounds like it's actually describing a different level of the hierarchy than the one currently being discussed (e.g. the user describes a "service" that's actually two services, or a "scenario" that's actually the whole feature). Surface that friction to the user rather than silently reclassifying it.
