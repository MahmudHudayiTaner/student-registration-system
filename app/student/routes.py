from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app.student import student
from app.student.forms import ProfileUpdateForm, ChangePasswordForm
from app.models.student_profile import StudentProfile
from app import db, mail
from flask_mail import Message
from functools import wraps
from sqlalchemy.orm import joinedload
import time

def student_required(f):
    """Student yetkisi gerektiren decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Bu sayfaya erişim yetkiniz yok.', 'error')
            return redirect(url_for('auth.login'))
        
        # Rate limiting for student actions
        current_time = time.time()
        student_actions = session.get('student_actions', [])
        
        # Remove actions older than 1 minute
        student_actions = [action for action in student_actions if current_time - action < 60]
        
        # Limit to 20 actions per minute
        if len(student_actions) >= 20:
            flash('Çok fazla işlem yapıyorsunuz. Lütfen bekleyin.', 'error')
            return redirect(url_for('student.dashboard'))
        
        student_actions.append(current_time)
        session['student_actions'] = student_actions
        
        return f(*args, **kwargs)
    return decorated_function

@student.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Öğrenci dashboard sayfası - Ana sayfa"""
    return render_template('student/dashboard.html')

@student.route('/profile')
@login_required
@student_required
def profile():
    """Öğrenci profil görüntüleme sayfası"""
    profile = current_user.student_profile
    return render_template('student/profile.html', profile=profile)

@student.route('/change-password', methods=['GET', 'POST'])
@login_required
@student_required
def change_password():
    """Öğrenci şifre değiştirme sayfası"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        try:
            # Mevcut şifreyi kontrol et
            if not current_user.check_password(form.current_password.data):
                flash('Mevcut şifreniz yanlış.', 'error')
                return render_template('student/change_password.html', form=form)
            
            # Yeni şifreyi ayarla
            current_user.set_password(form.new_password.data)
            db.session.commit()
            
            flash('Şifreniz başarıyla değiştirildi.', 'success')
            return redirect(url_for('student.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Şifre değiştirilirken bir hata oluştu. Lütfen tekrar deneyin.', 'error')
            print(f"Password change error: {e}")
    
    return render_template('student/change_password.html', form=form)

@student.route('/courses')
@login_required
@student_required
def courses():
    """Öğrenci kurs programı sayfası"""
    # Öğrencinin aktif kurs kayıtlarını al
    from app.models.course import CourseEnrollment, CourseAnnouncement
    
    enrollments = CourseEnrollment.query.filter_by(
        student_id=current_user.id,
        is_active=True
    ).join(CourseEnrollment.course).filter(
        CourseEnrollment.course.has(is_active=True, is_deleted=False)
    ).all()
    
    # Her kurs için duyuruları al (creator ile birlikte)
    for enrollment in enrollments:
        enrollment.course.announcements = CourseAnnouncement.query.options(
            joinedload(CourseAnnouncement.creator)
        ).filter_by(
            course_id=enrollment.course.id
        ).order_by(CourseAnnouncement.created_at.desc()).all()
    
    return render_template('student/courses.html', enrollments=enrollments)

@student.route('/announcements/<int:announcement_id>/react', methods=['POST'])
@login_required
@student_required
def react_to_announcement(announcement_id):
    """Duyuruya emoji tepkisi verme"""
    from app.models.course import CourseAnnouncement, AnnouncementReaction, CourseEnrollment
    from flask_wtf.csrf import validate_csrf
    
    announcement = CourseAnnouncement.query.filter_by(
        id=announcement_id
    ).first_or_404()
    
    # Öğrencinin bu kursa kayıtlı olup olmadığını kontrol et
    enrollment = CourseEnrollment.query.filter_by(
        course_id=announcement.course_id,
        student_id=current_user.id,
        is_active=True
    ).first()
    
    if not enrollment:
        flash('Bu duyuruya tepki vermek için kursa kayıtlı olmalısınız.', 'error')
        return redirect(url_for('student.courses'))
    
    # CSRF token kontrolü
    try:
        validate_csrf(request.form.get('csrf_token'))
    except:
        flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'error')
        return redirect(url_for('student.courses'))
    
    emoji = request.form.get('emoji')
    
    if not emoji:
        flash('Emoji seçmelisiniz.', 'error')
        return redirect(url_for('student.courses'))
    
    try:
        # Önceki tepkiyi kontrol et
        existing_reaction = AnnouncementReaction.query.filter_by(
            announcement_id=announcement_id,
            student_id=current_user.id
        ).first()
        
        if existing_reaction:
            # Mevcut tepkiyi güncelle
            existing_reaction.emoji = emoji
        else:
            # Yeni tepki oluştur
            reaction = AnnouncementReaction(
                announcement_id=announcement_id,
                student_id=current_user.id,
                emoji=emoji
            )
            db.session.add(reaction)
        
        db.session.commit()
        flash('Emoji tepkiniz kaydedildi.', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Emoji reaction error: {e}")
        flash(f'Tepki kaydedilirken hata oluştu: {str(e)}', 'error')
    
    return redirect(url_for('student.courses'))

def send_profile_update_email(user, profile):
    """Profil güncelleme email bildirimi gönder"""
    try:
        msg = Message(
            subject='Profil Güncelleme Bildirimi',
            recipients=[user.email]
        )
        
        # HTML email template'ini kullan
        msg.html = render_template('emails/profile_update.html', profile=profile)
        
        # Plain text alternatifi
        msg.body = f"""
Merhaba {profile.first_name} {profile.last_name},

Profil bilgileriniz başarıyla güncellendi.

Güncellenen Bilgiler:
- Ad: {profile.first_name}
- Soyad: {profile.last_name}
- Telefon: {profile.phone or 'Belirtilmemiş'}
- Adres: {profile.address or 'Belirtilmemiş'}

Bu işlemi siz yapmadıysanız, lütfen hemen bizimle iletişime geçin.

Saygılarımızla,
Dil Kursu Yönetimi
        """.strip()
        
        mail.send(msg)
        print(f"Profile update email sent to {user.email}")
    except Exception as e:
        print(f"Email sending error: {e}")
        # Email gönderilemese bile işlemi durdurma 