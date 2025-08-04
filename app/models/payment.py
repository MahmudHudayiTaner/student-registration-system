from app import db
from datetime import datetime

class Payment(db.Model):
    """Ödeme kayıtları modeli"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # 10 basamak, 2 ondalık
    reference_no = db.Column(db.String(50), unique=True, nullable=True)
    payment_type = db.Column(db.String(50), nullable=True)  # nakit, kart, havale vb.
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # İlişkiler
    student = db.relationship('User', foreign_keys=[student_id], backref='payments')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_payments')
    
    def __repr__(self):
        return f'<Payment {self.id}: {self.amount} TL - {self.description}>'
    
    @property
    def formatted_amount(self):
        """Tutarı formatlı şekilde döndür"""
        return f"{self.amount:,.2f} TL"
    
    @property
    def formatted_date(self):
        """Tarihi formatlı şekilde döndür"""
        return self.transaction_date.strftime('%d.%m.%Y') 