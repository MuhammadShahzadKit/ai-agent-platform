from __future__ import annotations

import json
from typing import Any

import ollama
from openai import OpenAI

from app.core.config import settings


MODEL = "qwen2.5:3b"


def _extract_previous_results(
    arguments: dict[str, Any] | None,
) -> str:

    if not arguments:
        return ""

    previous_results = arguments.get(
        "previous_results",
        [],
    )

    if not previous_results:
        return ""

    parts: list[str] = []

    for item in previous_results:

        parts.append(
            f"""
STEP {item.get("step")}
TOOL: {item.get("tool")}
DESCRIPTION: {item.get("description", "")}

RESULT:
{item.get("result")}
"""
        )

    return "".join(parts)


def reason_about_task(
    objective: str,
    arguments: dict[str, Any] | None = None,
    config: Any = None,
) -> str:

    return (
        f"Objective analyzed: {objective}"
    )


def execute_action(
    objective: str,
    arguments: dict[str, Any] | None = None,
    config: Any = None,
) -> str:

    from app.services.agent_runtime.executor.executor import (
        AutonomousExecutor,
    )

    import json

    executor = AutonomousExecutor(
        config=config
    )

    execution = executor.execute(
        objective=objective,
        arguments=arguments,
    )

    return json.dumps(
        {
            "success": execution.success,
            "action": execution.action,
            "status": execution.status,
            "result": execution.result,
            "error": execution.error,
        },
        ensure_ascii=False,
        indent=2,
    )


def research_task(
    objective: str,
    arguments: dict[str, Any] | None = None,
    config: Any = None,
) -> str:

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY
    )

    prompt = f'''
You are the research component of an autonomous AI agent.

Research the following objective using current web information:

OBJECTIVE:
{objective}

RESEARCH REQUIREMENTS:
- Find current and relevant information.
- Prioritize recent and authoritative sources.
- Focus only on information useful for completing the objective.
- Distinguish established facts from opinions or predictions.
- Do not invent facts.
- Do not fabricate statistics, studies, quotations, people,
  product releases, dates, or events.
- If information is uncertain or conflicting, say so.
- Provide enough factual context for another AI agent to create
  accurate publish-ready content.

Return a concise research report containing:
1. Key findings
2. Important facts
3. Recent developments
4. Relevant dates
5. Important organizations, products, or people
6. Source references or URLs when available
7. Uncertainties or limitations
'''

    response = client.responses.create(
        model="gpt-5.6",
        input=prompt,
        tools=[
            {
                "type": "web_search"
            }
        ],
    )

    return response.output_text


