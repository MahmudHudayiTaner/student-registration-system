from app import db
from datetime import datetime

class AdminProfile(db.Model):
    """Admin profil bilgileri"""
    __tablename__ = 'admin_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', uselist=False, overlaps="admin_profile")
    
    def __repr__(self):
        return f'<AdminProfile {self.first_name} {self.last_name} - {self.user.email}>'
    
    @property
    def full_name(self):
        """Tam adı döndür"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.user.email 