

class Receipt:
    """
    Class untuk memformat dan mencetak struk belanja.
    """
    def __init__(self, transaction):
        self.transaction = transaction

    def format_receipt(self):
        """Membuat teks struk dengan perataan monospaced (String Manipulation)."""
        lines = []
        lines.append("\n" + "="*40)
        lines.append("          KASIR FIFO MART          ".center(40))
        lines.append("="*40)
        
        # Header tabel
        lines.append(f"{'Barang':<15} | {'Qty':>5} | {'Subtotal':>12}")
        lines.append("-" * 40)
        
        # Isi tabel
        for item in self.transaction.items:
            nama = item.product.name[:15] # Potong kalau nama terlalu panjang
            lines.append(f"{nama:<15} | {item.qty:>5} | {item.subtotal():>12,.0f}")
            
        lines.append("-" * 40)
        
        # Ringkasan
        total_belanja = self.transaction.total_sales()
        diskon = self.transaction.discount
        uang_bayar = self.transaction.paid_amount
        kembalian = self.transaction.change_due()
        
        # f-string padding (rata kanan)
        lines.append(f"{'Total Belanja:':<25} Rp {total_belanja:>10,.0f}")
        if diskon > 0:
            lines.append(f"{'Diskon:':<25} Rp {diskon:>10,.0f}")
        lines.append(f"{'Uang Bayar:':<25} Rp {uang_bayar:>10,.0f}")
        lines.append(f"{'Kembalian:':<25} Rp {kembalian:>10,.0f}")
        
        lines.append("="*40)
        lines.append("    Terima Kasih Sudah Berbelanja!    ".center(40))
        lines.append("="*40 + "\n")
        
        return "\n".join(lines)

    def print_receipt(self):
        """Mencetak struk ke layar terminal."""
        print(self.format_receipt())


class Report:
    """
    Class untuk merekap semua transaksi yang terjadi selama sesi.
    """
    def __init__(self):
        self.history = [] # List of Transaction

    def add_transaction(self, transaction):
        """Menyimpan transaksi yang sudah dibayar ke riwayat."""
        self.history.append(transaction)

    def total_revenue(self):
        """Menghitung total omzet (uang masuk)."""
        return sum(t.total_sales() for t in self.history)

    def total_profit(self):
        """Menghitung total laba kotor (omzet - HPP)."""
        return sum(t.gross_profit() for t in self.history)

    def print_report(self):
        """Menampilkan rekap laporan ke layar."""
        print("\n" + "="*40)
        print("        LAPORAN LABA/RUGI HARI INI       ".center(40))
        print("="*40)
        
        if not self.history:
            print("Belum ada transaksi hari ini.")
            return
            
        print(f"Total Transaksi : {len(self.history)} kali")
        print(f"Total Omzet     : Rp {self.total_revenue():,.2f}")
        print(f"Total Laba Kotor: Rp {self.total_profit():,.2f}")
        print("="*40 + "\n")