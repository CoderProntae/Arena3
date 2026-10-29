# Durum ve uyarı panosu — kullanıcı onay şartları

Model 7×6 durum/uyarı panosu olarak onaylandı; bu onay, dinamik işlevlerin uygulanması şartınadır. GLB içindeki görseller örnektir. Henüz gerçek oyun durumlarıyla bağlantı kurulmadı ve uçtan uca test edilmedi.

- Yazılar, sistemlerin gerçek işlevine ve mevcut olayına göre değişir. Kaynakta okunamayan etiketler için GLB'deki “—” geçici yer tutucudur, nihai olay adı değildir.
- Göstergeler karşılık gelen olaylara göre yanar, yanıp söner veya söner; diğer göstergelerin durumu ilişkili mantığa göre değişir. Örnek: başlama öncesinde “reaktör başlamadı” beyaz ışığı yanıp söner; başlatma başladığında o ışık söner, “reaktör başlatılıyor” sarı ışığı yanıp söner. Bu yalnız örnek durum zinciridir; tüm alarmların aynı biçimde yanıp sönmesi gerektiği anlamına gelmez.
- Renkler sistemin iyi/kötü durumunu ve olay türünü belirtir; tüm renkleri tek bir şiddet derecesine zorlamadan olay bazında eşlemek gerekir. Kullanıcının örnekleri: başlatıldı beyaz, başlatılıyor sarı; boru arızası sarı, soğutma arızası kırmızı; başlatılamadı gibi özel olaylar mor; Project Delta gibi özel/gizli deney olayları mavi.
- Event/etiket eşleşmeleri ve etkinlik koşulları gerçek mevcut reaktör/oyun sistemlerinden doğrulanmalı; var olmayan Project Delta işlevi veya muhtelif hatalar olmuş gibi gösterilmemeli.
- Roblox'ta GLB içindeki 42 ayrı yüzeyin importta korunması, metinlerin ve lamba renklerinin/yanıp sönmesinin gerçek olay verilerine bağlanması, kullanıcı senaryolarıyla Play testi ve oda onayı öncesinde sahneye kalıcı yerleştirmeme gereklidir.
