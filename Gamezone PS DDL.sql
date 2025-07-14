
-- ========== CREATE ENUM TYPES ==========
CREATE TYPE status_konsol AS ENUM ('0', '1');
CREATE TYPE transaksi_status AS ENUM ('paid', 'pending', 'canceled');

-- ========== CREATE TABLES ==========
CREATE TABLE konsol 
    ( 
     konsol_ID     SERIAL PRIMARY KEY,
     nama_konsol   VARCHAR(20) NOT NULL, 
     status_konsol CHAR(1) NOT NULL DEFAULT '1'
    );

CREATE TABLE game 
    ( 
     game_ID        SERIAL PRIMARY KEY,
     nama_game      VARCHAR(20) NOT NULL, 
     deskripsi_game TEXT NOT NULL
    );

CREATE TABLE detail_konsol 
    ( 
     konsol_konsol_ID INTEGER NOT NULL, 
     game_game_ID     INTEGER NOT NULL 
    );

CREATE TABLE metode_pembayaran 
    ( 
     metode_pembayaran_ID SERIAL PRIMARY KEY,
     nama_metode          VARCHAR(20) NOT NULL
    );

CREATE TABLE paket_sewa 
    ( 
     paket_sewa_ID SERIAL PRIMARY KEY,
     nama_paket    VARCHAR(20) NOT NULL, 
     durasi        INTEGER NOT NULL, 
     harga         INTEGER NOT NULL
    );

CREATE TABLE users 
    ( 
     users_ID   SERIAL PRIMARY KEY,
     role       VARCHAR(20) NOT NULL, 
     username   VARCHAR(20) NOT NULL, 
     password   VARCHAR(20) NOT NULL, 
     no_telepon VARCHAR(13) NOT NULL
    );

CREATE TABLE transaksi 
    ( 
     transaksi_ID                           SERIAL PRIMARY KEY,
     tanggal_transaksi                      DATE NOT NULL, 
     tanggal_dan_waktu_mulai                TIMESTAMP NOT NULL, 
     users_username                         VARCHAR(20) NOT NULL, 
     users_no_telepon                       VARCHAR(13) NOT NULL, 
     status_transaksi                       VARCHAR (10) NOT NULL DEFAULT 'pending',
     no_rekening                            VARCHAR(20) NOT NULL, 
     nama_pemilik_rekening                  VARCHAR(20) NOT NULL, 
     konsol_konsol_ID                       INTEGER NOT NULL, 
     metode_pembayaran_metode_pembayaran_ID INTEGER NOT NULL
    );

CREATE TABLE detail_paket 
    ( 
     detail_paket_ID          SERIAL PRIMARY KEY,
     quantity                 INTEGER NOT NULL, 
     sub_total                INTEGER NOT NULL, 
     transaksi_transaksi_ID   INTEGER NOT NULL, 
     paket_sewa_paket_sewa_ID INTEGER NOT NULL 
    );


