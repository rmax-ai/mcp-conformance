# HyperFrames Production Prompt — mcp-conformance

> **Generated:** 2026-06-27
> **Source material:** mcp-conformance project (repo, docs site, scenario YAML, runner source)
> **Target:** Technical explainer video for platform engineers, MCP implementers, and enterprise compliance teams
> **Status:** Ready for production

---

## 1. Production Brief

- **Working title:** MCP Conformance — Protocol Testing, Declared in YAML
- **Core thesis:** Conformance testing for MCP must be declarative, swappable, and wire-visible — not another pile of bespoke pytest scripts. mcp-conformance achieves this with a scenario runner, partner adapters, and layered assertions across HTTP, JSON-RPC, OAuth, PKCE, DCR, and CIMD.
- **Viewer promise:** After watching, you will understand why declarative conformance testing exists, how mcp-conformance maps scenarios to assertions against swappable partners, and how to integrate it as a CI gate for certifying MCP servers.
- **Target audience:** Platform engineers building MCP infrastructure, MCP SDK maintainers, gateway operators, enterprise compliance teams evaluating server conformance.
- **Assumed prior knowledge:** Familiarity with MCP (Model Context Protocol), JSON-RPC, OAuth 2.0/2.1, and CI pipelines. Does not require knowledge of DCR, CIMD, or PKCE internals.
- **Desired viewer understanding:**
  1. The problem: MCP implementations multiply without shared verification
  2. The approach: Declarative YAML scenarios + swappable partners + layered assertions
  3. The mechanism: How a scenario flows through the runner into assertions and reports
  4. The operational reality: CI gate, exit codes, JUnit XML, audit evidence
  5. One transferable principle: Test the protocol, not the implementation
- **Duration:** 120 seconds (2 min)
- **Resolution:** 720p 4:3 (960×720)
- **Aspect ratio:** 4:3
- **Frame rate:** 30 fps
- **Visual tone:** Dark technical — dark background, restrained color palette, precise diagrams. No decoration.
- **Narration tone:** Calm, precise, technically credible. Moderate pace (~140 wpm). Professional without being corporate.
- **Music tone:** Sparse ambient electronic underscore. No melodic hooks. Supports comprehension.
- **Distribution context:** Embedded in project README, docs site, and GitHub repo. Internal technical audience.

---

## 2. Source-Grounding Requirements

The downstream agent must ground every claim in the following source material:

### Primary sources (in order of authority)

1. **Project README** (`/home/rmax-10/src/rmax-ai/mcp-conformance/README.md`) — project overview, architecture, target users
2. **AGENTS.md** (`/home/rmax-10/src/rmax-ai/mcp-conformance/AGENTS.md`) — architecture diagram, design principles, key dependencies
3. **Docs site homepage** (`docs/site/src/routes/+page.svx`) — public-facing description, quick start, feature panels
4. **Scenario catalog** (`docs/site/src/routes/scenarios/+page.svx`) — 35 scenarios across 7 capability areas
5. **Partner adapters guide** (`docs/site/src/routes/adapters/+page.svx`) — built-in adapters, custom adapter ABC
6. **Runner source** (`src/mcp_conformance/runner.py`) — ScenarioRunner, ExitCode enum, assertion dispatch, action mapping, bearer token resolution
7. **Scenario YAML examples** (`scenarios/auth/auth-code-pkce-happy-path.yaml`, `scenarios/auth/dcr-happy-path.yaml`) — declarative format
8. **Report formats page** (`https://mcp-conformance.rmax.tech/reports/`) — JSON, Markdown, JUnit XML, exit codes, assertion catalog

### Claim sourcing requirements

For every major claim, identify whether it is:
- **Directly sourced** — verbatim from project files (e.g., "35 scenarios across seven capability areas" from scenarios page)
- **A synthesis across sources** — derived from multiple project files (e.g., architecture flow)
- **An illustrative example** — not from source, constructed for clarity (must be labeled)
- **A production analogy** — analogies must be labeled and must not distort the mechanism

### Constraints
- Do not invent statistics, APIs, features, or causal claims not present in source material
- Preserve qualifications: "Draft" status of scenarios, "experimental" or "production" maturity labels
- Use terminology consistently with source: "partner adapter" not "server connector", "scenario" not "test case"
- Remove all marketing puffery — the project already has precise language
- No appendix material from the repo unless directly relevant to the core explanation

---

## 3. Explanation Strategy

Construct the explanation around three conceptual transformations:

### Transformation 1: From bespoke tests to declarative scenarios
- **Viewer's initial model:** "You write pytest functions to test your MCP server."
- **What's incomplete:** Every implementation writes different tests. No shared baseline. No cross-server comparison.
- **New distinction:** Declarative YAML scenarios describe what to assert, not how to test. The runner handles mechanics.
- **Visualization:** Side-by-side: terminal with fragmented test files → single YAML file with clear steps and assertions.
- **Example:** The auth-code-pkce-happy-path YAML — 5 steps, 5 assertions, no Python code.
- **Implication:** Conformance becomes portable. Same scenario runs against any partner.
- **Principle:** Test the protocol, not the implementation.

