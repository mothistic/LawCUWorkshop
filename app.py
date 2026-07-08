import os

from flask import Flask, render_template, request, redirect, session
from logic import (
    determine_applicable_law,
    normalize_country,
    resolve_nationality_for_juristic_person,
    resolve_nationality_for_natural_person,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-for-production")


@app.route("/reset")
def reset():
    session.clear()
    return redirect("/")


def load_wizard_state():
    return {
        "explicit_law": request.form.get("explicit_law", "") or session.get("explicit_law", ""),
        "party1_country": request.form.get("party1_country", "") or session.get("party1_country", ""),
        "party2_country": request.form.get("party2_country", "") or session.get("party2_country", ""),
        "party2_person_type": request.form.get("party2_person_type", "") or session.get("party2_person_type", ""),
        "party2_nationalities": request.form.get("party2_nationalities", "") or session.get("party2_nationalities", ""),
        "party2_last_acquired": request.form.get("party2_last_acquired", "") or session.get("party2_last_acquired", ""),
        "party2_domicile": request.form.get("party2_domicile", "") or session.get("party2_domicile", ""),
        "party2_principal_office": request.form.get("party2_principal_office", "") or session.get("party2_principal_office", ""),
        "contract_place": request.form.get("contract_place", "") or session.get("contract_place", ""),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    person_nationality_message = None
    step = int(request.form.get("step", "0") or 0)

    state = load_wizard_state()
    explicit_law = state["explicit_law"]
    party1_country = state["party1_country"]
    party2_country = state["party2_country"]
    party2_person_type = state["party2_person_type"]
    party2_nationalities = state["party2_nationalities"]
    party2_last_acquired = state["party2_last_acquired"]
    party2_domicile = state["party2_domicile"]
    party2_principal_office = state["party2_principal_office"]
    contract_place = state["contract_place"]

    asked_contract_place = False
    if request.method == "POST":
        if step == 0:
            explicit_law = normalize_country(request.form.get("explicit_law", "")) or ""
            if explicit_law:
                law = determine_applicable_law(
                    explicit_law=explicit_law,
                    party1_nationality=None,
                    party2_nationality=None,
                    contract_place=None,
                )
                result = {
                    "law": law,
                    "message": (
                        f"OK, based on the Act on Conflict of Laws, if the dispute is filed with the Thai Court, the laws of {law} can be used if properly presented to the Court."
                    ),
                }
                step = 6
            else:
                step = 1
        elif step == 1:
            party1_country = normalize_country(request.form.get("party1_country", "")) or ""
            if not party1_country:
                error = "Party 1's nationality is required unless the contract specifies a governing law."
                step = 1
            else:
                step = 2
        elif step == 2:
            party2_country = normalize_country(request.form.get("party2_country", "")) or ""
            if party2_country:
                if party2_country == party1_country:
                    law = determine_applicable_law(
                        explicit_law=None,
                        party1_nationality=party1_country,
                        party2_nationality=party2_country,
                        contract_place=None,
                    )
                    result = {
                        "law": law,
                        "message": (
                            f"OK, based on the Act on Conflict of Laws, if the dispute is filed with the Thai Court, the laws of {law} can be used if properly presented to the Court."
                        ),
                    }
                    step = 6
                else:
                    step = 5
            else:
                step = 3
        elif step == 3:
            party2_person_type = request.form.get("party2_person_type", "").strip().lower()
            if party2_person_type not in {"natural", "juristic"}:
                error = "Please enter either 'natural' or 'juristic'."
                step = 3
            else:
                step = 4
        elif step == 4:
            if party2_person_type == "natural":
                party2_nationalities = request.form.get("party2_nationalities", "")
                party2_last_acquired = request.form.get("party2_last_acquired", "")
                party2_domicile = request.form.get("party2_domicile", "")
                if not party2_nationalities:
                    error = "Please list the nationalities for Party 2."
                    step = 4
                else:
                    step = 5
            else:
                party2_principal_office = request.form.get("party2_principal_office", "")
                if not party2_principal_office:
                    error = "Please provide the principal office or establishment for the juristic person."
                    step = 4
                else:
                    party2_nationality = resolve_nationality_for_juristic_person(party2_principal_office)
                    person_nationality_message = f"OK, this juristic person is a national of {party2_nationality}."
                    result = {
                        "law": party2_nationality,
                        "message": (
                            f"OK, based on the Act on Conflict of Laws, if the dispute is filed with the Thai Court, the laws of {party2_nationality} can be used if properly presented to the Court."
                        ),
                    }
                    step = 6
        elif step == 5:
            contract_place = normalize_country(request.form.get("contract_place", "")) or ""
            asked_contract_place = True
            party2_nationality = None
            if party2_country:
                party2_nationality = party2_country
            elif party2_person_type == "natural":
                party2_nationality = resolve_nationality_for_natural_person(
                    nationalities=[value.strip() for value in party2_nationalities.split(",") if value.strip()],
                    last_acquired=[value.strip() for value in party2_last_acquired.split(",") if value.strip()],
                    domicile=party2_domicile or None,
                )
                if party2_nationality:
                    person_nationality_message = f"OK, this person is a national of {party2_nationality}."
            elif party2_person_type == "juristic":
                party2_nationality = resolve_nationality_for_juristic_person(party2_principal_office or None)

            law = determine_applicable_law(
                explicit_law=None,
                party1_nationality=party1_country or None,
                party2_nationality=party2_nationality,
                contract_place=contract_place or None,
            )
            result = {
                "law": law,
                "message": (
                    f"OK, based on the Act on Conflict of Laws, if the dispute is filed with the Thai Court, the laws of {law} can be used if properly presented to the Court."
                    if law
                    else "The applicable law could not be determined from the provided information."
                ),
            }
            step = 6

    question_history = []
    if step >= 1:
        question_history.append(
            ("Does the contract specify which country's law to use?", explicit_law or "N")
        )
    if step >= 2:
        question_history.append(
            ("Do you know which nationality should be used for Party 1?", party1_country or "N")
        )
    if step >= 3:
        question_history.append(
            ("Do you know which nationality should be used for Party 2?", party2_country or "N")
        )
    if step >= 4 and party2_country == "":
        question_history.append(
            ("Is Party 2 a natural person or a juristic person?", party2_person_type or "N")
        )
    if step >= 5 and party2_person_type == "natural":
        question_history.extend([
            ("Party 2 nationalities", party2_nationalities or "N"),
            ("Nationality last acquired", party2_last_acquired or "N"),
            ("Party 2 domicile", party2_domicile or "N"),
        ])
    if step >= 5 and party2_person_type == "juristic":
        question_history.append(
            ("Party 2 principal office or establishment", party2_principal_office or "N")
        )
    if step >= 6 and asked_contract_place:
        question_history.append(("Where was the contract made?", contract_place or "N"))

    session["explicit_law"] = explicit_law
    session["party1_country"] = party1_country
    session["party2_country"] = party2_country
    session["party2_person_type"] = party2_person_type
    session["party2_nationalities"] = party2_nationalities
    session["party2_last_acquired"] = party2_last_acquired
    session["party2_domicile"] = party2_domicile
    session["party2_principal_office"] = party2_principal_office
    session["contract_place"] = contract_place

    return render_template(
        "index.html",
        result=result,
        error=error,
        step=step,
        explicit_law=explicit_law,
        party1_country=party1_country,
        party2_country=party2_country,
        party2_person_type=party2_person_type,
        party2_nationalities=party2_nationalities,
        party2_last_acquired=party2_last_acquired,
        party2_domicile=party2_domicile,
        party2_principal_office=party2_principal_office,
        contract_place=contract_place,
        question_history=question_history,
        person_nationality_message=person_nationality_message,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("DEBUG", "false").lower() in {"1", "true", "yes"}
    app.run(debug=debug, host="0.0.0.0", port=port)
