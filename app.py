from flask import Flask, render_template, request, jsonify, redirect, url_for
from Server import ServerConnection
from markupsafe import Markup

app = Flask(__name__)


@app.route('/')
def login_page():
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    global server

    # TODO PASTE PARAMETRES
    server = ServerConnection(username, password)

    if server.status >= 300:
        return jsonify({'message': 'error'})

    return redirect(url_for('home'))


@app.route('/home')
def home():
    return render_template('courses.html', data=server.get_subjects())


@app.route('/course/<int:course_id>')
def course(course_id):
    return render_template('contest.html', content=server.get_course_tasks(course_id), subject='АиСД')

@app.route('/task/<int:task_id>')
def task(task_id):
    statement, languages, submissions = server.get_task_by_id(task_id)
    return render_template('task.html', statement=Markup(statement), languages=languages, submissions=submissions)

@app.route('/task/<int:task_id>/submit', methods=['POST'])
def submit(task_id):
    data = request.get_json()
    code = data['code']
    language = data['language']

    return server.sumbit_solution(task_id, code, language)

@app.route('/task/<int:task_id>/submission/<int:code_id>')
def get_code(task_id, code_id):
    return server.get_code(task_id, code_id)


if __name__ == '__main__':
    app.run()