### Transformation 2: From opaque tests to wire-visible evidence
- **Viewer's initial model:** "Tests pass or fail — that's the output."
- **What's incomplete:** A pass/fail boolean gives no audit trail. You can't debug why something failed.
- **New distinction:** Every step captures the full HTTP request/response, JSON-RPC message, redirect chain, and elapsed time. Failures come with evidence.
- **Visualization:** A failed assertion expands to show: actual HTTP status code, response body, expected value, diff.
- **Example:** "Expected status 200, got 401" — with the full Authorization header and response body visible.
- **Implication:** Reports become audit-grade. Platform teams can certify servers with evidence.
- **Principle:** Failures must come with evidence.

### Transformation 3: From coupled tests to swappable partners
- **Viewer's initial model:** "The test is written against a specific server."
- **What's incomplete:** MCP has multiple implementations — SDKs, gateways, hosted servers. You need one scenario catalog that works against all of them.
- **New distinction:** Partner adapters translate generic scenario operations into the concrete API of the system under test. Plug in a new adapter, run the same scenarios.
- **Visualization:** Scenario YAML → Partner Adapter (ABC) → [mcp-auth-test-server | generic-mcp | custom-impl]
- **Example:** Switch `--partner mcp-auth-test-server` to `--partner generic-mcp --base-url http://my-server:8080`.
- **Implication:** Write scenarios once. Run them against every MCP server you onboard.
- **Principle:** The scenario catalog is the invariant. The partner is the variable.

### Narrative progression (60 seconds allocated per transformation block + 20s intro/outro):
1. **0:00–0:05** — Problem: MCP implementations proliferating, no shared verification
2. **0:05–0:10** — What mcp-conformance is (one-sentence definition)
3. **0:10–0:30** — Transformation 1: Declarative scenarios (YAML walkthrough)
4. **0:30–0:50** — Transformation 2: Wire-visible evidence (assertion + audit trail)
5. **0:50–1:10** — Transformation 3: Swappable partners (adapter ABC)
6. **1:10–1:35** — Architecture walkthrough: Scenario → Runner → Partner → Assertions → Report
7. **1:35–1:55** — Operational reality: CI gate, exit codes, JUnit XML, 35 scenarios
8. **1:55–2:00** — Final principle + call to action

### Avoid
- Excessive jargon without explanation
- Unexplained acronyms (expand DCR, CIMD, PKCE on first use)
- Marketing language or motivational framing
- Artificial suspense
- Starting with implementation before establishing why
- Treating every sentence as equally important — hierarchy is: core thesis → key distinctions → concrete examples → operational details

---

## 4. Narrative Script

**Total: ~280 words at ~140 wpm for 120 seconds**

---

[00:00] [calm and precise]
MCP implementations are proliferating. Every SDK, every gateway, every hosted server — each one implements the protocol slightly differently. And there's no shared mechanism to verify whether any of them actually conform to the spec.

[00:10] [slightly slower]
mcp-conformance is a scenario-driven test runner that solves this. You describe what to assert in YAML. It executes against any MCP server. It produces structured pass/fail reports suitable for CI gates and enterprise audit evidence.

[00:22] [emphasize: declarative]
The key insight: scenarios are declarative, not imperative. Here's an OAuth authorization code flow with PKCE. Five steps — discover, register, authorize, token exchange, MCP request. Each step has assertions: expected HTTP status, expected response keys, expected token type. No Python test code. No bespoke setup scripts. Just the protocol, declared.

[00:46]
And when something fails? [emphasize: wire-visible] Every step captures the full HTTP request and response. The actual status code. The actual body. The redirect chain. Elapsed time. Failures come with evidence — not just "test failed," but "expected 200, got 401, here's the Authorization header that was sent."

[01:05]
The third design choice: test partners are swappable. [pronounce MCP as M-C-P] The default partner is mcp-auth-test-server. But you can plug in a generic MCP server. Or write a custom adapter by implementing five async methods. Same thirty-five scenarios. Any server.

[01:22]
[calm and precise] Here's the architecture. [slightly slower] YAML scenarios load into the scenario runner. The runner delegates each step to a partner adapter. The adapter translates generic operations into the concrete API of the system under test. Responses flow back through an assertion library — HTTP status, JSON body paths, JSON-RPC schema, OAuth token validation, wire-level headers. Results go to a reporter that produces JSON, Markdown, or JUnit XML.

[01:48]
In practice, this runs as a CI gate. Exit code zero means all selected scenarios passed. Exit code one means failures. JUnit XML plugs directly into GitHub Actions or Jenkins. Thirty-five scenarios across seven capability areas: [pronounce OAuth] OAuth with PKCE, Dynamic Client Registration, Client-Initiated Metadata Discovery, core MCP protocol shape, no-auth, bearer token, and error paths.

[01:58]
[final, deliberate] Test the protocol, not the implementation. One scenario catalog. Any server. CI-gate ready.

---

### Delivery instructions applied
- `[calm and precise]` — sections that require technical authority
- `[slightly slower]` — definitional or architectural moments
- `[emphasize: X]` — key terms that anchor understanding
- `[pronounce MCP as M-C-P]` — always spell out acronym on first audio use in a scene; subsequent occurrences can use the acronym
- `[final, deliberate]` — closing principle, slower pacing

---

## 5. Scene-by-Scene Storyboard

