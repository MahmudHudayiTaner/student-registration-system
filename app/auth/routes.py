from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth
from app.auth.forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from app.models.user import User
from app.models.student_profile import StudentProfile
from app import db, mail
from datetime import datetime, timedelta
import re
import secrets
from flask_mail import Message

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Input sanitization
        email = re.sub(r'[^\w@.-]', '', form.email.data.strip().lower())
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Hesabınız aktif değil. Lütfen yönetici ile iletişime geçin.', 'error')
                return render_template('auth/login.html', form=form)
            
            # Clear failed login attempts
            session.pop('failed_login_attempts', None)
            
            login_user(user, remember=form.remember_me.data)
            
            # Redirect based on role
            if user.role == 'admin':
                next_page = request.args.get('next') or url_for('admin.dashboard')
            else:
                next_page = request.args.get('next') or url_for('student.dashboard')
            
            return redirect(next_page)
        else:
            # Track failed login attempts
            failed_attempts = session.get('failed_login_attempts', 0) + 1
            session['failed_login_attempts'] = failed_attempts
            
            if failed_attempts >= 3:
                flash('Çok fazla başarısız giriş denemesi. Lütfen 5 dakika bekleyin.', 'error')
            else:
                flash('Geçersiz email veya şifre', 'error')
    
    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            # Input sanitization
            email = re.sub(r'[^\w@.-]', '', form.email.data.strip().lower())
            first_name = re.sub(r'[^\w\s]', '', form.first_name.data.strip())
            last_name = re.sub(r'[^\w\s]', '', form.last_name.data.strip())
            phone = re.sub(r'[^\d+\-\(\)\s]', '', form.phone.data.strip()) if form.phone.data else None
            
            # Create user
            user = User(
                email=email,
                role='student',
                is_active=True
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Create student profile
            profile = StudentProfile(
                user_id=user.id,
                first_name=first_name,
                last_name=last_name,
                birth_date=form.birth_date.data,
                gender=form.gender.data,
                phone=phone,
                address=form.address.data.strip() if form.address.data else None
            )
            db.session.add(profile)
            db.session.commit()
            
            flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Kayıt sırasında bir hata oluştu. Lütfen tekrar deneyin.', 'error')
            print(f"Registration error: {e}")
    
    return render_template('auth/register.html', form=form)

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Şifremi unuttum sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        # Input sanitization
        email = re.sub(r'[^\w@.-]', '', form.email.data.strip().lower())
        
        user = User.query.filter_by(email=email).first()
        if user and user.is_active:
            # Token oluştur
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # Email gönder
            try:
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                msg = Message(
                    subject='Şifre Sıfırlama - Kafka Dil Akademisi',
                    recipients=[user.email]
                )
                
                msg.html = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">Şifre Sıfırlama</h2>
                    <p>Merhaba,</p>
                    <p>Şifrenizi sıfırlamak için aşağıdaki linke tıklayın:</p>
                    <p style="margin: 20px 0;">
                        <a href="{reset_url}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Şifremi Sıfırla
                        </a>
                    </p>
                    <p><strong>Bu link 1 saat sonra geçersiz olacaktır.</strong></p>
                    <p>Eğer bu isteği siz yapmadıysanız, bu emaili görmezden gelebilirsiniz.</p>
                    <hr style="margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Kafka Dil Akademisi<br>
                        Bu email otomatik olarak gönderilmiştir.
                    </p>
                </div>
                """
                
                # Gerçek email gönder
                mail.send(msg)
                
                flash('Şifre sıfırlama linki email adresinize gönderildi. Lütfen email kutunuzu kontrol edin.', 'success')
                
            except Exception as e:
                # Token'ı temizle
                user.reset_token = None
                user.reset_token_expires = None
                db.session.commit()
                flash('Email gönderilirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.', 'error')
                print(f"Email sending error: {e}")
        else:
            # Güvenlik için aynı mesajı göster
            flash('Şifre sıfırlama linki email adresinize gönderildi. Lütfen email kutunuzu kontrol edin.', 'success')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Şifre sıfırlama sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))
    
    # Token'ı kontrol et
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        flash('Geçersiz veya süresi dolmuş şifre sıfırlama linki.', 'error')
        return redirect(url_for('auth.login'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            # Şifreyi güncelle
            user.set_password(form.password.data)
            user.reset_token = None
            user.reset_token_expires = None
            db.session.commit()
            
            flash('Şifreniz başarıyla güncellendi. Şimdi yeni şifrenizle giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Şifre güncellenirken bir hata oluştu. Lütfen tekrar deneyin.', 'error')
            print(f"Password reset error: {e}")
    
    return render_template('auth/reset_password.html', form=form, token=token)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('auth.login')) 