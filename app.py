import os
import sqlite3

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from datetime import datetime
import random, string, requests

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///heypresto.db")


@app.after_request
def after_request(response):
    # Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    session["code"] = ''

    # Check for and delete old boxes and their contents
    today = datetime.now()
    if today.month > 6:
        boxes = db.execute("SELECT * FROM boxes WHERE CAST(substr(date, -4) AS INTEGER) < ?", today.year)
        for box in range(len(boxes)):
            if boxes[box]["type"] == 'image':
                images = db.execute("SELECT contents FROM box_contents WHERE box_code= ?", boxes[box]["code"])
                for image in range(len(images)):
                    if os.path.exists('static/uploads/' + images[image]["contents"]):
                        os.remove('static/uploads/' + images[image]["contents"])
            db.execute("DELETE FROM box_contents WHERE box_code= ?", boxes[box]["code"])
            db.execute("DELETE FROM boxes WHERE code= ?", boxes[box]["code"])

    return render_template("index.html")


@app.route("/gobox", methods=["GET", "POST"])
def gobox():
    open = ''
    manual_session_code = request.form.get('session_code')
    if manual_session_code != None:
        session["code"] = manual_session_code
    code = session["code"]
    open = request.form.get("open")

    # Show box details
    box = db.execute("SELECT * FROM boxes WHERE code= ?", code)
    box_contents = db.execute("SELECT * FROM box_contents WHERE box_code= ?", code)

    # Calculate time since submissions were made
    today_date = datetime.now()
    for submission in range(len(box_contents)):
        if box_contents[submission]["submitted"] != 'no':
            subdate = box_contents[submission]["submitted"].split('-')
            box_contents[submission]["subtime"] = time_since_submission(subdate, today_date)
        else:
            box_contents[submission]["subtime"] = 'no'

    # Work out display size for text
    if box[0]["type"] != 'image':
        for submission in range(len(box_contents)):
            box_contents[submission]["display_size"] = calc_display_size(box_contents[submission]["contents"])

    return render_template("gobox.html", box=box, box_contents=box_contents, open=open)


@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method != "POST":
        if session["code"] != '':   # For safety, in case javascript has wiped session code
            return redirect("/gobox")
        return redirect("/")

    date_time = datetime.now()
    date = str(date_time.day) + '-' + str(date_time.month) + '-' + str(date_time.year)
    box = db.execute("SELECT * FROM boxes WHERE code= ?", session["code"])
    username = request.form.get("username").strip().capitalize()

    if box[0]["type"] != 'image':
        submission = request.form.get("submission").strip().capitalize()
        if submission == '':
            flash("Enter your submission")
            return redirect("/gobox")
        if len(submission) > 310:
            flash("Your text can't be longer than 310 characters")
            return redirect("/gobox")
        # Check that box slots haven't all been filled
        count = db.execute("SELECT COUNT(*) AS count FROM box_contents WHERE box_code=? and submitted='no'", session["code"])
        if count[0]["count"] == 0:
            flash("No slots left in this box!")
            return redirect("/gobox")
        # Submit the submission
        db.execute("UPDATE box_contents SET username= ?, contents= ?, submitted= ?, type='text' WHERE id= (SELECT MIN(id) FROM box_contents WHERE box_code= ? AND submitted='no')", username, submission, date, session["code"])
        flash("Entry submitted!")

    if box[0]["type"] == 'image':
        try:
            file = request.files["image"]
            file_content = request.files["image"].read()
            size = len(file_content)
            if size > (500 * 1000):
                flash("Your image must be smaller than 500KB")
                return redirect("/gobox")
        except:
            pass

        # Check if file exists and is an allowed type
        if file and allowed_file(file.filename):
            suffix = ''
            for char in range(-4, 0, 1):
                suffix = suffix + file.filename[char]
            unique_code = False
            while unique_code == False:
                filename = session["code"] + str(random.randint(0, 1000)) + suffix
                code_check = db.execute("SELECT * FROM box_contents WHERE contents= ?", filename)
                if len(code_check) == 0:
                    unique_code = True

            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
                f.write(file_content)
            db.execute("UPDATE box_contents SET username= ?, contents= ?, submitted= ?, type='image' WHERE id= (SELECT MIN(id) FROM box_contents WHERE box_code= ? and submitted='no')", username, filename, date, session["code"])

    # Check if box is ready to open
    count = db.execute("SELECT * FROM box_contents WHERE box_code= ? AND submitted!='no'", session["code"])
    if len(count) == box[0]["number_of_users"]:
        db.execute("UPDATE boxes SET status='ready' WHERE code= ?", session["code"])
        flash("This box is ready to open!")
        return redirect('gobox')

    return redirect("/gobox")


