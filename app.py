import os
import smtplib
import ssl
from email.mime.text import MIMEText

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for
from werkzeug.exceptions import HTTPException


load_dotenv()
app = Flask(__name__)


def get_env_value(*names):
    for name in names:
        value = os.getenv(name)
        if value:
            return value.strip()
    return None


def clean_app_password(password):
    return "".join(password.split())


def send_with_ssl(sender_email, sender_password, email_message):
    server = smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        timeout=30,
        context=ssl.create_default_context()
    )
    try:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [sender_email], email_message.as_string())
    finally:
        server.quit()


def send_with_starttls(sender_email, sender_password, email_message):
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
    try:
        server.ehlo()
        server.starttls(context=ssl.create_default_context())
        server.ehlo()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [sender_email], email_message.as_string())
    finally:
        server.quit()


def send_contact_email(name, reply_to_email, message):
    sender_email = get_env_value(
        "PORTFOLIO_EMAIL",
        "portfolio_email",
        "EMAIL",
        "GMAIL_USER"
    )
    sender_password = get_env_value(
        "PORTFOLIO_EMAIL_PASSWORD",
        "PORTFOLIO_PASSWORD",
        "portfolio_password",
        "EMAIL_PASSWORD",
        "GMAIL_APP_PASSWORD"
    )

    if not sender_email or not sender_password:
        app.logger.error("Contact email environment variables are missing")
        return False

    sender_password = clean_app_password(sender_password)

    email_body = "Name: {}\nEmail: {}\n\nMessage:\n{}".format(
        name,
        reply_to_email,
        message
    )
    email_message = MIMEText(email_body, "plain", "utf-8")
    email_message["Subject"] = "Portfolio Contact Form Submission"
    email_message["From"] = sender_email
    email_message["To"] = sender_email
    email_message["Reply-To"] = reply_to_email

    for method_name, send_method in (
        ("SMTP_SSL_465", send_with_ssl),
        ("STARTTLS_587", send_with_starttls),
    ):
        try:
            send_method(sender_email, sender_password, email_message)
            app.logger.info("Contact form email sent with %s", method_name)
            return True
        except smtplib.SMTPAuthenticationError as error:
            app.logger.error(
                "Contact form Gmail authentication failed with %s: %s",
                method_name,
                error.smtp_error
            )
            return False
        except Exception as error:
            app.logger.warning(
                "Contact form email failed with %s: %s: %s",
                method_name,
                type(error).__name__,
                error
            )

    app.logger.error("Contact form email failed after all SMTP methods")
    return False


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
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            return redirect(url_for("contact", error="invalid_form"))

        if send_contact_email(name, email, message):
            return redirect(url_for("contact", sent="1"))

        return redirect(url_for("contact", error="send_failed"))

    return render_template(
        "contact.html",
        page="contact",
        sent=request.args.get("sent"),
        error=request.args.get("error")
    )


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    if isinstance(error, HTTPException):
        return error

    app.logger.exception("Unexpected application error")
    if request.path == "/contact":
        return redirect(url_for("contact", error="send_failed"))
    return "Something went wrong. Please try again later.", 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
