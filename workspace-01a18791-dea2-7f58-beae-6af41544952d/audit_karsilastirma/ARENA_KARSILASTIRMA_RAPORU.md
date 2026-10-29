# Arena → Arena2 bağımsız karşılaştırma ve çevrimdışı denetim

## Kapsam ve yöntem
Arena deposundaki ZIP `/home/user/.cache/arena1/unpacked/` altına çıkarıldı (geçici, snapshot dışında). Arena2'nin açılmış çalışma alanı `/home/user` altındadır. Dosyalar yol ve SHA-256 içeriğiyle karşılaştırıldı; kaynak farkları ve Faz 3/4 kayıtları incelendi. Bu bir tam çalıştırma testi veya bütün 785 dosyanın satır satır denetimi değildir. Roblox Studio'ya bağlanılmadı.

## Dosya envanteri
- Arena ZIP: 328 dosya. Arena2: inceleme başlangıcında 785 dosya.
- Ortak: 328; yalnız Arena'da: 0; yalnız Arena2'de: 457; ortak dosyalar arasında değişmiş: 4.
- Değişenler: `AEGIS_REAKTOR_ANA_YOL_HARITASI_VE_MODELLEME_PLANI.md`, `CORE_PROTOCOL_REMAKE_Server_MESH_INTEGRATED.server.lua`, köprünün `community_active_hello.json` ve `community_jobs.json` durum kayıtları. Son ikisi oyun kodu değildir.
- Birinci modelin Faz 2/3 kaynakları ve onaylı modelleri depoda korunmuş; ikinci modelin bütün projeyi baştan yazdığı iddiası desteklenmiyor. Fakat canlı Studio'nun yerel dosyalarla aynı olduğunu şu an doğrulayamıyoruz.

## Ana sunucu kodu farkı
Sunucu kodunun 296 satırlık diff'i Faz 4.1'de eski yanık küreleri, boru ağzı küreleri ve düz cam çiziklerinin kaldırılması; bunlar nil olduğundan korumalar eklenmesi ve ilgili ses kaynağının değiştirilmesinden oluşuyor. `crackPanes` artık yalnızca ses/sarsıntı üretir. Boru hasarının gerçek M13 görseline otomatik bağlandığı da gösterilmiyor. Dolayısıyla hasar olayları eski sahte görsellerle çalışıyordu; yeni kodda yerine konulacak sistem tamamlanana kadar görsel gerileme / eksiklik beklenir. Bunu tek başına yanlışlık değil açıkça kaydedilmiş ara durum olarak değerlendiriyoruz. Eski sahte efektleri körlemesine geri getirmek ve mevcut çalışmayı silmek doğru değil.

## Faz 3 denetimi ve Faz 4 ekleri
- Önceki kayda göre büyük PreciseConvexDecomposition uygulaması Studio'yu çökertmiş; ardından geri yükleme yapılmış. O kayıt bunu önceki asistan hatası olarak belirtir. Mevcut ortamda canlı doğrulama yok; söz konusu sayılar kayda dayanır.
- M13: yeni 4 patlak spool GLB ve Studio oluşturucu mevcut; notlarda 32 MeshPart ve 8 ankraj ile manuel Play değişimi anlatılıyor. Otomatik oyun tetiklemesi ve hacimsel sızıntı tamamlanmış olarak gösterilmemiş.
- M14: yol haritası hâlâ modellenecek derken `model_work/damage_glass/make_damage_glass_kit.py`, GLB ve bir render mevcut. Bunların kullanıcı onaylı veya Studio'ya kurulu olduğunu kanıtlayan kayıt bulmadık; geliştirilmiş fakat entegrasyonu belirsiz aday sayılmalı.

