from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from skill_scan.models import Finding, Severity
from skill_scan.rules.base import Rule


class PromptInjectionRule(Rule):
    name = "prompt-injection"
    description = "Detects system prompt override and instruction injection patterns"
    severity = Severity.HIGH

    _patterns: list[tuple[str, str, str, str]] = [
        (r'(?i)ignore\s+(all\s+)?previous\s+(instructions|commands|directives)',
         "ignore-prev", "Instruction override: 'Ignore previous instructions' detected",
         "Ignore-previous patterns are used to bypass system prompt restrictions and inject new commands."),
        (r'(?i)disregard\s+(all\s+)?(previous|above|prior)',
         "disregard", "Instruction override: 'Disregard' detected",
         "Disregard instructions tell the model to ignore its configured system prompt."),
        (r'(?i)(you\s+are\s+now|act\s+as\s+if|pretend\s+you\s+are)\s+(?!.*(?:helpful|assistant|bot|ai))',
         "role-play", "Role-play override detected: instructing model to adopt new persona",
         "Role-play overrides can be used to bypass safety guardrails by assuming privileged personas."),
        (r'(?i)(system\s*:|system\s+prompt\s*:)\s+.*',
         "system-msg", "System message injection in user content detected",
         "Embedding system-level instructions in user content can override the original system prompt."),
        (r'(?i)<system>.*?</system>',
         "system-tag", "System tag injection detected in user content",
         "System tags appearing in user-provided content may attempt to override the system prompt."),
        (r'```(?:yaml|yml|json|text|plain)\s*\n.*?(?:instructions|prompt|role|system).*?\n```',
         "instruction-block", "Instruction override detected inside code block",
         "Attackers embed override instructions in code blocks to hide them from surface-level inspection."),
        (r'(?i)forget\s+(your\s+)?(training|guidelines|rules|instructions)',
         "forget-training", "Training override: 'Forget your training' detected",
         "Asking the model to forget its training is a direct attempt to disable safety alignment."),
        (r'(?i)ignore\s+(your\s+)?(guidelines|rules|boundaries|constraints)',
         "ignore-rules", "Guideline override: 'Ignore your guidelines' detected",
         "Directing the model to ignore its guidelines circumvents content safety policies."),
    ]

    _skip_extensions = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff2", ".woff", ".eot", ".ttf", ".pyc", ".exe", ".dll", ".zip"}

    def match(self, file_path: Path, content: str) -> list[Finding]:
        ext = file_path.suffix.lower()
        if ext in self._skip_extensions:
            return []

        if not content:
            return []

        findings: list[Finding] = []
        for pattern, rule_id, message, explanation in self._patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count("\n") + 1
                start = max(0, match.start() - 20)
                end = min(len(content), match.end() + 30)
                snippet = content[start:end].strip()
                findings.append(Finding(
                    rule_id=f"prompt-injection/{rule_id}",
                    severity=self.severity,
                    message=message,
                    file_path=file_path,
                    line_number=line_num,
                    snippet=snippet,
                    recommendation=(
                        f"This looks like a prompt injection attempt. {explanation} "
                        "Ensure user-provided content is separated from system instructions."
                    ),
                ))
        return findings
