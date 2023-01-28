import requests
import os
import datetime
from dotenv import load_dotenv
from forms import PostForm, RegisterForm, LoginForm, CommentForm
from functools import wraps
from flask import Flask, render_template, redirect, flash, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import and_
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_ckeditor import CKEditor
load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
login_manager = LoginManager()
login_manager.init_app(app)

# Connect to Database
print(os.environ.get("POSTGRES_DATABASE_URL", "sqlite:///blog.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("POSTGRES_DATABASE_URL")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ckeditor = CKEditor(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(401)
        return f(*args, **kwargs)
    return decorated_function

# TABLE Configurations
class BlogPost(db.Model):
    __tablename__ = 'blogpost'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(250))
    title = db.Column(db.Text, nullable=False)
    subtitle = db.Column(db.String(250))
    categories = db.Column(db.Text)
    body = db.Column(db.Text)
    captions = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", back_populates="posts")
    comments = db.relationship("Comment", back_populates="post")


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(500), unique=True)
    email = db.Column(db.String(500), unique=True)
    password = db.Column(db.String(500))
    posts = db.relationship("BlogPost", back_populates="author")
    comments = db.relationship("Comment", back_populates="author")
    
    
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text)
    date = db.Column(db.String(250))
    post_id = db.Column(db.Integer, db.ForeignKey("blogpost.id"))
    post = db.relationship("BlogPost", back_populates="comments")
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", back_populates="comments")

    
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


@app.route("/post/<id>", methods=["GET", "POST"])
def post(id):
    id = int(id)
    form = CommentForm()
    post = db.session.execute(db.select(BlogPost).where(BlogPost.id == id)).scalar()
    comments = db.session.execute(db.select(Comment).where(Comment.post_id == id).order_by(Comment.id.desc())).scalars()
    if form.validate_on_submit():
        new_comment = Comment(
            comment = form.comment.data,
            post_id = id,
            author_id = current_user.id,
            date = datetime.datetime.now().strftime("%d-%m-%Y")
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(f"/post/{id}")
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
        form=form,
        comments = comments
    )


@app.route("/create-post", methods=["GET", "POST"])
@admin_only
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
            parent_id = current_user.id
            # captions = form.captions.data
        )
        db.session.add(new_post)
        db.session.commit()
        
        return redirect("/")
    return render_template("create-post.html", form=form)


@app.route("/edit-post/<id>", methods=["GET", "POST"])
@admin_only
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


@app.route("/delete/<type>/<id>")
@admin_only
def delete(type, id):
    if type == 'post':
        post = db.session.execute(db.select(BlogPost).where(BlogPost.id == id)).scalar()
        db.session.delete(post)
        db.session.commit()

    elif type == 'comment':
        comment = db.session.execute(db.select(Comment).where(Comment.id == id)).scalar()
        comment_id = comment.post.id
        db.session.delete(comment)
        db.session.commit()
        return redirect(f"/post/{comment_id}")
    return redirect("/")



@app.route("/register-login", methods=["GET", "POST"])
def register_login():
    form1 = RegisterForm()
    form2 = LoginForm()
    if form1.submit1.data and form1.validate():
        user = User(
            email = form1.email.data,
            password = generate_password_hash(form1.password.data, method='pbkdf2:sha256', salt_length=24),
            username = form1.username.data
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect("/")
    if form2.submit2.data and form2.validate():
        user = db.session.execute(db.select(User).where(User.email == form2.email.data)).scalar()
        if user == None or not check_password_hash(user.password, form2.password.data):
            flash('Incorrect email/password. Please contact the Administrator to reset password')
        else:
            login_user(user)
            return redirect("/")
    return render_template("register-login.html", form1 = form1, form2=form2)
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


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")
    
@app.route("/create-db")
def create_db():
    data = requests.get("https://api.npoint.io/3eb913c6b75fee8d844d").json()
    admin = User(
            id = 1,
            username = "Al Dwyer",
            email = "adwyer@gmail.com",
            password = generate_password_hash("hello", method='pbkdf2:sha256', salt_length=24)
    )
    db.session.add(admin)
    db.session.commit()

    for post in data:
        new_post = BlogPost(
            id = int(post['id']),
            date = post['date'],
            title = post['title'],
            subtitle = post['subtitle'],
            categories = post['categories'],
            body = post['content'],
            captions = post['captions'],
            author_id = 1
        )
        db.session.add(new_post)
        db.session.commit()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
