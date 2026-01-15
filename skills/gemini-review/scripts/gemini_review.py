#!/usr/bin/env python3
"""
Gemini Code Review Script

Automatically reviews code using Google Gemini 3.0 Flash API.
Outputs structured JSON for interactive issue selection.

Usage:
    python gemini_review.py --files "file1.py,file2.ts"
    python gemini_review.py --files "src/main.py" --json
    python gemini_review.py --files "src/main.py" --json --think high
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

# JSON Schema for review output
JSON_SCHEMA = """{
  "summary": {
    "verdict": "approve|request_changes",
    "overview": "string",
    "stats": {"blocking": 0, "warning": 0, "suggestion": 0}
  },
  "issues": [
    {
      "id": 1,
      "type": "issue|suggestion|nitpick|praise",
      "severity": "blocking|non-blocking",
      "priority": "critical|high|medium|low",
      "category": "security|performance|quality|bug|style",
      "file": "filename.py",
      "line": 42,
      "code_snippet": "problematic code here",
      "title": "Short issue title",
      "description": "Detailed explanation",
      "suggested_fix": "Code or description of fix",
      "effort": "trivial|small|medium|large"
    }
  ],
  "positive_aspects": ["Good use of...", "Clean structure..."]
}"""


def get_api_key() -> Optional[str]:
    """Get API key from environment or .env file."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        return api_key

    env_file = Path.cwd() / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith('GEMINI_API_KEY='):
                    value = line.split('=', 1)[1]
                    return value.strip('"\'')
    return None


def ensure_genai_installed():
    """Ensure google-genai package is installed."""
    try:
        from google import genai
        return True
    except ImportError:
        print("📦 Installing google-genai package...")
        result = os.system(f"{sys.executable} -m pip install -q google-genai")
        return result == 0


def calculate_thinking_level(files: list, code_content: str) -> str:
    """Auto-detect appropriate thinking level based on code complexity."""
    total_lines = code_content.count('\n')
    file_count = len(files)

    # Check for complexity indicators
    has_security_code = any(kw in code_content.lower() for kw in
        ['password', 'auth', 'token', 'secret', 'encrypt', 'sql', 'query'])
    has_async = 'async' in code_content or 'await' in code_content
    has_classes = code_content.count('class ') > 2

    complexity_score = 0
    complexity_score += min(total_lines / 200, 2)  # Max 2 points for lines
    complexity_score += file_count * 0.5  # 0.5 per file
    complexity_score += 1 if has_security_code else 0
    complexity_score += 0.5 if has_async else 0
    complexity_score += 0.5 if has_classes else 0

    if complexity_score < 1.5:
        return "minimal"
    elif complexity_score < 3:
        return "medium"
    else:
        return "high"


def build_review_prompt(code_content: str, focus: Optional[str] = None) -> str:
    """Build the review prompt with Conventional Comments methodology."""

    focus_instruction = ""
    if focus:
        focus_map = {
            "security": "Focus especially on security: injection, secrets, auth, XSS, CSRF.",
            "performance": "Focus especially on performance: O(n²), memory leaks, blocking ops.",
            "quality": "Focus especially on quality: SOLID, naming, modularity, complexity."
        }
        focus_instruction = focus_map.get(focus, "")

    return f"""You are an expert code reviewer using Conventional Comments methodology.

## Review Methodology

**Label each issue:**
- `issue(blocking)`: MUST fix - security vulnerabilities, bugs, data loss risks
- `issue(non-blocking)`: SHOULD fix - performance, error handling
- `suggestion`: Could improve - refactoring, patterns
- `nitpick`: Minor - style, naming preferences
- `praise`: What's done well

**Priority (Microsoft guidelines):**
1. Security vulnerabilities → critical
2. Bugs/correctness → high
3. Performance → high (if measurable)
4. Maintainability → medium
5. Style → low

{focus_instruction}

## Code to Review

{code_content}

## Output Requirements

Respond with **valid JSON only** (no markdown, no code blocks, no extra text).

Schema:
{JSON_SCHEMA}

IMPORTANT:
- Include exact line numbers (count from 1)
- code_snippet: The actual problematic code
- suggested_fix: Copy-pasteable fix or clear instruction
- effort: trivial (<5min), small (<30min), medium (<2hr), large (>2hr)
- If code is excellent with no issues, verdict="approve" with empty issues array
- Maximum 10 issues unless code has serious problems
- Always include at least one positive_aspect"""