def write_content(
    objective: str,
    arguments: dict[str, Any] | None = None,
    config: Any = None,
) -> str:

    arguments = arguments or {}

    previous_context = _extract_previous_results(
        arguments
    )

    prompt = f"""
You are the content-generation and YouTube SEO component
of an autonomous AI agent.

Your responsibility is to create an ORIGINAL, COMPLETE,
USEFUL and PUBLISH-READY content package for the current
YouTube video mission.

USER OBJECTIVE:
{objective}

PREVIOUS AGENT WORK:
{previous_context}

==================================================
CORE REQUIREMENTS
==================================================

Use the previous agent work as input.

If research results are available:

- use the research as the factual foundation
- extract relevant facts and useful information
- do not ignore available research
- do not claim research was unavailable
- do not invent specific facts that are unsupported
- distinguish factual information from opinion or general advice
- keep the final content relevant to the requested topic

The generated package must be specific to THIS video.

Do NOT reuse generic titles, descriptions, tags or hashtags
when they do not match the current topic.

==================================================
YOUTUBE CONTENT PACKAGE
==================================================

Generate all of the following:

1. title
2. description
3. script
4. tags
5. hashtags
6. seo_keywords
7. thumbnail_prompt
8. content_type
9. target_audience
10. hook
11. call_to_action
12. policy_notes

==================================================
TITLE REQUIREMENTS
==================================================

Create a compelling but accurate YouTube title.

The title should:

- clearly represent the actual video
- contain the main topic naturally
- be understandable to the target audience
- encourage clicks without deception
- avoid fake claims
- avoid excessive capitalization
- avoid excessive punctuation
- avoid misleading promises
- avoid keyword stuffing

==================================================
DESCRIPTION REQUIREMENTS
==================================================

Create a useful YouTube description based on the actual video.

Include naturally:

- what the viewer will learn or see
- important context from the research
- relevant search terms
- a concise call to action
- relevant hashtags at the end when appropriate

Do not stuff keywords.

Do not claim that the video contains something
that is not actually in the script.

==================================================
SCRIPT REQUIREMENTS
==================================================

Write a complete, usable script.

The script must:

- have a strong opening hook
- stay focused on the requested topic
- use the available research
- be understandable for the target audience
- have logical sections
- provide useful information
- end naturally
- include a suitable call to action

Do not fabricate statistics, quotations, studies,
events, people, or other specific facts.

==================================================
TAGS REQUIREMENTS
==================================================

Generate relevant YouTube tags based specifically on
the video's topic.

Use a mixture of:

- primary topic terms
- closely related terms
- natural search phrases
- relevant long-tail phrases

Do not include unrelated trending keywords.

Do not use tags simply because they are popular.

Do not use misleading tags.

Return tags as a JSON array of strings.

==================================================
HASHTAG REQUIREMENTS
==================================================

Generate a small set of highly relevant hashtags.

Hashtags must:

- directly relate to the video
- be relevant to the channel topic
- avoid spam
- avoid unrelated trending hashtags

Return hashtags as a JSON array of strings.

Each hashtag should begin with "#".

==================================================
SEO KEYWORDS
==================================================

Generate relevant search phrases that naturally describe
the video.

These are planning keywords, not keyword stuffing.

Return them as a JSON array of strings.

==================================================
THUMBNAIL PROMPT
==================================================

Create a detailed prompt for generating a YouTube thumbnail.

The thumbnail should:

- visually represent the actual video topic
- have one clear focal subject
- be understandable at small size
- use strong visual hierarchy
- avoid misleading imagery
- avoid unnecessary text
- use short readable text only when useful

==================================================
CONTENT STRATEGY
==================================================

Identify:

- content_type
- target_audience
- hook
- call_to_action

The strategy should be appropriate for the actual
video topic and should help improve viewer relevance,
clarity and retention without using deceptive tactics.

==================================================
POLICY / QUALITY
==================================================

Create policy_notes that identify important quality and
platform-safety considerations for this specific content.

Do not attempt to bypass YouTube policies.

Do not recommend:

- spam
- deceptive metadata
- misleading titles
- fake engagement
- artificial views
- fake comments
- impersonation
- copyright infringement
- unsafe instructions
- fabricated facts

The objective is sustainable, policy-aware channel growth.

==================================================
OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

Do not use Markdown code fences.

Use exactly this structure:

{{
    "success": true,
    "type": "content_package",
    "package": {{
        "title": "...",
        "description": "...",
        "script": "...",
        "tags": [],
        "hashtags": [],
        "seo_keywords": [],
        "thumbnail_prompt": "...",
        "content_type": "...",
        "target_audience": "...",
        "hook": "...",
        "call_to_action": "...",
        "policy_notes": []
    }}
}}

All fields must be present.

The script must be complete and usable.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    content = response["message"]["content"].strip()

    # Some local models occasionally return JSON inside
    # Markdown code fences even when explicitly instructed
    # not to. Remove those fences before parsing.
    if content.startswith("```"):
        lines = content.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines).strip()

    try:

        parsed = json.loads(content)

        if not isinstance(parsed, dict):
            raise ValueError(
                "Content writer returned JSON that is not an object."
            )

        package = parsed.get("package")

        if isinstance(package, dict):

            # Ensure the structured package always exposes
            # the fields expected by downstream tools.
            package.setdefault("title", "")
            package.setdefault("description", "")
            package.setdefault("script", "")
            package.setdefault("tags", [])
            package.setdefault("hashtags", [])
            package.setdefault("seo_keywords", [])
            package.setdefault("thumbnail_prompt", "")
            package.setdefault("content_type", "")
            package.setdefault("target_audience", "")
            package.setdefault("hook", "")
            package.setdefault("call_to_action", "")
            package.setdefault("policy_notes", [])

            parsed["success"] = True
            parsed["type"] = "content_package"

        return json.dumps(
            parsed,
            ensure_ascii=False,
            indent=2,
        )

    except Exception as exc:

        return json.dumps(
            {
                "success": False,
                "type": "content_package",
                "status": "content_json_parse_failed",
                "error": str(exc),
                "raw_response": content,
            },
            ensure_ascii=False,
            indent=2,
        )

def browser_task(
    objective: str,
    arguments: dict[str, Any] | None = None,
    config: Any = None,
) -> str:

    from app.services.agent_runtime.browser.browser import (
        BrowserAutomation,
    )

    arguments = arguments or {}

    browser = BrowserAutomation(
        headless=False
    )

    objective_text = objective.lower()

    # ---------------------------------------------
    # Login / Studio status
    # ---------------------------------------------

    if (
        "check whether" in objective_text
        or "logged in" in objective_text
        or "login status" in objective_text
    ):
        result = browser.is_logged_in()

        return json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )

    # ---------------------------------------------
    # Open YouTube Studio
    # ---------------------------------------------

    if (
        "open youtube studio" in objective_text
        and "upload" not in objective_text
        and "publish" not in objective_text
    ):
        result = browser.open_youtube_studio()

        return json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )

    # ---------------------------------------------
    # Upload / publish
    # ---------------------------------------------

    video_path = arguments.get("video_path")
    title = arguments.get("title")
    description = arguments.get("description")
    tags = arguments.get("tags")
    thumbnail_path = arguments.get("thumbnail_path")

    previous_results = arguments.get(
        "previous_results",
        [],
    )

    # Try to recover generated content from
    # previous content_writer results.
    if not title or not description:

        for previous in reversed(previous_results):

            result = previous.get("result")

            if not isinstance(result, str):
                continue

            try:
                parsed = json.loads(result)
            except Exception:
                continue

            package = parsed.get("package", {})

            if package:

                title = title or package.get("title")
                description = (
                    description
                    or package.get("description")
                )

                tags = tags or package.get("tags")

                thumbnail_path = (
                    thumbnail_path
                    or package.get("thumbnail_path")
                )

                video_path = (
                    video_path
                    or package.get("video_path")
                )

    if video_path:

        result = browser.upload_video(
            video_path=video_path,
            title=title or "Untitled Video",
            description=description or "",
            tags=tags,
            thumbnail_path=thumbnail_path,
            publish=(
                "publish" in objective_text
                or "published" in objective_text
            ),
        )

        return json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )

    return json.dumps(
        {
            "success": False,
            "type": "browser_task",
            "status": "missing_video",
            "message": (
                "Browser is authenticated, but no generated "
                "video_path was supplied to the browser executor."
            ),
            "objective": objective,
        },
        ensure_ascii=False,
        indent=2,
    )