## Kanıtlanmış M14 kusurları
1. `hanging_flake` pozitif X dönüşü kullanıyordu. Alt kenarın yerel Z değeri negatif olduğundan author Y pozitif tarafa gider; yorum ve dönüşüm ise oda tarafını author Y < -46.625 olarak tanımlar. GLB ölçümü: özgün parçaların ortalama Y'si -46.3759 (ters taraf). Düzeltilmiş aday: -46.8741 (oda tarafı).
2. `vein` yalnız dış dikdörtgene kırpıyor; ±11.25'teki 0.42 stud dikmeleri hesaba katmıyor. Orijinal GLB'de sırasıyla kademe 1/2/3'te dikmenin tüm enini geçen 24/138/256 çatlak şeridi üçgeni var. Dikmenin arkasında görünmesi her durumda yanlış olmayabilir, ancak belgelenen bölme sınırlarına uyum iddiası doğrulanmıyor.
3. Estetik değerlendirme: render'da bazı çatlaklar şerit ve kare parçalar gibi okunuyor; üç kademe bağımsız rastgele oluşturulduğu için geçişte desenin bir anda değişme riski var. Bunu Studio ışığında ve kullanıcı referansıyla değerlendirmek gerekir. Bazı krater pulları sıfır kalınlıklı çift yüzlü üçgenler; tüm geometriye '%0 2D' demek teknik olarak isabetli değil.

## Çevrimdışı düzeltme — orijinal korunarak
- `model_work/damage_glass/make_damage_glass_kit_duzeltilmis.py`: parçaların eğimi ters çevrildi; çatlak şeritleri gerçek iki dikmenin etrafında pay bırakılarak kırpıldı.
- `model_exports/DAMAGE_GLASS_FRACTURE_STAGES_ADAY_YON_DUZELTME.glb` ve aynı adlı `.png`: yeni aday; orijinal GLB ve render değiştirilmedi. Kaynak orijinalinin ek kopyası `audit_karsilastirma/M14_original.py`.
- `audit_karsilastirma/test_m14.py`: geometri yönü ve şerit üçgenlerinin dikme enini tamamen aşması test edildi. Adayda üç kademe için sıfır; bu test bütün donanım, yama, krater veya sınır çakışmalarının sıfır olduğunu kanıtlamaz.
- GLB 10 mesh / 14.448 üçgen olarak yeniden üretildi. Görsel tasarım açısından hâlâ adaydır ve Studio'da test edilmedi; hiçbir şeyi otomatik kurmaz.

## Diğer testler / sınırlar
- Çalışma alanındaki 63 Python kaynağı sözdizimi AST kontrolünden geçti; çalıştırıldıkları anlamına gelmez.
- `CORE_PROTOCOL_StaticChecks.py` ve V2 muadilleri, depoda yer almayan eski sunucu dosyalarını aradıkları için FileNotFoundError ile açılmadı. Bunlar eski nesil testlerdir; isimlerini güncel sunucuyla değiştirip sahte geçiş sonucu üretmedik.
- Roblox Luau çalıştırma, performans, görsel kalite, Edit/Play senkronizasyonu, gerçek cam çarpışması ve meltdown olayları çevrimdışı doğrulanamaz.
- Depodaki önceki köprü ayarları herkese açık depoya girmiş olduğundan güvenli kabul edilmemeli. Yenilenmeden otomatik köprü kullanılmamalıdır; sırlar rapora yazılmadı.

## Önerilen sıra
1. Kullanıcı video ve Studio hazır olduğunda önce yedek + yeni köprü sırrı, sonra yalnızca salt okunur yer/envanter kontrolü.
2. M13'ün kaydedilmiş ve doğru sürümde olduğunu, orijinal canlı durumunu doğrulama.
3. M14 için referans ve kullanıcı tercihiyle tasarımı gözden geçirme; bağımsız kademeleri süreklileştirme ve gerçek hacimli parçalar açısından yeniden modellemeyi değerlendirme. Yeni aday entegrasyon yetkisi veya kabulü anlamına gelmez.
4. Hasar tetikleri, sıfırlama ve kapanma dâhil test planını hazırlayıp gerçek entegrasyonu ayrı ve geri alınabilir adımlarla yapma.
