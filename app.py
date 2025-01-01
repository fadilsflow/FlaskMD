from flask import Flask, render_template
import markdown
import os
import yaml

app = Flask(__name__)

def get_posts():
    posts = []
    for filename in os.listdir('posts'):
        if filename.endswith('.md'):
            with open(os.path.join('posts', filename), 'r') as file:
                content = file.read()
                try:
                    _, yaml_str, content = content.split('---', 2)
                    metadata = yaml.safe_load(yaml_str)
                    posts.append({**metadata, 'filename': filename})
                except Exception as e:
                    print(f'Error parsing {filename}: {e}')
    
    return sorted(posts, key=lambda x: x['date'], reverse=True)[:10]

def get_post_content(filename):
    with open(os.path.join('posts', filename), 'r') as file:
        _, yaml_str, content = file.read().split('---', 2)
        return markdown.markdown(content.strip()), yaml.safe_load(yaml_str)

@app.route('/')
def index():
    return render_template('index.html', posts=get_posts())

@app.route('/post/<filename>')
def post(filename):
    content, metadata = get_post_content(filename)
    return render_template('post.html', content=content, post=metadata)

if __name__ == '__main__':
    app.run(debug=True)