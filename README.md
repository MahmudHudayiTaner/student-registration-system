# Kafka Dil Akademisi - Öğrenci Yönetim Sistemi

Modern ve kapsamlı bir dil kursu öğrenci yönetim sistemi. Flask framework kullanılarak geliştirilmiş, güvenli ve kullanıcı dostu bir web uygulaması.

## 🎯 Proje Hakkında

Kafka Dil Akademisi, dil kursları için özel olarak tasarlanmış bir öğrenci yönetim sistemidir. Sistem, öğrenci kayıtları, kurs yönetimi, ödeme takibi ve admin paneli gibi temel işlevleri içerir.

## 🚀 Özellikler

### 👨‍💼 Admin Paneli
- **Öğrenci Yönetimi**: Öğrenci listesi, arama, filtreleme, düzenleme
- **Kurs Yönetimi**: Kurs ekleme, düzenleme, program yönetimi
- **Ödeme Takibi**: Ödeme durumu, ekstre yükleme, ödeme kayıtları
- **İstatistikler**: Dashboard'da detaylı istatistikler ve grafikler
- **Hızlı İşlemler**: Kolay erişim için hızlı işlem kartları
- **Şifre Yönetimi**: Güvenli admin şifre değiştirme sistemi

### 👨‍🎓 Öğrenci Paneli
- **Profil Yönetimi**: Kişisel bilgi güncelleme
- **Şifre Değiştirme**: Güvenli şifre değiştirme
- **Kurs Bilgileri**: Kayıtlı kurslar ve programlar
- **Ödeme Durumu**: Ödeme geçmişi ve durumu

### 🔐 Güvenlik Özellikleri
- **Güvenli Kimlik Doğrulama**: Flask-Login ile oturum yönetimi
- **Rol Tabanlı Erişim**: Admin ve öğrenci rolleri
- **CSRF Koruması**: Form güvenliği
- **Rate Limiting**: İstek sınırlama
- **Input Sanitization**: Kullanıcı girdilerinin temizlenmesi
- **Şifre Hashleme**: Güvenli şifre saklama
- **Admin Şifre Değiştirme**: Güvenli şifre güncelleme sistemi

### 📧 Email Sistemi
- **Profil Güncellemeleri**: Otomatik email bildirimleri
- **SMTP Desteği**: Gmail ve diğer SMTP servisleri
- **HTML Template'leri**: Profesyonel email tasarımları

### 🎨 Modern UI/UX
- **Responsive Tasarım**: Bootstrap 5 ile modern arayüz
- **Gradient Renkler**: Kafka Dil Akademisi renk paleti
- **Hover Efektleri**: Etkileşimli kartlar ve butonlar
- **Grafikler**: Chart.js ile ödeme durumu grafikleri
- **Modal'lar**: Modern popup'lar ve form'lar
- **Şifre Değiştirme Arayüzü**: Kullanıcı dostu güvenlik formu

## 📋 Gereksinimler

- **Python**: 3.8 veya üzeri
- **PostgreSQL**: 12 veya üzeri
- **pip**: Python paket yöneticisi
- **Git**: Versiyon kontrol sistemi

## 🛠️ Kurulum

### 1. Repository'yi Klonlayın
```bash
git clone https://github.com/MahmudHudayiTaner/kafka-proje.git
cd kafka-proje
```

### 2. Virtual Environment Oluşturun
```bash
python -m venv venv

# Linux/Mac için:
source venv/bin/activate

# Windows için:
venv\Scripts\activate
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Environment Variables Ayarlayın
```bash
cp env.example .env
# .env dosyasını düzenleyin
```

### 5. PostgreSQL Veritabanı Oluşturun
```sql
CREATE DATABASE kafka_dil_akademisi;
```

### 6. Veritabanı Migration'larını Çalıştırın
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 7. Uygulamayı Çalıştırın
```bash
python run.py
```

Uygulama `http://localhost:5000` adresinde çalışacaktır.

## 🔧 Konfigürasyon

### Environment Variables

`.env` dosyasında aşağıdaki değişkenleri ayarlayın:

