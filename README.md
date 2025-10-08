# Gas.in
### PBP D 07 
- Aisyah Saajidah (2406435585)
- Ananda Gautama Sekar Khosmana  (2406352613)
- Keira Nuzahra Anjani (2406423282)
- Nezzaluna Azzahra (2406495741)
- Satirah Nurul Fikriyyah (2406351112)

Platform ini menyediakan wadah bagi pengguna untuk berbagi pengalaman dan tips olahraga melalui forum, kemudian bisa mendaftar event olahraga yang tersedia, dan juga mengelola profil pribadi. Terdapat dua jenis role, yaitu user dan penyelenggara event. Fitur utama terdiri dari Forum, Event, Rekomendasi Event, Dashboard/Profile, dan fitur Ticketing sederhana (booking melalui WhatsApp). Kemudian pada fitur rekomendasi event, user bisa memilih kategori olahraga yang diminati lalu sistem akan menampilkan daftar event sesuai kategori tersebut.

### Modul 
#### 1. EventFilter 
bertindak sebagai discovery engine yang menampilkan rekomendasi event yang dipersonalisasi kepada pengguna. Pengguna dapat dengan mudah menemukan acara melalui filter mendalam berdasarkan kategori lokasi dan jenis olahraga yang pengguna inginkan.
Fungsi utama / fitur yang dimiliki:
a. Halaman default (berisi semua event olahraga tanpa filter) 
b. Fungsi filtering berdasarkan kategori :
- filter lokasi: menampilkan rekomendasi event di lokasi tersebut
- filter jenis olahraga : menampilkan rekomendasi berdasarkan jenis olaharaga

#### 2. ForumKomunitas 
bertindak untuk mendorong interaksi sosial, berbagi pengalaman, dan membangun loyalitas pengguna terhadap platform dan event. Disana pengguna dapat berbagi pengalaman, ulasan, dan foto dari event yang telah dihadiri, serta terlibat dalam diskusi sehingga membangun loyalitas dan keterlibatan jangka panjang.
Fungsi utama / fitur yang dimiliki:
a. Halaman Utama (berisi ulasan-ulasan atau postingan semua pengguna web yang bisa di like dan komen) 
b. Halaman My page (berisi postingan yang di-upload oleh diri kita sendiri) 

#### 3. Venue 
memungkinkan pengguna untuk mem-booking lapangan dengan menampilkan informasi yang sangat detail.
Fungsi utama / fitur yang dimiliki:
a. Header Utama: Berisi nama lapangan
b. Galeri Visual: Menampilkan foto-foto berkualitas tinggi dari lapangan dan seluruh fasilitas pendukung (venue, ruang ganti, tempat parkir, dll.).
c. Detail Lapangan: Mencakup informasi esensial seperti lokasi, deskripsi singkat, tipe lapangan (misalnya: futsal indoor dengan rumput sintetis), dan daftar fasilitas pendukung yang tersedia.
d. tombol Call-to-Action yang akan secara langsung mengarahkan pengguna ke saluran komunikasi (WhatsApp/nomor telepon) yang telah disediakan oleh pemilik/penjual lapangan untuk memproses transaksi dan konfirmasi lebih lanjut secara off-platform.

#### 4. Admin 
Sebagai gatekeeper atau gerbang peninjauan setiap pengajuan event baru. Admin memastikan bahwa seluruh data acara memenuhi standar kelayakan, legalitas, dan kelengkapan konten sebelum ditampilkan ke publik.
Fungsi utama / fitur yang dimiliki:
a. Dashboard Event:
Melihat daftar seluruh event yang:
- Menunggu persetujuan (baru diajukan oleh EventMaker)
- Disetujui (sudah tampil ke publik)
- Ditolak (tidak lolos verifikasi)

#### 5. EventMaker 
memungkinkan user untuk untuk membuat dan mengelola event. EventMaker bisa mengajukan event baru yang kemudian akan direview oleh Admin sebelum tampil ke publik.
Fungsi utama / fitur yang dimiliki:
a. Buat Event Baru:
Mengisi form berisi detail event (nama, tanggal, lokasi, deskripsi, gambar/banner, dan jenis olahraga).
Setelah submit → status event = Menunggu persetujuan admin.
b. Edit Event:
Bisa mengubah detail event selama event belum disetujui.
Jika sudah disetujui dan ingin ubah → perlu ajukan revisi yang kembali diverifikasi admin.
c. Hapus Event:
Bisa menghapus event miliknya (hanya sebelum event dimulai).
d. Lihat Status Event:
Melihat apakah event-nya sedang menunggu, disetujui, atau ditolak (beserta alasan).
e. Fitur Join Event:
Memberikan opsi bagi audience (user umum) untuk join atau booking seat/tiket.
Melihat daftar peserta yang sudah join (kalau event-nya publik).
Bisa atur kuota peserta, batas waktu pendaftaran, dsb.

#### 6. Authentication
bertanggung jawab untuk mengelola proses login, registrasi, dan manajemen akses pengguna ke sistem. Tujuannya memastikan bahwa hanya pengguna yang terdaftar dan terverifikasi yang dapat mengakses fitur tertentu sesuai peran mereka (Admin dan Reguler User)
Fungsi utama / fitur yang dimiliki:
a. Registrasi (Sign Up):
Pengguna dapat membuat akun baru dengan mengisi data seperti:
- Username
- Password
- Password konfirmasi
- Role (Admin, Regular user)
b. Login (Sign In):
Pengguna masuk ke sistem menggunakan username dan password yang valid.
Sistem memverifikasi kredensial dan menentukan akses sesuai peran pengguna.
c. Logout:
Mengakhiri sesi pengguna dan membersihkan token/session yang aktif.
d. Manajemen Role & Akses:
Setiap pengguna memiliki role yang menentukan hak akses( Admin & Reguler User)

### Sumber Dataset 
- [AYO](https://ayo.co.id/main-bareng)

### Role User
- #### User
    User berperan sebagai partisipan utama dalam platform ini. Mereka dapat berbagi pengalaman serta tips seputar olahraga melalui forum, mencari dan mendaftar pada event olahraga yang diminati, serta mengelola profil pribadi mereka. Melalui fitur Rekomendasi Event, user juga dapat memilih kategori olahraga favorit agar sistem menampilkan daftar event yang sesuai minatnya.
- #### Admin
    Admin berfungsi sebagai gerbang pengawasan yang menilai setiap pengajuan event sebelum ditayangkan ke publik. Ia memastikan seluruh acara telah memenuhi aspek kelayakan, legalitas, serta kelengkapan konten, sehingga hanya event yang sesuai standar yang dapat dipublikasikan.
