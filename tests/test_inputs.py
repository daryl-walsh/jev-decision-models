from pathlib import Path

import pytest

from micrt_monitor.crtmonitor import load_overrides, load_people, search_groups


def csv_file(tmp_path, contents):
    path = tmp_path / "people.csv"
    path.write_text(contents)
    return path


def test_court_expansion_and_normalized_search_groups(tmp_path):
    path = csv_file(
        tmp_path,
        "court,last,first,middle,birth_year,label\nC54;D71B, Example ,Alex,,,Alex\nC54,example,Blair,,,Blair\n",
    )
    people = load_people(path)
    assert len(people) == 3
    assert search_groups(people) == [("C54", "EXAMPLE"), ("D71B", "EXAMPLE")]


@pytest.mark.parametrize(
    "contents",
    [
        "last,first\nExample,Alex\n",
        "court,last,first\nC54,Example,\n",
        "court,last,first\nOTHER,Example,Alex\n",
        "court,last,first\n,Example,Alex\n",
        "court,last,first,birth_year\nC54,Example,Alex,unknown\n",
        "court,last,first\n",
    ],
)
def test_invalid_people_fail_before_search(tmp_path, contents):
    with pytest.raises(ValueError):
        load_people(csv_file(tmp_path, contents))


def test_bom_and_comments_are_supported(tmp_path):
    path = csv_file(tmp_path, "\ufeffcourt,last,first\n# comment,,\nC54,Example,Alex\n")
    assert len(load_people(path)) == 1


def test_optional_overrides_and_validation(tmp_path):
    path = tmp_path / "overrides.csv"
    assert load_overrides(path) == {}
    path.write_text("case_id,label,decision,note\nSYNTHETIC-1,,confirm,reviewed\n")
    assert load_overrides(path)[("SYNTHETIC-1", "")] == ("confirm", "reviewed")
    path.write_text("case_id,decision\nSYNTHETIC-1,maybe\n")
    with pytest.raises(ValueError, match="confirm or exclude"):
        load_overrides(path)


def test_committed_examples_are_valid():
    assert len(load_people(Path("examples/people.csv"))) == 2
    assert load_overrides(Path("examples/overrides.csv")) == {}
