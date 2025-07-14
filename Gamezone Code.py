import psycopg2
import os
#import getpass  # Untuk input password yang lebih aman
import pandas as pd
import datetime
from datetime import timedelta

def connect_db():
    try:
        conn = psycopg2.connect(
            host="Localhost",
            database="Gamezone PS",
            user="postgres",
            password="warungijo"
        )
        cur = conn.cursor()
        return conn, cur
    except Exception as e:
        print(f"Koneksi gagal: {e}")
        return None, None  # return dua None agar bisa di-unpack

def register():
    os.system('cls')
    print("====================================[REGISTRASI]====================================")
    
    conn, cur = connect_db()
    if conn is None or cur is None:
        print("Gagal terhubung ke database.")
        input("Tekan Enter untuk kembali ke menu...")
        return login()
    
    try:
        username = input("Masukkan username baru: ").strip()
        no_telp = input("Masukkan nomor telepon: ").strip()
        password = input("Masukkan password: ").strip()
        role = 'Customer'  # default role

        if not username or not password or not no_telp:
            print("Semua field wajib diisi!")
            input("Tekan Enter untuk ulangi...")
            return register()

        # Cek apakah username + no telp sudah terdaftar
        cur.execute("""
            SELECT 1 FROM users 
            WHERE username = %s AND no_telepon = %s
        """, (username, no_telp))
        if cur.fetchone():
            print("Username dan No. Telepon sudah terdaftar.")
            input("Tekan Enter untuk kembali ke menu...")
            return login()

        cur.execute("""
            INSERT INTO users (role, username, password, no_telepon)
            VALUES (%s, %s, %s, %s)
        """, (role, username, password, no_telp))
        conn.commit()
        print("Registrasi berhasil! Silakan login.")
        input("Tekan Enter untuk kembali ke menu login...")
        login()

    except Exception as e:
        print(f"Gagal registrasi: {e}")
        input("Tekan Enter untuk kembali...")
        return login()
    finally:
        conn.close()


def login():
    os.system('cls')
    print("""
    ░██████╗░░█████╗░███╗░░░███╗███████╗███████╗░█████╗░███╗░░██╗███████╗
    ██╔════╝░██╔══██╗████╗░████║██╔════╝╚════██║██╔══██╗████╗░██║██╔════╝
    ██║░░██╗░███████║██╔████╔██║█████╗░░░░███╔═╝██║░░██║██╔██╗██║█████╗░░
    ██║░░╚██╗██╔══██║██║╚██╔╝██║██╔══╝░░██╔══╝░░██║░░██║██║╚████║██╔══╝░░
    ╚██████╔╝██║░░██║██║░╚═╝░██║███████╗███████╗╚█████╔╝██║░╚███║███████╗
    ░╚═════╝░╚═╝░░╚═╝╚═╝░░░░░╚═╝╚══════╝╚══════╝░╚════╝░╚═╝░░╚══╝╚══════╝
    """)
    print("1. Login")
    print("2. Registrasi")
    print("3. Keluar")

    pilih = input("Pilih opsi (1/2/3): ").strip()
    if pilih == '2':
        register()
        return
    elif pilih == '3':
        print("Sampai jumpa!")
        exit()

    os.system('cls')
    conn, cur = connect_db()

    print("====================================[LOGIN]====================================")
    username = input("Masukkan username: ")
    password = input("Masukkan password: ")

    if conn is None or cur is None:
        print("Gagal terhubung ke database. Silakan coba lagi.")
        input("Klik Enter untuk melanjutkan...")
        return login()

    try:
        cur.execute("""
            SELECT username, role FROM users 
            WHERE username = %s AND password = %s
        """, (username, password))
        
        user_data = cur.fetchone()
        
        if user_data:
            username, role = user_data
            print(f"\nSelamat datang, {username}!")
            input("Klik Enter untuk melanjutkan...")

            if role == 'Admin':
                menu_admin(username)
            else:
                menu_customer(username)
        else:
            print("\nUsername atau password salah!")
            input("Klik Enter untuk mencoba lagi...")
            return login()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()


