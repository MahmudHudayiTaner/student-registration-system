from app import db
from datetime import datetime

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    instructor_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)  # Kurs ücreti
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    schedules = db.relationship('CourseSchedule', backref='course', cascade='all, delete-orphan')
    enrollments = db.relationship('CourseEnrollment', backref='course', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.name}>'
    
    @property
    def total_expected_payment(self):
        """Beklenen toplam ödeme (aktif öğrenci sayısı * kurs ücreti)"""
        active_enrollments = [e for e in self.enrollments if e.is_active]
        return len(active_enrollments) * float(self.price)
    
    @property
    def total_completed_payment(self):
        """Tamamlanmış ödeme toplamı (sadece aktif kayıtlardan)"""
        total = 0
        for enrollment in self.enrollments:
            if enrollment.is_active and enrollment.payments:
                total += sum(float(payment.amount) for payment in enrollment.payments)
        return total
    
    @property
    def pending_payment(self):
        """Bekleyen ödeme (toplam beklenen - tamamlanmış)"""
        return self.total_expected_payment - self.total_completed_payment

class CourseSchedule(db.Model):
    __tablename__ = 'course_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)  # Monday, Tuesday, etc.
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CourseSchedule {self.day_of_week} {self.start_time}-{self.end_time}>'

class CourseEnrollment(db.Model):
    """Kursa kayıtlı öğrenciler"""
    __tablename__ = 'course_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    enrolled_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Admin who enrolled
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    student = db.relationship('User', foreign_keys=[student_id])
    admin = db.relationship('User', foreign_keys=[enrolled_by])
    payments = db.relationship('CoursePayment', backref='enrollment', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CourseEnrollment {self.student.email} - {self.course.name}>'
    
    @property
    def total_paid(self):
        """Bu öğrencinin bu kurs için ödediği toplam tutar"""
        return sum(float(payment.amount) for payment in self.payments)
    
    @property
    def remaining_payment(self):
        """Bu öğrencinin bu kurs için kalan ödeme tutarı"""
        return float(self.course.price) - self.total_paid

class CoursePayment(db.Model):
    """Kurs ödemeleri"""
    __tablename__ = 'course_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('course_enrollments.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=True)  # Genel ödeme ile bağlantı
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50))  # nakit, kart, havale vb.
    reference_no = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])
    payment = db.relationship('Payment', foreign_keys=[payment_id])  # Genel ödeme ile bağlantı
    
    def __repr__(self):
        return f'<CoursePayment {self.amount} TL - {self.enrollment.student.email}>' 