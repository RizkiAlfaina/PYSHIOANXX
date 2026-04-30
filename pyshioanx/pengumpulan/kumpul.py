import gspread

# Inisialisasi koneksi (sama seperti kode Anda sebelumnya)
try:
    gc = gspread.service_account(filename='pengumpulan/service_account.json')
    sht2 = gc.open_by_url('https://docs.google.com/spreadsheets/d/1JGaNiwB-bztN4Sf_W_QayTde6UpcALphXjupHNuUct8/edit?gid=0#gid=0')
    worksheet = sht2.get_worksheet(0)
except FileNotFoundError:
    print("Error: File 'pengumpulan/service_account.json' tidak ditemukan.")
    exit()
except Exception as e:
    print(f"Error connecting to Google Sheets: {e}")
    exit()

# --- Logika untuk menginput dan append data ---

# 1. Tentukan data yang ingin Anda masukkan
# Anda bisa mengganti nilai ini, atau menggunakan input() untuk membuatnya dinamis.
date = "Andi Wijaysssssssssa"
hr_input = "11223344"
st_input = "SI-A"
gsr_input = 85
klasifikasi = "normal to mild"

# 2. Susun data dalam list sesuai urutan kolom (Nama, NIM, Kelas, Nilai)
data_row = [date, hr_input, st_input, gsr_input,klasifikasi]

# 3. Tambahkan (append) data tersebut ke worksheet
# Metode append_row() otomatis akan mencari baris kosong pertama setelah data yang ada (termasuk header).
try:
    worksheet.append_row(data_row, value_input_option='USER_ENTERED')
    print(f"Berhasil menambahkan data: {data_row}")
except Exception as e:
    print(f"Gagal menambahkan data: {e}")