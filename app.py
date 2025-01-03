from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import markdown
import os
import yaml
import datetime
from werkzeug.utils import secure_filename
from PIL import Image
import shutil

app = Flask(__name__)

# MySQL Configuration
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/blog_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
ALLOWED_EXTENSIONS_IMAGE = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS_MD = {'md'}

db = SQLAlchemy(app)

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    filename = db.Column(db.String(200), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<Post {self.title}>'

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_image(file):
    if file and allowed_file(file.filename, ALLOWED_EXTENSIONS_IMAGE):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Optimize and resize image
        with Image.open(filepath) as img:
            img = img.convert('RGB')
            img.thumbnail((800, 800))
            img.save(filepath, 'JPEG', quality=85)
        
        return filename
    return None

def process_markdown_file(file):
    if file and allowed_file(file.filename, ALLOWED_EXTENSIONS_MD):
        content = file.read().decode('utf-8')
        try:
            # Split the content to get front matter and markdown content
            _, yaml_str, content = content.split('---', 2)
            metadata = yaml.safe_load(yaml_str)
            
            # Get title from front matter
            title = metadata.get('title', 'Untitled')
            
            # Create a unique filename
            new_filename = f"{secure_filename(title.lower().replace(' ', '-'))}-{datetime.datetime.now().strftime('%Y%m%d')}.md"
            
            return new_filename, title, content, metadata
        except Exception as e:
            raise ValueError(f"Error processing markdown file: {str(e)}")
    return None, None, None, None

@app.route('/add_blog', methods=['GET', 'POST'])
def add_blog():
    if request.method == 'POST':
        if 'markdown_file' not in request.files or 'cover_image' not in request.files:
            flash('Both markdown file and cover image are required!')
            return redirect(request.url)
        
        md_file = request.files['markdown_file']
        image_file = request.files['cover_image']
        
        if md_file.filename == '' or image_file.filename == '':
            flash('No selected files!')
            return redirect(request.url)
        
        try:
            # Process markdown file
            new_filename, title, content, metadata = process_markdown_file(md_file)
            if not new_filename:
                flash('Invalid markdown file!')
                return redirect(request.url)
            
            # Save cover image
            image_filename = save_image(image_file)
            if not image_filename:
                flash('Invalid image file!')
                return redirect(request.url)
            
            # Update metadata with new image path
            metadata['image'] = f'/static/uploads/{image_filename}'
            
            # Save markdown file with updated metadata
            with open(os.path.join('posts', new_filename), 'w', encoding='utf-8') as f:
                f.write('---\n')
                f.write(yaml.dump(metadata))
                f.write('---\n\n')
                f.write(content)
            
            # Save to database
            new_post = Post(
                title=title,
                image=f'/static/uploads/{image_filename}',
                filename=new_filename
            )
            db.session.add(new_post)
            db.session.commit()
            
            flash('Blog post created successfully!')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Error creating blog post: {str(e)}')
            return redirect(request.url)
    
    return render_template('add_blog.html')

@app.route('/')
def index():
    blog_count = get_blog_count()
    current_year = datetime.datetime.now().year
    return render_template('index.html', posts=get_posts(), blog_count=blog_count, current_year=current_year)

def get_posts():
    return Post.query.order_by(Post.date.desc()).limit(10).all()

def get_post_content(filename):
    post = Post.query.filter_by(filename=filename).first_or_404()
    with open(os.path.join('posts', filename), 'r') as file:
        _, yaml_str, content = file.read().split('---', 2)
    return markdown.markdown(content.strip()), yaml.safe_load(yaml_str)

def get_blog_count():
    return Post.query.count()

@app.route('/post/<filename>')
def post(filename):
    content, metadata = get_post_content(filename)
    return render_template('post.html', content=content, post=metadata)

if __name__ == '__main__':
    with app.app_context():
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs('posts', exist_ok=True)
        db.create_all()
    app.run(debug=True)