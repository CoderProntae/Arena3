# CORE PROTOCOL V2 — görüntü itirazı, düzeltmeler, test durumu

## Kullanıcının iki ekran görüntüsündeki asıl problem

Yeni yüklenen `uploads/image-1.png` (eski CORE PROTOCOL Studio karesi) ve `uploads/image-2.png` (orijinal video karesi) incelendi. UI kenarları yaklaşık kırpılıp sRGB luma hesaplandığında, **eski Studio karesinde** luma > %90 olan piksellerin payı **%34,7**, videoda ise **%4,0**; herhangi bir renk kanalı > %98 olanlar **%39,4'e karşı %4,7**. Ortanca luma **0,626'ya karşı 0,316**. Karşılaştırılan sahne/oyuncu açısı aynı olmadığından bu değerler birebir renk hedefi değildir; fakat *eski paketin bariz beyaz patlamasını* sayısal olarak doğrular. **V2 için Studio karesi bulunmadığından V2'nin bu oranlara ulaştığı iddia edilmez.**

Görüntüdeki temel farklar: (1) sol tarafta panel bankı yerine devasa Neon renkli masa; (2) merkezin fiziksel düğmelerle dolması yerine referansta boş floor hatch; (3) kontrollü kızıl/ivory iç ışık yerine siyan-beyaz global ışık; (4) mavi-siyah reactor arka planı yerine koyu turuncu/yanlış ton; (5) altı machined barrel'ın okunmaması; (6) beyaz ışık saçan dağınık neon çubukları; (7) aşırı büyük beyaz enerji kürelerinin pencereye/odaya kadar genişlemesi; (8) fazla bloom; (9) gereğinden uzak erişimli/güçlü çekirdek PointLight; (10) yansımalı beyaz zeminin kadrajı patlatması; (11) yanlış kamera/masa yerleşimi; (12) alttaki projektörün yüksek sill arkasına düşme riski. Listeyi yapay biçimde 100 maddeye bölmek yerine bu **kök nedenler** düzeltildi.

## V2'de gerçekten değiştirilenler

- Normal bloom `0.91 → 0.16`, maksimum kriz bloom `1.55 → 0.38`; threshold `1.25 → 2.45`; `Lighting.ExposureCompensation=-0.82` başlangıç değeri; oda Brightness üst sınırları düşürüldü.
- Çekirdeğin PointLight menzili `120 → 59` (yıldızdan cama > 67 stud); parlaklığı normalde yaklaşık `8–15 → 2–3.3`, kriz sonunda `31 → ≤ 5.4` aralığına düşürüldü. Oda için ayrı küçük *sıcak* aydınlatmalar, alarm için ayrı kontrollü kırmızı dolgular kullanılıyor.
- Büyük beyaz Neon tavan ışığı opak ivory difüzör, beyaz yansıtıcı zemin daha düşük yansımalı sıcak gri, pencere çerçeveleri kırmızı-koyu metal oldu; mavi duvar bantları/bulb ışıkları küçültüldü.
- V1'in büyüyebilen **187 stud çaplı** beyaz plazma küresi kaldırıldı: süreli merkez darbesi **≤52 stud çap** ve camın çok gerisinde. Parlayan düşen şarapnel metal/karanlık geometriye çevrildi. V1'de tek bir boru alarmı kontrol odasında **4×31/s sürekli beyaz sis** açıp açık bırakıyordu; V2 bunu kısa, düşük emisyonlu darbeye indirdi. Sürekli buhar yalnızca gerçekten E-COOLANT veya FREEZEDOWN çalışırken vardır.
- Sol kontrol masası pencere önüne alındı ve ~56 stud genişlikten ~35 studa küçültüldü. Yedi kumandanın tıklanabilir gövdeleri ~11.6×9.5'ten ~8×6.5'e indi; düğme/kol bezel'leri artık metal ve bakelit ağırlıklı. Süs ışığı ve dial ibresi **CanQuery=false**; oyuncu kol/düğmenin kendi ClickDetector'una gerçekten erişebilsin diye.
- Sağdaki ana camın **sol ucunda dar, sabit**, gerçek verilerle güncellenen enstrüman bankı; sol yan duvar paneli. Sol yan duvarda büyük siyah monitörün **üstüne üç kırmızı lamba bankası**, **yanına küçük renkli tanı tuşları** dizildi: V1'deki monitör üstüne yayılan dev renk ızgarası kaldırıldı. Sabit bank x=-54..-36 ile sınırlı; projeksiyonda tüm altı yayıcı başı açık. Kapanan panjur yok.
- Kontrollü altı kollu yıldız: beyaz odak daha küçük; kollar **magenta** (altısı beyaza dönmez); metal barrel'lar koyu iç çap ve siyan diyaframla okunur; halka/ark saydamlıkları düşürüldü; arka duvar opak kobalt üstünde katmanlı mavi sis/damar/uzak ışık.
- İlk spawn `(-29, z=151)` çapraz kadrajda. Alt pencere sill'i düşük; gerçek oyuncu kamera yüksekliği yakınında (y≈31) **ALT yayıcı** da görünür. Studio scriptinde yeni `auditView()` altı emitter'ın **iki kamera yüksekliğinden** görüşünü ayrıca kontrol eder.
- Normal reaktör kontrol mantığı, 21 olaylık 435 saniyelik akış, yetki kartları, bunker, shutdown / freezedown dalları ve istemci müziği korunmuştur.

