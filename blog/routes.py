from flask import render_template, request, redirect, url_for, flash
from .models import Post
from config import Config

def init_routes(app):
    @app.route("/")
    def index():
        posts = Post.get_posts()
        return render_template("home.html", posts=posts, current_page="home")

    @app.route("/add_blog", methods=["GET", "POST"])
    def add_blog():
        if request.method == "POST":
            md_file = request.files["markdown_file"]

            if Post.add_post(md_file):
                flash("Post berhasil ditambahkan!")
                return redirect(url_for("index"))
            else:
                flash("Gagal menambahkan post")

        return render_template("add_blog.html")

    @app.route("/post/<filename>")
    def post(filename):
        post_data = Post.get_post_by_filename(filename)

        if not post_data:
            flash("Post tidak ditemukan")
            return redirect(url_for("index"))

        return render_template("post.html", post=post_data, content=post_data["markdown_content"])

    @app.route("/manage_blogs", methods=["GET", "POST"])
    def manage_blogs():
        if request.method == "POST":
            secret_key = request.form.get("secret_key")
            if secret_key == Config.SECRET_KEY:
                posts = Post.get_all_posts()
                return render_template("manage_blogs.html", posts=posts)
            else:
                flash("Wrong secret key🤭!")

        return render_template("enter_secret_key.html")

    @app.route("/edit_blog/<int:post_id>", methods=["GET", "POST"])
    def edit_blog(post_id):
        post = Post.get_post_by_id(post_id)

        if not post:
            flash("Post tidak ditemukan")
            return redirect(url_for("manage_blogs"))

        if request.method == "POST":
            md_file = request.files.get("markdown_file")
            image_file = request.files.get("cover_image")

            md_file = md_file if md_file and md_file.filename else None
            image_file = image_file if image_file and image_file.filename else None

            if Post.update_post(post_id, md_file, image_file):
                flash("Post berhasil diupdate!")
                return redirect(url_for("manage_blogs"))
            else:
                flash("Gagal mengupdate post")

        return render_template("edit_blog.html", post=post)

    @app.route("/delete_blog/<int:post_id>", methods=["POST"])
    def delete_blog(post_id):
        if Post.delete_post(post_id):
            flash("Post berhasil dihapus!")
        else:
            flash("Gagal menghapus post")

        return redirect(url_for("manage_blogs"))

    @app.route("/blog")
    def blog():
        posts = Post.get_all_posts()
        return render_template("index.html", posts=posts, current_page="index")

    @app.route("/blog/tag/<tag>")
    def blog_by_tag(tag):
        posts = Post.get_posts_by_tag(tag)
        return render_template("index.html", posts=posts, tag=tag)

    @app.route("/about")
    def about():
        return render_template("about.html", current_page="about")

    @app.route("/contact")
    def contact():
        return render_template("contact.html", current_page="contact")

    return app
