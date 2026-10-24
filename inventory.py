# =====================================================================
# MODUL INVENTARIS - Dikerjakan oleh Prima
# File: inventory.py
# =====================================================================
from datetime import datetime
import json
import os

class Batch:
    def __init__(self, purchase_price, qty, arrival_date=None):
        self.purchase_price = purchase_price
        self.qty = qty
        self.arrival_date = arrival_date or datetime.now().strftime("%Y-%m-%d")

    def to_dict(self):
        # Mengubah objek Batch menjadi format Dictionary agar bisa disimpan ke JSON
        return {
            "purchase_price": self.purchase_price,
            "qty": self.qty,
            "arrival_date": self.arrival_date
        }

    @classmethod
    def from_dict(cls, data):
        # Mengubah Dictionary dari JSON kembali menjadi objek Batch
        return cls(data['purchase_price'], data['qty'], data['arrival_date'])


class Product:
    def __init__(self, id_produk, name, selling_price):
        self.id = id_produk
        self.name = name
        self.selling_price = selling_price
        self.batches = []

    def add_batch(self, purchase_price, qty, arrival_date=None):
        batch_baru = Batch(purchase_price, qty, arrival_date)
        self.batches.append(batch_baru)

    def total_stock(self):
        return sum(batch.qty for batch in self.batches)

    def to_dict(self):
        # Mengubah objek Product beserta isi batch-nya menjadi Dictionary
        return {
            "id": self.id,
            "name": self.name,
            "selling_price": self.selling_price,
            "batches": [batch.to_dict() for batch in self.batches]
        }

    @classmethod
    def from_dict(cls, data):
        # Mengubah Dictionary dari JSON kembali menjadi objek Product
        produk = cls(data['id'], data['name'], data['selling_price'])
        for b_data in data['batches']:
            produk.batches.append(Batch.from_dict(b_data))
        return produk


class Inventory:
    def __init__(self):
        self.products = {}
        self.filename = "database_inventory.json" # Nama file penyimpanan

    def save_data(self):
        """Menyimpan seluruh data inventaris ke file JSON"""
        data_to_save = {id: prod.to_dict() for id, prod in self.products.items()}
        with open(self.filename, 'w') as file:
            json.dump(data_to_save, file, indent=4)
        print("💾 Data inventaris berhasil disimpan ke file.")

    def load_data(self):
        """Memuat data inventaris dari file JSON (jika ada) saat program dibuka"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as file:
                    data_loaded = json.load(file)
                    self.products = {id: Product.from_dict(prod_data) for id, prod_data in data_loaded.items()}
                print("📂 Data inventaris berhasil dimuat.")
            except Exception as e:
                print(f"❌ Gagal memuat data: {e}")

    def add_product(self, id_produk, name, selling_price):
        if id_produk in self.products:
            return False, "Produk dengan ID tersebut sudah terdaftar."
        produk_baru = Product(id_produk, name, selling_price)
        self.products[id_produk] = produk_baru
        return True, "Produk berhasil didaftarkan."

    def find_product(self, id_produk):
        return self.products.get(id_produk, None)

    def restock(self, id_produk, purchase_price, qty, arrival_date=None):
        produk = self.find_product(id_produk)
        if produk:
            produk.add_batch(purchase_price, qty, arrival_date)
            return True, f"Berhasil menambah {qty} stok ke {produk.name}."
        return False, "Produk tidak ditemukan."

    def list_products(self):
        if not self.products:
            print("Belum ada produk di dalam sistem.")
            return
        print("\n" + "="*65)
        print(f"{'ID':<6} | {'Nama Produk':<20} | {'Harga Jual':<12} | {'Total Stok':<10}")
        print("-" * 65)
        for prod in self.products.values():
            print(f"{prod.id:<6} | {prod.name:<20} | Rp {prod.selling_price:<9,.2f} | {prod.total_stock():<10}")
        print("="*65)


def proses_restock(inventory):
    print("\n" + "="*40)
    print("       TERMINAL RESTOCK KASIRFIFO      ")
    print("="*40)
    
    id_produk = input("Masukkan ID Produk (contoh: P001): ").strip().upper()
    produk = inventory.find_product(id_produk)

    if not produk:
        print(f"\nID '{id_produk}' belum terdaftar. Mari daftarkan produk baru.")
        nama_produk = input("Masukkan Nama Produk : ").strip()
        
        while True:
            try:
                harga_jual = float(input("Masukkan Harga Jual (Rp): "))
                if harga_jual <= 0:
                    print("❌ Harga jual harus lebih dari 0!")
                    continue
                break
            except ValueError:
                print("❌ Input harus berupa angka!")
                
        inventory.add_product(id_produk, nama_produk, harga_jual)
        print(f"✅ Produk '{nama_produk}' berhasil didaftarkan.")

    print(f"\n--- Input Batch Kulakan Baru ---")
    
    while True:
        try:
            qty = int(input("Masukkan Jumlah Stok Masuk : "))
            if qty <= 0:
                print("❌ Jumlah stok harus lebih dari 0!")
                continue
            break
        except ValueError:
            print("❌ Input harus berupa angka!")

    while True:
        try:
            harga_beli = float(input("Masukkan Harga Beli Batch / Satuan (Rp): "))
            if harga_beli <= 0:
                print("❌ Harga beli harus lebih dari 0!")
                continue
            break
        except ValueError:
            print("❌ Input harus berupa angka!")

    sukses, pesan = inventory.restock(id_produk, harga_beli, qty)
    
    if sukses:
        print(f"\n✅ {pesan}")
        print("Data batch berhasil disimpan di antrean FIFO.")
        inventory.save_data() # <--- OTOMATIS SIMPAN SETELAH RESTOCK
    else:
        print(f"\n❌ Gagal: {pesan}")