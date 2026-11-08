
from database.db import get_db_connection


# =========================================================
# 1. ADD MONTHLY TRACKING
# =========================================================

def add_tracking(
    student_id,
    tracking_month,
    avg_study_hours,
    avg_phone_usage_hours,
    study_hours_limit,
    phone_usage_limit
):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO monthly_tracking (
            student_id,
            tracking_month,
            avg_study_hours,
            avg_phone_usage_hours,
            study_hours_limit,
            phone_usage_limit
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        student_id,
        tracking_month,
        avg_study_hours,
        avg_phone_usage_hours,
        study_hours_limit,
        phone_usage_limit
    )

    try:
        cursor.execute(query, values)
        connection.commit()
        return True

    except Exception as e:
        connection.rollback()
        print("Error adding tracking:", e)
        return False

    finally:
        cursor.close()
        connection.close()


# =========================================================
# 2. GET DASHBOARD DATA
# =========================================================

def get_dashboard_data():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # A. INITIALIZE DASHBOARD DATA
        # -------------------------------------------------

        monthly_trends = []
        student_history = {}

        status_summary = {
            "On track": 0,
            "Partially on track": 0,
            "Needs attention": 0,
            "Not tracked": 0
        }

        # -------------------------------------------------
        # B. GET TOTAL NUMBER OF STUDENTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total_students
            FROM students
        """)

        total_students = cursor.fetchone()["total_students"]

        # -------------------------------------------------
        # C. GET LATEST TRACKING MONTH
        # -------------------------------------------------

        cursor.execute("""
            SELECT MAX(tracking_month) AS latest_month
            FROM monthly_tracking
        """)

        latest_month = cursor.fetchone()["latest_month"]

        # -------------------------------------------------
        # D. HANDLE EMPTY TRACKING DATABASE
        # -------------------------------------------------

        if latest_month is None:

            cursor.execute("""
                SELECT id, fullname, educational_level
                FROM students
                ORDER BY fullname ASC
            """)

            students = cursor.fetchall()

            for student in students:

                student.update({
                    "avg_study_hours": None,
                    "study_hours_limit": None,
                    "avg_phone_usage_hours": None,
                    "phone_usage_limit": None,
                    "study_change": None,
                    "phone_change": None,
                    "status": "Not tracked"
                })

            status_summary["Not tracked"] = total_students

            return {
                "total_students": total_students,
                "tracked_students": 0,
                "average_study_hours": None,
                "average_phone_usage_hours": None,
                "improved_students": 0,
                "needs_attention": total_students,
                "latest_month_label": "No tracking data yet",
                "student_progress": students,
                "monthly_trends": monthly_trends,
                "student_history": student_history,
                "status_summary": status_summary
            }

        # -------------------------------------------------
        # E. GET MONTHLY DATA FOR THE OVERALL CHARTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                DATE_FORMAT(MIN(tracking_month), '%b %Y') AS month_label,

                AVG(avg_study_hours) AS avg_study_hours,
                AVG(study_hours_limit) AS avg_study_target,

                AVG(avg_phone_usage_hours) AS avg_phone_usage_hours,
                AVG(phone_usage_limit) AS avg_phone_limit,

                COUNT(*) AS tracked_students

            FROM monthly_tracking

            GROUP BY
                YEAR(tracking_month),
                MONTH(tracking_month)

            ORDER BY
                YEAR(tracking_month),
                MONTH(tracking_month)
        """)

        trend_rows = cursor.fetchall()

        for row in trend_rows:

            monthly_trends.append({
                "month_label": row["month_label"],

                "avg_study_hours": round(
                    float(row["avg_study_hours"]), 2
                ),

                "avg_study_target": round(
                    float(row["avg_study_target"]), 2
                ),

                "avg_phone_usage_hours": round(
                    float(row["avg_phone_usage_hours"]), 2
                ),

                "avg_phone_limit": round(
                    float(row["avg_phone_limit"]), 2
                ),

                "tracked_students": row["tracked_students"]
            })

        # -------------------------------------------------
        # F. GET ALL INDIVIDUAL STUDENT HISTORY
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                student_id,

                DATE_FORMAT(tracking_month, '%b %Y') AS month_label,

                avg_study_hours,
                study_hours_limit,

                avg_phone_usage_hours,
                phone_usage_limit

            FROM monthly_tracking

            ORDER BY student_id ASC, tracking_month ASC
        """)

        history_rows = cursor.fetchall()

        for row in history_rows:

            student_key = str(row["student_id"])

            if student_key not in student_history:
                student_history[student_key] = []

            student_history[student_key].append({

                "month_label": row["month_label"],

                "avg_study_hours": float(
                    row["avg_study_hours"]
                ),

                "study_hours_limit": float(
                    row["study_hours_limit"]
                ),

                "avg_phone_usage_hours": float(
                    row["avg_phone_usage_hours"]
                ),

                "phone_usage_limit": float(
                    row["phone_usage_limit"]
                )
            })

        # -------------------------------------------------
        # G. GET LATEST AND PREVIOUS MONTH FOR EACH STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.fullname,
                s.educational_level,

                t.tracking_month,

                t.avg_study_hours,
                t.study_hours_limit,

                t.avg_phone_usage_hours,
                t.phone_usage_limit,

                p.avg_study_hours AS previous_study_hours,
                p.avg_phone_usage_hours AS previous_phone_hours

            FROM students s

            LEFT JOIN monthly_tracking t
                ON t.student_id = s.id
                AND t.tracking_month = %s

            LEFT JOIN monthly_tracking p
                ON p.student_id = s.id
                AND p.tracking_month = DATE_SUB(
                    %s, INTERVAL 1 MONTH
                )

            ORDER BY s.fullname ASC

        """, (latest_month, latest_month))

        student_progress = cursor.fetchall()

        # -------------------------------------------------
        # H. CALCULATE OVERALL STATISTICS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                COUNT(*) AS tracked_students,

                AVG(avg_study_hours) AS average_study_hours,

                AVG(avg_phone_usage_hours) AS average_phone_usage_hours

            FROM monthly_tracking

            WHERE tracking_month = %s
        """, (latest_month,))

        statistics = cursor.fetchone()

        tracked_students = statistics["tracked_students"]

        average_study_hours = statistics["average_study_hours"]
        average_phone_usage_hours = statistics["average_phone_usage_hours"]

        if average_study_hours is not None:
            average_study_hours = float(average_study_hours)

        if average_phone_usage_hours is not None:
            average_phone_usage_hours = float(
                average_phone_usage_hours
            )

        # -------------------------------------------------
        # I. CALCULATE INDIVIDUAL STUDENT PROGRESS
        # -------------------------------------------------

        improved_students = 0
        needs_attention = 0

        for student in student_progress:

            # Student has no record for the latest month
            if student["tracking_month"] is None:

                student["status"] = "Not tracked"

                student["study_change"] = None
                student["phone_change"] = None

                status_summary["Not tracked"] += 1
                needs_attention += 1

                continue

            # Current values
            study = float(student["avg_study_hours"])
            study_target = float(student["study_hours_limit"])

            phone = float(student["avg_phone_usage_hours"])
            phone_limit = float(student["phone_usage_limit"])

            # Check targets
            study_ok = study >= study_target
            phone_ok = phone <= phone_limit

            # Assign student status
            if study_ok and phone_ok:

                student["status"] = "On track"

            elif study_ok or phone_ok:

                student["status"] = "Partially on track"

            else:

                student["status"] = "Needs attention"

            status_summary[student["status"]] += 1

            # Count students who fail at least one target
            if not (study_ok and phone_ok):
                needs_attention += 1

            # Previous month values
            previous_study = student["previous_study_hours"]
            previous_phone = student["previous_phone_hours"]

            student["study_change"] = None
            student["phone_change"] = None

            # Calculate study-hours change
            if previous_study is not None:

                student["study_change"] = (
                    study - float(previous_study)
                )

            # Calculate phone-usage change
            if previous_phone is not None:

                student["phone_change"] = (
                    phone - float(previous_phone)
                )

            # Count students improving in both habits
            if (
                previous_study is not None
                and previous_phone is not None
                and study > float(previous_study)
                and phone < float(previous_phone)
            ):

                improved_students += 1

        # -------------------------------------------------
        # J. RETURN ALL DASHBOARD DATA
        # -------------------------------------------------

        return {

            "total_students": total_students,

            "tracked_students": tracked_students,

            "average_study_hours": average_study_hours,

            "average_phone_usage_hours": average_phone_usage_hours,

            "improved_students": improved_students,

            "needs_attention": needs_attention,

            "latest_month_label": latest_month.strftime("%B %Y"),

            "student_progress": student_progress,

            "monthly_trends": monthly_trends,

            "student_history": student_history,

            "status_summary": status_summary
        }

    finally:

        cursor.close()
        connection.close()
