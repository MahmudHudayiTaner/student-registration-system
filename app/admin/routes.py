from flask import render_template, redirect, url_for, flash, request, abort, jsonify, send_file
from flask_login import login_required, current_user
from app.admin import admin
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.admin_profile import AdminProfile
from app.models.course import Course, CourseSchedule, CourseEnrollment, CoursePayment, CourseAnnouncement, AnnouncementReaction
from app.models.payment import Payment
from app.admin.forms import CourseForm, AdminPasswordChangeForm, AdminProfileForm
from app import db
from functools import wraps
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
import pandas as pd
import os
from werkzeug.utils import secure_filename
from flask_wtf.csrf import validate_csrf
from werkzeug.security import generate_password_hash
import re
from markupsafe import escape
from flask import session
import time
from bs4 import BeautifulSoup

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        
        # Rate limiting for admin actions
        current_time = time.time()
        admin_actions = session.get('admin_actions', [])
        
        # Remove actions older than 1 minute
        admin_actions = [action for action in admin_actions if current_time - action < 60]
        
        # Limit to 30 actions per minute
        if len(admin_actions) >= 30:
            flash('Çok fazla işlem yapıyorsunuz. Lütfen bekleyin.', 'error')
            return redirect(url_for('admin.dashboard'))
        
        admin_actions.append(current_time)
        session['admin_actions'] = admin_actions
        
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Son 30 günlük istatistikler
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    # Öğrenci istatistikleri
    total_students = User.query.filter_by(role='student').count()
    active_students = User.query.filter_by(role='student', is_active=True).count()
    inactive_students = User.query.filter_by(role='student', is_active=False).count()
    new_students_this_month = User.query.filter(
        User.role == 'student',
        User.created_at >= thirty_days_ago
    ).count()
    
    # Kurs istatistikleri
    total_courses = Course.query.count()
    active_courses = Course.query.filter_by(is_active=True).count()
    
    # Ödeme istatistikleri
    total_payments = Payment.query.filter(Payment.is_active == True).count()
    total_amount = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.is_active == True
    ).scalar() or 0
    
    # Son aktiviteler
    recent_students = User.query.filter_by(role='student').order_by(User.created_at.desc()).limit(5).all()
    recent_courses = Course.query.order_by(Course.created_at.desc()).limit(5).all()
    recent_payments = Payment.query.filter(Payment.is_active == True).order_by(Payment.transaction_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_students=total_students,
                         active_students=active_students,
                         inactive_students=inactive_students,
                         new_students_this_month=new_students_this_month,
                         total_courses=total_courses,
                         active_courses=active_courses,
                         total_payments=total_payments,
                         total_amount=total_amount,
                         recent_students=recent_students,
                         recent_courses=recent_courses,
                         recent_payments=recent_payments)

