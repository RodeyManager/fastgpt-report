import pytest

from fastgpt_demo.cleaners.registry import get, clear, register
from fastgpt_demo.cleaners.rules.sensitive import MaskSensitiveRule


@pytest.fixture(autouse=True)
def _setup():
    clear()
    register(MaskSensitiveRule())
    yield
    clear()


class TestMaskSensitiveInsuranceMode:
    def test_masks_idcard_with_partial_preservation(self):
        rule = get("mask_sensitive")
        text = "身份证号：310115199001011234"
        result = rule.apply(text, insurance_mode=True)
        assert "310" in result
        assert "1234" in result
        assert "*" in result
        assert "310115199001011234" not in result

    def test_masks_bankcard_with_partial_preservation(self):
        rule = get("mask_sensitive")
        text = "银行卡号：6222021234567890"
        result = rule.apply(text, insurance_mode=True)
        assert "6222" in result
        assert "7890" in result
        assert "6222021234567890" not in result

    def test_masks_phone_with_partial_preservation(self):
        rule = get("mask_sensitive")
        text = "联系电话：13812345678"
        result = rule.apply(text, insurance_mode=True)
        assert "138" in result
        assert "5678" in result
        assert "13812345678" not in result

    def test_masks_email_with_partial_preservation(self):
        rule = get("mask_sensitive")
        text = "邮箱：zhangsan@example.com"
        result = rule.apply(text, insurance_mode=True)
        assert "z" in result
        assert "@example.com" in result
        assert "zhangsan@example.com" not in result

    def test_masks_policy_number(self):
        rule = get("mask_sensitive")
        text = "保单号：P202406010001"
        result = rule.apply(text, insurance_mode=True)
        assert "P" in result
        assert "001" in result
        assert "P202406010001" not in result

    def test_masks_insured_name(self):
        rule = get("mask_sensitive")
        text = "被保险人：张三"
        result = rule.apply(text, insurance_mode=True)
        assert "张*" in result
        assert "张三" not in result

    def test_generic_mode_still_works(self):
        rule = get("mask_sensitive")
        text = "身份证号：310115199001011234"
        result = rule.apply(text, insurance_mode=False)
        assert "***IDCARD***" in result
        assert "310115199001011234" not in result