def transaksi():
    conn, cur = connect_db()
    if conn is None or cur is None:
        print("Gagal koneksi ke database.")
        return

    try:
        # Ambil semua data transaksi
        query = """SELECT * FROM transaksi
        ORDER BY transaksi_id"""
        cur.execute(query)
        data = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(data, columns=colnames)
        # Tampilkan seluruh kolom dan isi panjangA

        # Pilih kolom penting saja
        tampilan_df = df[['transaksi_id', 'tanggal_transaksi', 'status_transaksi', 'no_rekening', 'nama_pemilik_rekening']]
        print("\n=== Data Transaksi ===")
        print(tampilan_df.to_string(index=False))


        if not data:
            print("Belum ada transaksi yang tercatat.")
            input("\nTekan Enter untuk kembali ke menu...")
            return

        # Pilih ID Transaksi yang ingin diedit
        id_transaksi = input("\nMasukkan ID Transaksi yang ingin diubah statusnya (atau Enter untuk batal): ")
        if id_transaksi.strip() == "":
            print("Pembatalan pengubahan status.")
            input("\nTekan Enter untuk kembali ke menu...")
            return

        # Cek apakah ID ada di data
        cur.execute("SELECT * FROM transaksi WHERE transaksi_id = %s", (id_transaksi,))
        transaksi_terpilih = cur.fetchone()

        if not transaksi_terpilih:
            print("ID Transaksi tidak ditemukan.")
            input("\nTekan Enter untuk kembali ke menu...")
            return

        # Pilihan status
        print("\nPilih status baru:")
        print("1. Paid")
        print("2. Canceled")
        pilihan = input("Masukkan pilihan (1/2): ")

        if pilihan == '1':
            status_baru = 'paid'
        elif pilihan == '2':
            status_baru = 'canceled'
        else:
            print("Pilihan tidak valid.")
            input("\nTekan Enter untuk kembali ke menu...")
            return

        # Update status di database
        cur.execute("""
            UPDATE transaksi SET status_transaksi = %s WHERE transaksi_id = %s
        """, (status_baru, id_transaksi))
        conn.commit()

        print(f"\nStatus transaksi dengan ID {id_transaksi} berhasil diubah menjadi '{status_baru}'.")
        input("\nTekan Enter untuk kembali ke menu...")

    except Exception as e:
        print(f"Terjadi error: {e}")
        input("\nTekan Enter untuk kembali ke menu...")

    finally:
        conn.close()


