"""Grade polling behavior."""

from types import SimpleNamespace

import pytest

from gradescope_autosubmitter.core import GradescopeSubmitter


class _FakeGradeElement:
    def __init__(self, text: str):
        self._text = text

    async def inner_text(self) -> str:
        return self._text


class _FakePage:
    def __init__(self):
        self.reload_calls = 0
        self.query_calls = 0

    async def reload(self):
        self.reload_calls += 1

    async def query_selector(self, _selector: str):
        self.query_calls += 1
        if self.query_calls < 2:
            return _FakeGradeElement("-/100")
        return _FakeGradeElement("92/100")


@pytest.mark.asyncio
async def test_wait_for_grade_does_not_reload_page(monkeypatch):
    submitter = GradescopeSubmitter()
    page = _FakePage()

    class _Spinner:
        def add_task(self, *_args, **_kwargs):
            return "task"

    class _ProgressContext:
        def __enter__(self):
            return _Spinner()

        def __exit__(self, *_args):
            return False

    async def _fast_sleep(_seconds):
        return None

    monkeypatch.setattr(
        "gradescope_autosubmitter.core.create_spinner_progress",
        lambda: _ProgressContext(),
    )
    monkeypatch.setattr("gradescope_autosubmitter.core.asyncio.sleep", _fast_sleep)

    grade = await submitter._wait_for_grade(page)

    assert grade == "92/100"
    assert page.reload_calls == 0
