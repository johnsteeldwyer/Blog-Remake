from flask import Flask, render_template
import requests

app = Flask(__name__)

data = requests.get("https://api.npoint.io/3eb913c6b75fee8d844d").json()


@app.route("/")
def index_first():
    page_posts = data[0:5]
    return render_template("index.html", posts=page_posts, next_page=1)


@app.route("/<current_page>")
def index(current_page):
    page = int(current_page)
    last_post = page * 5
    page_posts = data[last_post : (last_post + 5)]

    prev_page = page - 1
    if prev_page < 0:
        prev_page = 0

    next_page = page + 1
    if next_page > (len(data) / 5):
        next_page = page

    return render_template(
        "index.html", posts=page_posts, next_page=next_page, prev_page=prev_page
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/gallary")
def gallary():
    captions = requests.get("https://api.npoint.io/622e671822f1910ae3f9").json()
    for i, caption in enumerate(captions):
        if not captions[i]:
            captions[i] = ' '
    return render_template("gallary.html", captions=captions, len=len(captions))


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/post/<num>")
def post(num):
    num = int(num)
    return render_template('post.html', post=data[num], captionlen = len(data[num]['captions']))

if __name__ == "__main__":
    app.run(debug=True)
