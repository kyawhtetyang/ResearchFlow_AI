from __future__ import annotations


class ResearchFlowError(Exception):
    def __init__(self, code: str, user_message: str, detail: str | None = None) -> None:
        super().__init__(detail or user_message)
        self.code = code
        self.user_message = user_message
        self.detail = detail or user_message


class ConfigurationError(ResearchFlowError):
    def __init__(self, user_message: str, detail: str | None = None) -> None:
        super().__init__("configuration_error", user_message, detail)


class SearchProviderError(ResearchFlowError):
    def __init__(self, user_message: str, detail: str | None = None) -> None:
        super().__init__("search_error", user_message, detail)


class GenerationError(ResearchFlowError):
    def __init__(self, user_message: str, detail: str | None = None) -> None:
        super().__init__("generation_error", user_message, detail)


class NoSourcesFoundError(ResearchFlowError):
    def __init__(self, user_message: str = "No sources were found for this research question.") -> None:
        super().__init__("no_sources_found", user_message, user_message)