def kelola_playstation():
    conn, cur = connect_db()
    if conn is None or cur is None:
        print("Gagal koneksi ke database.")
        return

    while True:
        os.system('cls')
        print("=== KELOLA SLOT PLAYSTATION ===")
        print("1. Lihat semua slot")
        print("2. Tambah slot baru")
        print("3. Ubah status slot")
        print("4. Hapus slot")
        print("5. Kelola daftar game di slot")
        print("6. Kembali ke menu admin")

        pilihan = input("Pilih menu (1/2/3/4/5): ")

        if pilihan == '1':
            cur.execute("SELECT * FROM konsol ORDER BY konsol_id")
            data = cur.fetchall()
            if data:
                print("\n--- Daftar Slot Playstation ---")
                df = pd.DataFrame(data, columns=[desc[0] for desc in cur.description])
                print(df.to_string(index=False))
            else:
                print("Belum ada slot Playstation.")
            input("\nTekan Enter untuk melanjutkan...")

        elif pilihan == '2':
            nama = input("Masukkan nama konsol : ")
            status = input("Masukkan status (1 = Tersedia, 0 = Tidak Tersedia): ")
            cur.execute("INSERT INTO konsol (nama_konsol, status_konsol) VALUES (%s, %s)", (nama, status))
            conn.commit()
            print("Slot Playstation berhasil ditambahkan!")
            input("\nTekan Enter untuk melanjutkan...")

        elif pilihan == '3':
            id_konsol = input("Masukkan ID slot yang ingin diubah: ")
            if not id_konsol.strip().isdigit():
                print("ID tidak boleh kosong dan harus berupa angka.")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            cur.execute("SELECT * FROM konsol WHERE konsol_id = %s", (id_konsol,))
            if cur.fetchone():
                status_baru = input("Masukkan status baru (1 = Tersedia, 0 = Tidak Tersedia): ")
                cur.execute("UPDATE konsol SET status_konsol = %s WHERE konsol_id = %s", (status_baru, id_konsol))
                conn.commit()
                print("Status berhasil diubah.")
            else:
                print("ID tidak ditemukan.")
            input("\nTekan Enter untuk melanjutkan...")

        elif pilihan == '4':
            id_konsol = input("Masukkan ID slot yang ingin dihapus: ")
            if not id_konsol.strip().isdigit():
                print("ID tidak boleh kosong dan harus berupa angka.")
                input("\nTekan Enter untuk melanjutkan...")
                continue
            cur.execute("SELECT * FROM konsol WHERE konsol_id = %s", (id_konsol,))
            if cur.fetchone():
                konfirmasi = input("Yakin ingin menghapus slot ini? (y/n): ")
                if konfirmasi.lower() == 'y':
                    cur.execute("DELETE FROM konsol WHERE konsol_id = %s", (id_konsol,))
                    conn.commit()
                    print("Slot berhasil dihapus.")
                    cur.execute("""
                        SELECT setval(
                            pg_get_serial_sequence('konsol', 'konsol_id'),
                            COALESCE((SELECT MAX(konsol_id) FROM konsol), 0),
                            true
                        )
                    """)
                else:
                    print("Penghapusan dibatalkan.")
            else:
                print("ID tidak ditemukan.")
            input("\nTekan Enter untuk melanjutkan...")

        elif pilihan == '5':
            id_konsol = input("Masukkan ID konsol: ")
            if not id_konsol.strip().isdigit():
                print("ID tidak boleh kosong dan harus berupa angka.")
                input("\nTekan Enter untuk melanjutkan...")
                continue

            cur.execute("SELECT * FROM konsol WHERE konsol_id = %s", (id_konsol,))
            data_konsol = cur.fetchone()

            if data_konsol:
                os.system("cls")
                print(f"\n=== INFORMASI KONSOL ID {id_konsol} ===")
                print(f"Nama Konsol: {data_konsol[1]}")
                print(f"Status     : {'Tersedia' if data_konsol[2] == 1 else 'Tidak Tersedia'}")
                input("\nTekan Enter untuk melanjutkan ke pengelolaan game...")

                while True:
                    os.system('cls')
                    print(f"=== KELOLA GAME DI KONSOL ID {id_konsol} ===")
                    print("1. Lihat daftar game")
                    print("2. Tambah game")
                    print("3. Hapus game")
                    print("4. Kembali")

                    sub_pilihan = input("Pilih menu (1/2/3/4): ")

                    if sub_pilihan == '1':
                        cur.execute("""
                            SELECT g.game_id, g.nama_game
                            FROM detail_konsol dk
                            JOIN game g ON dk.game_game_id = g.game_id
                            WHERE dk.konsol_konsol_id = %s
                        """, (id_konsol,))
                        games = cur.fetchall()
                        if games:
                            print("\n--- Daftar Game di Konsol ---")
                            for game in games:
                                print(f"{game[0]} - {game[1]}")
                        else:
                            print("Belum ada game di konsol ini.")
                        input("\nTekan Enter untuk lanjut...")

                    elif sub_pilihan == '2':
                        print("\n--- Daftar Game yang Tersedia ---")
                        cur.execute("""
                            SELECT game_id, nama_game
                            FROM game
                            WHERE game_id NOT IN (
                                SELECT game_game_id FROM detail_konsol WHERE konsol_konsol_id = %s
                            )
                        """, (id_konsol,))
                        available_games = cur.fetchall()

                        if not available_games:
                            print("Semua game sudah ditambahkan ke konsol ini.")
                            input("\nTekan Enter untuk kembali...")
                            continue

                        for game in available_games:
                            print(f"{game[0]} - {game[1]}")

                        id_game = input("Masukkan ID game yang ingin ditambahkan: ")
                        cur.execute("SELECT 1 FROM game WHERE game_id = %s", (id_game,))
                        if not cur.fetchone():
                            print("ID game tidak ditemukan.")
                        else:
                            # Cek apakah game sudah ada di konsol
                            cur.execute("""
                                SELECT 1 FROM detail_konsol 
                                WHERE konsol_konsol_id = %s AND game_game_id = %s
                            """, (id_konsol, id_game))
                            if cur.fetchone():
                                print("Game sudah ada di konsol ini, tidak dapat ditambahkan lagi.")
                            else:
                                cur.execute("""
                                    INSERT INTO detail_konsol (konsol_konsol_id, game_game_id)
                                    VALUES (%s, %s)
                                """, (id_konsol, id_game))
                                conn.commit()
                                print("Game berhasil ditambahkan!")
                        input("\nTekan Enter untuk lanjut...")


                    elif sub_pilihan == '3':
                        print("\n--- Daftar Game di Konsol ---")
                        cur.execute("""
                            SELECT g.game_id, g.nama_game
                            FROM detail_konsol dk
                            JOIN game g ON dk.game_game_id = g.game_id
                            WHERE dk.konsol_konsol_id = %s
                        """, (id_konsol,))
                        games = cur.fetchall()
                        if games:
                            for game in games:
                                print(f"{game[0]} - {game[1]}")
                        else:
                            print("Tidak ada game untuk dihapus.")
                            input("\nTekan Enter untuk kembali...")
                            continue

                        id_game = input("Masukkan ID game yang ingin dihapus: ")
                        cur.execute("DELETE FROM detail_konsol WHERE konsol_konsol_id = %s AND game_game_id = %s", (id_konsol, id_game))
                        conn.commit()
                        print("Game berhasil dihapus.")
                        input("\nTekan Enter untuk lanjut...")

                    elif sub_pilihan == '4':
                        break
                    else:
                        print("Pilihan tidak valid.")
                        input("\nTekan Enter untuk lanjut...")

            else:
                print("ID Konsol tidak ditemukan.")
         
                input("\nTekan Enter untuk lanjut...")
        
        elif pilihan == '6':
            print("Kembali ke menu admin...")
            input("\nTekan Enter untuk lanjut...")
            break  # keluar dari while dan kembali ke menu_admin()

        else:
            print("Pilihan tidak valid.")
            input("\nTekan Enter untuk melanjutkan...")


