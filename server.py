from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash, session
import data_manager
import util
from bonus_questions import SAMPLE_QUESTIONS
import os
from psycopg2.errors import UniqueViolation

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './static/images'
app.secret_key = os.urandom(16)


@app.route('/bonus')
def bonus():
    return render_template('bonus_questions.html')


@app.route("/static/images/<path:filename>")
def images(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/catch-hacker")
def catch_hacker():
    return render_template('hack.html')


@app.route("/")
def load_main():
    return render_template('index.html', payload=data_manager.get_main_page_data(request.args))


@app.route("/list")
def load_list_page():
    if request.args.get('order'):
        if request.args.get('order').lower() not in ['asc', 'desc']:
            return redirect(url_for('catch_hacker'))
    return render_template("index.html", payload=data_manager.get_list_page_data(request.args))


@app.route("/question/<question_id>")
def load_question_page(question_id):
    data_manager.update_view_nuber(question_id=question_id)
    payload = data_manager.get_question_page_data(question_id, request.args)
    return render_template("question.html", payload=payload)


@app.route("/<table>/<record_id>/delete")
@app.route("/question/<question_id>/<table>/<record_id>/delete")
def delete_record_by_id(table, record_id, question_id=None):
    record = data_manager.get_fields_from_table_by_value('', table if table != 'question_tag' else "question", 'id', record_id if table != 'question_tag' else question_id)
    if session.get('user_id') != record.get('user_id'):
        flash('You have no permission to delete!', category='error')
        return redirect(url_for('load_question_page', question_id=record_id if table != 'question_tag' else question_id))
    if table != 'question_tag':
        data_manager.delete_record_by_identifier(table, record_id, question_id, 'id')
    else:
        data_manager.delete_record_by_identifier(table, record_id, question_id, 'tag_id')
    if table == 'question':
        return redirect(url_for('load_list_page'))
    return redirect(request.referrer)


@app.route("/vote_on_record", methods=['POST'])
def vote_on_record():
    table = request.form["table"]
    data_manager.update_record(table, request.form)
    return '', 202


@app.route("/question/<question_id>/new-<record>/", methods=['GET', 'POST'])
@app.route("/answer/<answer_id>/new-<record>", methods=['GET', 'POST'])
@app.route("/add-<record>", methods=['GET', 'POST'])
def add_new_record(record, question_id=None, answer_id=None):
    if 'username' not in session:
        flash('Please log in to contribute!', category='error')
        return redirect(url_for('login'))
    user_id = data_manager.get_fields_from_table_by_value(fields='user_id', table='users', key='email',
                                                          key_value=session['email'])
    if request.method == 'POST':
        data_manager.add_new_record(record, question_id, answer_id, request, user_id=user_id.get('user_id'))
        if record != 'question' and request.form.get('redirect'):
            return redirect(request.form['redirect'])
        question_id = data_manager.get_fields_from_table_by_value('id', 'question', ordered=True)['id']
        return redirect(url_for('load_question_page', question_id=question_id))
    return render_template('add_new_record.html', payload={'record': record,
                                                           'question_id': question_id,
                                                           'answer_id': answer_id,
                                                           'redirect': request.referrer})


@app.route('/<record_type>/<record_id>/edit', methods=['GET', 'POST'])
def edit_record(record_type, record_id):
    record = data_manager.get_fields_from_table_by_value('', record_type, 'id', record_id)
    if session.get('user_id') != record.get('user_id'):
        flash('You have no permission to edit!', category='error')
        return redirect(url_for('load_question_page', question_id=record_id))
    if request.method == 'POST':
        data_manager.update_record(record_type, request.form)
        return redirect(request.form['redirect'])
    return render_template('edit_record.html', payload={'record_type': record_type,
                                                        'record': record,
                                                        'redirect': request.referrer})


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
def add_tag(question_id):
    record = data_manager.get_fields_from_table_by_value('user_id', 'question', 'id', question_id)
    if session.get('user_id') != record.get('user_id'):
        flash('You have no permission to add tag!', category='error')
        return redirect(url_for('load_question_page', question_id=question_id))
    tags = data_manager.get_tag_table('tag', )
    if request.method == 'POST':
        data_manager.add_tag_to_question(question_id, form=dict(request.form))
        return redirect(url_for('load_question_page', question_id=question_id))
    if request.method == 'GET':
        return render_template('add_tags.html', question_id=question_id, tags=tags)


# need refactor from down there


@app.route("/search")
def search():
    column_names = ["vote_number", "a_vote_number", "submission_time", "a_submission_time"]
    sort_by = request.args['sort_by'] if request.args.get('sort_by') in column_names else None
    order = request.args['order'] if sort_by else None
    if len(request.args['q'].strip()) > 0:
        search_result = data_manager.get_records_by_search(searched_word=request.args['q'],
                                                           sort_by=sort_by,
                                                           order=order)
    else:
        return redirect(url_for('load_main'))
    if order not in ['asc', 'desc', None]:
        return redirect(url_for('catch_hacker'))
    return render_template("search.html", cards=search_result, columns=column_names)


@app.route("/bonus-questions")
def main():
    return render_template('bonus_questions.html', questions=SAMPLE_QUESTIONS)


@app.route("/tags")
def load_tags_page():
    session['username'] = session.get('username')
    tags = data_manager.get_tag_page_data()
    return render_template('tags.html', tags=tags)


@app.route("/users")
@app.route("/users/<user_id>")
def load_users_list(user_id=None):
    if 'username' not in session:
        flash('Please log in to view fellow users!', category='error')
        return redirect(url_for('login'))

    if not user_id:
        users = data_manager.get_users_list()
        return render_template("users_list.html", users=users)
    return redirect(url_for('load_user_page', user_id=user_id))


@app.route("/registration", methods=["GET", "POST"])
def register_user():
    if request.method == "GET":
        return render_template("registration_page.html")
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            user_name = request.form.get('user_name')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            if len(email) < 4:
                flash('Email has to be at least 4 characters!', category='error')
            elif len(user_name) < 2:
                flash('First name has to be at least 2 characters!', category='error')
            elif password1 != password2:
                flash('Passwords must match!', category='error')
            elif len(password1) < 7:
                flash('Password has to be at least 7 characters!', category='error')
            else:
                flash(f"Nice to meet you {user_name} your account is ready!", category='success')
                data_manager.add_new_user(email, user_name, password=util.hash_password(password1))
                return redirect(url_for('load_main'))
        except UniqueViolation:
            flash('Username or email is already taken!', category='error')
            return render_template("registration_page.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = data_manager.get_fields_from_table_by_value(fields=['user_id', 'user_name', 'password', 'email'],
                                                               table='users',
                                                               key='email',
                                                               key_value=request.form['email'])
            if util.verify_password(request.form['password'], user['password']):
                session['username'] = user['user_name']
                session['user_id'] = user['user_id']
                session['email'] = user['email']
                flash(f"Welcome {session['username']}!", category='success')
                return redirect(url_for("load_main"))
            else:
                flash('Invalid credentials!', category='error')
                return render_template("login.html")
        except TypeError:
            flash('Invalid credentials!', category='error')
            return render_template("login.html")
    else:
        return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('load_main'))


@app.route('/accept-answer', methods=['POST'])
def mark_accepted():
    if request.form['status'] == 'False':
        data_manager.answer_accept_status(status='true', answer_id=request.form['answer_id'])
        data_manager.gain_when_accepted(answer_id=request.form['answer_id'], value=+15)
    else:
        data_manager.answer_accept_status(status='false', answer_id=request.form['answer_id'])
        data_manager.gain_when_accepted(answer_id=request.form['answer_id'], value=-15)
    return '', 202


@app.route('/user/<user_id>')
def load_user_page(user_id):
    return render_template('user_page.html', payload=data_manager.get_user_page_data(user_id))


if __name__ == "__main__":
    app.run(debug=True)
