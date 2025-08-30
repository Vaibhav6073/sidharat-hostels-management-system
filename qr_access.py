import socket
import qrcode
from PIL import Image

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def create_qr_code():
    ip = get_local_ip()
    url = f"http://{ip}:5000"
    
    print(f"Creating QR code for: {url}")
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("mobile_access_qr.png")
    
    print(f"QR code saved as 'mobile_access_qr.png'")
    print(f"Scan with mobile to access: {url}")

if __name__ == "__main__":
    create_qr_code()