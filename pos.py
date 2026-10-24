# =====================================================================
# MODUL KASIR (POS) - Dikerjakan oleh Andra
# File: pos.py
# =====================================================================

# Import mesin FIFO milik Bachtiar (cogs.py) agar bisa dipanggil di sini
from modules.cogs import HPPEngine 

class TransactionItem:
    """
    Class untuk menyimpan satu baris barang yang dibeli pelanggan.
    """
    def __init__(self, product, qty):
        self.product = product      # Objek dari class Product (milik Prima)
        self.qty = qty              # Jumlah yang dibeli
        self.hpp_item = 0.0         # Variabel untuk menyimpan total modal (HPP) barang ini

    def subtotal(self):
        """Menghitung total harga jual untuk item ini (Harga Jual x Qty)."""
        return self.product.selling_price * self.qty

    def item_cogs(self):
        """
        Mengembalikan nilai HPP (modal) yang sudah dihitung oleh mesin FIFO.
        Fungsi ini HANYA mengambil nilai yang sudah disimpan, tidak menghitung ulang.
        """
        return self.hpp_item        


class Transaction:
    """
    Class untuk menyimpan data satu nota transaksi penuh.
    """
    def __init__(self):
        self.items = []             # List yang menampung objek TransactionItem
        self.discount = 0.0         # Diskon dalam bentuk nominal (Rp)
        self.paid_amount = 0.0      # Uang yang dibayarkan pelanggan
        self.is_finalized = False   # Penanda: Apakah stok sudah dipotong atau belum

    def add_item(self, product, qty):
        """Menambahkan barang ke dalam keranjang belanja."""
        item_baru = TransactionItem(product, qty)
        self.items.append(item_baru)

    def finalize_checkout(self):
        """
        FUNGSI PENTING: Memotong stok fisik (FIFO) dan menghitung HPP.
        Fungsi ini dipanggil HANYA SEKALI saat pelanggan berhasil membayar.
        """
        # Cegah pemotongan stok ganda jika fungsi ini terpanggil 2x
        if self.is_finalized:
            return
        
        # Looping setiap barang yang ada di keranjang
        for item in self.items:
            # Panggil mesin FIFO milik Bachtiar (cogs.py)
            # Mesin ini akan memotong antrean batch di inventory.py 
            # dan mengembalikan nilai total modal (HPP)
            hpp_didapat = HPPEngine.compute_fifo(item.product, item.qty)
            
            # Simpan nilai modal ke dalam item
            item.hpp_item = hpp_didapat
            
        self.is_finalized = True    # Tandai bahwa transaksi ini sudah diproses

    def total_sales(self):
        """Menghitung total yang harus dibayar (Subtotal - Diskon)."""
        total = sum(item.subtotal() for item in self.items)
        return total - self.discount

    def total_cogs(self):
        """Menghitung total modal (HPP) dari semua barang di keranjang."""
        return sum(item.item_cogs() for item in self.items)

    def gross_profit(self):
        """Menghitung laba kotor (Penjualan Bersih - Total HPP)."""
        # Laba = Total Belanja (setelah diskon) - Total Modal
        return self.total_sales() - self.total_cogs()

    def change_due(self):
        """Menghitung uang kembalian."""
        return self.paid_amount - self.total_sales()


# =====================================================================
# FUNGSI CLI UNTUK MENJALANKAN KASIR
# =====================================================================

def proses_kasir(inventory):
    """
    Fungsi ini dipanggil oleh main.py (Wisam) saat user pilih menu '1. Kasir'.
    Parameter 'inventory' adalah objek dari file inventory.py milik Prima.
    """
    print("\n" + "="*40)
    print("       TERMINAL KASIR KASIRFIFO       ")
    print("="*40)

    transaksi = Transaction()

    # --- LOOP INPUT BARANG ---
    while True:
        print("\n--- Masukkan Barang (Ketik '0' untuk selesai) ---")
        id_produk = input("Masukkan ID Produk : ").strip().upper()
        
        # Keluar dari loop jika user ketik 0
        if id_produk == '0':
            break

        # Validasi 1: Cek apakah produk ada di Inventory
        produk = inventory.find_product(id_produk)
        if not produk:
            print("❌ Error: Produk tidak ditemukan di database!")
            continue

        # Validasi 2: Input Qty harus angka dan > 0
        try:
            qty = int(input(f"Masukkan Jumlah '{produk.name}' : "))
            if qty <= 0:
                print("❌ Error: Jumlah harus lebih dari 0!")
                continue
        except ValueError:
            print("❌ Error: Input jumlah harus berupa angka!")
            continue

        # Validasi 3: Cek stok cukup atau tidak
        if produk.total_stock() < qty:
            print(f"❌ Error: Stok tidak cukup! Sisa stok '{produk.name}' hanya {produk.total_stock()}.")
            continue

        # Jika lolos validasi, tambahkan ke keranjang
        transaksi.add_item(produk, qty)
        print(f"✅ {qty} {produk.name} masuk keranjang.")

    # Jika keranjang kosong, batalkan transaksi
    if not transaksi.items:
        print("\n⚠️ Tidak ada barang yang dibeli. Transaksi dibatalkan.")
        return None

    # --- PROSES PEMBAYARAN ---
    print("\n" + "-"*40)
    print(f"Total Belanja : Rp {transaksi.total_sales():,.2f}")
    
    # Input Diskon (Opsional)
    try:
        diskon = float(input("Masukkan Diskon (Rp, ketik 0 jika tidak ada): "))
        if diskon > 0:
            transaksi.discount = diskon
            print(f"Total setelah diskon : Rp {transaksi.total_sales():,.2f}")
    except ValueError:
        print("Input diskon tidak valid, dianggap 0.")

    # Input Uang Bayar
    while True:
        try:
            uang_bayar = float(input("Masukkan Uang Bayar : Rp "))
            transaksi.paid_amount = uang_bayar
            
            if transaksi.paid_amount < transaksi.total_sales():
                print(f"❌ Uang kurang! Kurang Rp {transaksi.total_sales() - transaksi.paid_amount:,.2f}")
                print("Silakan masukkan uang yang cukup.")
            else:
                break # Uang cukup, keluar dari loop
        except ValueError:
            print("❌ Error: Input harus berupa angka!")

    # --- SELESAI & POTONG STOK ---
    # PENTING: Panggil fungsi ini agar stok di inventory terpotong via FIFO!
    transaksi.finalize_checkout()  
    
    print("\n" + "="*40)
    print(f"Uang Kembalian : Rp {transaksi.change_due():,.2f}")
    
    # Kembalikan objek transaksi ke main.py agar struk bisa dicetak 
    # dan laporan bisa disimpan oleh Wisam
    return transaksi