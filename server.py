import datetime
import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import data_manager
from psycopg2 import sql


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './static/images'


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
    # if request.args.get('order'):
    #     if request.args.get('order').lower() not in ['asc', 'desc']:
    #         return redirect(url_for('catch_hacker'))
    return render_template("index.html", payload=data_manager.get_list_page_data(request.args))


@app.route("/question/<question_id>")
def load_question_page(question_id):
    return render_template("question.html", payload=data_manager.get_question_page_data(question_id, request.args))


@app.route("/<table>/<record_id>/delete")
def delete_record_by_id(table, record_id):
    data_manager.delete_record_by_id(table, record_id)
    if table == 'question':
        return redirect(url_for('load_list_page'))
    return redirect(request.referrer)


@app.route("/vote_on_record", methods=['POST'])
def vote_on_record():
    table = request.form["table"]
    record_id = request.form["record_id"]
    vote = request.form["vote"]
    data_manager.update_vote_number(table, record_id, vote)
    return '', 202


@app.route("/question/<question_id>/new-<record>", methods=['GET', 'POST'])
@app.route("/question/<question_id>/new-<record>", methods=['GET', 'POST'])
@app.route("/add-new-<record>", methods=['GET', 'POST'])
def add_new_record(record, question_id=None, answer_id=None):
    if request.method == 'GET':
        return render_template('add_new_record.html', payload={'record': record})


# need refactor from down there


# @app.route("/add-question", methods=['GET', 'POST'])
# def add_new_question():
#     if request.method == 'POST':
#         print('question' in request.referrer)
#
#         if request.files.get('image').filename == '':
#             path = 'no_image_found.png'
#         else:
#             image = request.files['image']
#             path = image.filename
#             image.save(path)
#         form = dict(request.form)
#         form.update({'image': path})
#         print(form)
#         data_manager.add_new_record('question', form)
#         question_id = str(data_manager.get_table('question', columns=['id'],
#                                                  sort_by='id', order='desc')[0].get('id'))
#         return redirect('/question/' + question_id)
#     return render_template('add_new_record.html', payload={'record': 'question'})


@app.route("/search")
def search():
    column_names = ["vote_number", "a_vote_number", "submission_time", "a_submission_time"]
    sort_by = request.args['sort_by'] if request.args.get('sort_by') in column_names else None
    order = request.args['order'] if sort_by else None
    if len(request.args['q'].strip()) > 0:
        search_result = data_manager.get_records_by_search(word=request.args['q'],
                                                           sort_by=sort_by,
                                                           order=order)
    else:
        return redirect(url_for('load_main'))
    if order not in ['asc', 'desc', None]: return redirect(url_for('catch_hacker'))
    return render_template("search.html", cards=search_result, columns=column_names)


# @app.route("/question/<question_id>/delete")
# def route_delete_question(question_id):
#     answers = data_manager.get_table('answer', columns=['id'],
#                                      selector='question_id',
#                                      selected_value=question_id)
#     for cell in answers:
#         data_manager.delete_record_by_id('comment', selector='answer_id', selected_value=cell.get('id'))
#     data_manager.delete_record_by_id('answer', 'question_id', question_id)
#     data_manager.delete_record_by_id('question_tag', 'question_id', question_id)
#     data_manager.delete_record_by_id('comment', 'question_id', question_id)
#     data_manager.delete_record_by_id('question', 'id', question_id)
#     return redirect("/list")


# @app.route("/question/<question_id>/new-answer", methods=['GET', 'POST'])
# def route_add_answer(question_id):
#     if request.method == 'GET':
#         return render_template("answer.html", question_id=question_id)
#     if not request.files.get('image'):
#         path = './static/images/no_image_found.png'
#     else:
#         image = request.files['image']
#         path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
#         image.save(path)
#     form = dict(request.form)
#     form['submission_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     form['image'] = path
#     data_manager.add_new_record('answer', form)
#     return redirect("/question/" + question_id)


