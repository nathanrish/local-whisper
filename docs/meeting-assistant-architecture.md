# Meeting Assistant Architecture (Granola-Style)

## 1) Product Vision
Build a desktop-first AI meeting assistant that:
- Captures meeting audio from Zoom/Teams/Meet directly on the user device.
- Produces low-latency live transcript with speaker-aware turns.
- Generates structured notes and actionable summaries in near real time.
- Supports post-meeting workflows: action items, decisions, follow-up emails, and knowledge sync.

## 2) User Experience Goals
1. **One-click start**: open app and click “Join as assistant” before a meeting.
2. **Invisible during calls**: no bot participant required for baseline functionality.
3. **Live confidence**: users see transcript and evolving notes while the meeting runs.
4. **High trust**: every generated note traces back to transcript evidence.
5. **Fast handoff**: immediately after meeting, export to Slack/Notion/Confluence/Jira/email.

## 3) Core Functional Requirements

### Real-time capture and transcription
- Capture system audio + microphone mix locally (with permission gating).
- Stream chunks (e.g., 1–3 seconds) to transcription engine.
- Support multilingual meetings and automatic language detection.
- Diarization (speaker separation) + timestamped segments.

### AI note generation
- Continuous rolling summaries:
  - Agenda and context
  - Key points by topic
  - Decisions made
  - Risks/open questions
  - Action items with owner + due date extraction
- “Ask meeting” chat grounded only in transcript + notes.

### Post-meeting output
- Final polished summary in multiple templates:
  - Executive summary
  - Team standup notes
  - Sales call recap
  - Product discovery notes
- Artifact export: Markdown, PDF, and direct integrations.

### Governance and controls
- Consent workflows and recording indicators.
- Workspace retention policies.
- Per-meeting data deletion and redaction controls.
- PII masking options for stored transcript.

## 4) Non-Functional Requirements
- **Latency**: transcript partials < 2s, finalized segments < 6s.
- **Reliability**: recover from temporary network loss via local buffer + retry.
- **Security**: encryption in transit and at rest; tenant isolation.
- **Scalability**: horizontal streaming workers, stateless APIs.
- **Observability**: trace each note sentence to source transcript spans.

## 5) High-Level System Architecture

```text
┌───────────────────────┐
│ Desktop App (Electron │
│ or Tauri)             │
│ - Audio capture       │
│ - Live transcript UI  │
│ - Notes panel         │
└──────────┬────────────┘
           │ WebSocket/gRPC
┌──────────▼───────────────────────────────────────┐
│ Realtime Ingestion Gateway                       │
│ - AuthN/AuthZ                                     │
│ - Session management                              │
│ - Stream fanout                                   │
└──────────┬───────────────────────────────────────┘
           │
┌──────────▼─────────┐   ┌───────────────────────┐
│ ASR Service         │   │ Diarization Service   │
│ - Streaming STT     │   │ - Speaker turns       │
│ - Lang detect       │   │ - Confidence          │
└──────────┬─────────┘   └──────────┬────────────┘
           └──────────────┬──────────┘
                          │
                 ┌────────▼──────────────┐
                 │ Transcript Orchestrator│
                 │ - Segment merge        │
                 │ - Temporal ordering    │
                 │ - Evidence indexing    │
                 └────────┬──────────────┘
                          │
       ┌──────────────────▼─────────────────────┐
       │ Notes & Insights Engine                 │
       │ - Incremental summarization             │
       │ - Action item extraction                │
       │ - Decision/risk detection               │
       │ - Grounded Q&A                          │
       └──────────────────┬─────────────────────┘
                          │
       ┌──────────────────▼─────────────────────┐
       │ Storage Layer                           │
       │ - Raw audio (optional, policy based)    │
       │ - Transcript store (OLTP)               │
       │ - Search index/vector index             │
       │ - Notes artifacts                        │
       └──────────────────┬─────────────────────┘
                          │
       ┌──────────────────▼─────────────────────┐
       │ Integrations + API                      │
       │ - Slack/Notion/Confluence/Jira/CRM      │
       │ - Webhooks + export endpoints           │
       └─────────────────────────────────────────┘
```

