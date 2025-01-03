from flask import Flask, render_template, request, redirect, url_for, flash
from supabase import create_client, Client
import markdown
import os
import yaml
import datetime
from werkzeug.utils import secure_filename
from PIL import Image
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Supabase configuration
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

ALLOWED_EXTENSIONS_IMAGE = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS_MD = {'md'}

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
            _, yaml_str, content = content.split('---', 2)
            metadata = yaml.safe_load(yaml_str)
            title = metadata.get('title', 'Untitled')
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
            
            # Get current user (important for user_id)
            try:
                user = supabase.auth.get_user()
                user_id = user.user.id if user else None
            except Exception as auth_error:
                print(f"Authentication error: {auth_error}")
                user_id = None
            
            # Save to Supabase
            post_data = {
                'title': title,
                'image': f'/static/uploads/{image_filename}',
                'filename': new_filename,
                'created_at': datetime.datetime.now(datetime.UTC).isoformat(),
                'metadata': json.dumps(metadata)
            }
            
            # Add user_id if available
            if user_id:
                post_data['user_id'] = user_id
            
            # Detailed error logging
            print("Attempting to insert post data:")
            print(json.dumps(post_data, indent=2))
            
            result = supabase.table('posts').insert(post_data).execute()
            
            # More detailed error checking
            print("Supabase insert result:")
            print(result)
            
            if hasattr(result, 'error') and result.error is not None:
                print(f"Supabase Error: {result.error}")
                raise Exception(result.error.message)
                
            flash('Blog post created successfully!')
            return redirect(url_for('index'))
            
        except Exception as e:
            print(f"Full Error creating blog post: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            flash(f'Error creating blog post: {str(e)}')
            return redirect(request.url)
    
    return render_template('add_blog.html')


def get_posts():
    try:
        result = supabase.table('posts').select('*').order('created_at', desc=True).limit(10).execute()
        if hasattr(result, 'error') and result.error is not None:
            print(f"Error fetching posts: {result.error.message}")
            return []
        return result.data
    except Exception as e:
        print(f"Error fetching posts: {str(e)}")
        return []

def get_post_content(filename):
    try:
        result = supabase.table('posts').select('*').eq('filename', filename).limit(1).execute()
        if hasattr(result, 'error') and result.error is not None:
            return None, None
        
        if not result.data:
            return None, None
            
        post = result.data[0]
        
        with open(os.path.join('posts', filename), 'r') as file:
            _, yaml_str, content = file.read().split('---', 2)
        return markdown.markdown(content.strip()), yaml.safe_load(yaml_str)
    except Exception as e:
        print(f"Error fetching post content: {str(e)}")
        return None, None

def get_blog_count():
    try:
        result = supabase.table('posts').select('*', count='exact').execute()
        if hasattr(result, 'error') and result.error is not None:
            return 0
        return result.count
    except Exception as e:
        print(f"Error getting blog count: {str(e)}")
        return 0

@app.route('/')
def index():
    blog_count = get_blog_count()
    current_year = datetime.datetime.now().year
    return render_template('index.html', posts=get_posts(), blog_count=blog_count, current_year=current_year)

@app.route('/post/<filename>')
def post(filename):
    content, metadata = get_post_content(filename)
    if content is None:
        return "Post not found", 404
    return render_template('post.html', content=content, post=metadata)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('posts', exist_ok=True)
    app.run(debug=True)