
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DB_PATHS = {
    "movie2": "db/movie2.db",
    "beyazesya": "db/beyazesya.db",
    "dreamhome": "db/dreamhome.db",
    "okul": "db/okul.db"
}

def get_tables_and_columns(db_path):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    structure = {}
    for (table_name,) in tables:
        cur.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cur.fetchall()]
        structure[table_name] = columns
    con.close()
    return structure

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    selected_db = request.form.get("db") if request.method == "POST" else request.args.get("db", "movie2")
    current_query = request.form.get("query", "") if request.method == "POST" else request.args.get("query", "")

    structure = get_tables_and_columns(DB_PATHS[selected_db])

    if request.method == "POST" and current_query.strip():
        try:
            lowered = current_query.strip().lower()
            if not lowered.startswith("select"):
                raise Exception("Sadece SELECT sorgularına izin verilmektedir.")
            con = sqlite3.connect(DB_PATHS[selected_db])
            cur = con.cursor()
            cur.execute(current_query)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            result = {"columns": columns, "rows": rows}
            con.close()
        except Exception as e:
            error = str(e)

    return render_template("index.html",
                           result=result,
                           error=error,
                           query=current_query,
                           selected_db=selected_db,
                           structure=structure)

@app.route("/run_query/<db>/<table>")
def run_query(db, table):
    return redirect(url_for("index", db=db, query=f"SELECT * FROM {table} LIMIT 10;"))

if __name__ == "__main__":
    app.run(debug=True)
