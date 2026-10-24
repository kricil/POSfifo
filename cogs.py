# =====================================================================
# MODUL HPP ENGINE (FIFO)
# File: cogs.py
# =====================================================================

class HPPEngine:
    """
    Class untuk melakukan kalkulasi Harga Pokok Penjualan (HPP)
    menggunakan metode First-In, First-Out (FIFO).
    """
    
    @staticmethod
    def compute_fifo(product, qty_beli):
        """
        Menghitung total HPP dan memotong antrean batch terlama.
        Parameter:
        - product: Objek Product dari inventory.py (milik Prima)
        - qty_beli: Jumlah barang yang dibeli pelanggan (int)
        
        Return: float (hpp_total)
        """
        # 1. Validasi kecukupan stok
        if product.total_stock() < qty_beli:
            raise ValueError(f"Stok tidak cukup! Sisa stok {product.name} hanya {product.total_stock()}.")

        hpp_total = 0.0
        sisa_butuh = qty_beli
        
        # 2. Looping selama masih ada sisa barang yang harus dipotong
        # Asumsi: product.batches sudah terurut dari yang terlama (indeks 0)
        while sisa_butuh > 0:
            batch_terlama = product.batches[0]
            
            # Jika qty di batch ini cukup atau lebih untuk memenuhi sisa_butuh
            if batch_terlama.qty >= sisa_butuh:
                hpp_total += sisa_butuh * batch_terlama.purchase_price
                batch_terlama.qty -= sisa_butuh
                sisa_butuh = 0  # Terpenuhi, hentikan loop
            else:
                # Jika qty di batch ini tidak cukup, habiskan batch ini
                hpp_total += batch_terlama.qty * batch_terlama.purchase_price
                sisa_butuh -= batch_terlama.qty
                product.batches.pop(0) # Hapus batch dari list karena sudah habis
                
        return hpp_total

    @staticmethod
    def compute_margin(laba_kotor, total_penjualan):
        """Menghitung Margin Kotor dalam persen (%)."""
        if total_penjualan == 0:
            return 0.0
        return (laba_kotor / total_penjualan) * 100

    @staticmethod
    def compute_markup(laba_kotor, hpp_total):
        """Menghitung Markup dalam persen (%)."""
        if hpp_total == 0:
            return 0.0
        return (laba_kotor / hpp_total) * 100


# =====================================================================
# UNIT TEST SEDERHANA (Bisa dites langsung tanpa nunggu file lain)
# =====================================================================
if __name__ == "__main__":
    # Import class buatan Prima untuk testing lokal
    from inventory import Product

    print("=== MENGUJI ENGINE FIFO BACHtiar ===")
    
    # 1. Buat produk dummy (Gula)
    gula = Product("P001", "Gula Pasir", selling_price=15000)
    
    # 2. Tambah 3 batch kulakan dengan harga berbeda
    # Batch 1 (Terlama): 10 unit @ 5000
    gula.add_batch(purchase_price=5000, qty=10)
    # Batch 2: 15 unit @ 6000
    gula.add_batch(purchase_price=6000, qty=15)
    # Batch 3: 20 unit @ 6500
    gula.add_batch(purchase_price=6500, qty=20)

    print(f"Total Stok Awal: {gula.total_stock()} unit") # Harusnya 45

    # 3. Simulasi Pelanggan beli 18 unit
    qty_beli = 18
    print(f"\nPelanggan membeli {qty_beli} unit.")
    
    # Hitung HPP FIFO
    hpp = HPPEngine.compute_fifo(gula, qty_beli)
    
    # 4. Verifikasi Hasil (Sesuai contoh di proposal)
    print(f"Total HPP FIFO: Rp {hpp:,.2f}") # Harusnya 98000 (10x5000 + 8x6000)
    print(f"Sisa Stok Akhir: {gula.total_stock()} unit") # Harusnya 27
    
    # Cek isi batch yang tersisa
    print("\nSisa Batch di Gudang:")
    for i, b in enumerate(gula.batches):
        print(f"- Batch {i+1}: {b.qty} unit @ Rp {b.purchase_price:,.2f}")

    # 5. Hitung Margin & Markup
    total_penjualan = qty_beli * gula.selling_price
    laba_kotor = total_penjualan - hpp
    
    margin = HPPEngine.compute_margin(laba_kotor, total_penjualan)
    markup = HPPEngine.compute_markup(laba_kotor, hpp)
    
    print(f"\nLaba Kotor: Rp {laba_kotor:,.2f}")
    print(f"Margin Kotor: {margin:.2f}%") # Harusnya 45.56%
    print(f"Markup: {markup:.2f}%")       # Harusnya 83.67%
    