CREATE OR REPLACE FUNCTION calculate_subtotal()
RETURNS TRIGGER AS $$
BEGIN
    NEW.sub_total := NEW.quantity * (
        SELECT harga 
        FROM paket_sewa 
        WHERE paket_sewa_ID = NEW.paket_sewa_paket_sewa_ID
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ========== CREATE TRIGGERS ==========
CREATE TRIGGER trg_subtotal_insert
BEFORE INSERT ON detail_paket
FOR EACH ROW EXECUTE FUNCTION calculate_subtotal();

CREATE TRIGGER trg_subtotal_update
BEFORE UPDATE ON detail_paket
FOR EACH ROW 
WHEN (OLD.quantity IS DISTINCT FROM NEW.quantity OR OLD.paket_sewa_paket_sewa_ID IS DISTINCT FROM NEW.paket_sewa_paket_sewa_ID)
EXECUTE FUNCTION calculate_subtotal();

-- ========== ADD CONSTRAINTS ==========
ALTER TABLE users 
    ADD CONSTRAINT users_username_no_telepon_UN UNIQUE (username, no_telepon);

ALTER TABLE detail_konsol 
    ADD CONSTRAINT detail_konsol_game_FK FOREIGN KEY 
    (game_game_ID) 
    REFERENCES game (game_ID);

ALTER TABLE detail_konsol 
    ADD CONSTRAINT detail_konsol_konsol_FK FOREIGN KEY 
    (konsol_konsol_ID) 
    REFERENCES konsol (konsol_ID);

ALTER TABLE detail_paket 
    ADD CONSTRAINT detail_paket_paket_sewa_FK FOREIGN KEY 
    (paket_sewa_paket_sewa_ID) 
    REFERENCES paket_sewa (paket_sewa_ID);

ALTER TABLE detail_paket 
    ADD CONSTRAINT detail_paket_transaksi_FK FOREIGN KEY 
    (transaksi_transaksi_ID) 
    REFERENCES transaksi (transaksi_ID);

ALTER TABLE transaksi 
    ADD CONSTRAINT transaksi_konsol_FK FOREIGN KEY 
    (konsol_konsol_ID) 
    REFERENCES konsol (konsol_ID);

ALTER TABLE transaksi 
    ADD CONSTRAINT transaksi_metode_pembayaran_FK FOREIGN KEY 
    (metode_pembayaran_metode_pembayaran_ID) 
    REFERENCES metode_pembayaran (metode_pembayaran_ID);

ALTER TABLE transaksi 
    ADD CONSTRAINT transaksi_users_FK FOREIGN KEY 
    (users_username, users_no_telepon) 
    REFERENCES users (username, no_telepon);


--INSERT data
INSERT INTO konsol(nama_konsol,status_konsol)
VALUES ('Konsol 1', '1'), ('Konsol 2', '1'), ('Konsol 3', '1'), ('Konsol 4', '1')

INSERT INTO users(role, username, password, no_telepon)
VALUES ('Admin', 'Admin', 'Admin123', '0895410570169'),
('Customer', 'Zaki', 'Zaki123', '0859191644907'),
('Customer', 'Jonatan', 'Jonatan123', '082334600521'),
('Customer', 'Okta', 'Okta123', '0895365651114')

INSERT INTO game(nama_game, deskripsi_game)
VALUES ('FIFA 25', 'Game simulasi sepak bola terbaru dari seri FIFA yang menghadirkan pengalaman bermain lebih realistis, dengan grafis yang ditingkatkan, gameplay yang disempurnakan, dan fitur manajerial yang lebih kompleks. Cocok untuk penggemar bola yang ingin merasakan sensasi bertanding di lapangan virtual.'),
('eFootball PES', 'Alternatif kuat dari FIFA, eFootball Pro Evolution Soccer (PES) menawarkan gameplay yang lebih taktis dan fokus pada kontrol bola serta strategi permainan. Dengan lisensi klub dan pemain terbatas, game ini tetap digemari karena kontrolnya yang responsif dan mekanik yang realistis.'),
('NBA 2K', 'Seri game basket paling populer yang menghadirkan simulasi pertandingan NBA dengan grafis canggih, mode karier yang mendalam, dan komunitas online aktif. Ideal untuk penggemar basket yang ingin merasakan atmosfer pertandingan di liga profesional.'),
('GTA V', 'Game open-world aksi-petualangan yang memungkinkan pemain menjelajahi dunia kriminal Los Santos dengan tiga karakter utama. Dengan alur cerita sinematik, kebebasan eksplorasi, dan berbagai misi, GTA V menjadi salah satu game paling ikonik sepanjang masa.'),
('TEKKEN 7', 'Game pertarungan ikonik yang melanjutkan saga keluarga Mishima. Menawarkan gameplay cepat, kombinasi serangan kompleks, serta roster karakter yang beragam. Cocok untuk pemain yang suka adu refleks dan strategi dalam duel satu lawan satu.'),
('RDR II', 'Game aksi-petualangan bertema koboi yang berlatar di Amerika Serikat pada akhir abad ke-19. Menawarkan dunia terbuka yang luas dan hidup, cerita yang emosional, serta detail visual yang memukau. Sebuah mahakarya dari Rockstar Games.'),
('God of War', 'Aksi petualangan epik dengan cerita mitologi Nordik, di mana Kratos dan anaknya, Atreus, menjelajahi dunia para dewa dan monster. Dengan pertarungan brutal, alur cerita mendalam, dan karakter yang kuat, God of War adalah salah satu game eksklusif PlayStation terbaik.'),
('Crash Team Racing', 'Game balapan seru dengan karakter dari semesta Crash Bandicoot. Menampilkan lintasan menantang, item lucu, dan mode multiplayer yang menghibur. Cocok untuk semua usia, terutama penggemar game kart racing klasik.'),
('WWE 2K', 'Simulasi gulat profesional dengan berbagai mode, dari karier hingga Royal Rumble. Pemain dapat memilih superstar WWE favorit dan bertarung di atas ring dengan gaya khas masing-masing. Game ini sangat cocok bagi penggemar dunia gulat hiburan.'),
('Resident Evil 2', 'Game survival horror yang membawa kembali kisah ikonik Leon dan Claire di Raccoon City. Dengan grafis modern dan atmosfer yang mencekam, remake ini sukses menghadirkan ketegangan dan nostalgia sekaligus.')


INSERT INTO paket_sewa(nama_paket, durasi, harga)
VALUES ('Satu jam', '1', '10000'), ('Tiga jam', '3', '28000'), ('Lima jam', '5', '45000')

INSERT INTO metode_pembayaran(nama_metode)
VALUES ('ovo'), ('gopay'), ('shopeepay'), ('bca'), ('mandiri')

INSERT INTO detail_konsol(konsol_konsol_id, game_game_id)
VALUES (1,1), (1,2), (1,3), (1,4), (1,5), (1,6), (1,7), (1,8), (2,1), (2,3), (2,4), (2,5),
(2,6), (2,7), (2,8), (2,9), (2,10), (3,2), (3,3), (3,4), (3,5), (3,7), (3,9), (3,10), (4,1), 
(4,2), (4,4), (4,5), (4,6), (4,9), (4,10)

INSERT INTO transaksi(tanggal_transaksi,tanggal_dan_waktu_mulai, users_username, users_no_telepon, status_transaksi, no_rekening, nama_pemilik_rekening, konsol_konsol_id, metode_pembayaran_metode_pembayaran_id)
VALUES ('2025-06-01', '2025-06-01 15:00:00', 'Zaki', '0859191644907', 'paid', '8913031006', 'LATIFUL ZAKI MUBARAK', '4', '4'),
('2025-06-01', '2025-06-01 20:00:00', 'Okta', '0895365651114', 'paid', '0895365651114', 'Octa Fajri Surya', '2', '2'),
('2025-06-02', '2025-06-02 19:00:00', 'Jonatan', '082334600521', 'paid', '1200828450', 'DJONATHAN PAULSEN', '1', '4')


INSERT INTO detail_paket(quantity, transaksi_transaksi_id, paket_sewa_paket_sewa_id)
VALUES ('2', '1', '1'), ('1', '2', '2'), ('1', '3', '3')


select * from metode_pembayaran
select * from detail_paket
select * from transaksi