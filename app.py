import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for


load_dotenv()
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html", page="home")


@app.route("/about")
def about():
    return render_template("about.html", page="about")


@app.route("/projects")
def projects():
    return render_template("projects.html", page="projects")


@app.route("/skills")
def skills():
    return render_template("skills.html", page="skills")


@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        sender_email = os.getenv("PORTFOLIO_EMAIL")
        sender_password = os.getenv("PORTFOLIO_EMAIL_PASSWORD")

        if not sender_email or not sender_password:
            return redirect(url_for("contact", error="missing_config"))

        email_message = MIMEText(
            "Name: {}\nEmail: {}\n\nMessage:\n{}".format(name, email, message)
        )

        email_message["Subject"] = "Portfolio Contact Form Submission"
        email_message["From"] = sender_email
        email_message["To"] = sender_email
        email_message["Reply-To"] = email

        server = None

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)

            server.starttls()

            server.login(sender_email, sender_password)

            server.sendmail(
                sender_email,
                sender_email,
                email_message.as_string()
            )

        except Exception as e:
            print("Error sending email: {}".format(e))

            return redirect(url_for("contact", error="send_failed"))

        finally:
            if server:
                try:
                    server.quit()
                except Exception:
                    print("Error quitting SMTP server")

        return redirect(url_for("contact", sent="1"))

    return render_template(
        "contact.html",
        page="contact",
        sent=request.args.get("sent"),
        error=request.args.get("error")
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
