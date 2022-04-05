import os
from flask import Flask, request, render_template, redirect
import data_manager


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploaded_files'


@app.route("/")
def main():
    questions = data_manager.get_table('question', limit='5',
                                       sort_by='submission_time',
                                       order='desc')
    return render_template("index.html", questions=questions)


@app.route("/list")
def list():
    questions = data_manager.get_table('question')
    return render_template("index.html", questions=questions)


@app.route("/question/<question_id>", methods=['GET', 'POST'])
def route_question(question_id):
    question = data_manager.get_records_by_id('question', question_id)
    print(question)
    if request.method == "GET":
        data_manager.get_all_records('answer')
        return render_template("question.html", question=question)


@app.route("/question/<question_id>/delete")
def route_delete_question(question_id):
    question = data_manager.get_entry_by_id(question_id, data_manager.QUESTION_FILE_PATH, data_manager.QUESTION_HEADER)
    data_manager.delete_entry(data_manager.QUESTION_FILE_PATH, data_manager.QUESTION_HEADER, question)
    answers_to_remove = [answer for answer in
                         data_manager.get_all_entries_with_unix_timestamp(data_manager.ANSWER_FILE_PATH,
                                                                          data_manager.ANSWER_HEADER)
                         if answer['question_id'] == question_id]
    for answer in answers_to_remove:
        data_manager.delete_entry(data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER, answer)
    return redirect("/list")


@app.route("/question/<question_id>/new-answer", methods=['GET', 'POST'])
def route_add_answer(question_id):
    if request.method == 'GET':
        return render_template("answer.html", question_id=question_id)
    if request.files.get('image').content_type == 'application/octet-stream':
        path = './uploaded_files/no_image_found.png'
    else:
        image = request.files['image']
        path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(path)
    data_manager.add_new_entry(data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER,
                               entry_to_add=request.form, upload_path=path)
    return redirect("/question/" + question_id)


@app.route("/answer/<answer_id>/delete")
def route_delete_answer(answer_id):
    answer = data_manager.get_entry_by_id(answer_id, data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER)
    question_id = answer['question_id']
    data_manager.delete_entry(data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER, answer)
    return redirect("/question/" + question_id)


@app.route('/add-question', methods=['GET', 'POST'])
def route_add_question():
    if request.method == 'POST':
        if request.files.get('image').content_type == 'application/octet-stream':
            path = './uploaded_files/no_image_found.png'
        else:
            image = request.files['image']
            path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(path)
        new_question = data_manager.add_new_entry(data_manager.QUESTION_FILE_PATH, data_manager.QUESTION_HEADER,
                                                  entry_to_add=request.form, upload_path=path)
        return redirect('/question/'+str(new_question['id']))
    return render_template('add_question.html', question=data_manager.QUESTION_HEADER)


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def route_edit_question(question_id):
    question = data_manager.get_entry_by_id(question_id, data_manager.QUESTION_FILE_PATH,
                                            data_manager.QUESTION_HEADER)
    if request.method == 'GET':
        return render_template('edit_question.html', question_headers=data_manager.QUESTION_HEADER, question=question)
    if request.method == 'POST':
        data_manager.update_entry(data_manager.QUESTION_FILE_PATH, data_manager.QUESTION_HEADER,
                                  entry_to_update=request.form)
        return redirect('/question/' + question_id)


@app.route("/answer/<answer_id>/<vote>", methods=["GET"])
@app.route("/question/<question_id>/<vote>'", methods=["GET", "POST"])
def add_vote(vote, answer_id=None, question_id=None):
    if question_id:
        data_manager.vote_on_entry(data_manager.QUESTION_FILE_PATH, data_manager.QUESTION_HEADER,
                                   vote=vote, entry_id=question_id)
        return redirect(request.form["original_url"])
    elif answer_id:
        data_manager.vote_on_entry(data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER,
                                   vote=vote, entry_id=answer_id)
        answer = data_manager.get_entry_by_id(answer_id,
                                              data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER)
        print("vote on answer in progress")
        return redirect("/question/"+answer["question_id"])


@app.route('/question/<question_id>/new-comment', methods=['POST'])
def route_add_comment(question_id):
        if request.method == "POST":
            data_manager.add_new_record('comment', request.form)
            return redirect('/question/<question_id>')
        return render_template('add_comment.html', question_id=question_id)


@app.route('/question/<question_id>/new-comment', methods=['POST'])
def route_add_comment_to_answer(question_id, answer_id):
    if request.method == "POST":
        question_id = request.form.get("question_id")
        answer_id = request.form.get("answer_id")
        message = request.form.get("message")
        edited_count = request.form.get('edited_count')
        data_manager.add_new_comment_to_answer(
            question_id, answer_id, message, edited_count)
        return redirect('/question/<question_id>')
    return render_template('add_comment_to_answer.html')


if __name__ == "__main__":
    app.run(debug=True)
