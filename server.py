from flask import Flask, request, render_template, redirect
import data_manager

app = Flask(__name__, static_folder="/")


@app.route("/")
@app.route("/list")
def main():
    if request.args:
        print("must be sorted by "+request.args["sort_by"])
    questions = data_manager.get_all_entries(data_manager.QUESTION_FILE_PATH, data_manager.QUESTION_HEADER)
    header = data_manager.QUESTION_HEADER
    return render_template("index.html", header=header, questions=questions)


@app.route("/question/<question_id>", methods=['GET', 'POST'])
def route_question(question_id):
    header = data_manager.QUESTION_HEADER
    questions = data_manager.get_all_entries(data_manager.QUESTION_FILE_PATH, header)
    if request.method == "GET":
        for question in questions:
            if question['id'] == question_id:
                print(question)
                return render_template("question.html", header=header, question=question)


@app.route("/answer/<answer_id>/delete")
def route_answer(answer_id=None):
    if answer_id:
        answer = data_manager.get_entry_by_id(answer_id, data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER)
        question_id = answer['question_id']
        data_manager.delete_entry(answer_id, data_manager.ANSWER_FILE_PATH, data_manager.ANSWER_HEADER)
        return redirect("/question/" + question_id)


if __name__ == "__main__":
    app.run(debug=True)
