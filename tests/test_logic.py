from logic import (
    determine_applicable_law,
    is_of_legal_age,
    resolve_nationality_for_juristic_person,
    resolve_nationality_for_natural_person,
)


def test_adult_by_age():
    assert is_of_legal_age(20) is True
    assert is_of_legal_age(30) is True


def test_not_adult_by_age():
    assert is_of_legal_age(19) is False
    assert is_of_legal_age(0) is False


def test_married_is_adult():
    assert is_of_legal_age(16, married=True) is True
    assert is_of_legal_age(0, married=True) is True


def test_invalid_age():
    import pytest

    with pytest.raises(ValueError):
        is_of_legal_age(None)
    with pytest.raises(ValueError):
        is_of_legal_age(-1)


def test_natural_person_nationality_uses_domicile_when_multiple_simultaneous_nationalities():
    nationality = resolve_nationality_for_natural_person(
        nationalities=["Philippines", "Cambodia"],
        last_acquired=["Philippines", "Cambodia"],
        domicile="Cambodia",
    )
    assert nationality == "Cambodia"


def test_natural_person_nationality_uses_last_acquired_when_successive():
    nationality = resolve_nationality_for_natural_person(
        nationalities=["Philippines", "Cambodia"],
        last_acquired=["Cambodia"],
        domicile="Philippines",
    )
    assert nationality == "Cambodia"


def test_natural_person_nationality_prefers_thailand_when_present():
    nationality = resolve_nationality_for_natural_person(
        nationalities=["Thailand", "France"],
        last_acquired=["France"],
        domicile="France",
    )
    assert nationality == "Thailand"


def test_juristic_person_nationality_uses_principal_office():
    nationality = resolve_nationality_for_juristic_person(principal_office="Singapore")
    assert nationality == "Singapore"


def test_applicable_law_uses_contract_place_when_parties_have_different_nationalities():
    law = determine_applicable_law(
        explicit_law=None,
        party1_nationality="Singapore",
        party2_nationality="Cambodia",
        contract_place="Malaysia",
    )
    assert law == "Malaysia"


def test_applicable_law_uses_explicit_choice_when_present():
    law = determine_applicable_law(
        explicit_law="Japan",
        party1_nationality="Singapore",
        party2_nationality="Cambodia",
        contract_place="Malaysia",
    )
    assert law == "Japan"


def test_applicable_law_ignores_n_answers_and_uses_contract_place():
    law = determine_applicable_law(
        explicit_law="N",
        party1_nationality="N",
        party2_nationality="N",
        contract_place="Malaysia",
    )
    assert law == "Malaysia"


def test_applicable_law_uses_common_nationality_when_parties_match():
    law = determine_applicable_law(
        explicit_law=None,
        party1_nationality="Singapore",
        party2_nationality="Singapore",
        contract_place="Malaysia",
    )
    assert law == "Singapore"


def test_applicable_law_returns_none_when_no_information_available():
    law = determine_applicable_law(
        explicit_law=None,
        party1_nationality=None,
        party2_nationality=None,
        contract_place=None,
    )
    assert law is None
