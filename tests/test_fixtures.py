import base64
import json
from pathlib import Path

import pytest

from scripts.prepare_fixtures import extract, synthetic_response
from tests.test_matching import case


@pytest.mark.parametrize("wrapped,encoded", [(False, False), (True, False), (True, True)])
def test_har_formats_extract_only_response(wrapped, encoded):
    payload = {"results": [case(name="PRIVATE, PERSON")], "xTotalCount": 1}
    text = json.dumps(payload)
    content = {"text": base64.b64encode(text.encode()).decode() if encoded else text}
    if encoded:
        content["encoding"] = "base64"
    entry = {
        "request": {
            "url": "https://micourt.courts.michigan.gov/api/casesearch/v1/cases/search",
            "headers": [{"name": "private-header", "value": "do-not-copy"}],
        },
        "response": {"content": content},
    }
    document = {"log": {"entries": [entry]}} if wrapped else entry
    sanitized = synthetic_response(extract(document), "C54")
    rendered = json.dumps(sanitized)
    assert "PRIVATE" not in rendered
    assert "do-not-copy" not in rendered
    assert "headers" not in rendered
    assert sanitized["response"]["xTotalCount"] == 1


def test_fixture_counts_and_null_fields():
    c54 = json.loads(Path("tests/fixtures/responses/C54_example_p1.json").read_text())
    d71b = json.loads(Path("tests/fixtures/responses/D71B_example_p1.json").read_text())
    assert len(c54["response"]["results"]) == 3
    assert len(d71b["response"]["results"]) == 7
    assert any(p["birthYear"] is None for c in c54["response"]["results"] for p in c["parties"])
    assert any(c["caseId"] != c["displayCaseId"] for c in d71b["response"]["results"])
