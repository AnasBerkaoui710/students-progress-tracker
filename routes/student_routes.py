
from flask import Blueprint, render_template, request, redirect, url_for, flash

from models.student import (
    get_all_students,
    add_student,
    delete_student
)

student_bp = Blueprint("students", __name__)


@student_bp.route("/students")
def students():
    all_students = get_all_students()

    return render_template(
        "students.html",
        students=all_students
    )


@student_bp.route("/students/add", methods=["POST"])
def add():
    fullname = request.form.get("fullname", "").strip()
    educational_level = request.form.get("educational_level", "").strip()

    valid_levels = [
        "1ère année Collège",
        "2ème année Collège",
        "3ème année Collège",
        "Tronc Commun",
        "1ère année Bac",
        "2ème année Bac"
    ]

    if not fullname:
        flash("Student name is required.", "error")
        return redirect(url_for("students.students"))

    if educational_level not in valid_levels:
        flash("Please select a valid educational level.", "error")
        return redirect(url_for("students.students"))

    add_student(fullname, educational_level)

    flash("Student added successfully!", "success")

    return redirect(url_for("students.students"))


@student_bp.route("/students/delete/<int:student_id>", methods=["POST"])
def delete(student_id):
    deleted = delete_student(student_id)

    if deleted:
        flash("Student deleted successfully.", "success")
    else:
        flash("Student not found.", "error")

    return redirect(url_for("students.students"))
