# 🌫️ Beijing Air Quality Dashboard

Ini adalah proyek Analisis Data menggunakan dataset **PRSA Beijing Air Quality (2013-2017)**. Proyek ini mencakup eksplorasi data (EDA) melalui Jupyter Notebook dan pembuatan dashboard interaktif menggunakan **Streamlit**.

## 🌐 Live Dashboard
Anda bisa melihat dashboard yang sudah di-deploy secara online melalui tautan berikut:
**[Beijing Air Quality Dashboard - Streamlit](https://submission-data-analysis-9njhez8qlzv8bfswnwgsc5.streamlit.app/)**

## 📂 Struktur Direktori
- `/PRSA_Data_20130301-20170228/`: Folder berisi dataset raw berformat `.csv` untuk 12 stasiun pemantauan.
- `notebook_air_quality.ipynb`: Jupyter Notebook yang berisi proses analisis data mulai dari Data Wrangling, Exploratory Data Analysis (EDA), hingga Explanatory Analysis.
- `dashboard.py`: Script Python utama untuk menjalankan aplikasi dashboard Streamlit.
- `requirements.txt`: Daftar library Python yang dibutuhkan untuk menjalankan proyek ini.
- `url.txt`: Tautan menuju aplikasi Streamlit yang telah di-deploy.

## 🚀 Cara Menjalankan Proyek secara Lokal

### 1. Persiapan Environment (Opsional namun disarankan)
Sangat disarankan untuk menggunakan virtual environment agar *library* tidak bentrok dengan proyek Python Anda yang lain.

**MacOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install Dependencies
Pastikan Anda sudah berada di dalam folder proyek ini (`submission`), lalu install seluruh *library* yang dibutuhkan dengan perintah:
```bash
pip install -r requirements.txt
```

### 3. Menjalankan Dashboard Streamlit
Setelah semua dependencies terinstall, Anda bisa langsung menjalankan dashboard dengan mengetikkan perintah berikut di terminal:
```bash
streamlit run dashboard.py
```
Aplikasi akan secara otomatis terbuka di browser default Anda pada alamat `http://localhost:8501`.

## 🛠️ Library yang Digunakan
- `pandas` - Manipulasi dan analisis data
- `numpy` - Komputasi numerik
- `matplotlib` & `seaborn` - Visualisasi data statis
- `streamlit` - Pembuatan dashboard web interaktif