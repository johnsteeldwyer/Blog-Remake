from flask_ckeditor import CKEditorField, CKEditor
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField, DateField, EmailField, PasswordField
from wtforms.validators import InputRequired, DataRequired, EqualTo
from flask_wtf.file import FileRequired, FileField


# Create Post Form
class PostForm(FlaskForm):
    submit = SubmitField("Create Post", render_kw={"style": "margin-left:45%", "class":"'form-submit btn btn-primary text-uppercase'"})
    title = StringField(
        "Title", validators=[DataRequired()], render_kw={"style": "width: 100%"}
    )
    subtitle = StringField("Subtitle", render_kw={"style": "width: 100%"})
    body = CKEditorField("Body", validators=[DataRequired()])
    categories = StringField("Categories (separate each category with a doubleslash, e.g. \"Location//Peru//Inca\")",render_kw={"style": "width: 100%"})
    photo0 = FileField("Upload Cover Photo")
    photo1 = FileField("Photo #1")
    photo2 = FileField("Photo #2")
    photo3 = FileField("Photo #3")
    photo4 = FileField("Photo #4")
    
class RegisterForm(FlaskForm):
    username = StringField("Name", validators=[InputRequired()], render_kw={"style": "width: 50%;"})
    email = EmailField("Email", validators=[InputRequired()], render_kw={"style": "width: 50%"})
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')
    submit1 = SubmitField("Register", render_kw={"style": "margin-left:45%", "class":"'form-submit btn btn-primary text-uppercase'"})

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired()], render_kw={"style": "width: 50%"})
    password = PasswordField('Password', [InputRequired()])
    submit2 = SubmitField("Login", render_kw={"style": "margin-left:45%", "class":"'form-submit btn btn-primary text-uppercase'"})

class CommentForm(FlaskForm):
    comment = CKEditorField("Post a Comment", validators=[DataRequired()])
    post_comment = SubmitField("Post Comment", render_kw={"class":"'form-submit btn btn-primary text-uppercase'"})