| # | Scene Name | Start | End | Dur | Narration | Learning Objective | Primary Visual | Secondary Visual | On-Screen Text | Animation Sequence | Transition In | Sync Cues | Required Assets |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Problem framing | 0:00 | 0:10 | 10s | "MCP implementations are proliferating..." | Understand why conformance testing is needed | Three server icons (SDK, gateway, hosted) with different shapes, question marks | Labels: "SDK A", "Gateway B", "Hosted C" | "Is it conformant?" | Servers fade in one by one, question marks appear | Fade from black | Question marks appear on "verify" | Server icons, question mark SVG |
| 2 | What is mcp-conformance | 0:10 | 0:22 | 12s | "mcp-conformance is a scenario-driven test runner..." | Know the one-sentence definition | Title card: "mcp-conformance" with three-panel feature grid | Feature icons: YAML file, server icon, report document | "Declared in YAML" / "Any server" / "CI-ready reports" | Title fades in, panels slide in from bottom | Crossfade | Title on "mcp-conformance", panels on each clause | Title card, feature icon SVGs |
| 3 | Declarative YAML walkthrough | 0:22 | 0:46 | 24s | "The key insight..." | Understand declarative scenario format | YAML file side-by-side with simplified flow diagram | YAML lines highlight as narration describes each step | "id: auth.auth_code_pkce_happy_path" / steps list | YAML file types out line by line, each step gets a highlight pulse | Slide left | Step highlights sync with narration phrases | YAML code rendering, step labels |
| 4 | Wire-visible evidence | 0:46 | 1:05 | 19s | "And when something fails..." | Understand raw wire capture and failure evidence | Failed assertion callout: red box showing expected vs actual | HTTP request/response trace expanding from the failure | "Expected: 200" / "Got: 401" / "Authorization: Bearer eyJ..." | Failure appears, expands to show wire trace, diff highlight | Morph from YAML scene | Wire trace expands on "actual status code" | Assertion diff UI, wire trace mockup |
| 5 | Swappable partners | 1:05 | 1:22 | 17s | "The third design choice..." | Understand partner adapter abstraction | Three server boxes with adapter arrows connecting to one scenario catalog | Adapter ABC interface card | "mcp-auth-test-server" / "generic-mcp" / "Custom adapter" | Scenario catalog stays fixed; different partners slide into place below it | Slide right | Partner icons swap on each named partner | Partner icons, ABC interface card |
| 6 | Architecture walkthrough | 1:22 | 1:48 | 26s | "Here's the architecture..." | Understand the end-to-end data flow | Full architecture diagram: YAML → Runner → Partner → Assertions → Reports | Each component highlights as narration reaches it | Component labels: "Scenarios", "Runner", "Partner Adapter", "Assertion Library", "Reporter" | Progressive disclosure — each component appears and connects as named | Crossfade | Components appear in order: scenarios first, then runner, then partner, etc. | Architecture diagram components |
| 7 | Operational reality + CI gate | 1:48 | 1:58 | 10s | "In practice, this runs as a CI gate..." | Know the operational integration | CI pipeline diagram with exit code badge, JUnit XML, GitHub Actions logo | Scenario count counter: 35 | "exit 0 = pass" / "exit 1 = fail" / "35 scenarios, 7 capability areas" | Pipeline flows left to right, exit codes appear at terminal step | Slide up | Exit codes appear on "exit code zero" | CI pipeline diagram, exit code badges |
| 8 | Conclusion | 1:58 | 2:00 | 2s | "Test the protocol, not the implementation..." | Remember the transferable principle | Black background with single centered line of text | None | "Test the protocol, not the implementation." | Text fades in, holds, fades to black | Crossfade | Text appears immediately on narration start | Final title card |

---

## 6. Visual System

### Components
- **Systems and services:** Rounded rectangles, 8px border radius, 1px border, dark background
- **Test partners:** Distinct colored rounded rectangles — green tint for auth-test-server, blue for generic-mcp, gray for custom
- **Scenario catalog:** Document icon or YAML file icon, fixed position, highlighted when active
- **Data flows:** Solid arrows (2px) for request paths, dashed arrows (1.5px) for response paths
- **Assertions:** Green checkmark (pass) or red X (fail) icons next to assertion results
- **Wire traces:** Monospace text blocks with line numbers, dark code background
- **Exit codes:** Terminal-style blocks with exit code numbers and meanings
- **Comparisons:** Side-by-side layouts or morph transitions between states