def kelola_data_pelanggan():
    conn, cur = connect_db()

    while True:
        os.system('cls')
        print("=== KELOLA DATA PELANGGAN ===")
        print("1. Lihat semua pelanggan")
        print("2. Cari pelanggan")
        print("3. Edit data pelanggan")
        print("4. Hapus pelanggan")
        print("5. Kembali")

        pilihan = input("Pilih menu (1-5): ")

        if pilihan == '1':
            cur.execute("SELECT users_id, username FROM users WHERE role = 'Customer'")
            pelanggan = cur.fetchall()
            print("\n--- Daftar Pelanggan ---")
            for p in pelanggan:
                print(f"ID: {p[0]} | Username: {p[1]}")
            input("\nTekan Enter untuk lanjut...")

        elif pilihan == '2':
            cari = input("Masukkan username yang ingin dicari: ")
            cur.execute("SELECT * FROM users WHERE username ILIKE %s AND role = 'Customer'", ('%' + cari + '%',))
            hasil = cur.fetchall()
            if hasil:
                for data in hasil:
                    print(data)
            else:
                print("Tidak ditemukan.")
            input("\nTekan Enter untuk lanjut...")

        elif pilihan == '3':
            id_edit = input("Masukkan ID pelanggan yang ingin diedit: ")
            cur.execute("SELECT * FROM users WHERE users_id = %s AND role = 'Customer'", (id_edit,))
            data = cur.fetchone()
            if data:
                new_pass = input("Masukkan password baru (kosongkan jika tidak ingin mengubah): ")
                if new_pass.strip() != "":
                    cur.execute("UPDATE users SET password = %s WHERE users_id = %s", (new_pass, id_edit))
                    conn.commit()
                    print("Password berhasil diperbarui.")
                else:
                    print("Tidak ada perubahan.")
            else:
                print("ID tidak ditemukan.")
            input("\nTekan Enter untuk lanjut...")

        elif pilihan == '4':
            id_hapus = input("Masukkan ID pelanggan yang ingin dihapus: ")
            confirm = input("Yakin ingin menghapus? (y/n): ")
            if confirm.lower() == 'y':
                cur.execute("DELETE FROM users WHERE users_id = %s AND role = 'Customer'", (id_hapus,))
                conn.commit()
                print("Data berhasil dihapus.")
            else:
                print("Dibatalkan.")
            input("\nTekan Enter untuk lanjut...")

        elif pilihan == '5':
            break
        else:
            print("Pilihan tidak valid.")
            input("\nTekan Enter untuk lanjut...")

    conn.close()


