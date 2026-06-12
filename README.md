# 👆 Yapay Zeka Tabanlı El Hareketleri ile Mouse Kontrol Sistemi

Bu proje; Python, OpenCV ve MediaPipe kütüphaneleri kullanılarak geliştirilmiş, bilgisayar kamerasından alınan el görüntülerini eş zamanlı (real-time) işleyerek fare (mouse) hareketlerine dönüştüren yapay zeka tabanlı bir masaüstü kontrol uygulamasıdır.

## 🚀 Özellikler (Features)
* **Gerçek Zamanlı El Takibi (Real-time Tracking):** MediaPipe Hands modülü ile el üzerindeki 21 referans noktası (landmark) yüksek doğrulukla takip edilir.
* **Hassas ve Akıcı İmleç Hareketi:** Matematiksel koordinat dönüşümleri (`numpy.interp`) ve özel yumuşatma filtreleri (smoothing) ile titremesiz imleç kontrolü sağlanır.
* **Akıllı Jest Algılama (Gesture Recognition):**
  * **Sol Tık & Çift Tık:** Başparmak ve orta parmak arasındaki mesafe ile tetiklenir.
  * **Sağ Tık & Sürükleme (Drag):** Yumruk yapma (fist) hareketi ve süresi analiz edilerek çalışır.
  * **Kaydırma (Scroll):** Başparmak ve işaret parmağı mesafesine göre dinamik dikey kaydırma yapılır.
* **Modern Kullanıcı Arayüzü (UI):** Tkinter ve Pillow kütüphaneleri kullanılarak karanlık mod (dark mode) tasarım standartlarına uygun kontrol paneli.
* **Windows DPI Desteği:** `ctypes` entegrasyonu sayesinde yüksek çözünürlüklü ekranlarda kusursuz ölçekleme.

## 🛠️ Kullanılan Teknolojiler (Tech Stack)
* **Programlama Dili:** Python
* **Görüntü İşleme ve Yapay Zeka:** OpenCV, MediaPipe
* **Matematiksel Hesaplamalar:** NumPy
* **Arayüz ve Sistem Entegrasyonu:** Tkinter, Pillow, pynput, ctypes

## 💻 Kurulum ve Çalıştırma (Installation)
Projeyi yerelinizde çalıştırmak için aşağıdaki adımları takip edebilirsiniz:

1. Gerekli kütüphaneleri yükleyin:
`pip install opencv-python mediapipe numpy pynput pillow`

2. Projeyi çalıştırın:
`python El_Ile_Mouse_Kontrol_Sistemi.py`

*Uygulama çalışırken sistemi durdurmak veya panele dönmek için **'q'** tuşuna basabilirsiniz.*
