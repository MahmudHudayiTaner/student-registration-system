# Öğrenci Yönetim Sistemi

Modern ve kullanıcı dostu bir öğrenci yönetim sistemi. Flask web framework kullanılarak geliştirilmiş, PostgreSQL veritabanı ile desteklenen kapsamlı bir eğitim yönetim platformu.

## 🚀 Özellikler

### 👨‍🎓 Öğrenci Modülü
- **Kayıt ve Giriş**: Güvenli öğrenci kayıt sistemi
- **Profil Yönetimi**: Kişisel bilgileri güncelleme
- **Kurs Başvurusu**: Açık kurslara başvuru yapma
- **Şifre Yönetimi**: Güvenli şifre değiştirme

### 👨‍🏫 Admin Modülü
- **Öğrenci Yönetimi**: Tüm öğrenci kayıtlarını görüntüleme ve yönetme
- **Kurs Yönetimi**: Kurs ekleme, düzenleme ve silme
- **Ödeme Takibi**: Öğrenci ödemelerini takip etme
- **Sistem Yönetimi**: Kullanıcı yetkilerini yönetme

### 💳 Ödeme Sistemi
- **Güvenli Ödeme**: SSL sertifikalı güvenli ödeme
- **Ödeme Geçmişi**: Detaylı ödeme kayıtları
- **Fatura Yönetimi**: Otomatik fatura oluşturma

## 🎨 Tasarım Özellikleri

- **Responsive Tasarım**: Tüm cihazlarda mükemmel görünüm
- **Modern UI/UX**: Kullanıcı dostu arayüz
- **Gradient Renkler**: Modern renk paleti
- **Bootstrap 5**: En güncel Bootstrap framework
- **Custom CSS**: Özel stil tanımlamaları

## 🛠️ Teknoloji Stack

### Backend
- **Flask 2.3.3**: Python web framework
- **SQLAlchemy**: ORM ve veritabanı yönetimi
- **Flask-Login**: Kullanıcı oturum yönetimi
- **Flask-Mail**: E-posta gönderimi
- **Flask-WTF**: Form işleme ve validasyon
- **Werkzeug**: Güvenlik ve şifreleme

### Frontend
- **Bootstrap 5.3.2**: Responsive CSS framework
- **jQuery 3.7.1**: JavaScript kütüphanesi
- **Custom CSS**: Özel stil tanımlamaları
- **Font Awesome**: İkon kütüphanesi

### Veritabanı
- **PostgreSQL**: Ana veritabanı
- **SQLite**: Geliştirme ortamı için

### DevOps
- **Docker**: Konteynerizasyon
- **GitHub Actions**: CI/CD pipeline
- **Gunicorn**: Production web server

## 📦 Kurulum

### Gereksinimler
- Python 3.8+
- PostgreSQL
- Git

### Adım 1: Repository'yi Klonlayın
```bash
git clone https://github.com/kullaniciadi/student-registration-system.git
cd student-registration-system
```

### Adım 2: Sanal Ortam Oluşturun
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### Adım 3: Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### Adım 4: Veritabanını Kurun
```sql
CREATE DATABASE student_registration_system;
```

### Adım 5: Ortam Değişkenlerini Ayarlayın
`.env` dosyası oluşturun:
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://username:password@localhost/student_registration_system
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Adım 6: Veritabanını Başlatın
```bash
flask db init
flask db migrate
flask db upgrade
```

### Adım 7: Uygulamayı Çalıştırın
```bash
flask run
```

Uygulama http://localhost:5000 adresinde çalışacaktır.

## 🐳 Docker ile Kurulum

### Docker Compose ile
```bash
docker-compose up -d
```

### Manuel Docker Kurulumu
```bash
# Image oluşturun
docker build -t student-management-system .

# Container çalıştırın
docker run -p 5000:5000 student-management-system
```

## 📁 Proje Yapısı

```
student-registration-system/
├── app/
│   ├── admin/           # Admin modülü
│   ├── auth/            # Kimlik doğrulama
│   ├── models/          # Veritabanı modelleri
│   ├── static/          # CSS, JS, resimler
│   ├── student/         # Öğrenci modülü
│   └── templates/       # HTML şablonları
├── config.py            # Konfigürasyon
├── requirements.txt     # Python bağımlılıkları
├── run.py              # Uygulama başlatıcı
└── Dockerfile          # Docker konfigürasyonu
```

## 🔧 Konfigürasyon

### Geliştirme Ortamı
```python
# config.py
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_app.db'
```

### Production Ortamı
```python
# config.py
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
```

## 🚀 Deployment

### Heroku
```bash
# Heroku CLI kurulumu
heroku create your-app-name
git push heroku main
```

### AWS
```bash
# Elastic Beanstalk
eb init
eb create
eb deploy
```

### DigitalOcean
```bash
# App Platform
# DigitalOcean dashboard'dan deploy edin
```

## 📊 Veritabanı Şeması

### Ana Tablolar
- **users**: Kullanıcı bilgileri
- **student_profiles**: Öğrenci profilleri
- **admin_profiles**: Admin profilleri
- **courses**: Kurs bilgileri
- **payments**: Ödeme kayıtları

### İlişkiler
- Öğrenci ↔ Kurs (Many-to-Many)
- Öğrenci ↔ Ödeme (One-to-Many)
- Admin ↔ Kurs (One-to-Many)

## 🔒 Güvenlik

- **Şifre Hashleme**: Werkzeug ile güvenli şifreleme
- **CSRF Koruması**: Flask-WTF ile form güvenliği
- **Session Yönetimi**: Flask-Login ile güvenli oturum
- **Input Validasyonu**: Form validasyonu
- **SQL Injection Koruması**: SQLAlchemy ORM

## 📧 E-posta Özellikleri

- **Şifre Sıfırlama**: Güvenli şifre sıfırlama e-postaları
- **Hoş Geldin E-postası**: Yeni kayıt bildirimi
- **Ödeme Onayı**: Ödeme tamamlandığında bildirim

## 🎯 API Endpoints

### Kimlik Doğrulama
- `POST /auth/login` - Giriş
- `POST /auth/register` - Kayıt
- `POST /auth/logout` - Çıkış
- `POST /auth/reset_password` - Şifre sıfırlama

### Öğrenci İşlemleri
- `GET /student/dashboard` - Öğrenci paneli
- `GET /student/courses` - Kurs listesi
- `POST /student/apply_course` - Kurs başvurusu
- `GET /student/profile` - Profil görüntüleme

### Admin İşlemleri
- `GET /admin/dashboard` - Admin paneli
- `GET /admin/students` - Öğrenci listesi
- `POST /admin/add_course` - Kurs ekleme
- `GET /admin/payments` - Ödeme takibi

## 🧪 Test

```bash
# Unit testler
python -m pytest tests/

# Coverage raporu
coverage run -m pytest
coverage report
```

## 📈 Performans

- **Database Indexing**: Optimize edilmiş sorgular
- **Caching**: Redis cache desteği
- **CDN**: Statik dosyalar için CDN
- **Load Balancing**: Çoklu sunucu desteği

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👥 Geliştirici

**Öğrenci Kayıt Sistemi** - Modern ve güvenli eğitim yönetim platformu

## 📞 İletişim

- **GitHub**: [github.com/kullaniciadi/student-management-system](https://github.com/kullaniciadi/student-management-system)
- **E-posta**: contact@example.com

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın! 