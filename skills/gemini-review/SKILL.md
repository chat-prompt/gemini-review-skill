---
name: gemini-review
description: Interactive code review using Google Gemini 3.0 Flash with Conventional Comments methodology. MANDATORY - runs automatically after every code implementation (Edit, Write tools). Provides numbered issues for selective fixing. Reviews for security, bugs, performance, and best practices. Triggers automatically - no user request needed.
---

# Gemini Review

Interactive code review with selective fix application using Gemini 3.0 Flash.

## Critical Behavior - MANDATORY

**After EVERY Edit or Write tool that modifies code files:**

1. Run review: `python scripts/gemini_review.py --files "<modified_files>"`
2. Display the numbered issue list
3. Ask user: "Which issues to fix? (1,2,3 / all / blocking / skip)"
4. Apply selected fixes using Edit tool
5. If blocking issues remain after fixes, re-run review

**Do NOT skip this. Do NOT ask permission. This is automatic.**

## Review Output Format

Issues are displayed with selection numbers:

```
═══════════════════════════════════════════════════════════════
🔍 GEMINI CODE REVIEW
═══════════════════════════════════════════════════════════════

📁 Reviewed: auth.py, utils.py
🧠 Thinking: medium
🔄 Verdict: REQUEST_CHANGES (2 blocking)

Code has security issues that need immediate attention.

┌───────────────────────────────────────────────────────────────┐
│ 🚨 BLOCKING (Must Fix)                                        │
├───────────────────────────────────────────────────────────────┤
│ [1] auth.py:42 - Plaintext password comparison                │
│     Category: security | Effort: small                        │
│     → Use secrets.compare_digest() for timing-safe compare    │
│                                                               │
│ [2] auth.py:67 - SQL injection vulnerability                  │
│     Category: security | Effort: small                        │
│     → Use parameterized queries                               │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│ ⚠️ WARNINGS (Should Fix)                                      │
├───────────────────────────────────────────────────────────────┤
│ [3] utils.py:15 - Missing error handling                      │
│     Effort: trivial                                           │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│ 💡 SUGGESTIONS (Optional)                                     │
├───────────────────────────────────────────────────────────────┤
│ [4] Consider using dataclass for User model                   │
└───────────────────────────────────────────────────────────────┘

✅ Positive: Good separation of concerns; Clean function naming

─────────────────────────────────────────────────────────────────
Select: numbers (1,2,3) | 'all' | 'blocking' | 'skip'
═══════════════════════════════════════════════════════════════
```

## Selection Options

| Input | Action |
|-------|--------|
| `1,2,3` | Fix specific issues by number |
| `all` | Fix all issues |
| `blocking` | Fix blocking issues only (recommended default) |
| `skip` | Continue without fixing |

## Workflow Example

```
User: "Add login function to auth.py"

Claude:
1. [Edit auth.py - add login function]
2. [Run] python scripts/gemini_review.py --files "auth.py"
3. [Display] Numbered issue list (2 blocking, 1 warning)
4. [Ask] "Found 2 blocking issues. Fix which? (1,2 / all / blocking / skip)"
5. [User] "blocking"
6. [Edit auth.py - fix issue 1: password comparison]
7. [Edit auth.py - fix issue 2: SQL injection]
8. [Report] "Fixed 2 blocking issues. Code ready."
```

## Command Options

```bash
# Standard review with interactive output
python scripts/gemini_review.py --files "file.py"

# JSON output for programmatic use
python scripts/gemini_review.py --files "file.py" --json

# Focus on specific area
python scripts/gemini_review.py --files "file.py" --focus security
python scripts/gemini_review.py --files "file.py" --focus performance
python scripts/gemini_review.py --files "file.py" --focus quality

# Manual thinking level (auto-detected by default)
python scripts/gemini_review.py --files "file.py" --think high
```

## Thinking Levels

| Level | When Used | Description |
|-------|-----------|-------------|
| `minimal` | <100 lines, simple code | Fast review |
| `medium` | Multiple files, complex logic | Balanced (default) |
| `high` | Security-sensitive, >500 lines | Deep analysis |

Thinking level is **auto-detected** based on:
- Code size and complexity
- Presence of security-related code (auth, passwords, SQL)
- Number of files and classes

## Exit Codes

| Code | Meaning | Claude Action |
|------|---------|---------------|
| 0 | Success / No issues | Show results, continue |
| 1 | API or general error | Log error, continue work |
| 2 | No API key | Prompt for key setup |
| 3 | Has blocking issues | Prompt for fix selection |

## Review Methodology

Uses **Conventional Comments** standard:

| Label | Severity | Meaning |
|-------|----------|---------|
| `issue(blocking)` | critical | Must fix (security, bugs) |
| `issue(non-blocking)` | high | Should fix |
| `suggestion` | medium | Optional improvement |
| `nitpick` | low | Style/preference |
| `praise` | - | What's done well |

## First-Time Setup

If exit code 2 (NO_API_KEY):

1. Prompt: "Gemini API key required. Get one at: https://aistudio.google.com/apikey"
2. Run: `python scripts/setup_api_key.py --key "<user_key>"`
3. Re-run review

## Files to Review

**Include:** `.py`, `.ts`, `.tsx`, `.js`, `.jsx`, `.go`, `.rs`, `.java`, `.kt`, `.swift`, `.c`, `.cpp`, `.rb`, `.php`

**Skip:** `.json`, `.yaml`, `.md`, `.txt`, `.lock`, `.log`, `.env`

## Error Handling

**Never block user's work due to review errors.** If API fails:
1. Log the error
2. Continue with the task
3. Note that review was skipped

## Detailed Criteria

For comprehensive review criteria, see `references/review-criteria.md`.
