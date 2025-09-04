from flask import Flask, render_template, request, redirect, url_for, session
import datetime

app = Flask(__name__)
app.secret_key = "finance_secret"  # sessiyalar uchun

# Dastlabki ma’lumotlar
PASSWORD = "5523"
monthly_salary = 400
balance_usd = monthly_salary
exchange_rate = 11000  # kursni qo‘lda o‘zgartirishingiz mumkin
journal = []


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        password = request.form.get("password")
        if password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            return render_template("index.html", error="Parol noto‘g‘ri!")
    return render_template("index.html")


@app.route("/home")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("index"))
    return render_template("home.html")


@app.route("/add", methods=["POST"])
def add():
    global balance_usd
    if not session.get("logged_in"):
        return redirect(url_for("index"))

    amount = request.form.get("amount")
    if not amount:
        return redirect(url_for("home"))

    note = request.form.get("note", "")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Agar $ bilan tugasa dollar deb qabul qilamiz
    if "$" in amount:
        value = float(amount.replace("$", "").strip())
        balance_usd -= value
        journal.append((now, f"-{value} $", note))
    else:
        value = float(amount.strip())
        usd_value = value / exchange_rate
        balance_usd -= usd_value
        journal.append((now, f"-{value} so‘m (~{usd_value:.2f}$)", note))

    return redirect(url_for("home"))


@app.route("/balance")
def balance():
    if not session.get("logged_in"):
        return redirect(url_for("index"))
    balance_sum = f"{balance_usd:.2f} $ ({balance_usd * exchange_rate:,.0f} so‘m)"
    last = journal[-1] if journal else None
    return render_template("balance.html", balance=balance_sum, last=last)


@app.route("/journal")
def show_journal():
    if not session.get("logged_in"):
        return redirect(url_for("index"))
    return render_template("journal.html", journal=journal)


@app.route("/reset")
def reset():
    global balance_usd, journal
    if not session.get("logged_in"):
        return redirect(url_for("index"))
    balance_usd = monthly_salary
    journal = []
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
