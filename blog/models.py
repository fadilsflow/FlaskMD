import pymysql
from flask import current_app
import yaml
import os
from werkzeug.utils import secure_filename
import markdown2

class Database:
    @staticmethod
    def get_connection():
        try:
            connection = pymysql.connect(
                host=current_app.config["DB_HOST"],
                port=current_app.config["DB_PORT"],
                user=current_app.config["DB_USER"],
                password=current_app.config["DB_PASSWORD"],
                database=current_app.config["DB_NAME"],
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
            return connection
        except pymysql.Error as e:
            print(f"Database connection error: {e}")
            raise

class Post:
    @staticmethod
    def get_posts(limit=6):
        connection = Database.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, title, date, author, readingtime, 
                           tags, image, filename 
                    FROM posts 
                    ORDER BY date DESC 
                    LIMIT %s
                    """,
                    (limit,),
                )
                return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error fetching posts: {e}")
            return []
        finally:
            connection.close()

    @staticmethod
    def save_uploaded_file(file, folder):
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(folder, filename)
            file.save(filepath)
            return filename
        return None

    @staticmethod
    def add_post(md_file):
        try:
            md_filename = Post.save_uploaded_file(md_file, current_app.config["POSTS_FOLDER"])

            with open(os.path.join(current_app.config["POSTS_FOLDER"], md_filename), "r") as f:
                content = f.read()
                parts = content.split("---", 2)

                if len(parts) < 3:
                    print("Invalid markdown format")
                    return False

                metadata = yaml.safe_load(parts[1])

            required_fields = ["title", "date", "author"]
            for field in required_fields:
                if field not in metadata:
                    print(f"Missing required field: {field}")
                    return False

            connection = Database.get_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO posts 
                        (title, date, author, readingtime, tags, image, filename) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (
                            metadata.get("title"),
                            metadata.get("date"),
                            metadata.get("author", "Anonymous"),
                            metadata.get("readingtime", ""),
                            ",".join(metadata.get("tags", [])) if metadata.get("tags") else "",
                            metadata.get("image", ""),
                            md_filename,
                        ),
                    )
                    connection.commit()
                return True
            except pymysql.Error as e:
                print(f"Error adding post: {e}")
                return False
            finally:
                connection.close()

        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    @staticmethod
    def get_post_by_filename(filename):
        connection = Database.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM posts WHERE filename = %s", (filename,))
                post_data = cursor.fetchone()

            if not post_data:
                return None

            with open(os.path.join(current_app.config["POSTS_FOLDER"], filename), "r") as f:
                content = f.read()
                parts = content.split("---", 2)
                post_data["markdown_content"] = markdown2.markdown(
                    parts[2].strip(), extras=["fenced-code-blocks", "tables"]
                )

            return post_data
        except FileNotFoundError:
            return None
        finally:
            connection.close()

    @staticmethod
    def get_all_posts():
        connection = Database.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM posts ORDER BY date DESC")
                return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error fetching all posts: {e}")
            return []
        finally:
            connection.close()

    @staticmethod
    def update_post(post_id, md_file=None, image_file=None):
        if md_file:
            md_filename = Post.save_uploaded_file(md_file, current_app.config["POSTS_FOLDER"])

            with open(os.path.join(current_app.config["POSTS_FOLDER"], md_filename), "r") as f:
                content = f.read()
                parts = content.split("---", 2)
                metadata = yaml.safe_load(parts[1])

        connection = Database.get_connection()
        try:
            with connection.cursor() as cursor:
                if md_file:
                    cursor.execute(
                        """UPDATE posts 
                        SET title=%s, date=%s, author=%s, readingtime=%s, 
                        tags=%s, filename=%s 
                        WHERE id=%s""",
                        (
                            metadata.get("title"),
                            metadata.get("date"),
                            metadata.get("author", "Anonymous"),
                            metadata.get("readingtime", ""),
                            ",".join(metadata.get("tags", [])) if metadata.get("tags") else "",
                            md_filename,
                            post_id,
                        ),
                    )

                if image_file:
                    image_filename = Post.save_uploaded_file(image_file, current_app.config["UPLOAD_FOLDER"])
                    cursor.execute(
                        "UPDATE posts SET image=%s WHERE id=%s",
                        (f"/static/uploads/{image_filename}", post_id),
                    )

                connection.commit()
            return True
        except pymysql.Error as e:
            print(f"Error updating post: {e}")
            return False
        finally:
            connection.close()

    @staticmethod
    def delete_post(post_id):
        connection = Database.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT filename FROM posts WHERE id=%s", (post_id,))
                post = cursor.fetchone()

                if post:
                    filename = post["filename"]
                    filepath = os.path.join(current_app.config["POSTS_FOLDER"], filename)
                    if os.path.exists(filepath):
                        os.remove(filepath)

                cursor.execute("DELETE FROM posts WHERE id=%s", (post_id,))
                connection.commit()
            return True
        except pymysql.Error as e:
            print(f"Error deleting post: {e}")
            return False
        finally:
            connection.close()

    @staticmethod
    def get_post_by_id(post_id):
        connection = Database.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
                return cursor.fetchone()
        except pymysql.Error as e:
            print(f"Error fetching post: {e}")
            return None
        finally:
            connection.close()

    @staticmethod
    def get_posts_count_by_tag(tag):
        connection = Database.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM posts WHERE tags LIKE %s",
                    (f"%{tag}%",),
                )
                result = cursor.fetchone()
                return result["count"] if result else 0
        except pymysql.Error as e:
            print(f"Error getting posts count by tag: {e}")
            return 0
        finally:
            connection.close()

    @staticmethod
    def get_posts_by_tag(tag):
        connection = Database.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM posts WHERE tags LIKE %s ORDER BY date DESC",
                    (f"%{tag.strip()}%",),
                )
                return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error getting posts by tag: {e}")
            return []
        finally:
            connection.close()
