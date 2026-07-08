from datetime import date
from flask import Flask, render_template, request

app = Flask(__name__)


def determine_legal_age(date_of_birth, married):
    today = date.today()
    age = today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )

    if age >= 20:
        return True, age, (
            "The person has reached the general age of majority under Thai law."
        )

    if married:
        return True, age, (
            "The person is married, and under Thai law that is treated as reaching legal adulthood for general legal capacity."
        )

    return False, age, (
        "The person has not reached the general age of majority under Thai law and is not married."
    )


@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        birth_date_raw = request.form.get("date_of_birth", "")
        married = request.form.get("married") == "on"

        try:
            birth_date = date.fromisoformat(birth_date_raw)
        except ValueError:
            result = {
                "error": "Please enter a valid date of birth in YYYY-MM-DD format."
            }
        else:
            is_legal, age, message = determine_legal_age(birth_date, married)
            result = {
                "is_legal": is_legal,
                "age": age,
                "message": message,
            }

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
