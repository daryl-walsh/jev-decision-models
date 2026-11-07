import argparse
import json
import shutil
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest
from playwright.sync_api import TimeoutError as PWTimeout

from micrt_monitor import crtmonitor as m
from scripts.migrate_state import migrate, restore
from tests.test_matching import case


def response(results=None, total=None, status=200, page=1):
    results = [case()] if results is None else results
    payload = {"results": results, "xTotalCount": len(results) if total is None else total}
    return SimpleNamespace(
        url=m.BASE + m.SEARCH_API,
        request=SimpleNamespace(
            method="POST",
            post_data_json={
                "courtId": "C54",
                "lastName": "Example",
                "pageSize": 1,
                "pageStartRecord": page - 1,
            },
        ),
        status=status,
        json=lambda: payload,
    )


class FakePage:
    def __init__(self, responses):
        self.responses = iter(responses)

    @contextmanager
    def expect_response(self, predicate, timeout):
        for item in self.responses:
            if isinstance(item, Exception):
                raise item
            if predicate(item):
                yield SimpleNamespace(value=item)
                return
        raise PWTimeout("no matching response")

    def goto(self, url, wait_until):
        pass

    def wait_for_timeout(self, timeout):
        pass


def collect(tmp_path, responses):
    return m.collect_search(
        FakePage(responses),
        "C54",
        "EXAMPLE",
        argparse.Namespace(captcha_timeout=1, delay=(0, 0)),
        tmp_path,
    )


def test_response_correlates_court_surname_page_and_origin():
    candidate = response()
    assert m.response_matches(candidate, "C54", "example", 1)
    for court, name, page in [("D71B", "Example", 1), ("C54", "Other", 1), ("C54", "Example", 2)]:
        assert not m.response_matches(candidate, court, name, page)
    candidate.url = "https://unrelated.test" + m.SEARCH_API
    assert not m.response_matches(candidate, "C54", "Example", 1)


def test_successful_browser_request_shape_matches_expected_pagination():
    body = json.loads(Path("tests/fixtures/requests/search.json").read_text())
    candidate = response()
    candidate.request.post_data_json = body
    assert m.response_matches(candidate, "C54", "EXAMPLE", 1)
    assert not m.response_matches(candidate, "C54", "EXAMPLE", 2)
    body["pageStartRecord"] = 50
    assert m.response_matches(candidate, "C54", "EXAMPLE", 2)
    assert not m.response_matches(candidate, "C54", "EXAMPLE", 1)


def test_pagination_collects_unique_cases(tmp_path):
    pages, errors = collect(
        tmp_path, [response(total=2), response([case("SYNTHETIC-2")], total=2, page=2)]
    )
    assert len(pages) == 2
    assert errors == []
    assert len(m.load_offline(tmp_path)) == 2


def test_repeated_page_is_incomplete(tmp_path):
    pages, errors = collect(tmp_path, [response(total=2), response(total=2, page=2)])
    assert len(pages) == 2
    assert any("repeated page" in error for error in errors)
    assert any("incomplete" in error for error in errors)


def test_changing_totals_are_not_a_complete_snapshot(tmp_path):
    _, errors = collect(
        tmp_path, [response(total=2), response([case("SYNTHETIC-2")], total=3, page=2)]
    )
    assert any("count changed" in error for error in errors)


@pytest.mark.parametrize(
    "item", [response(status=503), PWTimeout("synthetic timeout"), response([{"caseId": None}])]
)
def test_failed_search_has_no_successful_pages(tmp_path, item):
    pages, errors = collect(tmp_path, [item])
    assert pages == []
    assert errors


def test_empty_search_is_valid(tmp_path):
    pages, errors = collect(tmp_path, [response([], total=0)])
    assert len(pages) == 1 and not errors


def test_initial_captcha_rejection_waits_for_success(tmp_path):
    pages, errors = collect(tmp_path, [response(status=400), response(status=403), response()])
    assert len(pages) == 1 and not errors


def test_unsolved_captcha_keeps_http_status_in_timeout(tmp_path):
    pages, errors = collect(tmp_path, [response(status=400)])
    assert not pages
    assert "last HTTP 400" in errors[0]


def test_page_limit_reports_incomplete(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "MAX_PAGES", 1)
    _, errors = collect(tmp_path, [response(total=2)])
    assert any("incomplete" in error for error in errors)


@pytest.fixture
def offline(tmp_path):
    run = tmp_path / "saved"
    shutil.copytree("tests/fixtures/responses", run)
    people = tmp_path / "people.csv"
    shutil.copyfile("examples/people.csv", people)
    state = tmp_path / "state.json"
    args = [
        "--people",
        str(people),
        "--overrides",
        str(tmp_path / "absent.csv"),
        "--offline",
        str(run),
        "--state",
        str(state),
    ]
    return run, people, state, args


def test_offline_tuning_and_explicit_state_update(offline):
    run, _, state, args = offline
    assert m.main(args) == 0
    assert "10 new" in (run / "report.md").read_text()
    assert not state.exists()
    assert m.main([*args, "--update-state"]) == 0
    before = state.read_bytes()
    assert m.main(args) == 0
    assert "0 new" in (run / "report.md").read_text()
    assert state.read_bytes() == before


