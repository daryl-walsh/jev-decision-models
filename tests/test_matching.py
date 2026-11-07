"""Behavior captured from the original monitor before environment migration."""

import unittest

from micrt_monitor.crtmonitor import (
    Person,
    classify,
    diff_against_state,
    match_results,
    norm,
    parse_party_name,
    update_state,
)


def case(case_id="SYNTHETIC-1", name="EXAMPLE, ALEX ROBIN", birth_year=1980):
    return {
        "caseId": case_id,
        "displayCaseId": "DISPLAY-1",
        "entitlement": "Synthetic case",
        "fileDate": "2020-01-01T00:00:00",
        "caseStatus": "CLOSED",
        "parties": [{"name": name, "birthYear": birth_year, "typeDescription": "DEFENDANT"}],
    }


class MatchingTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(norm("  O'Neil-Smith,  Alex R. "), "O'NEIL-SMITH, ALEX R")
        self.assertEqual(parse_party_name("Example, Alex Robin"), ("EXAMPLE", ["ALEX", "ROBIN"]))

    def test_name_only_needs_review(self):
        self.assertEqual(
            classify(Person("C54", "Example", "Alex"), case()["parties"][0])[0], "review"
        )

    def test_initial_and_birth_year_confirm(self):
        person = Person("C54", "Example", "Alex", "R", "1980")
        self.assertEqual(classify(person, case()["parties"][0]), ("confirmed", []))

    def test_missing_detail_needs_review(self):
        person = Person("C54", "Example", "Alex", "Robin", "1980")
        self.assertEqual(classify(person, case(birth_year=None)["parties"][0])[0], "review")

    def test_conflicting_detail_excludes(self):
        person = Person("C54", "Example", "Alex", "Robin", "1981")
        self.assertEqual(classify(person, case()["parties"][0])[0], "excluded")

    def test_other_person_does_not_match(self):
        self.assertIsNone(classify(Person("C54", "Example", "Morgan"), case()["parties"][0]))

    def test_person_override_precedes_global(self):
        person = Person("C54", "Example", "Alex", label="Synthetic person")
        overrides = {
            ("SYNTHETIC-1", ""): ("exclude", "global"),
            ("SYNTHETIC-1", person.name): ("confirm", "specific"),
        }
        match = match_results([person], [case()], overrides)[0]
        self.assertEqual(match["tier"], "confirmed")
        self.assertEqual(match["reasons"], ["override: specific"])
        self.assertEqual(match["displayCaseId"], "DISPLAY-1")

    def test_new_then_changed_and_first_seen_preserved(self):
        person = Person("C54", "Example", "Alex")
        matches = match_results([person], [case()], {})
        self.assertEqual(diff_against_state(matches, {}), (matches, []))
        state = {}
        update_state(matches, state, "2020-01-01")
        self.assertEqual(diff_against_state(matches, state), ([], []))
        matches[0]["caseStatus"] = "OPEN"
        new, changed = diff_against_state(matches, state)
        self.assertEqual(new, [])
        self.assertEqual(changed[0][1], {"caseStatus": ("CLOSED", "OPEN")})
        update_state(matches, state, "2020-02-01")
        self.assertEqual(next(iter(state.values()))["first_seen"], "2020-01-01")

    def test_excluded_cases_do_not_alert(self):
        person = Person("C54", "Example", "Alex", birth_year="1999")
        matches = match_results([person], [case()], {})
        self.assertEqual(diff_against_state(matches, {}), ([], []))
