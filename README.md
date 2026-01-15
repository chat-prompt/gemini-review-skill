# Gemini Review Skill for Claude Code

Interactive code review using Google Gemini 3.0 Flash with Conventional Comments methodology.

## Features

- **Automatic Trigger**: Runs automatically after every code modification (Edit/Write tools)
- **Selective Fixing**: Numbered issue list for selective fix application
- **Smart Analysis**: Auto-detects thinking level based on code complexity
- **Conventional Comments**: Uses industry-standard review methodology
- **Multi-language Support**: Python, TypeScript, JavaScript, Go, Rust, Java, Kotlin, Swift, C/C++, Ruby, PHP

## Installation

### 1. Clone the skill

```bash
# For project-specific installation
mkdir -p skills
cd skills
git clone https://github.com/YOUR_USERNAME/gemini-review-skill.git gemini-review

# OR for global installation (all projects)
git clone https://github.com/YOUR_USERNAME/gemini-review-skill.git ~/.claude/skills/gemini-review
```

### 2. Install dependencies

```bash
pip install google-generativeai python-dotenv
```

### 3. Set up API key

Get your free API key from [Google AI Studio](https://aistudio.google.com/apikey)

```bash
python skills/gemini-review/scripts/setup_api_key.py --key "YOUR_API_KEY"
```

## Usage

The skill runs **automatically** after every code modification. No manual trigger needed.

### Workflow Example

```
User: "Add login function to auth.py"

Claude:
1. [Edit auth.py - add login function]
2. [Auto-run review]
3. [Display]
   🔍 GEMINI CODE REVIEW
   ═══════════════════════
   📁 Reviewed: auth.py
   🔄 Verdict: REQUEST_CHANGES (2 blocking)

   🚨 BLOCKING (Must Fix)
   [1] auth.py:42 - Plaintext password comparison
   [2] auth.py:67 - SQL injection vulnerability

   ⚠️ WARNINGS (Should Fix)
   [3] auth.py:89 - Missing error handling

4. [Ask] "Fix which issues? (1,2,3 / all / blocking / skip)"
5. [User] "blocking"
6. [Apply fixes for issues 1 and 2]
7. [Report] "Fixed 2 blocking issues. Code ready."
```

### Selection Options

| Input | Action |
|-------|--------|
| 1,2,3 | Fix specific issues by number |
| all | Fix all issues |
| blocking | Fix blocking issues only (recommended) |
| skip | Continue without fixing |

## Manual Usage

```bash
# Standard review
python scripts/gemini_review.py --files "file.py"

# Focus on specific area
python scripts/gemini_review.py --files "file.py" --focus security
python scripts/gemini_review.py --files "file.py" --focus performance

# Force thinking level
python scripts/gemini_review.py --files "file.py" --think high
```

## Review Criteria

### Issue Types

- **issue(blocking)**: Critical - Must fix (security, bugs)
- **issue(non-blocking)**: High - Should fix
- **suggestion**: Medium - Optional improvement
- **nitpick**: Low - Style/preference
- **praise**: What's done well

### Focus Areas

- **Security**: SQL injection, XSS, authentication issues
- **Bugs**: Logic errors, null references, race conditions
- **Performance**: O(n²) algorithms, memory leaks, unnecessary operations
- **Best Practices**: SOLID principles, clean code, error handling

## Configuration

### Thinking Levels

Auto-detected based on code size, complexity, and security sensitivity.

- **minimal**: <100 lines, simple code - Fast review
- **medium**: Multiple files, complex logic - Balanced (default)
- **high**: Security-sensitive, >500 lines - Deep analysis

## Troubleshooting

### No API Key Error

```bash
python scripts/setup_api_key.py --key "YOUR_API_KEY"
```

### API Rate Limits

Free tier: 15 RPM, 1M TPM, 1500 RPD
If you hit limits, wait a minute or upgrade to paid tier.

### Review Not Running

Ensure the skill is in the correct location:
- Project: `<project-root>/skills/gemini-review/`
- Global: `~/.claude/skills/gemini-review/`

## License

MIT License

## Credits

Built for Claude Code using Google Gemini 3.0 Flash API.
