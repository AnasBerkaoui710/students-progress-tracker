
from flask import Flask, render_template, redirect, url_for

from config import Config
from routes.student_routes import student_bp
from routes.tracking_routes import tracking_bp
from models.tracking import get_dashboard_data

app = Flask(__name__)

app.config.from_object(Config)
app.secret_key = "change-this-to-a-random-secret"

# Register blueprints
app.register_blueprint(student_bp)
app.register_blueprint(tracking_bp)


@app.route("/")
def home():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    dashboard_data = get_dashboard_data()

    return render_template(
        "dashboard.html",
        **dashboard_data
    )


if __name__ == "__main__":
    app.run(debug=True)
