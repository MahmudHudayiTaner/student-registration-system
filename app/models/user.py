from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student')  # student, admin
    is_active = db.Column(db.Boolean, default=True)
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    admin_profile = db.relationship('AdminProfile', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @property
    def display_name(self):
        """Kullanıcının görüntülenecek adını döndür"""
        if self.role == 'admin' and self.admin_profile:
            return self.admin_profile.full_name
        elif self.role == 'student' and self.student_profile:
            if self.student_profile.first_name and self.student_profile.last_name:
                return f"{self.student_profile.first_name} {self.student_profile.last_name}"
            elif self.student_profile.first_name:
                return self.student_profile.first_name
            elif self.student_profile.last_name:
                return self.student_profile.last_name
        return self.email

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 