def parse_json_response(response_text: str) -> dict:
    """Parse and validate JSON response from Gemini."""
    # Try to extract JSON if wrapped in markdown
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
    if json_match:
        response_text = json_match.group(1)

    # Clean up common issues
    response_text = response_text.strip()

    try:
        data = json.loads(response_text)

        # Validate required fields
        if "summary" not in data:
            data["summary"] = {"verdict": "request_changes", "overview": "Review completed", "stats": {}}
        if "issues" not in data:
            data["issues"] = []
        if "positive_aspects" not in data:
            data["positive_aspects"] = []

        # Ensure issues have IDs
        for i, issue in enumerate(data["issues"], 1):
            if "id" not in issue:
                issue["id"] = i

        # Calculate stats if missing
        if "stats" not in data["summary"]:
            data["summary"]["stats"] = {}
        stats = data["summary"]["stats"]
        stats["blocking"] = sum(1 for i in data["issues"] if i.get("severity") == "blocking")
        stats["warning"] = sum(1 for i in data["issues"] if i.get("severity") == "non-blocking")
        stats["suggestion"] = sum(1 for i in data["issues"] if i.get("type") == "suggestion")

        return data
    except json.JSONDecodeError as e:
        return {
            "error": "JSON_PARSE_ERROR",
            "message": f"Failed to parse response: {e}",
            "raw_response": response_text[:500]
        }


def review_code(files: list, focus: Optional[str] = None,
                thinking_level: Optional[str] = None, output_json: bool = False) -> dict:
    """Send code to Gemini for review."""

    if not ensure_genai_installed():
        return {"error": "INSTALL_FAILED", "message": "Could not install google-genai"}

    from google import genai

    api_key = get_api_key()
    if not api_key:
        return {"error": "NO_API_KEY", "message": "GEMINI_API_KEY not found"}

    # Read file contents
    code_parts = []
    valid_files = []
    skip_extensions = {'.json', '.yaml', '.yml', '.toml', '.md', '.txt', '.lock', '.log'}

    for file_path in files:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            continue
        if path.suffix.lower() in skip_extensions:
            continue

        try:
            content = path.read_text(encoding='utf-8')
            if len(content) > 50000:
                code_parts.append(f"### {file_path}\n[File too large - {len(content)} bytes, skipped]")
            else:
                # Add line numbers for reference
                numbered_lines = []
                for i, line in enumerate(content.split('\n'), 1):
                    numbered_lines.append(f"{i:4d} | {line}")
                numbered_content = '\n'.join(numbered_lines)
                code_parts.append(f"### {file_path}\n```{path.suffix[1:] if path.suffix else ''}\n{numbered_content}\n```")
                valid_files.append(file_path)
        except Exception as e:
            code_parts.append(f"### {file_path}\n[Error reading: {e}]")

    if not valid_files:
        return {"error": "NO_FILES", "message": "No valid code files to review"}

    code_content = '\n\n'.join(code_parts)

    # Auto-detect thinking level if not specified
    if not thinking_level:
        thinking_level = calculate_thinking_level(valid_files, code_content)

    prompt = build_review_prompt(code_content, focus)

    # Call Gemini API
    try:
        client = genai.Client(api_key=api_key)

        # Configure thinking based on level
        config = {}
        if thinking_level == "high":
            config["temperature"] = 0.2
        elif thinking_level == "minimal":
            config["temperature"] = 0.5
        else:
            config["temperature"] = 0.3

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config=config if config else None
        )

        result = parse_json_response(response.text)

        if "error" not in result:
            result["meta"] = {
                "files": valid_files,
                "thinking_level": thinking_level,
                "focus": focus
            }

        return result

    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper() or "401" in error_msg:
            return {"error": "INVALID_KEY", "message": "Invalid API key"}
        return {"error": "API_ERROR", "message": error_msg}


