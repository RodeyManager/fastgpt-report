import pytest

from fastgpt_demo.cleaners.registry import clear, register
from fastgpt_demo.cleaners.pipeline import CleanPipeline
from fastgpt_demo.cleaners.rules.sensitive import MaskSensitiveRule
from fastgpt_demo.cleaners.rules.whitespace import TrimRule


@pytest.fixture(autouse=True)
def _setup_registry():
    clear()
    register(TrimRule())
    register(MaskSensitiveRule())
    yield
    clear()


class TestMaskSensitiveEnhanced:
    def test_bankcard_16_digits(self):
        text = "\u94f6\u884c\u5361 6222021234567890"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"mask_sensitive": True, "trim": False})
        assert "***BANKCARD***" in result

    def test_bankcard_19_digits(self):
        text = "\u5361\u53f7 6222021234567890123"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"mask_sensitive": True, "trim": False})
        assert "***BANKCARD***" in result

    def test_bankcard_visa(self):
        text = "\u5361\u53f7 4123456789012345"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"mask_sensitive": True, "trim": False})
        assert "***BANKCARD***" in result

    def test_bankcard_mastercard(self):
        text = "\u5361\u53f7 5123456789012345"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"mask_sensitive": True, "trim": False})
        assert "***BANKCARD***" in result

    def test_passport(self):
        text = "\u62a4\u7167\u53f7 E12345678"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"mask_sensitive": True, "trim": False})
        assert "***PASSPORT***" in result

    def test_passport_k_prefix(self):
        text = "\u62a4\u7167 K12345678"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"mask_sensitive": True, "trim": False})
        assert "***PASSPORT***" in result

    def test_military_id(self):
        text = "\u519b\u5b57\u7b2c123456\u53f7"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"mask_sensitive": True, "trim": False})
        assert "***MILITARY***" in result

    def test_military_id_8_digits(self):
        text = "\u519b\u5b57\u7b2c12345678\u53f7"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"mask_sensitive": True, "trim": False})
        assert "***MILITARY***" in result

    def test_existing_idcard_still_works(self):
        text = "\u8eab\u4efd\u8bc1 110101199001011234"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"mask_sensitive": True, "trim": False})
        assert "***IDCARD***" in result

    def test_existing_phone_still_works(self):
        text = "\u624b\u673a 13812345678"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"mask_sensitive": True, "trim": False})
        assert "***PHONE***" in result

    def test_existing_email_still_works(self):
        text = "\u90ae\u7bb1 test@example.com"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"mask_sensitive": True, "trim": False})
        assert "***EMAIL***" in result

    def test_existing_ip_still_works(self):
        text = "\u670d\u52a1\u5668 192.168.1.100"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"mask_sensitive": True, "trim": False})
        assert "***IP***" in result

    def test_disabled_by_default(self):
        text = "E12345678 6222021234567890"
        pipeline = CleanPipeline()
        result = pipeline.execute(text, {"mask_sensitive": False, "trim": False})
        assert "E12345678" in result
        assert "6222021234567890" in result