@app.route("/make", methods=["GET", "POST"])
def make():
    if request.method != "POST":
        return render_template("make.html")

    name = request.form.get("name").strip().capitalize()
    type = request.form.get("type")
    users = request.form.get("users")
    users = int(users)
    instructions = request.form.get("instructions").strip().capitalize()

    if name == '':
        flash("Enter a name for this box")
        return render_template("make.html")

    # Generate a unique code for the box and create it
    codecheck = db.execute("SELECT code FROM boxes")
    if not codecheck:
        codecheck = [{'code': ''}]
    code_good = 0
    while code_good == 0:
        code = ''.join(random.choices(string.ascii_uppercase, k=5))
        if code not in codecheck[0].values():
            code_good = 1

    # Generate date of box creation
    date_time = datetime.now()
    date = str(date_time.day) + '-' + str(date_time.month) + '-' + str(date_time.year)

    db.execute("INSERT INTO boxes (code, name, instructions, type, number_of_users, status, date) VALUES (?, ?, ?, ?, ?, 'waiting', ?)", code, name, instructions, type, users, date)

    # Generate background colors and tilts for each box slot
    colors = ['purple', 'tan', 'yellow', 'neon-green', 'blue', 'orange', 'hot-pink', 'pale-pink', 'mint-green']
    for slots in range(users):
        bgcolor = random.choice(colors)
        tilt1 = random.uniform(-3, 3)
        tilt2 = random.uniform(-3, 3)
        db.execute("INSERT INTO box_contents (box_code, username, contents, submitted, type, bgcolor, tilt1, tilt2) VALUES (?, '???', '', 'no', ?, ?, ?, ?)", code, type, bgcolor, tilt1, tilt2)

    session["code"] = code
    return redirect("/made")


@app.route("/made")
def made():
    if session["code"] == '':
        return redirect("/make")

    box = db.execute("SELECT * FROM boxes WHERE code= ?", session["code"])
    return render_template("made.html", box=box)


def time_since_submission(subdate, today_date):
    sub_days_passed = (int(int(today_date.year) - int(subdate[2])) * 365) + int((int(today_date.month) - int(subdate[1])) * 30) + int(int(today_date.day) - int(subdate[0]))
    sub_years, sub_months, sub_weeks, sub_days, plural = '', '', '', '', ''
    if sub_days_passed > 364:
        if int(sub_days_passed / 365) > 1:
            plural = 's'
        sub_years = str(int(sub_days_passed / 365)) + ' year' + plural + ', '
        sub_days_passed = sub_days_passed % 365
        plural = ''
    if sub_days_passed > 29:
        if int(sub_days_passed / 30) > 1:
            plural = 's'
        sub_months = str(int(sub_days_passed / 30)) + ' month' + plural + ', '
        sub_days_passed = sub_days_passed % 30
        plural = ''
    if sub_days_passed != 0 and sub_days_passed > 6:
        if int(sub_days_passed / 7) > 1:
            plural = 's'
        sub_weeks = str(int(sub_days_passed / 7)) + ' week' + plural + ', '
        sub_days_passed = sub_days_passed % 7
        plural = ''
    if sub_days_passed != 0:
        if int(sub_days_passed) > 1:
            plural = 's'
        sub_days = str(sub_days_passed) + ' day' + plural
    subtime = sub_years + sub_months + sub_weeks + sub_days
    if subtime == '':
        subtime = 'today'
    if subtime[len(subtime) - 2] == ',':
        subtime = subtime[:-2] + subtime[-1]
    if subtime != 'today':
        subtime = subtime + ' ago'

    return subtime

# I found lots of info online about how to impliment recaptcha v2 in the client-side, but had
# real trouble finding anything about implimenting verification for server-side!
# In the end I had to go to ChatGPT to solve this one.
@app.route('/verify-recaptcha', methods=['POST'])
def verify_recaptcha():
    destination = request.form.get('destination')
    session["code"] = request.form.get('code')
    secret_key = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
    response = request.form.get('g-recaptcha-response')
    if response == '':
        flash("Tick the box to confirm you're not a robot")
        return redirect(request.referrer)
    data = {
        "secret": secret_key,
        "response": response
    }
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data)
    result = response.json()

    if result["success"] == False:
        flash("You might be a robot? Try it again")
        return redirect(request.referrer)
    else:
        return redirect(destination)


def calc_display_size(contents):
    if contents != '':
        size = 300 / len(contents)
        if size > 180:
            return 180
        if size < 18:
            return 18
        return size
    return 0


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
