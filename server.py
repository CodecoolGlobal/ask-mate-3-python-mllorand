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


@app.route("/answer/<answer_id>/delete")
def route_answer(answer_id=None):
    if answer_id:
        answer = data_manager.get_entry_by_id(answer_id, data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER)
        question_id = answer['question_id']
        data_manager.delete_entry(data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER, answer)
        return redirect("/question/" + question_id)


if __name__ == "__main__":
    app.run(debug=True)
