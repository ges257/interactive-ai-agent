# Architecture

## System Overview

The Interactive AI Agent is a context-injection system that transforms a static professional profile into an interactive conversational agent with autonomous action capabilities.

```mermaid
flowchart TB
    subgraph S1["Stage 1: Profile Loading"]
        A1["profile.yaml"]
        A2["Structured CV data"]
        A1 --> A2
    end

    subgraph S2["Stage 2: Context Injection"]
        B1["System prompt builder"]
        B2["Full profile embedded"]
        B1 --> B2
    end

    subgraph S3["Stage 3: Conversation"]
        C1["Claude API call"]
        C2["JSON response"]
        C1 --> C2
    end

    subgraph S4["Stage 4: Action Routing"]
        D1["Response parser"]
        D2["reply | log_lead"]
        D1 --> D2
    end

    S1 --> S2 --> S3 --> S4

    S4 --> E["User Response or Sheet Update"]

    style S1 fill:#1a1a2e,stroke:#A78BFA,color:#A3B8CC
    style S2 fill:#1a1a2e,stroke:#A78BFA,color:#A3B8CC
    style S3 fill:#1a1a2e,stroke:#A78BFA,color:#A3B8CC
    style S4 fill:#1a1a2e,stroke:#A78BFA,color:#A3B8CC
    style E fill:#A78BFA,stroke:#A78BFA,color:#0D1B2A
    linkStyle 0,1,2,3,4 stroke:#FFFFFF,stroke-width:2px
```

---

## Why Context Injection (Not RAG)

| Approach | Use Case | Our Choice |
|----------|----------|------------|
| RAG | Large document corpus, dynamic updates | No |
| Context Injection | Small, static data (~10KB) | Yes |

**Rationale:** A professional CV is small enough to fit entirely in the system prompt. This eliminates retrieval latency, ensures 100% recall, and guarantees factual grounding since the model can only reference injected content.

---

## Response Contract

The agent returns structured JSON to enable deterministic action routing:

### Format 1: Conversational Reply

```json
{
  "type": "reply",
  "message": "I worked at Ernst & Young as an external consultant..."
}
```

### Format 2: Lead Logging Action

```json
{
  "type": "log_lead",
  "company": "Acme Corp",
  "contact_name": "Jane Smith",
  "contact_email": "jane@acme.com",
  "role_title": "ML Engineer",
  "notes": "Discussed RAG systems and GNN experience"
}
```

---

## Intent Detection

The agent autonomously triggers lead logging when it detects hiring intent:

```mermaid
flowchart LR
    subgraph Triggers["Intent Triggers"]
        T1["Schedule request"]
        T2["Contact request"]
        T3["Resume request"]
        T4["Hiring statement"]
    end

    subgraph Action["Autonomous Action"]
        A1["Extract lead data"]
        A2["Log to Google Sheets"]
        A3["Confirm to user"]
    end

    Triggers --> Action

    style Triggers fill:#1a1a2e,stroke:#A78BFA,color:#A3B8CC
    style Action fill:#1a1a2e,stroke:#A78BFA,color:#A3B8CC
```

**Trigger Examples:**
- "Can we schedule an interview?"
- "What's your email?"
- "Send me your resume"
- "We'd like to move forward"

---

## Module Responsibilities

| Module | Lines | Responsibility |
|--------|-------|----------------|
| `app.py` | ~150 | Streamlit web interface, session management |
| `agent.py` | ~100 | Core chat logic, Claude API integration, response routing |
| `prompts.py` | ~60 | System prompt template with JSON contract |
| `tools.py` | ~150 | Profile loading, email validation, Google Sheets API |
| `profile.yaml` | ~200 | Structured professional profile data |

---

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant S as Streamlit
    participant A as Agent
    participant C as Claude API
    participant G as Google Sheets

    U->>S: Ask question
    S->>A: chat(message)
    A->>C: messages.create()
    Note over A,C: System prompt includes full profile
    C->>A: JSON response
    A->>A: Parse response type

    alt type = "reply"
        A->>S: Return message
        S->>U: Display response
    else type = "log_lead"
        A->>G: append_lead_to_sheet()
        A->>S: Return confirmation
        S->>U: Display confirmation
    end
```

---

## Graceful Degradation

| Component | Missing | Fallback |
|-----------|---------|----------|
| Claude API | No `ANTHROPIC_API_KEY` | Error message, sidebar still works |
| Google Sheets | No `GOOGLE_SHEETS_ID` | Simulation mode (logs to console) |
| Service Account | No `credentials.json` | Simulation mode |

---

## Profile Schema

```yaml
profile:
  name: string
  headline: string
  location: string
  contact:
    email: string
    phone: string
    linkedin: string
    github: string
  summary: string
  education: list
  experience: list
  publications: list
  skills:
    ml_frameworks: list
    llm_platforms: list
    concepts: list
```

---

## Security Considerations

| Risk | Mitigation |
|------|------------|
| API Key Exposure | Environment variables, .gitignore |
| Profile Injection | YAML safe_load, no code execution |
| Lead Data Privacy | Optional Google Sheets, simulation fallback |
| Hallucination | Context-injection ensures factual grounding |