@admin.route('/students')
@login_required
@admin_required
def students():
    """Öğrenci yönetimi"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    # Filtreleme
    query = User.query.filter_by(role='student')
    
    if search:
        # Input sanitization
        sanitized_search = re.sub(r'[^\w\s@.-]', '', search.strip())
        if sanitized_search:
            query = query.filter(
                db.or_(
                    User.email.contains(sanitized_search),
                    User.student_profile.has(db.or_(
                        StudentProfile.first_name.contains(sanitized_search),
                        StudentProfile.last_name.contains(sanitized_search),
                        StudentProfile.phone.contains(sanitized_search)
                    ))
                )
            )
    
    if status_filter:
        if status_filter == 'active':
            query = query.filter_by(is_active=True)
        elif status_filter == 'inactive':
            query = query.filter_by(is_active=False)
    
    # Sayfalama
    students = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/students.html', students=students, search=search, status_filter=status_filter)

@admin.route('/students/<int:id>')
@login_required
@admin_required
def student_detail(id):
    """Öğrenci detay sayfası"""
    # ID validation
    if not isinstance(id, int) or id <= 0:
        abort(404)
    
    student = User.query.get_or_404(id)
    if student.role != 'student':
        abort(404)
    
    return render_template('admin/student_detail.html', student=student)

@admin.route('/students/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_student_status(id):
    """Öğrenci durumunu değiştir"""
    try:
        validate_csrf(request.form.get('csrf_token'))
    except:
        flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'error')
        return redirect(url_for('admin.students'))
    
    student = User.query.get_or_404(id)
    if student.role != 'student':
        abort(404)
    
    try:
        student.is_active = not student.is_active
        db.session.commit()
        status = 'aktif' if student.is_active else 'pasif'
        flash(f'Öğrenci durumu {status} olarak güncellendi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Durum güncellenirken hata oluştu.', 'error')
    
    return redirect(url_for('admin.students'))

@admin.route('/students/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student(id):
    """Öğrenciyi sil"""
    try:
        validate_csrf(request.form.get('csrf_token'))
    except:
        flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'error')
        return redirect(url_for('admin.students'))
    
    student = User.query.get_or_404(id)
    if student.role != 'student':
        abort(404)
    
    try:
        db.session.delete(student)
        db.session.commit()
        flash('Öğrenci başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Öğrenci silinirken hata oluştu.', 'error')
    
    return redirect(url_for('admin.students'))

@admin.route('/courses')
@login_required
@admin_required
def courses():
    """Kurs yönetimi"""
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('admin/courses.html', courses=courses)

@admin.route('/courses/new', methods=['POST'])
@login_required
@admin_required
def new_course():
    """Yeni kurs oluşturma"""
    try:
        validate_csrf(request.form.get('csrf_token'))
    except:
        flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'error')
        return redirect(url_for('admin.courses'))
    
    try:
        # Kurs oluştur
        course = Course(
            name=request.form.get('name'),
            instructor_name=request.form.get('instructor_name'),
            price=float(request.form.get('price')),
            description=request.form.get('description'),
            is_active=bool(request.form.get('is_active'))
        )
        db.session.add(course)
        db.session.flush()  # ID'yi almak için flush
        
        # Ders saatlerini ekle
        i = 0
        while True:
            day_of_week = request.form.get(f'schedules[{i}][day_of_week]')
            start_time_str = request.form.get(f'schedules[{i}][start_time]')
            end_time_str = request.form.get(f'schedules[{i}][end_time]')
            
            # Eğer bu index'te veri yoksa döngüyü bitir
            if not day_of_week or not start_time_str or not end_time_str:
                break
                
            try:
                from datetime import time
                start_hour, start_minute = map(int, start_time_str.split(':'))
                end_hour, end_minute = map(int, end_time_str.split(':'))
                
                start_time = time(start_hour, start_minute)
                end_time = time(end_hour, end_minute)
                
                # Çakışma kontrolü
                existing_schedule = CourseSchedule.query.filter_by(
                    course_id=course.id,
                    day_of_week=day_of_week
                ).first()
                
                if not existing_schedule and start_time < end_time:
                    schedule = CourseSchedule(
                        course_id=course.id,
                        day_of_week=day_of_week,
                        start_time=start_time,
                        end_time=end_time
                    )
                    db.session.add(schedule)
            except Exception as e:
                continue
                
            i += 1
        
        db.session.commit()
        flash('Kurs başarıyla oluşturuldu.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Kurs oluşturulurken hata oluştu.', 'error')
    
    return redirect(url_for('admin.courses'))

@admin.route('/courses/update', methods=['POST'])
@login_required
@admin_required
def update_course():
    """Kurs bilgilerini güncelleme"""
    try:
        validate_csrf(request.form.get('csrf_token'))
    except:
        flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'error')
        return redirect(url_for('admin.courses'))
    
    course_id = request.form.get('course_id')
    course = Course.query.get_or_404(course_id)
    
    try:
        course.name = request.form.get('name')
        course.instructor_name = request.form.get('instructor_name')
        course.price = float(request.form.get('price'))
        course.description = request.form.get('description')
        course.is_active = bool(request.form.get('is_active'))
        db.session.commit()
        flash('Kurs bilgileri güncellendi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Kurs güncellenirken hata oluştu.', 'error')
    
    return redirect(url_for('admin.courses'))

@admin.route('/courses/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_course(id):
    """Kursu hard delete yap"""
    try:
        validate_csrf(request.form.get('csrf_token'))
    except:
        flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'error')
        return redirect(url_for('admin.courses'))
    
    course = Course.query.get_or_404(id)
    
    try:
        # Önce kursa ait ödemeleri sil (CoursePayment)
        enrollments = CourseEnrollment.query.filter_by(course_id=id).all()
        for enrollment in enrollments:
            CoursePayment.query.filter_by(enrollment_id=enrollment.id).delete()
        
        # Kursa ait ders saatlerini sil
        CourseSchedule.query.filter_by(course_id=id).delete()
        
        # Kursa ait kayıtları sil
        CourseEnrollment.query.filter_by(course_id=id).delete()
        
        # Kursu sil
        db.session.delete(course)
        db.session.commit()
        flash('Kurs başarıyla silindi.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Kurs silinirken hata oluştu.', 'error')
    
    return redirect(url_for('admin.courses'))

@admin.route('/courses/<int:id>/manage')
@login_required
@admin_required
def manage_course(id):
    """Kurs yönetimi sayfası"""
    course = Course.query.get_or_404(id)
    
    # Kursa kayıtlı öğrenciler
    enrollments = CourseEnrollment.query.filter_by(course_id=id, is_active=True).all()
    
    # Kursa kayıtlı olmayan öğrenciler
    enrolled_student_ids = [e.student_id for e in enrollments]
    available_students = User.query.filter(
        User.role == 'student',
        User.is_active == True,
        ~User.id.in_(enrolled_student_ids)
    ).all()
    
    # Kurs duyuruları
    announcements = CourseAnnouncement.query.options(joinedload(CourseAnnouncement.creator)).filter_by(course_id=id).order_by(CourseAnnouncement.created_at.desc()).all()
    
    return render_template('admin/manage_course.html', 
                         course=course, 
                         enrollments=enrollments,
                         available_students=available_students,
                         announcements=announcements)

@admin.route('/courses/<int:id>/export-students')
@login_required
@admin_required
def export_course_students(id):
    """Kursa kayıtlı öğrencilerin adres bilgilerini Excel formatında indir"""
    course = Course.query.get_or_404(id)
    
    # Kursa kayıtlı öğrencileri al
    enrollments = CourseEnrollment.query.filter_by(course_id=id, is_active=True).all()
    
    if not enrollments:
        flash('Bu kursa kayıtlı öğrenci bulunamadı.', 'warning')
        return redirect(url_for('admin.manage_course', id=id))
    
    # Excel için veri hazırla
    data = []
    for enrollment in enrollments:
        student = enrollment.student
        profile = student.student_profile
        
        # Ad soyad bilgilerini al
        first_name = profile.first_name if profile and profile.first_name else ''
        last_name = profile.last_name if profile and profile.last_name else ''
        # Telefon bilgisini al
        phone = profile.phone if profile and profile.phone else ''
        
        # Adres bilgisini al (StudentProfile'da address alanı varsa)
        address = profile.address if profile and hasattr(profile, 'address') and profile.address else ''
        
        data.append({
            'İsim': first_name,
            'Soyisim': last_name,
            'Telefon': phone,
            'Adres': address,
            'Email': student.email
        })
    
    # DataFrame oluştur
    df = pd.DataFrame(data)
    
    # Excel dosyası oluştur
    from io import BytesIO
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Öğrenci Adresleri', index=False)
    
    output.seek(0)
    
    # Dosya adını hazırla
    filename = f"{course.name}_ogrenci_adresleri_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filename = secure_filename(filename)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@admin.route('/courses/<int:id>/enroll-students', methods=['POST'])
@login_required
@admin_required
def enroll_students(id):
    """Kursa öğrenci ekleme"""
    try:
        validate_csrf(request.form.get('csrf_token'))
    except:
        flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'error')
        return redirect(url_for('admin.manage_course', id=id))
    
    course = Course.query.get_or_404(id)
    student_ids = request.form.getlist('student_ids')
    
    if not student_ids:
        flash('Lütfen en az bir öğrenci seçin.', 'error')
        return redirect(url_for('admin.manage_course', id=id))
    
    try:
        enrolled_count = 0
        for student_id in student_ids:
            # Öğrencinin zaten kayıtlı olup olmadığını kontrol et
            existing_enrollment = CourseEnrollment.query.filter_by(
                course_id=id, 
                student_id=student_id,
                is_active=True
            ).first()
            
            if not existing_enrollment:
                enrollment = CourseEnrollment(
                    course_id=id,
                    student_id=student_id,
                    enrolled_by=current_user.id
                )
                db.session.add(enrollment)
                enrolled_count += 1
        
        db.session.commit()
        flash(f'{enrolled_count} öğrenci kursa başarıyla eklendi.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Öğrenci eklenirken hata oluştu.', 'error')
    
    return redirect(url_for('admin.manage_course', id=id))

@admin.route('/courses/<int:id>/announcements/add', methods=['POST'])
@login_required
@admin_required
def add_announcement(id):
    """Kursa duyuru ekleme"""
    try:
        validate_csrf(request.form.get('csrf_token'))
    except:
        flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'error')
        return redirect(url_for('admin.manage_course', id=id))
    
    course = Course.query.get_or_404(id)
    
    # HTML içeriğini güvenli şekilde işle
 
    import re
    
    def sanitize_html(text):
        """HTML içeriğini güvenli hale getir"""
        # Sadece izin verilen HTML etiketlerini kabul et
        allowed_tags = ['strong', 'em', 'u', 'p', 'ul', 'li', 'br']
        allowed_attrs = {}
        
        # HTML'i parse et
        soup = BeautifulSoup(text, 'html.parser')
        
        # İzin verilmeyen etiketleri kaldır
        for tag in soup.find_all():
            if tag.name not in allowed_tags:
                tag.unwrap()
        
        # Sadece izin verilen etiketleri bırak
        for tag in soup.find_all():
            if tag.name not in allowed_tags:
                tag.replace_with(tag.get_text())
        
        return str(soup)
    
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    
    # HTML içeriğini temizle
    title = sanitize_html(title)
    content = sanitize_html(content)
    
    if not title or not content:
        flash('Başlık ve içerik alanları zorunludur.', 'error')
        return redirect(url_for('admin.manage_course', id=id))
    
    try:
        announcement = CourseAnnouncement(
            course_id=id,
            title=title,
            content=content,
            created_by=current_user.id
        )
        db.session.add(announcement)
        db.session.commit()
        flash('Duyuru başarıyla eklendi.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Duyuru eklenirken hata oluştu.', 'error')
    
    return redirect(url_for('admin.manage_course', id=id))

@admin.route('/courses/<int:id>/announcements/<int:announcement_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_announcement(id, announcement_id):
    """Kurs duyurusunu hard silme"""
    try:
        validate_csrf(request.form.get('csrf_token'))
    except:
        flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'error')
        return redirect(url_for('admin.manage_course', id=id))
    
    announcement = CourseAnnouncement.query.filter_by(
        course_id=id, 
        id=announcement_id
    ).first_or_404()
    
    try:
        # Duyuruyu veritabanından tamamen sil
        db.session.delete(announcement)
        db.session.commit()
        flash('Duyuru başarıyla silindi.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Duyuru silinirken hata oluştu.', 'error')
    
    return redirect(url_for('admin.manage_course', id=id))

@admin.route('/courses/<int:id>/unenroll-student/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def unenroll_student(id, student_id):
    """Kurstan öğrenci çıkarma"""
    try:
        validate_csrf(request.form.get('csrf_token'))
    except:
        flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'error')
        return redirect(url_for('admin.manage_course', id=id))
    
    enrollment = CourseEnrollment.query.filter_by(
        course_id=id, 
        student_id=student_id,
        is_active=True
    ).first_or_404()
    
    try:
        # Önce bu öğrencinin ödeme kayıtlarını sil
        CoursePayment.query.filter_by(enrollment_id=enrollment.id).delete()
        
        # Sonra öğrenciyi kurstan çıkar
        enrollment.is_active = False
        db.session.commit()
        flash('Öğrenci kurstan çıkarıldı ve ödeme kayıtları silindi.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Öğrenci çıkarılırken hata oluştu.', 'error')
    
    return redirect(url_for('admin.manage_course', id=id))



@admin.route('/courses/<int:id>/get-pending-payments/<int:student_id>')
@login_required
@admin_required
def get_pending_payments(id, student_id):
    """Bekleyen ödemeleri getir (API)"""
    try:
        # Önce atanmış ödeme ID'lerini al
        assigned_payment_ids = db.session.query(CoursePayment.payment_id).filter(
            CoursePayment.payment_id.isnot(None)
        ).distinct().all()
        assigned_payment_ids = [row[0] for row in assigned_payment_ids]
        
        # Bekleyen ödemeler (hiçbir kurs ödemesine bağlı olmayan)
        pending_payments = Payment.query.filter(
            Payment.is_active == True,
            ~Payment.id.in_(assigned_payment_ids) if assigned_payment_ids else True
        ).order_by(Payment.transaction_date.desc()).all()
        
        # JSON formatına çevir
        payments_data = []
        for payment in pending_payments:
                         payments_data.append({
                 'id': payment.id,
                 'formatted_date': payment.formatted_date,
                 'description': payment.description,
                 'amount': str(payment.amount)
             })
        
        return jsonify({
            'success': True,
            'payments': payments_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@admin.route('/courses/<int:id>/assign-payments/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def assign_payments_to_student_post(id, student_id):
    """Öğrenciye bekleyen ödemeleri atama (JSON API)"""
    try:
        # JSON verilerini al
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Geçersiz veri formatı'})
        
        payment_ids = data.get('payment_ids', [])
        
        if not payment_ids:
            return jsonify({'success': False, 'error': 'Lütfen en az bir ödeme seçin'})
        
        course = Course.query.get_or_404(id)
        student = User.query.get_or_404(student_id)
        
        # Öğrencinin bu kursa kaydı var mı kontrol et
        enrollment = CourseEnrollment.query.filter_by(
            course_id=id,
            student_id=student_id,
            is_active=True
        ).first_or_404()
        
        try:
            assigned_count = 0
            for payment_id in payment_ids:
                payment = Payment.query.get(payment_id)
                if payment and payment.is_active:
                    # Bu ödeme zaten başka bir kurs ödemesine bağlı mı kontrol et
                    existing_course_payment = CoursePayment.query.filter_by(payment_id=payment_id).first()
                    if not existing_course_payment:
                        # Kurs ödemesi oluştur
                        course_payment = CoursePayment(
                            enrollment_id=enrollment.id,
                            payment_id=payment_id,
                            amount=payment.amount,
                            payment_date=payment.transaction_date,
                                                     payment_method='otomatik_atama',
                         notes=f'Ödeme ataması - {payment.description}',
                            created_by=current_user.id
                        )
                        db.session.add(course_payment)
                        assigned_count += 1
            
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'{assigned_count} ödeme başarıyla öğrenciye atandı'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': f'Ödeme atama işlemi sırasında hata oluştu: {str(e)}'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Veri işleme hatası: {str(e)}'})

@admin.route('/payments')
@login_required
@admin_required
def payments():
    """Ödeme yönetimi ana sayfası"""
    # Tüm ödemeler (sayfalama ile)
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    date_filter = request.args.get('date_filter', '')
    
    # Ödeme sorgusu
    query = Payment.query.filter(Payment.is_active == True)
    
    # Arama filtresi
    if search:
        # Önce search'in sayısal olup olmadığını kontrol et
        try:
            search_amount = float(search)
            # Eğer sayısal ise, amount alanında tam eşleşme ara
            query = query.filter(
                db.or_(
                    Payment.description.contains(search),
                    Payment.amount == search_amount
                )
            )
        except ValueError:
            # Eğer sayısal değilse, sadece description'da ara
            query = query.filter(Payment.description.contains(search))

    # Tarih filtresi
    if date_filter:
        if date_filter == 'today':
            today = datetime.now().date()
            query = query.filter(Payment.transaction_date == today)
        elif date_filter == 'week':
            week_ago = datetime.now().date() - timedelta(days=7)
            query = query.filter(Payment.transaction_date >= week_ago)
        elif date_filter == 'month':
            month_ago = datetime.now().date() - timedelta(days=30)
            query = query.filter(Payment.transaction_date >= month_ago)
    
    # Sayfalama
    payments = query.order_by(Payment.transaction_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Bekleyen ödemeler (hiçbir kurs ödemesine bağlı olmayan)
    # Önce atanmış ödeme ID'lerini al
    assigned_payment_ids = db.session.query(CoursePayment.payment_id).filter(
        CoursePayment.payment_id.isnot(None)
    ).distinct().all()
    assigned_payment_ids = [row[0] for row in assigned_payment_ids]
    
    pending_payments = Payment.query.filter(
        Payment.is_active == True,
        ~Payment.id.in_(assigned_payment_ids) if assigned_payment_ids else True
    ).order_by(Payment.transaction_date.desc()).limit(10).all()
    
    # Toplam istatistikler
    total_payments = Payment.query.filter(Payment.is_active == True).count()
    total_amount = db.session.query(db.func.sum(Payment.amount)).filter(
        Payment.is_active == True
    ).scalar() or 0
    
    return render_template('admin/payments.html',
                         payments=payments,
                         pending_payments=pending_payments,
                         total_payments=total_payments,
                         total_amount=total_amount,
                         search=search,
                         date_filter=date_filter)

@admin.route('/payments/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_payment(id):
    """Ödeme silme"""
    try:
        validate_csrf(request.form.get('csrf_token'))
    except:
        flash('Güvenlik hatası. Lütfen tekrar deneyin.', 'error')
        return redirect(url_for('admin.payments'))
    
    payment = Payment.query.get_or_404(id)
    
    try:
        # 1. Önce bu payment'a ait CoursePayment kayıtlarını sil
        from app.models.course import CoursePayment
        course_payments = CoursePayment.query.filter_by(payment_id=id).all()
        for course_payment in course_payments:
            db.session.delete(course_payment)
        
        # 2. Sonra Payment kaydını sil
        db.session.delete(payment)
        db.session.commit()
        flash('Ödeme başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Payment deletion error: {e}")  # Debug için
        flash('Ödeme silinirken hata oluştu.', 'error')
    
    return redirect(url_for('admin.payments'))

@admin.route('/payments/bulk-delete', methods=['POST'])
@login_required
@admin_required
def bulk_delete_payments():
    """Toplu ödeme silme"""
    try:
        # CSRF token kontrolü
        csrf_token = request.headers.get('X-CSRFToken')
        if not csrf_token:
            return jsonify({'success': False, 'error': 'CSRF token eksik'})
        
        try:
            validate_csrf(csrf_token)
        except Exception as e:
            return jsonify({'success': False, 'error': 'Güvenlik hatası'})
        
        # JSON verilerini al
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Geçersiz veri formatı'})
        
        payment_ids = data.get('payment_ids', [])
        
        if not payment_ids:
            return jsonify({'success': False, 'error': 'Silinecek ödeme seçilmedi'})
        
        try:
            deleted_count = 0
            for payment_id in payment_ids:
                payment = Payment.query.get(payment_id)
                if payment and payment.is_active:
                    # 1. Önce bu payment'a ait CoursePayment kayıtlarını sil
                    course_payments = CoursePayment.query.filter_by(payment_id=payment_id).all()
                    for course_payment in course_payments:
                        db.session.delete(course_payment)
                    
                    # 2. Sonra Payment kaydını sil
                    db.session.delete(payment)
                    deleted_count += 1
            
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'{deleted_count} ödeme başarıyla silindi'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': f'Toplu silme işlemi sırasında hata oluştu: {str(e)}'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Veri işleme hatası: {str(e)}'})

@admin.route('/payments/upload', methods=['POST'])
@login_required
@admin_required
def upload_statement():
    """Ekstre yükleme"""
    try:
        validate_csrf(request.form.get('csrf_token'))
    except:
        return jsonify({'success': False, 'error': 'Güvenlik hatası'})
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Dosya seçilmedi'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Dosya seçilmedi'})
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'success': False, 'error': 'Sadece Excel dosyaları kabul edilir'})
    
    try:
        # Dosyayı oku
        df = pd.read_excel(file)
        
        # Sütun isimlerini temizle
        df.columns = df.columns.str.strip()
        
        # Gerekli sütunları kontrol et
        required_columns = ['Tarih', 'Açıklama', 'İşlem Tutarı (TL)']
        available_columns = list(df.columns)
        
        # Sütun eşleştirme
        date_column = None
        description_column = None
        amount_column = None
        
        # Tarih sütunu için alternatif isimler
        date_alternatives = ['Tarih', 'TARIH', 'Date', 'date']
        for col in available_columns:
            if col in date_alternatives:
                date_column = col
                break
        
        # Açıklama sütunu için alternatif isimler
        desc_alternatives = ['Açıklama', 'ACIKLAMA', 'Description', 'description']
        for col in available_columns:
            if col in desc_alternatives:
                description_column = col
                break
        
        # İşlem Tutarı sütunu için alternatif isimler
        amount_alternatives = ['İşlem Tutarı (TL)', 'İŞLEM TUTARI (TL)', 'Amount (TL)', 'amount (tl)', 'İşlem Tutarı', 'İŞLEM TUTARI', 'Tutar', 'TUTAR']
        for col in available_columns:
            if col in amount_alternatives:
                amount_column = col
                break
        
        if not date_column or not description_column or not amount_column:
            missing_columns = []
            if not date_column:
                missing_columns.append('Tarih')
            if not description_column:
                missing_columns.append('Açıklama')
            if not amount_column:
                missing_columns.append('Tutar')
            
            return jsonify({
                'success': False, 
                'error': f'Sütun isimlerinde problem var. \nŞu sütunlar eksik: {", ".join(missing_columns)} \nBu sütunlar tespit edildi: {", ".join(available_columns)}'
            })
        
        # Boş satırları temizle
        df = df.dropna(subset=[date_column, description_column, amount_column])
        
        # Tutar sütununu sayısal formata çevir
        df[amount_column] = pd.to_numeric(df[amount_column], errors='coerce')
        
        # Pozitif tutarları filtrele
        positive_payments = df[df[amount_column] > 0].copy()
        
        # Minimum tutar filtresi uygula
        min_amount = request.form.get('min_amount')
        if min_amount:
            try:
                min_amount_float = float(min_amount)
                positive_payments = positive_payments[positive_payments[amount_column] >= min_amount_float]
            except ValueError:
                return jsonify({'success': False, 'error': 'Geçersiz minimum tutar değeri'})
        
        if positive_payments.empty:
            return jsonify({'success': False, 'error': 'Filtre kriterlerine uygun ödeme bulunamadı'})
        
        # Mevcut kayıtları kontrol et
        processed_data = []

        for index, row in positive_payments.iterrows():
            try:
                # Tarihi parse et
                transaction_date = pd.to_datetime(row[date_column]).date()
                
                # Mevcut kayıt kontrolü (tarih + açıklama + tutar kombinasyonu)
                existing_payment = Payment.query.filter_by(
                    transaction_date=transaction_date,
                    description=str(row[description_column]),
                    amount=float(row[amount_column])
                ).first()
                
                processed_data.append({
                    'index': index,
                    'date': transaction_date.strftime('%d.%m.%Y'),
                    'description': str(row[description_column]),
                    'amount': float(row[amount_column]),
                    'exists': existing_payment is not None
                })
            except Exception as e:
                # Hatalı satırları atla
                continue
        
        if not processed_data:
            return jsonify({'success': False, 'error': 'Geçerli veri bulunamadı'})
        
        return jsonify({
            'success': True,
            'data': processed_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Dosya okuma hatası: {str(e)}'})

@admin.route('/payments/save', methods=['POST'])
@login_required
@admin_required
def save_payments():
    """Seçilen ödemeleri kaydet"""
    print("Save payments route called")  # Debug print
    
    # CSRF token kontrolü
    try:
        # JSON request'ler için CSRF token header'dan alınır
        csrf_token = request.headers.get('X-CSRFToken')
        if not csrf_token:
            # Form data'dan da kontrol et
            csrf_token = request.form.get('csrf_token')
        
        if csrf_token:
            validate_csrf(csrf_token)
        else:
            return jsonify({'success': False, 'error': 'CSRF token eksik'})
    except Exception as e:
        print(f"CSRF validation error: {e}")  # Debug print
        return jsonify({'success': False, 'error': 'Güvenlik hatası'})
    
    try:
        # JSON verilerini al
        data = request.get_json()
        print(f"Received data: {data}")  # Debug print
        if not data:
            return jsonify({'success': False, 'error': 'Geçersiz veri formatı'})
        
        selected_payments = data.get('payments', [])
        print(f"Selected payments: {selected_payments}")  # Debug print
        
        if not selected_payments:
            return jsonify({'success': False, 'error': 'Kaydedilecek ödeme seçilmedi'})
        
        try:
            saved_count = 0
            for payment_data in selected_payments:
                # Mevcut kayıt kontrolü
                existing_payment = Payment.query.filter_by(
                    transaction_date=datetime.strptime(payment_data['date'], '%d.%m.%Y').date(),
                    description=payment_data['description'],
                    amount=payment_data['amount']
                ).first()
                
                if not existing_payment:
                    payment = Payment(
                        transaction_date=datetime.strptime(payment_data['date'], '%d.%m.%Y').date(),
                        description=payment_data['description'],
                        amount=payment_data['amount'],
                        created_by=current_user.id
                    )
                    db.session.add(payment)
                    saved_count += 1
            
            db.session.commit()
            print(f"Saved {saved_count} payments")  # Debug print
            return jsonify({
                'success': True,
                'message': f'{saved_count} ödeme başarıyla kaydedildi'
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"Database error: {e}")  # Debug print
            return jsonify({'success': False, 'error': f'Kaydetme hatası: {str(e)}'})
            
    except Exception as e:
        print(f"General error: {e}")  # Debug print
        return jsonify({'success': False, 'error': f'Veri işleme hatası: {str(e)}'}) 

@admin.route('/courses/<int:id>/delete-payment/<int:payment_id>', methods=['POST'])
@login_required
@admin_required
def delete_course_payment(id, payment_id):
    """Kurs ödemesini sil"""
    try:
        # CSRF token kontrolü
        csrf_token = request.headers.get('X-CSRFToken')
        if not csrf_token:
            return jsonify({'success': False, 'error': 'CSRF token eksik'})
        
        try:
            validate_csrf(csrf_token)
        except Exception as e:
            return jsonify({'success': False, 'error': 'Güvenlik hatası'})
        
        # Ödemeyi bul
        payment = CoursePayment.query.get_or_404(payment_id)
        
        # Bu ödeme bu kursa ait mi kontrol et
        if payment.enrollment.course_id != id:
            return jsonify({'success': False, 'error': 'Bu ödeme bu kursa ait değil'})
        
        try:
            # Ödemeyi sil
            db.session.delete(payment)
            db.session.commit()
            return jsonify({
                'success': True
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': f'Ödeme silme işlemi sırasında hata oluştu: {str(e)}'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Veri işleme hatası: {str(e)}'}) 

@admin.route('/change-password', methods=['GET', 'POST'])
@login_required
@admin_required
def change_password():
    """Admin şifre değiştirme sayfası"""
    form = AdminPasswordChangeForm()
    if form.validate_on_submit():
        current_user.password_hash = generate_password_hash(form.new_password.data)
        db.session.commit()
        flash('Şifre başarıyla değiştirildi.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/change_password.html', title='Şifre Değiştir', form=form)

@admin.route('/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def profile():
    """Admin profil yönetimi"""
    # Mevcut profili al veya oluştur
    profile = AdminProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = AdminProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    form = AdminProfileForm(obj=profile)
    
    if form.validate_on_submit():
        profile.first_name = form.first_name.data
        profile.last_name = form.last_name.data
        profile.phone = form.phone.data
        
        try:
            db.session.commit()
            flash('Profil başarıyla güncellendi.', 'success')
            return redirect(url_for('admin.profile'))
        except Exception as e:
            db.session.rollback()
            flash('Profil güncellenirken hata oluştu.', 'error')
    
    return render_template('admin/profile.html', form=form, profile=profile) 