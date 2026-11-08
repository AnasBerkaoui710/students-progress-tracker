
from flask import Blueprint, render_template, request, redirect, url_for, flash

from models.student import get_all_students
from models.tracking import add_tracking

tracking_bp = Blueprint("tracking", __name__)


@tracking_bp.route("/tracking", methods=["GET", "POST"])
def monthly_tracking():

    if request.method == "POST":
        student_id = request.form.get("student_id")
        tracking_month = request.form.get("tracking_month")

        try:
            avg_study_hours = float(request.form.get("avg_study_hours"))
            avg_phone_usage_hours = float(
                request.form.get("avg_phone_usage_hours")
            )
            study_hours_limit = float(
                request.form.get("study_hours_limit")
            )
            phone_usage_limit = float(
                request.form.get("phone_usage_limit")
            )

            if (
                avg_study_hours < 0
                or avg_phone_usage_hours < 0
                or study_hours_limit < 0
                or phone_usage_limit < 0
            ):
                raise ValueError

        except (TypeError, ValueError):
            flash("Please enter valid, non-negative numbers.", "error")
            return redirect(url_for("tracking.monthly_tracking"))

        if not student_id or not tracking_month:
            flash("Please select a student and a month.", "error")
            return redirect(url_for("tracking.monthly_tracking"))

        tracking_month = tracking_month + "-01"

        success = add_tracking(
            student_id,
            tracking_month,
            avg_study_hours,
            avg_phone_usage_hours,
            study_hours_limit,
            phone_usage_limit
        )

        if success:
            flash("Monthly tracking added successfully!", "success")
        else:
            flash(
                "Could not save tracking. This student may already have a record for this month.",
                "error"
            )

        return redirect(url_for("tracking.monthly_tracking"))

    students = get_all_students()

    return render_template(
        "monthly_tracking.html",
        students=students
    )
