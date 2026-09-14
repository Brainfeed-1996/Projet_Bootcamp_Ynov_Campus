from schemas.analysis import AnalysisResult

from .base import LLMProvider, validate_log_message


class FakeLLMProvider(LLMProvider):
    def analyze(self, log_message: str) -> AnalysisResult:
        validate_log_message(log_message)
        return AnalysisResult(
            severity="LOW",
            category="TEST",
            summary="Fake analysis for testing purposes",
            recommendations=["Verify the log context", "Check related events"],
            provider="fake",
        )