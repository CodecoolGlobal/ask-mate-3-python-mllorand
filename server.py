from flask import Flask, request, render_template
import data_manager

app = Flask(__name__, static_folder="/home/fekete/codecool/web_projects/ask-mate-1-python-horvatht9411/images")


@app.route("/")
@app.route("/list")
def main():
    questions = data_manager.get_all_questions()
    header = data_manager.QUESTION_HEADER
    return render_template("index.html", header=header, questions=questions)


if __name__ == "__main__":
    app.run()
