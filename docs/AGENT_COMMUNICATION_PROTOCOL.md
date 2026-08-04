# AGENT COMMUNICATION PROTOCOL (ACP)

Version: 1.0

---

# Purpose

ACP defines how AI agents communicate, exchange tasks, report progress, handle failures, and collaborate within DigiEmp.

Every internal AI worker must follow ACP.

---

# Principles

- Standardized communication
- Stateless messages
- Traceable execution
- Secure communication
- Retry support
- Human approval support
- Complete logging

---

# Message Structure

Message ID

Mission ID

Workflow ID

Task ID

Parent Task ID

Source Agent

Destination Agent

Timestamp

Priority

Status

Payload

Attachments

Required Response

Timeout

Retry Count

Correlation ID

---

# Message Types

TASK_ASSIGNMENT

TASK_ACCEPTED

TASK_REJECTED

TASK_STARTED

TASK_PROGRESS

TASK_COMPLETED

TASK_FAILED

REQUEST_INFORMATION

SEND_INFORMATION

REQUEST_MEMORY

MEMORY_RESPONSE

REQUEST_APPROVAL

APPROVAL_GRANTED

APPROVAL_DENIED

WARNING

ERROR

HEARTBEAT

SYSTEM_EVENT

---

# Agent States

Idle

Thinking

Planning

Working

Waiting

Blocked

Reviewing

Completed

Failed

Offline

---

# Priority Levels

Critical

High

Medium

Low

Background

---

# Retry Policy

Immediate Retry

Delayed Retry

Escalation

Manual Review

Mission Abort

---

# Logging

Every message must be logged.

Every state change must be logged.

Every error must be logged.

---

# Future Features

Streaming Messages

Distributed Agents

Remote Workers

Encrypted Payloads

Digital Signatures

Cross-Server Communication