def test_incomplete_saved_run_cannot_update_state(offline):
    run, _, state, args = offline
    state.write_text("{}\n")
    (run / m.RUN_STATUS).write_text('{"complete":false}')
    assert m.main([*args, "--update-state"]) == 1
    assert state.read_text() == "{}\n"
    assert "INCOMPLETE RUN" in (run / "report.md").read_text()


def test_missing_search_is_incomplete(offline):
    run, _, state, args = offline
    (run / "D71B_example_p1.json").unlink()
    assert m.main([*args, "--update-state"]) == 1
    assert not state.exists()


def test_partial_live_run_preserves_state(offline, monkeypatch, tmp_path):
    _, people, state, _ = offline
    state.write_text("{}\n")
    monkeypatch.setattr(m, "fetch_live", lambda *args: ([], ["synthetic timeout"]))
    out = tmp_path / "runs"
    assert m.main(["--people", str(people), "--state", str(state), "--out-dir", str(out)]) == 1
    assert state.read_text() == "{}\n"
    run = next(out.iterdir())
    assert json.loads((run / m.RUN_STATUS).read_text())["complete"] is False
    assert "INCOMPLETE RUN" in (run / "report.md").read_text()


def test_interrupted_browser_cleanup_preserves_state_and_incomplete_marker(
    offline, monkeypatch, tmp_path, capsys
):
    _, people, state, _ = offline
    state.write_text("{}\n")

    def interrupted(*args):
        raise KeyboardInterrupt

    def close_failed():
        raise RuntimeError("driver stopped during interrupt")

    context = SimpleNamespace(pages=[object()], close=close_failed)
    browser = SimpleNamespace(launch_persistent_context=lambda *args, **kwargs: context)

    @contextmanager
    def playwright():
        yield SimpleNamespace(chromium=browser)

    monkeypatch.setattr("playwright.sync_api.sync_playwright", playwright)
    monkeypatch.setattr(m, "collect_search", interrupted)
    out = tmp_path / "interrupted"
    assert (
        m.main(
            [
                "--people",
                str(people),
                "--state",
                str(state),
                "--out-dir",
                str(out),
                "--profile",
                str(tmp_path / "profile"),
            ]
        )
        == 130
    )
    assert state.read_text() == "{}\n"
    run = next(out.iterdir())
    assert json.loads((run / m.RUN_STATUS).read_text())["complete"] is False
    assert "Interrupted; previous state preserved" in capsys.readouterr().err


def test_court_qualified_identity_prevents_cross_court_dedup(offline):
    run, _, state, args = offline
    for path in run.glob("*.json"):
        data = json.loads(path.read_text())
        data["response"] = {"results": [case("SHARED-CASE-ID")], "xTotalCount": 1}
        path.write_text(json.dumps(data))
    assert m.main([*args, "--update-state"]) == 0
    entries = m.load_state(state)
    assert len(entries) == 2
    assert {e["court"] for e in entries.values()} == {"C54", "D71B"}


def test_state_migration_preserves_entries_and_backup(tmp_path):
    path = tmp_path / "state.json"
    entry = {
        "court": "C54",
        "label": "Synthetic",
        "caseId": "SYNTHETIC-1",
        "first_seen": "2020-01-01",
    }
    original = json.dumps({"Synthetic|SYNTHETIC-1": entry}).encode()
    path.write_bytes(original)
    with pytest.raises(ValueError, match="Legacy state"):
        m.load_state(path)
    assert migrate(path)
    assert path.with_name("state.json.v1.bak").read_bytes() == original
    assert m.load_state(path) == {m.state_key(entry): entry}
    assert not migrate(path)
    migrated = path.read_bytes()
    assert restore(path)
    assert path.read_bytes() == original
    assert path.with_name("state.json.v2.bak").read_bytes() == migrated
    assert not restore(path)


def test_migration_conflicting_backup_blocks_replacement(tmp_path):
    path = tmp_path / "state.json"
    entry = {"court": "C54", "label": "Synthetic", "caseId": "SYNTHETIC-1"}
    path.write_text(json.dumps({"Synthetic|SYNTHETIC-1": entry}))
    original = path.read_bytes()
    path.with_name("state.json.v1.bak").write_text("existing backup")
    with pytest.raises(ValueError, match="backup already exists"):
        migrate(path)
    assert path.read_bytes() == original


def test_atomic_state_write_failure_preserves_previous_file(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    path.write_text("original")

    def fail(*args):
        raise OSError("simulated replacement failure")

    monkeypatch.setattr(m.os, "replace", fail)
    with pytest.raises(OSError):
        m.atomic_json(path, {"new": "state"})
    assert path.read_text() == "original"
    assert list(tmp_path.iterdir()) == [path]


def test_raw_har_is_rejected(tmp_path):
    (tmp_path / "capture.json").write_text('{"log":{"entries":[]}}')
    with pytest.raises(ValueError, match="envelope"):
        m.load_offline(tmp_path)
