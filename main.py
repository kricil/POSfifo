# =====================================================================
# MENU UTAMA CLI & INTEGRASI - Dikerjakan oleh Wisam
# File: main.py
# =====================================================================
import sys
from modules.inventory import Inventory, proses_restock
from modules.pos import proses_kasir
from modules.report import Receipt, Report

class KasirApp:
    def __init__(self):
        self.inventory = Inventory()
        self.inventory.load_data() # <--- 1. Muat Data Saat Aplikasi dibuka
        self.report = Report()

    def validate_choice(self, choice_input):
        """Memvalidasi input menu (harus angka 1-5)."""
        if not choice_input.isdigit():
            return False
        return 1 <= int(choice_input) <= 5

    def main_menu(self):
        """Loop utama aplikasi CLI."""
        while True:
            print("\n" + "="*40)
            print("       APLIKASI KASIRFIFO (CLI)       ".center(40))
            print("="*40)
            print("1. Kasir (Transaksi Penjualan)")
            print("2. Restock (Tambah Stok Batch)")
            print("3. Lihat Stok & Batch")
            print("4. Laporan Laba/Rugi")
            print("5. Keluar")
            print("="*40)
            
            pilihan = input("Pilih Menu (1-5): ").strip()
            
            # Validasi input menu
            if not self.validate_choice(pilihan):
                print("❌ Pilihan tidak valid! Masukkan angka 1 sampai 5.")
                continue
                
            pilihan = int(pilihan)

            if pilihan == 1:
                # Panggil fungsi kasir milik Andra
                transaksi_selesai = proses_kasir(self.inventory)
                
                # Jika transaksi tidak batal, cetak struk & simpan laporan
                if transaksi_selesai:
                    struk = Receipt(transaksi_selesai)
                    struk.print_receipt()
                    self.report.add_transaction(transaksi_selesai)
                    self.inventory.save_data() # <--- 2. SIMPAN DATA SETELAH TRANSAKSI (KARENA STOK BERKURANG)
                    
            elif pilihan == 2:
                # Panggil fungsi restock milik Prima
                proses_restock(self.inventory) # (Simpan otomatis sudah dihandle di dalam fungsi ini)
                
            elif pilihan == 3:
                # Panggil fungsi lihat stok milik Prima
                self.inventory.list_products()
                
            elif pilihan == 4:
                # Panggil fungsi laporan milik Wisam
                self.report.print_report()
                
            elif pilihan == 5:
                print("\nTerima kasih! Program selesai.")
                sys.exit(0)

# --- TITIK MASUK PROGRAM ---
if __name__ == "__main__":
    app = KasirApp()
    app.main_menu()