def format_interactive_output(result: dict) -> str:
    """Format review result with numbered issues for selection."""
    lines = []
    lines.append("")
    lines.append("═" * 65)
    lines.append("🔍 GEMINI CODE REVIEW")
    lines.append("═" * 65)
    lines.append("")

    if "error" in result:
        error = result["error"]
        if error == "NO_API_KEY":
            lines.append("❌ API Key Required")
            lines.append("")
            lines.append("GEMINI_API_KEY not found. Get one at:")
            lines.append("  → https://aistudio.google.com/apikey")
            lines.append("")
            lines.append("Then run:")
            lines.append('  python scripts/setup_api_key.py --key "YOUR_KEY"')
        elif error == "JSON_PARSE_ERROR":
            lines.append("⚠️ Response Parse Error")
            lines.append("")
            lines.append(result.get("message", "Unknown error"))
            if "raw_response" in result:
                lines.append("")
                lines.append("Raw response preview:")
                lines.append(result["raw_response"][:200] + "...")
        else:
            lines.append(f"❌ Error: {result.get('message', 'Unknown error')}")
    else:
        meta = result.get("meta", {})
        summary = result.get("summary", {})
        issues = result.get("issues", [])
        positive = result.get("positive_aspects", [])

        # Header
        files_str = ", ".join(meta.get("files", []))
        lines.append(f"📁 Reviewed: {files_str}")
        lines.append(f"🧠 Thinking: {meta.get('thinking_level', 'medium')}")

        verdict = summary.get("verdict", "request_changes")
        stats = summary.get("stats", {})

        if verdict == "approve":
            lines.append("✅ Verdict: APPROVED")
        else:
            blocking = stats.get("blocking", 0)
            lines.append(f"🔄 Verdict: REQUEST_CHANGES ({blocking} blocking)")

        lines.append("")
        lines.append(summary.get("overview", ""))
        lines.append("")

        # Group issues by severity
        blocking_issues = [i for i in issues if i.get("severity") == "blocking"]
        warning_issues = [i for i in issues if i.get("severity") == "non-blocking" and i.get("type") != "suggestion"]
        suggestion_issues = [i for i in issues if i.get("type") == "suggestion"]

        # Blocking issues
        if blocking_issues:
            lines.append("┌" + "─" * 63 + "┐")
            lines.append("│ 🚨 BLOCKING (Must Fix)" + " " * 40 + "│")
            lines.append("├" + "─" * 63 + "┤")
            for issue in blocking_issues:
                file_line = f"{issue.get('file', '?')}:{issue.get('line', '?')}"
                title = issue.get('title', 'Issue')[:40]
                effort = issue.get('effort', '?')
                lines.append(f"│ [{issue['id']}] {file_line} - {title}")
                lines.append(f"│     Category: {issue.get('category', '?')} | Effort: {effort}")
                fix = issue.get('suggested_fix', '')[:55]
                if fix:
                    lines.append(f"│     → {fix}")
                lines.append("│")
            lines.append("└" + "─" * 63 + "┘")
            lines.append("")

        # Warning issues
        if warning_issues:
            lines.append("┌" + "─" * 63 + "┐")
            lines.append("│ ⚠️ WARNINGS (Should Fix)" + " " * 38 + "│")
            lines.append("├" + "─" * 63 + "┤")
            for issue in warning_issues:
                file_line = f"{issue.get('file', '?')}:{issue.get('line', '?')}"
                title = issue.get('title', 'Issue')[:40]
                effort = issue.get('effort', '?')
                lines.append(f"│ [{issue['id']}] {file_line} - {title}")
                lines.append(f"│     Effort: {effort}")
                lines.append("│")
            lines.append("└" + "─" * 63 + "┘")
            lines.append("")

        # Suggestions
        if suggestion_issues:
            lines.append("┌" + "─" * 63 + "┐")
            lines.append("│ 💡 SUGGESTIONS (Optional)" + " " * 37 + "│")
            lines.append("├" + "─" * 63 + "┤")
            for issue in suggestion_issues:
                title = issue.get('title', 'Suggestion')[:50]
                lines.append(f"│ [{issue['id']}] {title}")
            lines.append("└" + "─" * 63 + "┘")
            lines.append("")

        # Positive aspects
        if positive:
            lines.append("✅ Positive: " + "; ".join(positive[:3]))
            lines.append("")

        # Selection hint
        if issues:
            lines.append("─" * 65)
            lines.append("Select: numbers (1,2,3) | 'all' | 'blocking' | 'skip'")

    lines.append("═" * 65)
    lines.append("")

    return "\n".join(lines)


def format_legacy_output(result: dict) -> str:
    """Format as plain text (legacy mode)."""
    if "error" in result:
        return format_interactive_output(result)

    lines = []
    lines.append("═" * 65)
    lines.append("🔍 GEMINI CODE REVIEW")
    lines.append("═" * 65)
    lines.append("")

    summary = result.get("summary", {})
    lines.append(f"## Summary\n{summary.get('overview', 'No summary')}")
    lines.append("")

    issues = result.get("issues", [])
    blocking = [i for i in issues if i.get("severity") == "blocking"]
    warnings = [i for i in issues if i.get("severity") == "non-blocking"]

    if blocking:
        lines.append("## Critical Issues")
        for i in blocking:
            lines.append(f"- **{i.get('file')}:{i.get('line')}** - {i.get('title')}")
            lines.append(f"  {i.get('description', '')}")
        lines.append("")

    if warnings:
        lines.append("## Warnings")
        for i in warnings:
            lines.append(f"- {i.get('title')}: {i.get('description', '')}")
        lines.append("")

    positive = result.get("positive_aspects", [])
    if positive:
        lines.append("## Positive Aspects")
        for p in positive:
            lines.append(f"- {p}")

    lines.append("═" * 65)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Review code using Gemini 3.0 Flash",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gemini_review.py --files "src/main.py"
  python gemini_review.py --files "app.ts,utils.ts" --json
  python gemini_review.py --files "auth.py" --json --focus security --think high
        """
    )
    parser.add_argument("--files", required=True, help="Comma-separated file paths")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    parser.add_argument("--focus", choices=["security", "performance", "quality"])
    parser.add_argument("--think", choices=["minimal", "medium", "high"],
                        help="Thinking depth (auto-detected if not specified)")

    args = parser.parse_args()
    files = [f.strip() for f in args.files.split(",") if f.strip()]

    if not files:
        print("❌ No files specified")
        sys.exit(1)

    result = review_code(files, args.focus, args.think, args.json)

    # Output
    if args.json:
        if "error" not in result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_interactive_output(result))
    else:
        print(format_interactive_output(result))

    # Exit codes
    if result.get("error") == "NO_API_KEY":
        sys.exit(2)
    elif result.get("error") == "NO_FILES":
        sys.exit(0)
    elif "error" in result:
        sys.exit(1)
    elif result.get("summary", {}).get("stats", {}).get("blocking", 0) > 0:
        sys.exit(3)  # Has blocking issues
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
