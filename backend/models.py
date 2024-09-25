from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
from flask import flash, redirect, url_for
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Remove or comment out the SQLAlchemy initialization
# db = SQLAlchemy()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
assert SUPABASE_URL is not None and SUPABASE_KEY is not None, "Supabase credentials are missing"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Remove or comment out the Users class
# class Users(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(255), nullable=False)  # Make sure this is not nullable

#     # Add this line to create the relationship
#     models = db.relationship('Models', back_populates='user', cascade='all, delete-orphan')

#     def __init__(self, username, email):
#         self.username = username
#         self.email = email

#     def set_password(self, password):
#         if not password:
#             raise ValueError("Password cannot be empty")
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         if not self.password_hash:
#             return False
#         return check_password_hash(self.password_hash, password)
    
#     def get_models(self):
#         return self.models
    
#     @classmethod
#     def get_user_by_id(cls, id):
#         user = cls.query.get(id)
#         return user if user else None
    
#     @classmethod
#     def get_user_by_email(cls, email):
#         user = cls.query.filter_by(email=email).first()
#         return user if user else None

#     @classmethod
#     def get_user_by_username(cls, username):
#         user = cls.query.filter_by(username=username).first()
#         return user if user else None
    
#     @classmethod
#     def create_user(cls, username, email, password):
#         if cls.query.filter((cls.username == username) | (cls.email == email)).first():
#             flash("Username or email already exists", "error")
#             return redirect(url_for('signup'))
#         new_user = cls(username=username, email=email)
#         new_user.set_password(password)
#         db.session.add(new_user)
#         db.session.commit()
#         return new_user

#     def __repr__(self):
#         return f'<User {self.username}>'

# Remove or comment out the Models class
# class Models(db.Model):
#     __tablename__ = 'models'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
#     name = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.Text)
#     created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
#     updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
#     model_version = db.Column(db.String(100))
#     status = db.Column(db.String(50))

#     # Relationship
#     user = db.relationship('Users', back_populates='models')

#     # Unique constraint
#     __table_args__ = (
#         db.UniqueConstraint('user_id', 'name', name='unique_user_model_name'),
#     )

#     def __init__(self, user_id, name, description, model_version, status):
#         self.user_id = user_id
#         self.name = name
#         self.description = description
#         self.model_version = model_version
#         self.status = status

#     @classmethod
#     def insert_model(cls, user_id, name, description, model_version, status):
#         if cls.query.filter_by(user_id=user_id, name=name).first():
#             raise ValueError("A model with this name already exists for this user")

#         new_model = cls(user_id=user_id, name=name, description=description, 
#                         model_version=model_version, status=status)
#         db.session.add(new_model)
#         db.session.commit()
#         return new_model
    
#     def __repr__(self):
#         return f'<Model {self.name}>'

class SupabaseModels:
    @staticmethod
    def insert_model(user_id, name, description, model_version, status):
        data = {
            "user_id": user_id,
            "name": name,
            "description": description,
            "model_version": model_version,
            "status": status
        }
        return supabase.table("models").insert(data).execute()
    @staticmethod
    def get_model_by_id(model_id):
        response = supabase.table('models').select('*').eq('id', model_id).single().execute()
        print(f"Supabase response for model_id {model_id}: {response}")  # Add this line for debugging
        return response

    @staticmethod
    def get_models_by_user_id(user_id):
        return supabase.table("models").select("*").eq("user_id", user_id).execute()
    
    @staticmethod
    def delete_model_by_id(model_id):
        return supabase.table('models').delete().eq('id', model_id).execute()
    

    # Add other methods as needed

    # Consider adding any missing methods that were previously in the Models class
    # For example:
    @staticmethod
    def update_model(model_id, data):
        return supabase.table('models').update(data).eq('id', model_id).execute()

    @staticmethod
    def get_models_by_name(user_id, name):
        return supabase.table("models").select("*").eq("user_id", user_id).eq("name", name).execute()

    # Add any other methods you need for your Supabase operations

class SupabaseUsers:
    @staticmethod
    def sign_up_user(email, password, username):
        user = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "username": username
                }
            }
        })
        return user

    @staticmethod
    def delete_user(user_id):
        # Note: This requires admin privileges in Supabase
        return supabase.auth.admin.delete_user(user_id)

    @staticmethod
    def update_user(user_id, user_data):
        # Note: This requires admin privileges in Supabase
        return supabase.auth.admin.update_user_by_id(user_id, user_data)

    @staticmethod
    def get_user(user_id):
        # Note: This requires admin privileges in Supabase
        return supabase.auth.admin.get_user_by_id(user_id)
    
    
  
    
    
