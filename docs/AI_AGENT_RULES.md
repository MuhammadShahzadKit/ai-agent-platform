# AI AGENT RULES

## General Rules

Every AI agent must:

- Perform only its assigned responsibility.
- Never modify another agent's internal state.
- Return structured outputs.
- Log important actions.
- Handle failures gracefully.
- Request clarification when required.
- Respect user permissions.
- Support human approval for sensitive actions.

---

## Communication Rules

Agents communicate only through the Master Orchestrator.

Agents do not directly invoke other agents.

---

## Security Rules

- Never expose secrets.
- Never store plaintext credentials.
- Validate all inputs.
- Log security events.