def kelola_harga_paket_main():
    conn, cur = connect_db()

    while True:
        os.system('cls')
        print("=== KELOLA HARGA PAKET MAIN ===")
        print("1. Lihat semua paket")
        print("2. Tambah paket baru")
        print("3. Edit paket")
        print("4. Hapus paket")
        print("5. Kembali")

        pilihan = input("Pilih menu (1-5): ")

        if pilihan == '1':
            cur.execute("SELECT * FROM paket_sewa")
            data = cur.fetchall()
            print("\n--- Daftar Paket Main ---")
            for row in data:
                print(f"ID: {row[0]}, Durasi: {row[2]} jam, Harga: Rp{row[3]}")
            input("\nTekan Enter untuk lanjut...")

        elif pilihan == '2':
            nama_paket = input("Masukkan nama paket: ")
            durasi = input("Masukkan durasi (dalam jam): ")
            harga = input("Masukkan harga paket: ")
            cur.execute("INSERT INTO paket_sewa (nama_paket, durasi, harga) VALUES (%s, %s, %s)", (nama_paket, durasi, harga))
            conn.commit()
            print("Paket berhasil ditambahkan!")
            input("\nTekan Enter untuk lanjut...")

        elif pilihan == '3':
            id_paket = input("Masukkan ID paket yang ingin diedit: ")
            cur.execute("SELECT * FROM paket_sewa WHERE paket_sewa_id = %s", (id_paket,))
            paket = cur.fetchone()
            if paket:
                nama_paket = input(f"Nama paket baru (kosongkan jika tidak diubah, saat ini {paket[1]}): ")
                durasi = input(f"Durasi baru (kosongkan jika tidak diubah, saat ini {paket[2]} jam): ")
                harga = input(f"Harga baru (kosongkan jika tidak diubah, saat ini Rp{paket[3]}): ")

                if nama_paket.strip() != "":
                    cur.execute("UPDATE paket_sewa SET nama_paket = %s WHERE paket_sewa_id = %s", (nama_paket, id_paket))
                if durasi.strip() != "":
                    cur.execute("UPDATE paket_sewa SET durasi = %s WHERE paket_sewa_id = %s", (durasi, id_paket))
                if harga.strip() != "":
                    cur.execute("UPDATE paket_sewa SET harga = %s WHERE paket_sewa_id = %s", (harga, id_paket))
                conn.commit()
                print("Paket berhasil diperbarui.")
            else:
                print("Paket tidak ditemukan.")
            input("\nTekan Enter untuk lanjut...")

        elif pilihan == '4':
            id_hapus = input("Masukkan ID paket yang ingin dihapus: ")
            confirm = input("Yakin ingin menghapus paket ini? (y/n): ")
            if confirm.lower() == 'y':
                cur.execute("DELETE FROM paket_sewa WHERE paket_sewa_id = %s", (id_hapus,))
                conn.commit()
                print("Paket berhasil dihapus.")
                cur.execute("""
                    SELECT setval(
                        pg_get_serial_sequence('paket_sewa', 'paket_sewa_id'),
                        COALESCE((SELECT MAX(paket_sewa_id) FROM paket_sewa), 0),
                        true
                    )
                """)
            else:
                print("Penghapusan dibatalkan.")
            input("\nTekan Enter untuk lanjut...")

        elif pilihan == '5':
            break
        else:
            print("Pilihan tidak valid!")
            input("\nTekan Enter untuk lanjut...")

    conn.close()


def melihat_laporan_keuntungan():
    conn, cur = connect_db()
    os.system('cls')
    print("=== LAPORAN KEUNTUNGAN ===\n")

    try:
        # Total Pendapatan Keseluruhan
        cur.execute("""
            SELECT COALESCE(SUM(dp.sub_total), 0)
            FROM detail_paket dp
            JOIN transaksi t ON dp.transaksi_transaksi_ID = t.transaksi_ID
            WHERE t.status_transaksi = 'paid';
        """)
        total_pendapatan = cur.fetchone()[0]
        print(f"Total Pendapatan Keseluruhan: Rp{total_pendapatan:,}\n")

        print("1. Lihat Pendapatan Per Hari")
        print("2. Lihat Pendapatan Per Bulan")
        print("3. Kembali ke Menu\n")

        pilihan = input("Pilih menu (1/2/3): ")

        if pilihan == '1':
            # Pendapatan per hari
            cur.execute("""
                SELECT t.tanggal_transaksi, SUM(dp.sub_total) AS total
                FROM transaksi t
                JOIN detail_paket dp ON dp.transaksi_transaksi_ID = t.transaksi_ID
                WHERE t.status_transaksi = 'paid'
                GROUP BY t.tanggal_transaksi
                ORDER BY t.tanggal_transaksi;
            """)
            hasil = cur.fetchall()
            print("\n=== Pendapatan Per Hari ===")
            for tanggal, total in hasil:
                print(f"{tanggal}: Rp{total:,}")

        elif pilihan == '2':
            # Pendapatan per bulan
            cur.execute("""
                SELECT TO_CHAR(t.tanggal_transaksi, 'YYYY-MM') AS bulan, SUM(dp.sub_total) AS total
                FROM transaksi t
                JOIN detail_paket dp ON dp.transaksi_transaksi_ID = t.transaksi_ID
                WHERE t.status_transaksi = 'paid'
                GROUP BY bulan
                ORDER BY bulan;
            """)
            hasil = cur.fetchall()
            print("\n=== Pendapatan Per Bulan ===")
            for bulan, total in hasil:
                print(f"{bulan}: Rp{total:,}")

        elif pilihan == '3':
            return
        else:
            print("Pilihan tidak valid.")

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

    finally:
        conn.close()
        input("\nTekan Enter untuk kembali ke menu...")
 

