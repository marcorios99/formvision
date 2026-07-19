from formvision.config.schema import FieldConfig
from formvision.validators.rules import ValidationIssue, ValidationRules


class FieldValidator:
    def __init__(self, rules: ValidationRules | None = None) -> None:
        self.rules = rules or ValidationRules()

    def validate(self, field: FieldConfig, value) -> list[ValidationIssue]:
        return self.rules.validate(value, field.validators)
