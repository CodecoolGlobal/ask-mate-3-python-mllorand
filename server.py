from flask import Flask, request, render_template, redirect
import data_manager

app = Flask(__name__, static_folder="/")


@app.route("/")
@app.route("/list")
def main():
    header = data_manager.QUESTION_HEADER
    if request.args:
        questions = data_manager.get_all_entries(data_manager.QUESTION_FILE_PATH,
                                                 data_manager.QUESTION_HEADER,
                                                 request.args["sort_by"],
                                                 order=True if request.args["order"] == "desc" else False)
    else:
        questions = data_manager.get_all_entries(data_manager.QUESTION_FILE_PATH, data_manager.QUESTION_HEADER)
    return render_template("index.html", header=header, questions=questions)


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


@app.route("/question/<question_id>/delete")
def route_delete_question(question_id):
    question = data_manager.get_entry_by_id(question_id, data_manager.QUESTION_FILE_PATH, data_manager.QUESTION_HEADER)
    data_manager.delete_entry(data_manager.QUESTION_FILE_PATH, data_manager.QUESTION_HEADER, question)
    answers_to_remove = [answer for answer in
                         data_manager.get_all_entries_with_unix_timestamp(data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER)
                         if answer['question_id'] == question_id]
    for answer in answers_to_remove:
        data_manager.delete_entry(data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER, answer)
    return redirect("/list")


@app.route("/question/<question_id>/new-answer", methods=['GET', 'POST'])
def route_add_answer(question_id):
    if request.method == 'GET':
        return render_template("answer.html", question_id=question_id)
    new_answer = request.form
    data_manager.add_new_entry(data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER,
                               entry_to_add=new_answer)
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
        new_question = request.form
        new_question = data_manager.add_new_entry(data_manager.QUESTION_FILE_PATH, data_manager.QUESTION_HEADER,
                                                  entry_to_add=new_question)
        return redirect('/question/'+new_question['id'])
    return render_template('add_question.html', question=data_manager.QUESTION_HEADER)


if __name__ == "__main__":
    app.run(debug=True)
