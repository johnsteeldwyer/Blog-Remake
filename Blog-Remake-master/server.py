import requests
import os
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, and_
from flask_ckeditor import CKEditorField, CKEditor
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField
from wtforms.validators import InputRequired, DataRequired
from flask_wtf.file import FileRequired
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config["SECRET_KEY"] = "dwyeral"

# Connect to Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog-posts.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ckeditor = CKEditor(app)

# Blogpost TABLE Configuration
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(250))
    title = db.Column(db.Text, nullable=False)
    subtitle = db.Column(db.String(250))
    categories = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    captions = db.Column(db.Text, nullable=False)


# Create Post Form
class PostForm(FlaskForm):
    title = StringField(
        "Title", validators=[DataRequired()], render_kw={"style": "width: 100%"}
    )
    subtitle = StringField("Subtitle", render_kw={"style": "width: 100%"})
    body = CKEditorField("Body", validators=[DataRequired()])
    submit = SubmitField("Submit", render_kw={"style": "margin-left:45%"})
    photo = MultipleFileField("Upload Photos")


with app.app_context():
    db.create_all()


@app.route("/<current_page>")
def index(current_page):
    # Get number of blog posts
    count = db.session.query(BlogPost).count()

    # Get 5 blogposts to be displayed
    current_page = int(current_page)
    first_displayed = count - (current_page * 5)
    last_displayed = first_displayed - 5
    posts = db.session.execute(
        db.select(BlogPost)
        .where(and_(BlogPost.id <= first_displayed, BlogPost.id > last_displayed))
        .order_by(BlogPost.id.desc())
    ).scalars()
    return render_template(
        "index.html",
        posts=posts,
        next_page=(current_page + 1),
        prev_page=(current_page - 1),
    )


@app.route("/post/<id>")
def post(id):
    id = int(id)
    post = db.session.execute(db.select(BlogPost).where(BlogPost.id == id)).scalar()
    captions = post.captions.split("//")
    categories = post.categories.split("//")
    return render_template(
        "post.html",
        post=post,
        categories=categories,
        captions=captions,
        captionlen=len(captions),
    )


@app.route("/create-post", methods=["GET", "POST"])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        files_filenames = []
        for file in form.photo.data:
            file_filename = secure_filename(file.filename)
            file.save(os.path.join('instance', file_filename))
            files_filenames.append(file_filename)
        print(files_filenames)
        return redirect("/create-post")
    return render_template("create-post.html", form=form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/gallery")
def gallery():
    captions = requests.get("https://api.npoint.io/622e671822f1910ae3f9").json()
    for i, caption in enumerate(captions):
        if not captions[i]:
            captions[i] = " "
    return render_template("gallery.html", captions=captions, len=len(captions))


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/")
def index_first():
    return redirect("/0")


# @app.route("/create-db")
# def create_db():
#     data = requests.get("https://api.npoint.io/3eb913c6b75fee8d844d").json()
#     for post in data:
#         new_post = BlogPost(
#             id = int(post['id']),
#             date = post['date'],
#             title = post['title'],
#             subtitle = post['subtitle'],
#             categories = post['categories'],
#             content = post['content'],
#             captions = post['captions']
#         )
#         db.session.add(new_post)
#         db.session.commit()
#     return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