def informasi():
    os.system('cls')
    print("=== Tampilkan Game dan Status Konsol Berdasarkan ID Konsol ===\n")

    conn,cur = connect_db()
    if conn is None:
        input("Tekan Enter untuk kembali ke menu...")
        return

    try:
        konsol_id_input = input("Masukkan ID Konsol yang ingin ditampilkan: ").strip()
        if not konsol_id_input.isdigit():
            print("Input ID tidak valid. Harus berupa angka.")
            input("Tekan Enter untuk kembali ke menu...")
            return
        konsol_id = int(konsol_id_input)

        with conn.cursor() as cur:
            # Query gabungkan detail_konsol dan konsol untuk ID tertentu
            cur.execute("""
                SELECT g.nama_game, k.status_konsol
                FROM detail_konsol d
                JOIN game g ON d.game_game_id = g.game_id
                JOIN konsol k ON d.konsol_konsol_id = k.konsol_id
                WHERE d.konsol_konsol_id = %s
                ORDER BY d.game_game_id;
            """, (konsol_id,))

            rows = cur.fetchall()

            if not rows:
                print("Tidak ditemukan data untuk ID Konsol tersebut.")
                input("\nTekan Enter untuk kembali ke menu...")
                return

            status_konsol = "Berfungsi" if rows[0][1] == '1' else "Rusak"

            print(f"\nStatus Konsol ID {konsol_id}: {status_konsol}")
            print("Game terkait:")
            print("{:<15}".format("ID Game"))
            for game_id, _ in rows:
                print(f"{game_id:<15}")

            input("\nTekan Enter untuk kembali ke menu...")

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        input("Tekan Enter untuk kembali ke menu...")
    finally:
        conn.close()

