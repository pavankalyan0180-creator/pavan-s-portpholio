import os

from flask import Flask, render_template, request
from werkzeug.exceptions import HTTPException


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


@app.route("/contact")
def contact():
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
    return "Something went wrong. Please try again later.", 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
