from flask import Flask, request, render_template, redirect
import data_manager

app = Flask(__name__, static_folder="/")


@app.route("/")
@app.route("/list")
def main():
    if request.args:
        print("must be sorted by "+request.args["sort_by"])
    questions = data_manager.get_all_questions()
    header = data_manager.QUESTION_HEADER
    return render_template("index.html", header=header, questions=questions)


@app.route("/answer/<answer_id>/delete")
def route_answer(answer_id=None):
    if answer_id:
        return redirect(("question/"))




if __name__ == "__main__":
    app.run(debug=True)