def pesan_durasi(username):
    conn, cur = connect_db()
    if conn is None:
        input("Tekan Enter untuk kembali ke menu...")
        return

    os.system('cls')
    print("=== Pemesanan Durasi Playstation ===\n")

    # Input tanggal dan waktu mulai
    while True:
        tanggal_input = input("Masukkan tanggal main (format: YYYY-MM-DD): ").strip()
        try:
            tanggal_main = datetime.datetime.strptime(tanggal_input, "%Y-%m-%d").date()
            break
        except ValueError:
            print("Format tanggal salah. Silakan masukkan dalam format YYYY-MM-DD.")

    while True:
        waktu_mulai_input = input("Masukkan waktu mulai (format: HH:MM): ").strip()
        try:
            waktu_mulai = datetime.datetime.strptime(waktu_mulai_input, "%H:%M").time()
            break
        except ValueError:
            print("Format waktu salah. Silakan masukkan dalam format HH:MM.")

    waktu_mulai_datetime = datetime.datetime.combine(tanggal_main, waktu_mulai)

    try:
        # Tampilkan daftar paket
        print("\n--- Daftar Paket Sewa ---")
        cur.execute("SELECT paket_sewa_id, nama_paket, durasi, harga FROM paket_sewa ORDER BY durasi")
        daftar_paket = cur.fetchall()

        for pid, nama, durasi, harga in daftar_paket:
            print(f"ID: {pid} - {nama} ({durasi} jam) - Rp{harga:,}")

        while True:
            try:
                paket_id = int(input("Masukkan ID paket sewa yang ingin dipesan: "))
                durasi_paket = next((d for pid, _, d, _ in daftar_paket if pid == paket_id), None)
                if durasi_paket:
                    break
                else:
                    print("ID tidak valid.")
            except ValueError:
                print("Input tidak valid, masukkan angka.")

        while True:
            try:
                quantity = int(input("Masukkan jumlah paket: "))
                if quantity > 0:
                    break
                else:
                    print("Jumlah harus lebih dari 0.")
            except ValueError:
                print("Input tidak valid, masukkan angka.")

        total_durasi = durasi_paket * quantity
        waktu_selesai_datetime = waktu_mulai_datetime + timedelta(hours=total_durasi)

        # Cari konsol yang tidak dipakai di waktu tersebut
        cur.execute("""
            SELECT k.konsol_id, k.nama_konsol
            FROM konsol k
            WHERE k.konsol_id NOT IN (
                SELECT t.konsol_konsol_id
                FROM transaksi t
                JOIN detail_paket dp ON t.transaksi_id = dp.transaksi_transaksi_id
                JOIN paket_sewa ps ON ps.paket_sewa_id = dp.paket_sewa_paket_sewa_id
                WHERE t.status_transaksi IN ('paid', 'pending')
                AND (
                    (%s < t.tanggal_dan_waktu_mulai + INTERVAL '1 hour' * (ps.durasi * dp.quantity))
                    AND (%s > t.tanggal_dan_waktu_mulai)
                )
            )
            ORDER BY k.konsol_id;
        """, (waktu_mulai_datetime, waktu_selesai_datetime))

        konsol_tersedia = cur.fetchall()

        if not konsol_tersedia:
            print("Maaf, tidak ada konsol yang tersedia pada waktu tersebut.")
            input("Tekan Enter untuk kembali ke menu...")
            return

        print("\n--- Konsol Tersedia ---")
        for konsol_id, nama_konsol in konsol_tersedia:
            print(f"ID: {konsol_id} - {nama_konsol}")

        while True:
            try:
                konsol_pilih = int(input("Masukkan ID konsol yang ingin dipesan: "))
                if any(k[0] == konsol_pilih for k in konsol_tersedia):
                    break
                else:
                    print("ID tidak tersedia.")
            except ValueError:
                print("Masukkan angka yang valid.")

        # Input data customer
        # username sudah diketahui dari parameter fungsi, tidak perlu input lagi
        # print(f"Username: {username}")  # Hapus baris ini agar tidak dobel

        # Ambil no telepon dari database berdasarkan username
        cur.execute("SELECT no_telepon FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        if result:
            no_telepon = result[0]
        else:
            no_telepon = "-"
        print(f"Username: {username}")
        print(f"No Telepon: {no_telepon}")
        no_rek = input("Masukkan nomor rekening Anda: ")
        nama_rek = input("Masukkan nama pemilik rekening: ")

        # Pilih metode pembayaran
        cur.execute("SELECT metode_pembayaran_id, nama_metode FROM metode_pembayaran")
        metode = cur.fetchall()
        print("\n--- Metode Pembayaran ---")
        for mid, nama in metode:
            print(f"{mid}. {nama}")

        while True:
            try:
                metode_id = int(input("Pilih ID metode pembayaran: "))
                if any(m[0] == metode_id for m in metode):
                    break
                else:
                    print("ID tidak valid.")
            except ValueError:
                print("Masukkan angka yang valid.")

        # Tampilkan QR code setelah memilih metode pembayaran
        print("\nSilakan scan QR code berikut untuk pembayaran:")
        print("""
█████████████████████████████
████ ▄▄▄▄▄ █ ▄ ▀█  ▄▄▄▄▄ ████
████ █   █ █ ▀▄█ █ █   █ ████
████ █▄▄▄█ █▀ ▄ ▀█ █▄▄▄█ ████
████▄▄▄▄▄▄▄█ ▀ █ ▀▄▄▄▄▄▄▄████
████ ▄▄ ▄ ▄▄█▄▄▄█▀█ ▄ ▄▄ ████
████ █ ▄▄▄▀ ▀▀▄▀ ▀█ ▀▀▄▀▀████
████▄█ ▄▀▀▀▄█▀▀ ▄▄▄ ▀█ ▄▀████
████▀ ▄▀█▄ ▄▀▄▀ ▄▄  ▀▄ ▄ ████
████ ▄▄▀▄ ▄▄▀ ▀ ▄▀▀▀ ▄ ██████
████▄█▄▄▄▄▄█▄▀ ▀▄▀█ █▀▀█▄████
████ ▄▄▄▄▄ █ ▀▀ █▄▀ ▄█ ▄▀████
████ █   █ █ ▀ █  ▀▄▄▄▀▄▄████
████ █▄▄▄█ █▄▀ ▄▄ ▀▀▄█ █▄████
████▄▄▄▄▄▄▄█▄█▄█▄█▄█▄█▄█▄████
█████████████████████████████
""")
        input("Tekan Enter setelah melakukan pembayaran...")

        # Simpan transaksi
        cur.execute("""
            INSERT INTO transaksi (
                tanggal_transaksi,
                tanggal_dan_waktu_mulai,
                users_username,
                users_no_telepon,
                status_transaksi,
                no_rekening,
                nama_pemilik_rekening,
                konsol_konsol_id,
                metode_pembayaran_metode_pembayaran_id
            ) VALUES (NOW(), %s, %s, %s, 'pending', %s, %s, %s, %s)
            RETURNING transaksi_id;
        """, (waktu_mulai_datetime, username, no_telepon, no_rek, nama_rek, konsol_pilih, metode_id))
        transaksi_id = cur.fetchone()[0]

        # Simpan detail_paket
        cur.execute("""
            INSERT INTO detail_paket (quantity, transaksi_transaksi_ID, paket_sewa_paket_sewa_ID)
            VALUES (%s, %s, %s)
        """, (quantity, transaksi_id, paket_id))

        conn.commit()
        print(f"\nPemesanan berhasil dengan ID Transaksi: {transaksi_id}")
        input("Tekan Enter untuk kembali ke menu...")

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        input("Tekan Enter untuk kembali ke menu...")
    finally:
        conn.close()


def logout():
    os.system('cls')
    input ("Anda telah logout. Sampai jumpa!")
    os.system('cls')
    exit()

def menu_customer(username):
    while True:
        os.system('cls')
        teks = """
    ░██████╗░░█████╗░███╗░░░███╗███████╗███████╗░█████╗░███╗░░██╗███████╗
    ██╔════╝░██╔══██╗████╗░████║██╔════╝╚════██║██╔══██╗████╗░██║██╔════╝
    ██║░░██╗░███████║██╔████╔██║█████╗░░░░███╔═╝██║░░██║██╔██╗██║█████╗░░
    ██║░░╚██╗██╔══██║██║╚██╔╝██║██╔══╝░░██╔══╝░░██║░░██║██║╚████║██╔══╝░░
    ╚██████╔╝██║░░██║██║░╚═╝░██║███████╗███████╗╚█████╔╝██║░╚███║███████╗
    ░╚═════╝░╚═╝░░╚═╝╚═╝░░░░░╚═╝╚══════╝╚══════╝░╚════╝░╚═╝░░╚══╝╚══════╝
    """

        print(teks)

        print(f"===================== MENU UTAMA (Customer: {username}) =====================")
        print("1. Informasi Slot Playstation")
        print("2. Booking Playstation")
        print("3. Keluar")

        pilihan = input("Pilih menu (1/2/3/4/5): ")

        if pilihan == '1':
            os.system('cls')
            informasi()
        elif pilihan == '2':
            os.system('cls')
            pesan_durasi(username)
        elif pilihan == '3':
            os.system('cls')
            logout()
        else:
            print("Pilihan tidak valid!")
            input("\nTekan Enter untuk melanjutkan...")


def menu_admin(username):
    while True:
        os.system('cls')
        teks = """
    ░██████╗░░█████╗░███╗░░░███╗███████╗███████╗░█████╗░███╗░░██╗███████╗
    ██╔════╝░██╔══██╗████╗░████║██╔════╝╚════██║██╔══██╗████╗░██║██╔════╝
    ██║░░██╗░███████║██╔████╔██║█████╗░░░░███╔═╝██║░░██║██╔██╗██║█████╗░░
    ██║░░╚██╗██╔══██║██║╚██╔╝██║██╔══╝░░██╔══╝░░██║░░██║██║╚████║██╔══╝░░
    ╚██████╔╝██║░░██║██║░╚═╝░██║███████╗███████╗╚█████╔╝██║░╚███║███████╗
    ░╚═════╝░╚═╝░░╚═╝╚═╝░░░░░╚═╝╚══════╝╚══════╝░╚════╝░╚═╝░░╚══╝╚══════╝
    """

        print(teks)

        print(f"===================== MENU UTAMA {username} =====================")
        print("1. Transaksi")
        print("2. Kelola Slot Playstation")
        print("3. Kelola Data Pelanggan")
        print("4. Kelola Harga Paket Main")
        print("5. Melihat Laporan Keuntungan")
        print("6. Keluar")

        pilihan = input("Pilih menu (1/2/3/4/5): ")

        if pilihan == '1':
            os.system('cls')
            transaksi()
        elif pilihan == '2':
            os.system('cls')
            kelola_playstation()
        elif pilihan == '3':
            os.system('cls')
            kelola_data_pelanggan()
        elif pilihan == '4':
            os.system('cls')
            kelola_harga_paket_main()
        elif pilihan == '5':
            os.system('cls')
            melihat_laporan_keuntungan()
        elif pilihan == '6':
            os.system('cls')
            logout()
        else:
            print("Pilihan tidak valid!")
            input("\nTekan Enter untuk melanjutkan...")

login()