## Yapılan testler — ve yapılmayan

- `npx --yes luaparse` hem V2 sunucu hem V2 istemci dosyasında sözdizimi: **geçti**.
- `python CORE_PROTOCOL_V2_StaticChecks.py`: ses anahtarı, 7 kontrolün server click bağlantısı, 3 kart/yuva, kriz süresi, parlama bütçesi, mühürlenmiş merkez darbesi ve **23 analitik görüş hattı**: **geçti**. Analitik geometri gerçek Roblox işleyicisi değildir.
- İç mühendislik Lupa/Lua **sahte-Roblox** çalıştırması: V2 startup, failed startup, freezedown+recovery, acil rezerv, erken başarılı SCRAM, 3 kartlı shutdown, geç SCRAM, patlama/bunker/reset ve istemci kamera/ses olayları: **geçti**. Bu taklit **Roblox Studio'da Play yapılmış anlamına gelmez**.
- **Roblox Studio Play / render, Roblox gerçek raycast, asset oynatma yetkileri ve yayınlanmış çok oyunculu performans BU ORTAMDA TEST EDİLEMEDİ.** Kodun referans kareyle görsel olarak eşleştiği garanti edilmez.

## Sizde Studio'da mutlaka bakılacak kontrol listesi

1. Eski `CORE_PROTOCOL_Server` ve `CORE_PROTOCOL_Client` scriptlerini kaldırın. V2 tek başına çalışsın; eskiyle bir arada iki dünya/iki aydınlatma olabilir.
2. Output'ta `[CORE PROTOCOL V2] Geometry rays: 23/23 clear` arayın. Farklıysa Output hangi parçanın hangi yayıcıyı engellediğini yazar; tam adını iletin.
3. Oyuncu doğar doğmaz **solda küçük kontrol bankı**, ortada siyah zemin çukuru, sağda koyu mavi fon üzerinde **altı silindirik yayıcı ve küçük magenta/beyaz yıldız** görmeli. Ana camı hiçbir büyük panjur kapatmamalı. Fiziksel kontroller sessiz süs olmamalı; çevrildiğinde altlarındaki değerler değişmeli.
4. `STUDIO_AUTO_MELTDOWN=true` ve `STUDIO_PREVIEW_SECOND=244` ile **YouTube 15:53** civarını prova edin. Yaklaşık 12 saniyelik Play sonrası 5–10 saniye darbelerin oturmasını bekleyip screenshot alın. Kontrol odası sınırlı kırmızı alarm ışığına dönmeli; **zemin/çekirdek tamamen beyaza patlamamalı**. Altı yayıcıdan o ana dek kopan başlar mekanik biçimde farklı görünmeli.
5. `STUDIO_PREVIEW_SECOND=0` ile tam 435 saniyelik olay akışını; normal gameplay ve kart senaryolarını ayrıca test edin. Sesler yüklenmiyorsa Creator Store izinlerini kontrol edin.
6. Bir karenin hâlâ fazla parlak/karanlık olması hâlinde `CFG.VISUAL.ROOM_EXPOSURE` değerini küçük adımlarla ayarlayın; **karşılaştırmalı yeni V2 görüntüsünü** gönderirseniz gerçek Studio görünümüne göre yeniden iterasyon gerekir.
