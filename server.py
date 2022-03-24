import os
from flask import Flask, request, render_template, redirect
import data_manager


app = Flask(__name__, static_folder="/")
app.config['UPLOAD_FOLDER'] = './uploaded_files'


@app.route("/")
@app.route("/list")
def main():
    if request.args:
        questions = data_manager.get_all_entries(data_manager.QUESTION_FILE_PATH,
                                                 data_manager.QUESTION_HEADER,
                                                 request.args["sort_by"],
                                                 order=True if request.args["order"] == "desc" else False)
    else:
        questions = data_manager.get_all_entries(data_manager.QUESTION_FILE_PATH, data_manager.QUESTION_HEADER)
    return render_template("index.html", header=data_manager.QUESTION_HEADER,
                           questions=questions)


@app.route("/question/<question_id>", methods=['GET', 'POST'])
def route_question(question_id):
    question_headers = data_manager.QUESTION_HEADER
    questions = data_manager.get_all_entries(data_manager.QUESTION_FILE_PATH, question_headers)
    if request.method == "GET":
        answer_headers = data_manager.ANSWER_HEADER
        answers_list = data_manager.get_all_entries(data_manager.ANSWER_FILE_PATH, answer_headers)
        answers = [answer for answer in answers_list if answer['question_id'] == question_id]
        for question in questions:
            if question['id'] == question_id:
                return render_template("question.html", question_headers=question_headers,
                                       answer_headers=answer_headers,
                                       question=question, question_id=question_id, answers=answers)


@app.route("/question/<question_id>/new-answer", methods=['GET', 'POST'])
def route_add_answer(question_id):
    if request.method == 'GET':
        return render_template("answer.html", question_id=question_id)
    new_answer = request.form
    if request.files.get('image').content_type == 'application/octet-stream':
        path = './uploaded_files/no_image_found.png'
    else:
        image = request.files['image']
        path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(path)
    data_manager.add_new_entry(data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER,
                               entry_to_add=new_answer, upload_path=path)
    return redirect("/question/" + question_id)


@app.route("/answer/<answer_id>/delete")
def route_answer(answer_id):
    answer = data_manager.get_entry_by_id(answer_id, data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER)
    question_id = answer['question_id']
    data_manager.delete_entry(data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER, answer)
    return redirect("/question/" + question_id)


@app.route('/add-question', methods=['GET', 'POST'])
def route_add_question():
    if request.method == 'POST':
        new_question = request.form
        if request.files.get('image').content_type == 'application/octet-stream':
            path = './uploaded_files/no_image_found.png'
        else:
            image = request.files['image']
            path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(path)
        new_question = data_manager.add_new_entry(data_manager.QUESTION_FILE_PATH, data_manager.QUESTION_HEADER,
                                                  entry_to_add=new_question, upload_path=path)
        return redirect('/question/'+new_question['id'])
    return render_template('add_question.html', question=data_manager.QUESTION_HEADER)


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


if __name__ == "__main__":
    app.run(debug=True)
