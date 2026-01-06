# Learnings: Agentic AI Patterns for Professional Representation

Key insights from building an intelligent interactive AI agent with autonomous action capabilities.

---

## 1. Context Injection vs. RAG Trade-off

**When to use RAG:**
- Large document corpus (100+ pages)
- Frequently updated content
- Need semantic search across many topics

**When to use Context Injection:**
- Small, stable data (<50KB)
- Need 100% recall guarantee
- Simplicity over scalability

| Factor | RAG | Context Injection |
|--------|-----|-------------------|
| Latency | Higher (retrieval) | Lower (direct) |
| Recall | Depends on chunks | 100% |
| Complexity | Higher | Lower |
| Updates | Dynamic | Requires redeploy |

**This project:** CV is ~10KB → Context injection wins.

---

## 2. Structured Outputs Enable Determinism

**The insight:** LLMs are stochastic, but the ACTION taken can be deterministic.

**Pattern:**
```
LLM → JSON with "type" field → Router → Deterministic handler
```

**Implementation:**
```python
if response_type == 'reply':
    return self._handle_reply(parsed)
elif response_type == 'log_lead':
    return self._handle_lead_log(parsed)
```

**Result:** Variable LLM output, but consistent system behavior.

---

## 3. Agentic Workflow = Perception-Action Loop

**Traditional chatbot:** Input → Response → Done

**Agentic pattern:** Input → Perceive → Reason → Act → Observe → Respond

| Stage | This Project |
|-------|--------------|
| Perceive | Parse user message for intent signals |
| Reason | LLM decides response type |
| Act | Log to Google Sheets (tool use) |
| Observe | Capture API result |
| Respond | Confirm action to user |

**Key insight:** The "agentic" part is the autonomous decision to take external action.

---

## 4. Knowledge Grounding Eliminates Hallucination

**Problem:** LLMs hallucinate plausible facts.

**Solution hierarchy:**
1. **Source of truth:** Single YAML file with all facts
2. **Prompt injection:** Full profile in system prompt
3. **Negative instruction:** "Do NOT invent facts"
4. **Fallback response:** "That's not in my profile"

**Effectiveness:**
| Technique | Hallucination Risk |
|-----------|-------------------|
| None | High |
| Instruction only | Medium |
| Context + instruction | Low |
| Context + instruction + fallback | Very Low |

---

## 5. Few-Shot > Fine-Tuning for Intent Detection

**Without labeled data, how to detect intent?**

**Fine-tuning:** Requires thousands of labeled examples, compute, iteration.

**Few-shot:** Provide 4-5 examples in prompt:
```
Trigger examples:
- "Can we schedule a call?"
- "What's your email?"
- "Send me your resume"
```

**Result:** LLM generalizes from examples to detect novel phrasings.

**Lesson:** For narrow intent detection, few-shot prompting often beats fine-tuning.

---

## 6. Graceful Degradation Enables Demos

**Problem:** External API dependencies (Google Sheets) block demos.

**Pattern:** Simulation mode with identical interface:
```python
def append_lead_to_sheet(...) -> dict:
    return {'status': 'ok', 'message': 'Lead logged'}

def simulate_lead_logging(...) -> dict:
    return {'status': 'ok', 'message': 'Lead logged (simulation)'}
```

**Key insight:** Same return type enables transparent fallback.

---

## 7. Persona Prompting for Voice Consistency

**Challenge:** Maintain first-person voice across all responses.

**Weak prompting:** "Speak as Gregory"
- Model sometimes slips to third person

**Strong prompting:**
```
"You are an agentic professional profile for {name}.
You speak in FIRST PERSON as {name}. You ARE {name}."
```

**Reinforcement:** Repeat persona at end of prompt:
```
"Remember: You ARE {name}. Speak as yourself."
```

---

## 8. Email Validation at System Boundaries

**Principle:** Validate at boundaries, trust internal code.

**Boundary:** User-provided email before external API call.

```python
def validate_email(email: str) -> bool:
    if email.count('@') != 1:
        return False
    local_part, domain = email.split('@')
    # ... additional checks
```

**Don't:** Validate at every function call (over-engineering).

---

## Summary

| Learning | Application |
|----------|-------------|
| Context injection for small data | Simpler than RAG, 100% recall |
| Structured outputs | Deterministic routing from stochastic LLM |
| Perception-action loop | Agentic = autonomous external actions |
| Knowledge grounding | Context + instruction + fallback |
| Few-shot intent detection | No fine-tuning needed |
| Graceful degradation | Demos work without APIs |
| Strong persona prompting | Consistent first-person voice |
| Boundary validation | Validate at edges, trust internal |

---

> See [CHALLENGES.md](CHALLENGES.md) for implementation challenges.
> See [ARCHITECTURE.md](ARCHITECTURE.md) for system design.
