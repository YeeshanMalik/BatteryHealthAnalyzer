import time
import hashlib
from barcode import Code128
from barcode.writer import ImageWriter


def generate_cell_id():
    return hashlib.sha1(str(time.time_ns()).encode()).hexdigest()[:10].upper()


def generate_barcode(cell_id):
    code = Code128(cell_id, writer=ImageWriter())
    path = f"static/barcodes/{cell_id}"
    code.save(path)
    return f"/static/barcodes/{cell_id}.png"
