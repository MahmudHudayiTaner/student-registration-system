from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.student import student
from app.student.forms import ProfileUpdateForm, ChangePasswordForm
from app.models.student_profile import StudentProfile
from app import db, mail
from flask_mail import Message
from functools import wraps

def student_required(f):
    """Student yetkisi gerektiren decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Bu sayfaya erişim yetkiniz yok.', 'error')
            return redirect(url_for('auth.login'))
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