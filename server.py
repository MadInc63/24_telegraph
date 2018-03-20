from flask import Flask, render_template, request, make_response
from flask import redirect, url_for
from datetime import datetime
from uuid import uuid4
import re


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def form():
    cookie = request.cookies.get('uuid')
    if request.method == 'POST':
        if cookie is None:
            cookie = str(uuid4())
        title_string = re.sub(' +', '-', request.form['header'])
        date_string = datetime.strftime(datetime.now(), "%m-%d")
        article_file_name = title_string + '-' + date_string
        with open(
            'static/articles/{}'.format(article_file_name),
            'w',
            encoding='utf8'
        ) as article:
            article.write(cookie + '\n')
            article.write(request.form['header'] + '\n')
            article.write(request.form['signature'] + '\n')
            body = request.form['body'].replace('\r\n', '\n')
            article.write(body)
        response_with_cookie = make_response(
            redirect(request.url + article_file_name, code=302)
        )
        response_with_cookie.set_cookie('uuid', cookie)
        return response_with_cookie
    else:
        return render_template('form.html', cookie=cookie)


@app.route('/<article_header>', methods=['GET', 'POST'])
def show_article(article_header):
    button = True
    cookie = request.cookies.get('uuid')
    path = 'static/articles/{}'.format(article_header)
    if request.method == 'POST':
        with open(path, 'w', encoding='utf8') as article:
            article.write(cookie + '\n')
            article.write(request.form['header'] + '\n')
            article.write(request.form['signature'] + '\n')
            body = request.form['body'].replace('\r\n', '\n')
            article.write(body)
    try:
        with open(path, 'r', encoding='utf8') as article:
            article_cookie = article.readline()
            article_header = article.readline()
            article_signature = article.readline()
            article_body = article.read()
    except IOError:
        return page_not_found()
    if cookie != article_cookie.strip():
        button = None
    return render_template(
        'form.html',
        header=article_header,
        signature=article_signature,
        body=article_body,
        cookie=cookie,
        button=button
    )


@app.errorhandler(404)
def page_not_found():
    return redirect(url_for('form'))


if __name__ == "__main__":
    app.run()
