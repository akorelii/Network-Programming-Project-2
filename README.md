# Multi-User Chat System (Project 02)

Bu proje, Ağ Programlama dersi kapsamında geliştirilmiş, üç ana bileşenden (Server, Client, Relay) oluşan çok kullanıcılı bir sohbet sistemidir. Proje; **TCP Soket Programlama**, **Threading** ve **HTTP Protokolü** kullanılarak Python ile yazılmıştır.

## 🛠️ Proje Bileşenleri

| Dosya Adı | Rolü | Sohbet/Web Portu |
| :---      | :--- | :--- |
| chat_server.py | Ana Sunucu (Chat, Log Yönetimi ve Web Arayüzü) | 55555 / 8080 |
| chat_client.py | Grafik Arayüzlü İstemci (GUI) | İhtiyaca göre değişir |
| relay_server.py | Aktarıcı Sunucu (Nickname Proxy) | 55556 |


## ✅ Kurulum ve Gereksinimler

Proje, Python 3'ün standart kütüphaneleri ile geliştirilmiştir. Herhangi bir harici **`pip install`** komutu **gerekmez**.


## 🚀 Çalıştırma Rehberi

### 1. Temel Sunucu ve İstemci (Normal Bağlantı)

İstemci varsayılan olarak chat_server.py'ye (55555) bağlanır.

1.  Sunucuyu Başlatın:
    ```
    py chat_server.py
    ```
    
2.  İstemciyi Başlatın: (Her yeni kullanıcı için bu komutu yeni bir terminalde çalıştırın.)
    ```
    py chat_client.py
    ```

### 2. Web Loglarını Görüntüleme (HTTP Testi)

Sunucu loglarını (sohbet geçmişini) tarayıcı üzerinden görüntülemek için:

* Tarayıcınızın adres çubuğuna şunu yazın: `http://127.0.0.1:8080`

### 3. Relay Server Testi (Opsiyonel)

Relay sunucusunun ismin başına `*` eklediğini kanıtlamak için:

1.  Yukarıdaki adımla Ana Sunucuyu (chat_server.py) başlatın.
2.  Yeni bir terminal açın ve Relay'i başlatın:
    ```
    py relay_server.py
    ```
3.  chat_client.py dosyasını açın ve **`PORT = 55555`** satırını **`PORT = 55556`** olarak değiştirin ve kaydedin.
4.  İstemciyi başlatıp bağlanın. Ana sunucu terminalinde isminizin **`*`** ile başladığını göreceksiniz.

***(Not: Test bittikten sonra chat_client.py içindeki portu tekrar 55555 yapmayı unutmayın.)***