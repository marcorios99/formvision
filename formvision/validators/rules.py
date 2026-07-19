import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str


class ValidationRules:
    def validate(self, value: Any, rules: tuple[str, ...]) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        text = "" if value is None else str(value)
        for rule in rules:
            if rule == "required" and not text.strip():
                issues.append(ValidationIssue("required", "Field is required."))
            elif rule.startswith("digits:"):
                expected = int(rule.split(":", 1)[1])
                if not re.fullmatch(rf"\d{{{expected}}}", text):
                    issues.append(
                        ValidationIssue(
                            "digits",
                            f"Expected exactly {expected} numeric characters.",
                        )
                    )
            elif rule == "single_choice" and not text:
                issues.append(ValidationIssue("single_choice", "Expected one selected option."))
        return issues
