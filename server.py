from flask import Flask, request, render_template
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


@app.route("/question/<question_id>", methods=['GET', 'POST'])
def route_question(question_id):
    database = data_manager.read_csv()
    dict_for_show = {}
    if request.method == "GET":
        for line in database:
            if line['id'] == question_id:
                print(line)
                dict_for_show = line
    header = data_manager.QUESTION_HEADER
    return render_template("question.html", header=header, dict_for_show=dict_for_show)


if __name__ == "__main__":
    app.run(debug=True)