### Visual hierarchy
1. Primary concept (current scene's main idea) → largest, most contrast
2. Supporting structures (diagram components) → medium contrast
3. Labels → readable but subordinate
4. Annotations → small, muted
5. Captions → bottom-aligned, high contrast
6. Source references → bottom corner, smallest

All elements must remain readable at 960×720.

### Typography
- **Primary font:** Inter (sans-serif, clean, technical)
- **Code font:** JetBrains Mono (monospace, for YAML, JSON, terminal output)
- **Size tiers:**
  - Scene titles: 28px, weight 700
  - Primary labels: 20px, weight 600
  - Body text: 16px, weight 400
  - Code: 14px, weight 400
  - Annotations: 12px, weight 400
  - Source/captions: 11px, weight 400
- **Maximum text per screen:** 3 short lines of body text, or 1 code block ≤8 lines
- **Contrast:** WCAG AA minimum (4.5:1 for body text)
- **Safe margins:** 40px on all sides
- **Line length:** ≤60 characters for body text

Do not show narration paragraphs on screen. On-screen text is limited to: key terms, short definitions, contrasts, numeric values, and the final principle.

### Color semantics (dark theme)

| Meaning | Color | Hex |
|---------|-------|-----|
| Background | Dark gray-black | `#0D1117` |
| Surface / cards | Slightly lighter | `#161B22` |
| Primary text | Near white | `#E6EDF3` |
| Secondary text | Muted gray | `#8B949E` |
| Active flow / success | Muted green | `#3FB950` |
| Request / data movement | Blue | `#58A6FF` |
| Assertion / verification | Amber | `#D29922` |
| Failure / error | Muted red | `#F85149` |
| Code background | Darker surface | `#0D1117` with `#30363D` border |
| Borders / dividers | Subtle gray | `#30363D` |
| Highlight / emphasis | Cyan | `#79C0FF` |

Use a restrained palette. Strong contrast, no saturation spikes.

### Motion semantics

| Concept | Motion |
|---------|--------|
| Data flow (request) | Elements move left to right |
| Data flow (response) | Elements move right to left |
| Dependency (B follows A) | B appears after A with a brief delay (200ms) |
| Sequence | Items appear one at a time, 150ms stagger |
| Causality (A causes B) | A pulses, then B appears with connecting arrow |
| Comparison | Two elements appear simultaneously, side by side |
| Failure | Element turns red, shakes briefly (2 oscillations), holds |
| Verification (assertion passes) | Green checkmark appears with scale-up ease-out |
| Abstraction | Surrounding elements fade to 20% opacity |

Avoid: arbitrary floating, bouncing, spinning, or particle effects unless they express a real concept.

---

## 7. Diagram and Concept-Animation Instructions

### Diagram 1: Problem Space (Scene 1)
- **Nodes:** Three rounded rectangles labeled "SDK A", "Gateway B", "Hosted C"
- **Edges:** None initially — disconnected servers to convey lack of shared verification
- **Question marks:** Appear over each server, pulsing gently
- **Reveal order:** Left server → center server → right server → question marks (staggered 300ms)

### Diagram 2: YAML Walkthrough (Scene 3)
- **Layout:** Split screen — left: YAML code block, right: simplified flow diagram
- **YAML code:** Render the auth-code-pkce-happy-path.yaml with syntax highlighting
- **Reveal order:** Type out YAML line by line. Each step lights up in the flow diagram as it's typed
- **Active element:** The YAML line currently being narrated is highlighted (cyan background)
- **Flow diagram:** 5 nodes in sequence: Discover → Register → Authorize → Token Exchange → MCP Request
- **Assertions:** Below each flow node, a small assertion badge appears (green checkmark on pass)

### Diagram 3: Wire Trace Expansion (Scene 4)
- **Initial state:** A failed assertion — red X, "Expected: 200, Got: 401"
- **Expansion:** Click/zoom to reveal the full wire trace below:
  - Request block: method, URL, headers (with Authorization header highlighted red)
  - Response block: status code, headers, body (truncated if long)
- **Animation:** Failure box expands downward, wire trace slides in from below, request/response blocks fade in sequentially
- **Active element:** The Authorization header is highlighted as narration mentions "here's the Authorization header"

### Diagram 4: Partner Swap (Scene 5)
- **Fixed element (center):** Scenario catalog icon — document with "35 scenarios"
- **Variable elements:** Three partner boxes slide in below one at a time:
  - "mcp-auth-test-server" (green tint) — appears first
  - "generic-mcp" (blue tint) — replaces it via slide-out/slide-in
  - "Custom adapter" (gray tint) — replaces it
- **ABC interface card:** Appears to the right, showing the 6 methods
- **Animation:** Scenario catalog stays fixed. Partner boxes slide in/out horizontally. Arrows connect catalog to active partner.

### Diagram 5: Full Architecture (Scene 6)
- **Progressive disclosure:** Start with only "Scenarios (YAML)" visible. Each component appears as narrated:
  1. Scenarios (YAML) — document icon, 35 files
  2. Scenario Runner — gear icon, Python module
  3. Partner Adapter — plug icon, ABC interface
  4. Test Server — server icon (mcp-auth-test-server by default)
  5. Assertion Library — checkmark/X icon, 4 assertion modules
  6. Reports — document icon, 3 format badges (JSON, MD, JUnit XML)
- **Arrows:** Solid arrows for primary flow (scenarios → runner → partner → server). Dashed arrows for secondary flow (partner → assertions → reports).
- **Active element:** The component being narrated is highlighted (cyan glow) while others remain at 60% opacity.
- **State:** All components connected by scene end.

### Diagram 6: CI Pipeline (Scene 7)
- **Layout:** Horizontal pipeline: Git Push → mcp-conformance run → Exit Code → GitHub Actions / Jenkins → Badge
- **Exit code decision diamond:** After "mcp-conformance run", a decision node splits to:
  - Exit 0 → green path → "All Passed" badge
  - Exit 1 → red path → "Failures" report
- **Scenario counter:** "35 scenarios" appears as a badge near the mcp-conformance step
- **JUnit XML:** A document with XML tags appears below the pipeline

### Code rendering
- YAML: syntax-highlighted, 2-space indent, key: value coloring
- JSON: compact representation, syntax-highlighted
- Terminal output: monospace, dark background, no syntax highlighting
- Highlight only the line being discussed — avoid scrolling large files

---

## 8. HyperFrames Implementation Specification

Build the video as a deterministic HyperFrames project.

### Project structure
```
mcp-conformance-video/
├── index.html              # Main composition entry point
├── scenes/                 # One HTML file per scene
│   ├── 01-problem.html
│   ├── 02-what-is.html
│   ├── 03-yaml-walkthrough.html
│   ├── 04-wire-evidence.html
│   ├── 05-partner-swap.html
│   ├── 06-architecture.html
│   ├── 07-ci-gate.html
│   └── 08-conclusion.html
├── components/             # Reusable primitives
│   ├── diagram-node.js     # Rounded rectangle node
│   ├── flow-arrow.js       # Directional arrow (solid/dashed)
│   ├── assertion-badge.js  # Pass/fail badge
│   ├── code-block.js       # Syntax-highlighted code block
│   ├── wire-trace.js       # HTTP request/response display
│   └── partner-icon.js     # Partner adapter icon
├── assets/                 # Static assets
│   ├── icons/              # SVG icons
│   ├── fonts/              # Inter + JetBrains Mono
│   └── brand/              # Logo, watermark
├── audio/                  # Generated audio
│   ├── narration.mp3
│   ├── music-intro.mp3
│   ├── music-mechanism.mp3
│   └── music-outro.mp3
├── captions/               # Subtitle files
│   ├── captions.srt
│   └── captions.vtt
├── scene-manifest.yaml     # Source of truth for timing
├── hyperframes.config.js   # Timeline, audio, render config
├── validate.js             # Validation script
└── README.md               # Reproduction instructions
```

### Technology stack
- HTML + CSS for layout and styling
- JavaScript (no framework) for animation control
- GSAP (GreenSock Animation Platform) for timeline-anchored animations
- Web Animations API for simple transitions
- No Three.js — no 3D elements needed
- No Lottie — not needed for this technical style

### Timeline requirements
- All animations must derive from the video timeline
- No dependence on uncontrolled real-time timers (setTimeout, setInterval)
- Animations must be seekable — jumping to any timestamp produces the correct visual state
- Deterministic rendering — same output on every render

### Configuration
- Resolution: 960×720
- Frame rate: 30 fps
- Duration: 120 seconds
- Audio tracks: narration (primary), music (background, ducked)
- Caption track: SRT and VTT from final narration audio
- Rendering: Headless Chromium via Playwright as specified in HyperFrames docs

### Scene manifest (YAML)
```yaml
video:
  duration_seconds: 120
  width: 960
  height: 720
  fps: 30
scenes:
  - id: 01-problem
    start: 0.0
    end: 10.0
    narration_segment: "MCP implementations are proliferating..."
    learning_goal: "Understand why conformance testing is needed"
    visual_type: diagram
    elements: [server-icons, question-marks]
    animation_cues: [servers-fade-in, questions-appear]
    transition: fade-from-black
  - id: 02-what-is
    start: 10.0
    end: 22.0
    narration_segment: "mcp-conformance is a scenario-driven test runner..."
    learning_goal: "Know the one-sentence definition"
    visual_type: title-card
    elements: [title, feature-panels]
    animation_cues: [title-fade, panels-slide-up]
    transition: crossfade
  - id: 03-yaml-walkthrough
    start: 22.0
    end: 46.0
    narration_segment: "The key insight: scenarios are declarative..."
    learning_goal: "Understand declarative scenario format"
    visual_type: code-walkthrough
    elements: [yaml-code, flow-diagram, assertion-badges]
    animation_cues: [code-type-out, step-highlight, badge-appear]
    transition: slide-left
  - id: 04-wire-evidence
    start: 46.0
    end: 65.0
    narration_segment: "And when something fails..."
    learning_goal: "Understand raw wire capture"
    visual_type: failure-callout
    elements: [assertion-failure, wire-trace, diff-highlight]
    animation_cues: [failure-appear, trace-expand, highlight-auth]
    transition: morph
  - id: 05-partner-swap
    start: 65.0
    end: 82.0
    narration_segment: "The third design choice..."
    learning_goal: "Understand partner adapter abstraction"
    visual_type: partner-swap
    elements: [scenario-catalog, partner-boxes, abc-interface]
    animation_cues: [catalog-fixed, partners-swap, abc-appear]
    transition: slide-right
  - id: 06-architecture
    start: 82.0
    end: 108.0
    narration_segment: "Here's the architecture..."
    learning_goal: "Understand end-to-end data flow"
    visual_type: architecture-diagram
    elements: [all-architecture-components]
    animation_cues: [progressive-disclosure, component-highlight, arrows-appear]
    transition: crossfade
  - id: 07-ci-gate
    start: 108.0
    end: 118.0
    narration_segment: "In practice, this runs as a CI gate..."
    learning_goal: "Know operational integration"
    visual_type: ci-pipeline
    elements: [pipeline-flow, exit-codes, junit-xml, gh-actions]
    animation_cues: [pipeline-flow, exit-code-split, counter-appear]
    transition: slide-up
  - id: 08-conclusion
    start: 118.0
    end: 120.0
    narration_segment: "Test the protocol, not the implementation..."
    learning_goal: "Remember the transferable principle"
    visual_type: final-title
    elements: [principle-text]
    animation_cues: [text-fade-in, hold, fade-to-black]
    transition: crossfade
audio:
  narration: audio/narration.mp3
  music:
    - track: audio/music-intro.mp3
      start: 0.0
      end: 30.0
    - track: audio/music-mechanism.mp3
      start: 26.0
      end: 95.0
    - track: audio/music-outro.mp3
      start: 91.0
      end: 120.0
  ducking: true
  target_loudness: -16
captions:
  format: [srt, vtt]
  source: captions/captions.srt
```

---

## 9. Gemini TTS Narration Instructions

### Voice selection
Use **Charon** — calm, professional male voice. Best for technical/strategy content.

### Voice direction
- **Speaking rate:** Moderate (~140 wpm). Slower on definitions and architectural descriptions. Slightly faster on concrete examples.
- **Emotional range:** Narrow. Calm and precise throughout. No enthusiasm spikes. No sales energy.
- **Authority:** Confident but not performative. The voice of someone who has built this.
- **Pauses:** Natural pauses after definitions ("M-C-P"), after contrasts, and before the final principle.
- **Consonants:** Clear enunciation on technical terms: "P-K-C-E", "JSON-RPC", "JUnit", "OAuth"

### Pronunciation guidance
- "MCP" → spell out: "M-C-P"
- "PKCE" → spell out: "P-K-C-E"
- "JSON-RPC" → "JSON R-P-C"
- "JUnit" → "J-Unit"
- "OAuth" → "O-Auth" (two syllables)
- "CIMD" → spell out: "C-I-M-D"
- "DCR" → spell out: "D-C-R"
- "mcp-conformance" → "M-C-P conformance" (hyphen = pause)

### Acronym expansion
First occurrence in narration (not on-screen text):
- DCR: "Dynamic Client Registration, or D-C-R"
- CIMD: "Client-Initiated Metadata Discovery"
- PKCE: "P-K-C-E, Proof Key for Code Exchange"

### Post-generation steps
1. Measure actual audio duration
2. Extract word-level timestamps
3. Update scene boundaries in scene-manifest.yaml to match audio
4. Add 200ms silence at scene boundaries where cognitive pauses are needed
5. Ensure important visual reveals occur within 300ms of the corresponding spoken phrase
6. Do not accelerate narration to satisfy duration — revise script if it meaningfully exceeds 120s
7. **Convert WAV to MP3** before referencing in HyperFrames — WAV at non-44.1kHz rates may fail to load

---

## 10. Gemini/Lyria Music Instructions

### Strategy
Generate **3 complementary 30-second clips** with 4-second overlap crossfades. The 30-second generation limit requires multi-track composition for a 120-second video. Use HyperFrames multi-track audio for natural crossfades — no ffmpeg pre-stitching.

### Track 1: Introduction (0:00–0:30)
- **Duration:** 30 seconds
- **Character:** Sparse, ambient, minimal
- **Instrumentation:** Single sustained pad, very subtle low pulse
- **Energy curve:** Flat, barely present
- **Purpose:** Establish tone without competing with the problem statement
- **End behavior:** Gentle fade out over last 4 seconds

### Track 2: Mechanism (0:26–0:95, with 4s crossfade on each end)
- **Duration:** 30 seconds
- **Character:** Restrained rhythmic pulse, subtle forward motion
- **Instrumentation:** Light electronic percussion (kick on downbeats, soft hi-hat pattern), bass drone, evolving pad
- **Energy curve:** Gradual build from 0:26 to 0:50, steady at medium energy through 1:22, slight decrease through end
- **Purpose:** Support the technical explanation without dominating
- **End behavior:** Gentle fade out over last 4 seconds

### Track 3: Conclusion (0:91–1:20, with 4s crossfade at start)
- **Duration:** 30 seconds
- **Character:** Controlled resolution, minimal closing
- **Instrumentation:** Pad fade, final soft pulse, silence
- **Energy curve:** Decreasing — starts at low energy, fades to near silence
- **Purpose:** Support the conclusion and final principle
- **End behavior:** Fade to silence by 1:18, 2 seconds of near-silence for final words

### Crossfade specification
```
Track 1: [0:00 ======== 0:26--0:30]  (4s fade out from 0:26)
Track 2:          [0:26--0:30 ======== 0:91--0:95]  (4s fade in to 0:30, 4s fade out from 0:91)
Track 3:                                     [0:91--0:95 ======== 1:18--1:20]  (4s fade in to 0:95, fade to silence)
```

### Audio mixing parameters
- **Track volume:** `data-volume="0.12"` (~-20dB) for all music tracks
- **Avoid:** Vocals, prominent melodic hooks, heavy bass, trailer-style percussion, sudden drops, emotional manipulation
- **Frequency space:** Leave 250Hz–4kHz clear for narration intelligibility

---

## 11. Audio Mixing

### Mix specification
1. **Narration is primary** — must remain intelligible throughout
2. **Music ducking:** When narration is present, reduce music by 18–22dB. Use gentle attack/release (50ms/200ms) to avoid pumping
3. **Crossfades:** 4-second overlap between music tracks. Use equal-power crossfade curves
4. **Normalization:** Final integrated loudness target -16 LUFS (suitable for web embedding)
5. **Peak:** -1 dBTP maximum — no clipping

### HyperFrames audio configuration
```javascript
// In hyperframes.config.js
audio: {
  tracks: [
    { src: 'audio/narration.mp3', volume: 0.80, type: 'narration' },
    { src: 'audio/music-intro.mp3', volume: 0.12, start: 0, end: 30, type: 'music' },
    { src: 'audio/music-mechanism.mp3', volume: 0.12, start: 26, end: 95, type: 'music' },
    { src: 'audio/music-outro.mp3', volume: 0.12, start: 91, end: 120, type: 'music' },
  ],
  ducking: {
    target: 'music',
    triggeredBy: 'narration',
    reduction: 20,  // dB
    attack: 0.05,   // seconds
    release: 0.2,   // seconds
  }
}
```

### Quality check
- Listen through headphones and verify narration intelligibility
- Check that music crossfades are inaudible — no abrupt transitions
- Verify no clipping at any point
- Confirm music is reduced during dense technical sections (scenes 3, 4, 6)

---

## 12. Captions and Accessibility

### Caption generation
1. Generate captions from the **final narration audio**, not from the script
2. Use word-level timing from Gemini TTS output
3. Format: SRT and VTT files

### Caption formatting rules
- Maximum 42 characters per line
- Maximum 2 lines per caption
- Minimum 1.5 seconds display duration
- Maximum 6 seconds display duration
- Split at natural phrase boundaries
- Technical terms must be correctly capitalized (JSON-RPC, OAuth, PKCE, MCP)
- Acronyms spelled correctly (M-C-P when spoken as letters)

### Caption placement
- Bottom center, 40px from bottom edge
- Semi-transparent dark background (`rgba(13, 17, 23, 0.85)`) behind text
- White text, weight 500, 18px Inter
- Do not cover diagrams or code — if a caption would overlap a diagram, move it up

### Accessibility requirements
- Important meaning is not conveyed by color alone — all state changes have shape or text differences
- Labels remain readable at 960×720 — minimum 12px font size
- Motion is not rapid enough to cause discomfort — no elements move faster than 300px/second
- No flashing effects — no element toggles visibility faster than 3 times per second
- Acronyms expanded at first use in narration
- Audio-only listeners can follow the central argument through narration alone
- Muted viewers can follow through captions and visual structure alone

### Subtitle files
Generate both `captions.srt` and `captions.vtt`:
- SRT for broad compatibility
- VTT for web embedding with styling hooks

---

## 13. Transitions and Pacing

### Transition semantics (every transition communicates)

| Transition | When to use | Scene application |
|-----------|-------------|-------------------|
| **Fade from black** | Opening, establishing a new context | Scene 1 (start of video) |
| **Crossfade** | Moving between related concepts at same level | Scenes 1→2, 6→7, 7→8 |
| **Slide left** | Moving deeper into detail (zoom in) | Scene 2→3 (title → YAML detail) |
| **Morph** | One diagram transforms into another (redesign) | Scene 3→4 (YAML pass → assertion failure) |
| **Slide right** | Introducing a new orthogonal concept | Scene 4→5 (wire visibility → partner swap) |
| **Slide up** | Moving from architecture to operational reality | Scene 6→7 (architecture → CI gate) |

### Pacing requirements
- **Visual dwell time:** Each diagram state must be visible for at least 2 seconds before animating further
- **Label reading time:** Allow 1.5 seconds per on-screen label before transitioning away
- **Arrow comprehension:** Directional arrows must be visible for at least 1 second before the element they point to appears
- **Code reading time:** Code blocks must be visible for at least 3 seconds before the next element appears
- **Scene transitions:** 300ms transition duration, ease-in-out curve
- **No scene ends before its concept is understandable**

---

## 14. Branding and Overlays

### Branding
- **Logo:** rmax.ai logo or mcp-conformance project logo (if available) — bottom-right corner, 24px height, 20% opacity
- **Watermark:** None — this is a public technical explainer
- **Confidentiality:** Not applicable — MIT-licensed open source project
- **Source footer:** "github.com/rmax-ai/mcp-conformance" — bottom-left corner, 11px, 40% opacity, visible during scenes 2–7, hidden during scene 1 (opening) and scene 8 (conclusion)
- **Author:** Not displayed — the project is the subject
- **Website:** "mcp-conformance.rmax.tech" — appears briefly in scene 8 alongside the repo URL
- **Intro treatment:** Fade from black, title appears
- **Outro treatment:** Final principle holds for 2 seconds, fades to black over 500ms

### Overlay rules
- Branding must remain subordinate to the explanation — never compete with diagrams or labels
- Source footer stays inside safe margins (40px from edges)
- Source footer visibility: 40% opacity, ensure contrast against both dark backgrounds and code blocks

---

## 15. Rendering and Export

### Final render specification
- **Format:** MP4
- **Codec:** H.264 (High Profile, Level 4.0)
- **Resolution:** 960×720 (4:3 at 720p)
- **Aspect ratio:** 4:3
- **Frame rate:** 30 fps
- **Audio codec:** AAC-LC, 192 kbps
- **Audio sample rate:** 48 kHz
- **Audio channels:** Stereo
- **Bitrate target:** 3–5 Mbps (VBR)
- **Captions:** Burned-in (always visible) + separate SRT/VTT files
- **Thumbnail:** Frame at 00:05 (architecture diagram or title card) — 960×720 PNG
- **File name:** `mcp-conformance-overview-720p.mp4`
- **Metadata:** Title="MCP Conformance — Protocol Testing, Declared in YAML", Author="rmax.ai"

### ARM64 rendering specific
- Set `HYPERFRAMES_BROWSER_PATH` to Playwright's Chromium
- Use Node ≥22 (`nvm use 24`)
- Ensure ffprobe is available: `which ffprobe`
- Clean `/tmp` before rendering: `rm -rf /tmp/hyperframes-*`
- Verify `/tmp` has at least 500MB free

### Tail buffer
Add a 5-second invisible padding element past the intended video end (at 120s) to prevent narration cutoff during rendering.

### Post-render trim
If audio extends past the composition, trim with:
```bash
ffmpeg -y -i output.mp4 -t 120 -c copy mcp-conformance-overview-720p.mp4
```

### Web-optimized derivative
Generate a 720p web-optimized version:
```bash
ffmpeg -y -i mcp-conformance-overview-720p.mp4 \
  -c:v libx264 -crf 23 -preset fast \
  -movflags +faststart \
  -c:a aac -b:a 128k \
  mcp-conformance-overview-720p-web.mp4
```

---

## 16. Quality-Assurance Checklist

Require the downstream agent to verify:

### Content
- [ ] Central thesis is clear within the first 10 seconds
- [ ] All major claims are supported by source material (see §2)
- [ ] Qualifications are preserved — "Draft" status of scenarios, "experimental" maturity labels
- [ ] No unsupported statistics, quotations, API names, or features introduced
- [ ] Terminology is consistent with the project: "partner adapter" not "server connector"
- [ ] Conclusion states a transferable principle ("Test the protocol, not the implementation")

### Pedagogy
- [ ] Audience can follow without hidden prerequisites
- [ ] Each scene has exactly one learning objective (from storyboard §5)
- [ ] Complexity is introduced progressively: problem → approach → mechanism → operation
- [ ] Declarative YAML example actually demonstrates the concept
- [ ] Architecture diagram is understandable when paused
- [ ] No scene introduces more than one new concept

### Visuals
- [ ] All labels are readable at 960×720 on a 13-inch display
- [ ] Arrows and directionality are unambiguous
- [ ] Color has consistent meaning throughout (green = success, red = failure, blue = data flow)
- [ ] Motion communicates concepts (never purely decorative)
- [ ] No visual element is decorative unless intentionally atmospheric (none should be)
- [ ] Diagrams match the project's actual architecture

### Synchronization
- [ ] Visual reveals align with narration (within 300ms of corresponding phrase)
- [ ] Scene cuts do not interrupt mid-sentence
- [ ] Captions match final audio (not only the original script)
- [ ] Music transitions align with scene boundaries (within 200ms)
- [ ] No scene ends before its learning objective is visually complete

### Audio
- [ ] Narration is intelligible throughout — no word is masked by music
- [ ] Music never exceeds -18dB relative to narration during speech
- [ ] No clipping, abrupt cuts, or audible loop seams in music tracks
- [ ] Pronunciations correct: "M-C-P", "P-K-C-E", "J-Unit", "O-Auth"
- [ ] Integrated loudness is consistent — no volume jumps between scenes

### Technical
- [ ] Project renders deterministically — same output on two consecutive renders
- [ ] All assets resolve locally (no CDN dependencies for fonts, icons)
- [ ] Final duration is 120s ±3s
- [ ] Frame rate is stable at 30 fps — no dropped frames
- [ ] No missing fonts or layout shifts on headless render
- [ ] Headless rendering succeeds without browser interaction
- [ ] Final MP4 plays correctly in VLC, Chrome, and Firefox
- [ ] Subtitle files load correctly and display in-sync

---

## 17. Required Deliverables

The production agent must produce:

1. **Final narration script** — the script from §4, verified against final audio
2. **Scene-by-scene storyboard** — the table from §5, updated with actual timings from audio
3. **Machine-readable scene manifest** — `scene-manifest.yaml` with exact timestamps
4. **HyperFrames project source** — complete `mcp-conformance-video/` directory with all HTML, CSS, JS, and config files
5. **Generated narration audio** — `audio/narration.mp3` (Charon voice, 140 wpm target)
6. **Generated music** — 3 MP3 files: `music-intro.mp3`, `music-mechanism.mp3`, `music-outro.mp3`
7. **Mixed audio** — embedded in final MP4 with ducking applied
8. **Captions** — `captions/captions.srt` and `captions/captions.vtt`
9. **Final rendered MP4** — `mcp-conformance-overview-720p.mp4`
10. **Thumbnail** — `thumbnail.png` at 960×720
11. **Source and attribution file** — `SOURCES.md` listing all source material and claims
12. **README** — `README.md` with exact reproduction commands (dependencies, audio generation, render command)
13. **QA report** — `QA-REPORT.md` documenting checklist results and any known limitations

---

## 18. Acceptance Criteria

The video is accepted when:

- **Duration:** 120 seconds ±3 seconds
- **Thesis clarity:** The core thesis is clear within the first 10 seconds
- **All QA checklist items pass** (see §16)
- **Narration intelligibility:** Every word is understandable throughout
- **Final principle stated explicitly:** "Test the protocol, not the implementation."
- **Viewer comprehension test:** A platform engineer with assumed prior knowledge can restate:
  - What mcp-conformance does (scenario-driven conformance testing)
  - How it works (YAML scenarios → runner → partner → assertions → reports)
  - Why the partner adapter pattern matters (one scenario catalog, any server)
  - How to integrate it (CI gate, exit codes, JUnit XML)
- **Audio-only comprehension:** The video works as audio-only (narration alone conveys the argument)
- **Muted comprehension:** The video works muted with captions (visuals + captions convey the argument)
- **Deterministic reproduction:** The project re-renders from source producing identical output
- **Source claims verifiable:** Every claim can be traced to source material listed in §2
