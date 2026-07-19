from formvision.validators.rules import ValidationRules


def test_required_rule_rejects_blank_value():
    issues = ValidationRules().validate("", ("required",))

    assert issues
    assert issues[0].code == "required"


def test_digits_rule_accepts_expected_length():
    issues = ValidationRules().validate("12345678", ("digits:8",))

    assert issues == []