```env
# Flask Ayarları
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# PostgreSQL Veritabanı
DATABASE_URL=postgresql://username:password@localhost/kafka_dil_akademisi

# Email Ayarları (Gmail için)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

## 👥 Kullanım

### Varsayılan Admin Hesabı

Uygulama ilk çalıştırıldığında otomatik olarak oluşturulur:
- **Email**: admin@admin.com
- **Şifre**: admin123

### Öğrenci Kaydı

1. Ana sayfadan "Kayıt Ol" butonuna tıklayın
2. Gerekli bilgileri doldurun (ad, soyad, email, şifre)
3. Kayıt formunu gönderin
4. Giriş yapın ve profil bilgilerinizi tamamlayın

### Admin Paneli

1. Admin hesabı ile giriş yapın
2. Dashboard'da genel istatistikleri görün
3. Hızlı İşlemler kartlarından ilgili bölüme erişin:
   - **Öğrenci Yönetimi**: Öğrenci listesi ve yönetimi
   - **Kurs Yönetimi**: Kurs ekleme ve düzenleme
   - **Ödeme Yönetimi**: Ödeme takibi ve ekstre yükleme

### Admin Şifre Değiştirme

1. Admin paneline giriş yapın
2. Dashboard'da "Şifre Değiştir" butonuna tıklayın
3. Mevcut şifrenizi girin
4. Yeni güçlü şifrenizi belirleyin
5. Şifreyi onaylayın ve kaydedin

## 🏗️ Proje Yapısı

```
kafka/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models/                  # Veritabanı modelleri
│   │   ├── user.py             # Kullanıcı modeli
│   │   ├── student_profile.py  # Öğrenci profili
│   │   ├── course.py           # Kurs modeli
│   │   └── payment.py          # Ödeme modeli
│   ├── auth/                   # Kimlik doğrulama
│   │   ├── forms.py           # Giriş/kayıt formları
│   │   └── routes.py          # Auth route'ları
│   ├── admin/                  # Admin paneli
│   │   ├── forms.py           # Admin formları (şifre değiştirme dahil)
│   │   └── routes.py          # Admin route'ları
│   ├── student/                # Öğrenci işlemleri
│   │   ├── forms.py           # Öğrenci formları
│   │   └── routes.py          # Öğrenci route'ları
│   ├── templates/              # HTML template'leri
│   │   ├── admin/             # Admin sayfaları
│   │   │   ├── dashboard.html # Ana dashboard
│   │   │   ├── courses.html   # Kurs yönetimi
│   │   │   └── change_password.html # Şifre değiştirme
│   │   ├── auth/              # Giriş/kayıt sayfaları
│   │   ├── student/           # Öğrenci sayfaları
│   │   └── emails/            # Email template'leri
│   └── static/                 # Statik dosyalar
│       └── style.css          # CSS stilleri
├── config.py                   # Konfigürasyon
├── run.py                      # Uygulama başlatıcı
├── requirements.txt            # Python bağımlılıkları
└── README.md                  # Proje dokümantasyonu
```

## 🎨 Tasarım Özellikleri

### Renk Paleti
- **Ana Renk**: #1a237e (Koyu Mavi)
- **İkincil Renk**: #1976d2 (Mavi)
- **Başarı**: #4caf50 (Yeşil)
- **Uyarı**: #ff9800 (Turuncu)
- **Tehlike**: #f44336 (Kırmızı)

### UI Bileşenleri
- **Gradient Arka Planlar**: Modern görünüm
- **Hover Efektleri**: Etkileşimli kartlar
- **Responsive Kartlar**: Mobil uyumlu
- **Modal'lar**: Modern popup'lar
- **Grafikler**: Chart.js entegrasyonu
- **Şifre Değiştirme Formu**: Güvenli ve kullanıcı dostu

## 🔒 Güvenlik

### Uygulanan Güvenlik Önlemleri
- **Rate Limiting**: Login ve register işlemleri için istek sınırlama
- **CSRF Koruması**: Tüm formlarda CSRF token
- **Input Sanitization**: Kullanıcı girdilerinin temizlenmesi
- **SQL Injection Koruması**: SQLAlchemy ORM kullanımı
- **Session Güvenliği**: Güvenli session konfigürasyonu
- **Password Hashing**: Güvenli şifre hashleme
- **Admin Şifre Değiştirme**: Güvenli şifre güncelleme sistemi

### Şifre Güvenliği
- **Minimum 8 Karakter**: Şifre uzunluğu zorunluluğu
- **Hashleme**: Werkzeug ile güvenli hashleme
- **Validasyon**: Mevcut şifre doğrulama
- **Güvenlik İpuçları**: Kullanıcı eğitimi

## 📧 Email Sistemi

### Özellikler
- **Profil Güncellemeleri**: Otomatik email bildirimleri
- **HTML Template'leri**: Profesyonel email tasarımları
- **SMTP Desteği**: Gmail ve diğer SMTP servisleri

### Gmail Kurulumu
1. Gmail'de 2FA'yı etkinleştirin
2. App Password oluşturun
3. `.env` dosyasında email ayarlarını yapın

## 🚀 Production Deployment

### 1. Environment Variables
```env
FLASK_ENV=production
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=True
```

### 2. Güvenli SECRET_KEY
```python
import secrets
secrets.token_hex(32)
```

### 3. WSGI Server (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### 4. Nginx Konfigürasyonu
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🐛 Hata Ayıklama

### Yaygın Sorunlar

1. **Veritabanı Bağlantı Hatası**
   - PostgreSQL servisinin çalıştığından emin olun
   - Veritabanı URL'sini kontrol edin

2. **Email Gönderim Hatası**
   - SMTP ayarlarını kontrol edin
   - Gmail App Password'ünü doğru girdiğinizden emin olun

3. **Import Hatası**
   - Virtual environment'ın aktif olduğundan emin olun
   - Bağımlılıkların yüklendiğini kontrol edin

### Loglar
Uygulama logları terminal'de görüntülenir. Production'da log dosyalarına yönlendirin.

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📞 İletişim

Sorularınız için issue açabilir veya email gönderebilirsiniz.

---

**Kafka Dil Akademisi** - Modern ve güvenli öğrenci yönetim sistemi 