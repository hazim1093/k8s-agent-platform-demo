import os

import pytest
from deepeval.models import LocalModel


@pytest.fixture(scope="session")
def judge():
    return LocalModel(
        model=os.environ.get("LLM_MODEL", "default"),
        base_url=os.environ.get("JUDGE_BASE_URL", "http://localhost:8081/llm/v1"),
        api_key=os.environ.get("JUDGE_API_KEY", "unused"),
    )
