from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import markdown
import os
import yaml
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['POSTS_FOLDER'] = 'posts'

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        port=8889,
        user='root',
        password='root',
        db='blog_app',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def get_posts(limit=10):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, title, date, author, readingtime, 
                       tags, image, filename 
                FROM posts 
                ORDER BY date DESC 
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
    finally:
        connection.close()

def save_uploaded_file(file, folder):
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(folder, filename)
        file.save(filepath)
        return filename
    return None

@app.route('/')
def index():
    posts = get_posts() 
    return render_template('index.html', posts=posts, )

@app.route('/add_blog', methods=['GET', 'POST'])
def add_blog():
    if request.method == 'POST':
       
        md_file = request.files['markdown_file']

        md_filename = save_uploaded_file(md_file, app.config['POSTS_FOLDER'])
        
        # Baca konten markdown
        with open(os.path.join(app.config['POSTS_FOLDER'], md_filename), 'r') as f:
            content = f.read()
            parts = content.split('---', 2)
            metadata = yaml.safe_load(parts[1])
        
        # Simpan ke database
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO posts 
                    (title, date, author, readingtime, tags, image, filename) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""", 
                    (
                        metadata.get('title'),
                        metadata.get('date'),
                        metadata.get('author', 'Anonymous'),
                        metadata.get('readingtime', ''),
                        ','.join(metadata.get('tags', [])) if metadata.get('tags') else '',
                        metadata.get('image', ''),
                        md_filename
                    )
                )
                connection.commit()
            flash('Post berhasil ditambahkan!')
            return redirect(url_for('index'))
        except pymysql.Error as e:
            flash(f'Gagal menambahkan post: {str(e)}')
        finally:
            connection.close()
    
    return render_template('add_blog.html')
@app.route('/post/<filename>')
def post(filename):
    connection = get_db_connection() 
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM posts WHERE filename = %s", (filename,))
            post_data = cursor.fetchone()
        
        if not post_data:
            flash('Post tidak ditemukan')
            return redirect(url_for('index'))
        
        # Baca konten markdown
        with open(os.path.join(app.config['POSTS_FOLDER'], filename), 'r') as f:
            content = f.read()
            parts = content.split('---', 2)
            markdown_content = markdown.markdown(parts[2].strip())
        
        return render_template('post.html', 
                               post=post_data, 
                               content=markdown_content
                               )
    except FileNotFoundError:
        flash('File post tidak ditemukan')
        return redirect(url_for('index'))
    finally:
        connection.close()

if __name__ == '__main__':
    # Pastikan folder ada
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['POSTS_FOLDER'], exist_ok=True)
    
    app.run(debug=True)