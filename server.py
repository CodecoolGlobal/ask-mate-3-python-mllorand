from flask import Flask, request, render_template
import util

app = Flask(__name__)


@app.route("/")
def main():
    questions = util.get_all_question()
    header = util.QUESTION_HEADER
    return render_template("index.html", header=header, questions=questions)


if __name__ == "__main__":
    app.run()
