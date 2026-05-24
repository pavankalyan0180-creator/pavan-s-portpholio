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

    # OPEN CONTACT PAGE
    if request.method == "GET":

        return render_template(
            "contact.html",
            page="contact",
            sent=request.args.get("sent"),
            error=request.args.get("error")
        )

    # HANDLE FORM SUBMISSION
    if request.method == "POST":

        try:

            # FORM DATA
            name = request.form.get("name")
            email = request.form.get("email")
            message = request.form.get("message")

            print("FORM SUBMITTED")
            print(name)
            print(email)
            print(message)

            # EMAIL VARIABLES
            sender_email = os.getenv("PORTFOLIO_EMAIL")
            sender_password = os.getenv("PORTFOLIO_EMAIL_PASSWORD")

            print("EMAIL:", sender_email)
            print("PASSWORD EXISTS:", bool(sender_password))

            # CHECK VARIABLES
            if not sender_email or not sender_password:

                return """
                <h1>Environment Variable Error</h1>
                <p>PORTFOLIO_EMAIL or PASSWORD missing.</p>
                """

            # CREATE EMAIL
            email_body = f"""
Name: {name}

Email: {email}

Message:
{message}
"""

            email_message = MIMEText(email_body)

            email_message["Subject"] = "Portfolio Contact Form Submission"
            email_message["From"] = sender_email
            email_message["To"] = sender_email
            email_message["Reply-To"] = email

            print("CONNECTING SMTP")

            # SMTP CONNECTION
            server = smtplib.SMTP("smtp.gmail.com", 587)

            server.starttls()

            print("LOGGING IN")

            server.login(
                sender_email,
                sender_password
            )

            print("SENDING MAIL")

            server.sendmail(
                sender_email,
                sender_email,
                email_message.as_string()
            )

            print("MAIL SENT SUCCESSFULLY")

            server.quit()

            return redirect(
                url_for("contact", sent="1")
            )

        except Exception as e:

            print("EMAIL ERROR:", str(e))

            return f"""
            <h1>Email Sending Failed</h1>

            <p><b>Error:</b> {str(e)}</p>
            """

    return render_template(
        "contact.html",
        page="contact"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