# @app.route("/answer/<answer_id>/delete")
# def route_delete_answer(answer_id):
#     question_id = data_manager.get_table('answer', columns=['question_id'], selector='id',
#                                          selected_value=answer_id)[0]
#     data_manager.delete_record_by_id('comment', 'answer_id', answer_id)
#     data_manager.delete_record_by_id('answer', 'id', answer_id)
#     return redirect("/question/" + str(question_id.get('question_id')))


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
def route_add_tag(question_id):
    if request.method == 'POST':
        data_manager.add_new_record('tag', request.form)
        tag_id = data_manager.get_table('tag', columns=['id'])[-1:]
        data_manager.tag_to_question_tag(question_id, tag_id)
        return redirect(url_for('route_add_tag', question_id=question_id))
    if request.method == 'GET':
        data_manager.add_existing_tag_to_question_tag(question_id, request.args.values())
    tags = data_manager.get_table(table='tag')
    return render_template('add_tags.html', question_id=question_id, tags=tags)


# @app.route('/question/<question_id>/delete-tag', methods=['GET'])
# def delete_tag_from_question(question_id):
#     data_manager.delete_record_by_id('question_tag', selector='tag_id', selected_value=request.args.get('tag_id'))
#     return redirect(url_for("route_question", question_id=question_id))


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def route_edit_question(question_id):
    question = data_manager.get_table('question', selector='id', selected_value=question_id)[0]
    if request.method == 'GET':
        return render_template('edit_question.html', question_headers=data_manager.get_column_names('question'),
                               question=question)
    if request.method == 'POST':
        data_manager.update_question(request.form)
        return redirect('/question/' + question_id)


# @app.route("/answer/<answer_id>/<vote>", methods=["GET"])
# @app.route("/question/<question_id>/<vote>'", methods=["GET", "POST"])
# def add_vote(vote, answer_id=None, question_id=None):
#     if question_id:
#         data_manager.update_vote_number('question', question_id, vote)
#         return redirect('question/' + question_id)
#     elif answer_id:
#         data_manager.update_vote_number('answer', answer_id, vote)
#         answer = data_manager.get_table('answer', selector='id', selected_value=answer_id)[0]
#         return redirect('/question/' + str(answer.get('question_id')))


# @app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
# def route_add_comment_to_question(question_id):
#     if request.method == "POST":
#         form = dict(request.form)
#         form['submission_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         data_manager.add_new_record('comment', form)
#         return redirect(url_for('route_question', question_id=question_id))
#     return render_template('add_comment.html', question_id=question_id)


@app.route('/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
def route_add_comment_to_answer(answer_id):
    question_id = data_manager.get_table('answer', selector='id', selected_value=answer_id)[0].get('question_id')
    if request.method == "POST":
        form = dict(request.form)
        form['submission_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_manager.add_new_record('comment', form)
        return redirect(url_for('route_question', question_id=question_id))
    return render_template('add_comment_to_answer.html', answer_id=answer_id)


@app.route('/comment/<comment_id>/edit', methods=['GET', 'POST'])
def route_edit_comment(comment_id):
    comment = data_manager.get_table('comment', selector="id", selected_value=comment_id)[0]
    if request.method == 'GET':
        return render_template('edit_comment.html', comment=comment)
    data_manager.update_message('comment', comment_id, request.form.get('message'),
                                request.form.get('edited_count'))
    return redirect('/question/' + str(comment.get('question_id')))


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def route_edit_answer(answer_id):
    answer = data_manager.get_table('answer', selector="id", selected_value=answer_id)[0]
    if request.method == 'GET':
        return render_template('edit_answer.html', answer=answer)
    data_manager.update_message('answer', answer_id, request.form.get('message'))
    return redirect('/question/' + str(answer.get('question_id')))


# @app.route("/comments/<comment_id>/delete", methods=['POST', 'GET', 'DELETE'])
# def delete_comment(comment_id):
#     question_id = data_manager.get_table('comment', columns=['question_id'], selector='id', selected_value=comment_id)
#     data_manager.delete_record_by_id('comment', selector='id', selected_value=comment_id)
#     for cell in question_id:
#         return redirect(url_for("route_question", question_id=cell.get('question_id')))


if __name__ == "__main__":
    app.run(debug=True)
