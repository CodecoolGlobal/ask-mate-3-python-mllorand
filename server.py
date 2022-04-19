from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import data_manager


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
    if request.args.get('order'):
        if request.args.get('order').lower() not in ['asc', 'desc']:
            return redirect(url_for('catch_hacker'))
    return render_template("index.html", payload=data_manager.get_list_page_data(request.args))


@app.route("/question/<question_id>")
def load_question_page(question_id):
    return render_template("question.html", payload=data_manager.get_question_page_data(question_id, request.args))


@app.route("/<table>/<record_id>/delete")
@app.route("/question/<question_id>/<table>/<record_id>/delete")
def delete_record_by_id(table, record_id, question_id=None):
    if table != 'question_tag':
        data_manager.delete_record_by_identifier(table, record_id, question_id, 'id')
    else:
        data_manager.delete_record_by_identifier(table, record_id, question_id, 'tag_id')
    if table == 'question':
        return redirect(url_for('load_list_page'))
    return redirect(request.referrer)


@app.route("/vote_on_record", methods=['POST'])
def vote_on_record():
    table = request.form["table"]
    data_manager.update_record(table, request.form)
    return '', 202


@app.route("/question/<question_id>/new-<record>/", methods=['GET', 'POST'])
@app.route("/answer/<answer_id>/new-<record>", methods=['GET', 'POST'])
@app.route("/add-<record>", methods=['GET', 'POST'])
def add_new_record(record, question_id=None, answer_id=None):
    if request.method == 'POST':
        data_manager.add_new_record(record, question_id, answer_id, request)
        if record != 'question' and request.form.get('redirect'):
            return redirect(request.form['redirect'])
        question_id = data_manager.get_fields_from_table_by_value('id', 'question', ordered=True)['id']
        return redirect(url_for('load_question_page', question_id=question_id))
    return render_template('add_new_record.html', payload={'record': record,
                                                           'question_id': question_id,
                                                           'answer_id': answer_id,
                                                           'redirect': request.referrer})


@app.route('/<record_type>/<record_id>/edit', methods=['GET', 'POST'])
def edit_record(record_type, record_id):
    record = data_manager.get_fields_from_table_by_value('', record_type, 'id', record_id)
    if request.method == 'POST':
        print(request.form)
        data_manager.update_record(record_type, request.form)
        return redirect(request.form['redirect'])
    return render_template('edit_record.html', payload={'record_type': record_type,
                                                        'record': record,
                                                        'redirect': request.referrer})


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
def add_tag(question_id):
    tags = data_manager.get_tag_table('tag', )
    if request.method == 'POST':
        data_manager.add_tag_to_question(question_id, form=dict(request.form))
        return redirect(url_for('load_question_page', question_id=question_id))
    if request.method == 'GET':
        return render_template('add_tags.html', question_id=question_id, tags=tags)


# need refactor from down there


@app.route("/search")
def search():
    column_names = ["vote_number", "a_vote_number", "submission_time", "a_submission_time"]
    sort_by = request.args['sort_by'] if request.args.get('sort_by') in column_names else None
    order = request.args['order'] if sort_by else None
    if len(request.args['q'].strip()) > 0:
        search_result = data_manager.get_records_by_search(searched_word=request.args['q'],
                                                           sort_by=sort_by,
                                                           order=order)
    else:
        return redirect(url_for('load_main'))
    if order not in ['asc', 'desc', None]:
        return redirect(url_for('catch_hacker'))
    return render_template("search.html", cards=search_result, columns=column_names)


if __name__ == "__main__":
    app.run(debug=True)