## 6) Recommended Tech Stack

### Client
- **Desktop**: Tauri (Rust + web frontend) for smaller footprint or Electron for faster iteration.
- **UI**: React + TypeScript.
- **Audio capture**: OS-native APIs wrapped in desktop shell.

### Backend
- **API/Gateway**: Go or Node.js (WebSocket/gRPC streaming).
- **Orchestration**: Python service for NLP pipeline composition.
- **ASR options**:
  - Managed: Deepgram, AssemblyAI, Azure Speech.
  - Self-hosted: Whisper large-v3 / faster-whisper (GPU-backed).
- **LLM layer**:
  - Real-time summarization: GPT-4.1/4o class model.
  - Cost control: small model for extraction/classification + larger model for final synthesis.

### Data
- **Transactional DB**: Postgres.
- **Cache/queues**: Redis + Kafka (or NATS).
- **Search**: OpenSearch/Elasticsearch for transcript lookup.
- **Object storage**: S3-compatible buckets.

## 7) Data Model (Core Entities)
- `workspace`
- `user`
- `meeting_session`
- `audio_chunk`
- `transcript_segment` (speaker, start_ts, end_ts, confidence)
- `note_block` (type: summary/decision/action/risk)
- `action_item` (owner, due_date, status, evidence_span_ids)
- `integration_export`
- `consent_event` and `retention_policy`

## 8) Real-Time Processing Flow
1. Desktop app opens meeting session and captures audio stream.
2. Chunks are sent to gateway with sequence IDs.
3. ASR returns partial and final transcript segments.
4. Diarization enriches speaker labels.
5. Orchestrator writes canonical segment timeline.
6. Notes engine updates rolling summary every N finalized segments.
7. UI receives transcript + notes diffs over WebSocket.
8. On meeting end, finalize summary and generate exports.

## 9) Quality Strategy
- **ASR WER tracking** by domain (sales, eng, support).
- **Note faithfulness score**: % of note claims backed by transcript spans.
- **Action item precision/recall** on labeled evaluation sets.
- **Human feedback loop**: user edits become supervised signals.

## 10) Security, Privacy, and Compliance
- SOC 2 controls from day one.
- Optional HIPAA-ready deployment profile.
- Tenant-based encryption keys (KMS).
- Regional data residency controls.
- Fine-grained RBAC and audit logs for note access/edit/export.

## 11) MVP Scope (90 days)
- Desktop capture for macOS + Windows.
- English transcription with speaker labels.
- Live transcript + rolling notes.
- Final recap with decisions + action items.
- Notion + Slack export.
- Basic workspace/user management and retention settings.

## 12) Roadmap Beyond MVP
- Native calendar integration with auto-start suggestions.
- Multi-meeting memory (project-level context stitching).
- CRM-specific templates (SFDC/HubSpot).
- Voiceprint-based speaker identification.
- “Prep me for this meeting” pre-brief using prior notes.

## 13) Build Phasing Plan

### Phase 1: Foundations (Weeks 1–4)
- Session/auth model, streaming gateway, basic desktop capture.
- Baseline ASR integration and transcript rendering.

### Phase 2: Intelligence (Weeks 5–8)
- Incremental summarization, action extraction, evidence links.
- Notes editor and post-meeting finalization.

### Phase 3: Productization (Weeks 9–12)
- Integrations, security hardening, observability dashboards.
- Beta program with quality instrumentation.

## 14) Risks and Mitigations
- **OS audio capture complexity** → ship with robust diagnostics and fallback capture modes.
- **Model hallucination in notes** → strict grounding and citation-only generation policy.
- **Latency spikes** → dynamic model selection + backpressure handling.
- **Privacy concerns** → transparent consent UX + clear retention controls.

## 15) Benchmarking Against Granola
To approach Granola-like user delight:
- Keep UI minimal and keyboard-first.
- Prioritize transcript readability and confidence indicators.
- Make generated notes editable and traceable to exact utterances.
- Deliver post-call output in < 30 seconds after end.
