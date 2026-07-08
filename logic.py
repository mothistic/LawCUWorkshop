from typing import Optional, Sequence


def normalize_country(value: Optional[str]) -> Optional[str]:
    """Normalize country answers so blank or 'N' values are treated as absent."""
    if value is None:
        return None
    normalized = value.strip()
    if not normalized or normalized.upper() == "N":
        return None
    return normalized


def is_of_legal_age(age: Optional[int], married: bool = False) -> bool:
    """Determine whether a person is of legal age under assumed Thai rules.

    Rules used by this tool (assumptions — see README):
    - Legal majority is 20 years old.
    - For the purpose of this simple tool, a person who is married is
      considered to have adult status regardless of numeric age.
    """
    if age is None:
        raise ValueError("age must be provided")
    try:
        age_int = int(age)
    except (TypeError, ValueError):
        raise ValueError("age must be an integer")
    if age_int < 0:
        raise ValueError("age must be non-negative")

    if married:
        return True
    return age_int >= 20


def status_text(age: Optional[int], married: bool = False) -> str:
    """Human-friendly status message for UI/testing."""
    adult = is_of_legal_age(age, married)
    if adult:
        return "Person is an adult under the assumed Thai rule."
    return "Person is NOT an adult under the assumed Thai rule."


def resolve_nationality_for_natural_person(
    nationalities: Optional[Sequence[str]] = None,
    last_acquired: Optional[Sequence[str]] = None,
    domicile: Optional[str] = None,
) -> Optional[str]:
    """Resolve nationality for a natural person under the Thai conflict rules.

    The implementation follows the simplified rules described in the prompt:
    - If the person has multiple nationalities acquired successively, use the last one acquired.
    - If they were acquired simultaneously, use the domicile country if present.
    - If a Thai nationality is among the conflicts, Thailand governs.
    """
    normalized_nationalities = [normalize_country(country) for country in (nationalities or [])]
    normalized_nationalities = [country for country in normalized_nationalities if country]

    if any(country.lower() == "thailand" for country in normalized_nationalities):
        return "Thailand"

    resolved_last_acquired = [normalize_country(country) for country in (last_acquired or [])]
    resolved_last_acquired = [country for country in resolved_last_acquired if country]

    if len(resolved_last_acquired) == 1:
        return resolved_last_acquired[0]

    if len(resolved_last_acquired) > 1:
        if domicile:
            return domicile.strip()
        return resolved_last_acquired[-1]

    if len(normalized_nationalities) == 1:
        return normalized_nationalities[0]

    if domicile:
        return domicile.strip()

    return None


def resolve_nationality_for_juristic_person(principal_office: Optional[str] = None) -> Optional[str]:
    """Resolve nationality for a juristic person under the Thai conflict rules."""
    if principal_office:
        return principal_office.strip()
    return None


def determine_applicable_law(
    explicit_law: Optional[str],
    party1_nationality: Optional[str],
    party2_nationality: Optional[str],
    contract_place: Optional[str] = None,
) -> Optional[str]:
    """Determine which country's law should be applied in a Thai court dispute."""
    explicit_law = normalize_country(explicit_law)
    party1_nationality = normalize_country(party1_nationality)
    party2_nationality = normalize_country(party2_nationality)
    contract_place = normalize_country(contract_place)

    if explicit_law:
        return explicit_law

    if party1_nationality and party2_nationality and party1_nationality == party2_nationality:
        return party1_nationality

    if contract_place:
        return contract_place

    return None
