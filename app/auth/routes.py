from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth
from app.auth.forms import LoginForm, RegisterForm
from app.models.user import User
from app.models.student_profile import StudentProfile
from app import db
from datetime import datetime
import re

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect based on role
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

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('auth.login')) 