from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for
from Server import ServerConnection
from markupsafe import Markup
import json

app = Flask(__name__)
server: ServerConnection


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if not server.is_authorized:
                return redirect('/')
            return f(*args, **kwargs)
        except:
            return redirect('/')
    return decorated_function

@app.route('/')
def login_page():
    try:
        if not server.is_authorized:
            return render_template("login.html")
        return redirect(url_for('home'))
    except:
        return render_template("login.html")


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    global server
    server = ServerConnection(username, password)

    if not server.is_authorized:
        return jsonify({'message': 'error'})

    return redirect(url_for('home'))


@app.route('/home')
@login_required
def home():
    subjects = server.get_subjects()
    return render_template('courses.html',
                           subjects=subjects,
                           username=server.username)


@app.route('/course/<int:course_id>')
@login_required
def course(course_id):
    tasks, subject_name = server.get_course_tasks(course_id), 'АиСД'
    return render_template('contest.html',
                           content=tasks,
                           subject=subject_name,
                           username=server.username)


@app.route('/task/<int:task_id>')
@login_required
def task(task_id):
    statement, languages, submissions = server.get_task_by_id(task_id)
    return render_template('task.html',
                           statement=Markup(statement),
                           languages=languages,
                           submissions=submissions,
                           username=server.username,
                           notsolved=(len(languages) > 0))


@app.route('/task/<int:task_id>/submit', methods=['POST'])
@login_required
def submit(task_id):
    data = request.get_json()
    code = data['code']
    language = data['language']

    return server.sumbit_solution(task_id, code, language)


@app.route('/task/<int:task_id>/submission/<int:code_id>')
@login_required
def get_code(task_id, code_id):
    code, task_name, verdict, lang, report, cheating, comment = server.get_task_report(task_id, code_id)
    return render_template('report.html',
                           task_name=task_name,
                           code=Markup(code),
                           lang=lang,
                           verdict=verdict,
                           report=Markup(report),
                           cheating=cheating,
                           comment=comment,
                           username=server.username)

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html',
                           username=server.username)


@app.route('/logout')
@login_required
def turn_off():
    # TODO редирект на фронте
    return redirect(url_for('home'))

def main():
    try:
        global server
        with open('info.json') as f:
            info = f.read()
            settings = json.loads(info)

            if settings.get('username') and settings.get('password'):
                server = ServerConnection(settings.get('username'), settings.get('password'))
    except:
        pass
    app.run()


# if __name__ == '__main__':
#    main()

main()
