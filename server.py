import requests
import os
import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, and_
from flask_ckeditor import CKEditorField, CKEditor
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField, DateField
from wtforms.validators import InputRequired, DataRequired
from flask_wtf.file import FileRequired, FileField
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
    body = db.Column(db.Text)
    captions = db.Column(db.Text)


# Create Post Form
class PostForm(FlaskForm):
    submit = SubmitField("Create Post", render_kw={"style": "margin-left:45%"})
    title = StringField(
        "Title", validators=[DataRequired()], render_kw={"style": "width: 100%"}
    )
    subtitle = StringField("Subtitle", render_kw={"style": "width: 100%"})
    body = CKEditorField("Body", validators=[DataRequired()])
    categories = StringField("Categories (separate each category with a doubleslash, e.g. \"Location//Peru//Inca\"")
    photo0 = FileField("Upload Cover Photo")
    photo1 = FileField("Photo #1")
    photo2 = FileField("Photo #2")
    photo3 = FileField("Photo #3")
    photo4 = FileField("Photo #4")



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
    try:
        captions = post.captions.split("//")
    except AttributeError:
        captions = ''
    try:
        categories = post.categories.split("//")
    except AttributeError:
        categories = ''
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
    last_post_id = (db.session.execute(db.select(BlogPost).order_by(BlogPost.id.desc())).scalar()).id
    post_number = last_post_id + 1
    print(last_post_id)
    
    if form.validate_on_submit():
        # Save Photos
        if not os.path.exists(f'static/assets/pics/post{post_number}'):
            os.makedirs(f'static/assets/pics/post{post_number}')
        count = 0
        for field in form:
            if field.type == 'FileField':
                if not field.data:
                    continue
                pic = field.data
                file_filename = f"pic{count}.jpg"
                pic.save(os.path.join(f'static/assets/pics/post{post_number}', file_filename))
                count += 1
        
        # Update Database
        new_post = BlogPost(
            date = datetime.datetime.now().strftime("%d-%m-%Y"),
            title = form.title.data,
            subtitle = form.subtitle.data,
            categories = form.categories.data,
            body = form.body.data,
            # captions = form.captions.data
        )
        db.session.add(new_post)
        db.session.commit()
        
        return redirect("/")
    return render_template("create-post.html", form=form)


@app.route("/edit-post/<id>", methods=["GET", "POST"])
def edit_post(id):
    post = db.session.execute(db.select(BlogPost).where(BlogPost.id == id)).scalar()
    form = PostForm(obj=post)
    form.submit.label.text = 'Save'
    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.categories = form.categories.data
        post.body = form.body.data
        db.session.commit()

        return redirect("/")
    return render_template("edit-post.html", form = form)


@app.route("/delete-post/<id>")
def delete_post(id):
    post = db.session.execute(db.select(BlogPost).where(BlogPost.id == id)).scalar()
    db.session.delete(post)
    db.session.commit()
    return redirect("/")
#---------------------------------STATIC PAGES BELOW----------------------------------------

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


@app.route("/create-db")
def create_db():
    data = requests.get("https://api.npoint.io/3eb913c6b75fee8d844d").json()
    for post in data:
        new_post = BlogPost(
            id = int(post['id']),
            date = post['date'],
            title = post['title'],
            subtitle = post['subtitle'],
            categories = post['categories'],
            body = post['content'],
            captions = post['captions']
        )
        db.session.add(new_post)
        db.session.commit()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
