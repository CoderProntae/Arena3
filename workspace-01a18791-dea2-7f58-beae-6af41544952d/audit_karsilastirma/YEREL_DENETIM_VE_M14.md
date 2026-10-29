# Yerel denetim ve M14 yeniden tasarım

## Kapsam
Studio, kullanıcı makinesi ve köprüyle hiç bağlantı kurulmadı; yalnızca Arena2'nin yerel kopyası incelendi. Önceki Arena ile farkların ayrıntısı `ARENA_KARSILASTIRMA_RAPORU.md` içindedir. İnceleme, bütün mantığın çalışma zamanı doğruluğunu kanıtlayan kapsamlı bir oyun testi değildir.

## Toplu otomatik kontrol
- Çalışma alanındaki 49 Luau dosyası bağımsız Luau derleyicisinde sözdiziminden geçti. Bu, Roblox API davranışını veya oyun durumlarını test etmez.
- 66 Python dosyası AST sözdizimi kontrolünden geçti. Bunlar bütünüyle çalıştırılmadı.
- 20 GLB yüklendi; meshlerin koordinatları sonlu, yüzleri boş değil ve üçgenlerde sıfır alan bulunmadı. Geometrinin işlevsel, estetik veya çarpışmasız olduğunu garantilemez.
- Tekrarlanabilir komut: `PYTHONPATH=/home/user/.cache/modeldeps python audit_karsilastirma/test_yerel.py`. Bu dosya `.cache` altındaki geçici bağımlılıklara ve derleyiciye ihtiyaç duyar; cache silinirse yeniden kurulmalıdır.

## Cam: sıfırdan alternatif
Eski M14 görselleri çatlakları kalın, geometrik beyaz bantlar ve kare parçalar şeklinde gösteriyordu; kullanıcının yapay göründüğü yönündeki eleştirisi yerinde. Yeni üreteç `model_work/damage_glass/make_damage_glass_natural.py`:
- ince, düzensiz, dallanan hacimli üçgen prizma çatlaklar ve az sayıda üçgen cam pulundan oluşur;
- ızgara görünümü yerine düzensiz yarıklar ve kesintili darbe halkaları kullanır;
- daha önceki çatlakların yeni aşamaya geçerken kaybolmaması için üç **birikimli** katman üretir: 1; 1+2; 1+2+3;
- iki ana dikmenin çevresine güvenli aralık bırakır;
- her üç katman ve 14.776 üçgen ayrı `DAMAGE_GLASS_NATURAL_CANDIDATE.glb` dosyasındadır; orijinal M14 değiştirilmemiştir.

Aşamalar `DAMAGE_GLASS_NATURAL_KADEME_1.png`, `_2.png`, `_3.png` dosyalarında çevrimdışı gösterilir. Görselde arka cam koyu bir **render dekorudur**, GLB'ye dahil değildir. Bu yalnızca model adayıdır; sahne entegrasyonu, camın kendi kırılıp düşmesi, olay tetikleri ve gerçek Studio görünürlüğü henüz yapılmamış / doğrulanmamıştır. İnce çizgiler Studio çözünürlüğü ve aydınlatmasında fazla silik kalabilir; kullanıcı görsel değerlendirmesi ve canlı test gerekir. Bu yüzden bitmiş ürün veya onaylanmış model denmemelidir.

## M13 kurucu kodu: veri kaybı riski
Özgün `faz4/FAZ4_DamageAssets.server.lua` yeni geometri oluşturmayı denemeden önce `Faz4Generated` işaretli önceki çocukları siliyor. Her mesh üretim hatası `warn` ile yutulduğundan, bir API/bellek hatası eski kitin kaybıyla veya eksik kitle sonuçlanabilir ve son mesaj yine kuruldu diyebilir. İnceleme ile saptanan mantıksal risk; bu oturumda Studio'da tetiklenmedi.

Yerel, ayrıca saklanan aday `faz4/FAZ4_DamageAssets_GUVENLI_ADAY.server.lua` önce parent'ı olmayan kit üretir; 32 MeshPart, 8 ankraj ve 4 spool kontrolünü başarırsa sahneye koyar ve yalnızca `Faz4Generated` + `Faz4DamageKit` işaretli eski kitleri siler. Hata/eksik sayıda yeni kiti silip eskiyi bırakır. Sözdizimi derlenmiştir; Roblox'ta EditableMesh yaratma, parent'sız oluşturma, bellek, yarış koşulları ve başarısızlık senaryoları denenmemiştir. Henüz canlıya kurulmamıştır. Eski kit korunurken yenisinin üretilmesi geçici bellek ihtiyacını artırabilir.

## Diğer eksikler / canlı doğrulama
- M13 otomatik hasar tetikleri ve hacimsel sızıntı entegrasyonu tamamlanmış değil.
- `crackPanes` şu anda sadece ses/sarsıntı; yeni M14 katmanlarına bağlanmış değil.
- Önceki notlar Faz 3 kurtarması ve M13'ün Play testini bildirir; makinenin kapanmasından sonra son Edit kaydının gerçek hali bilinmiyor. Faz 3 mührü ve M13 kaydının varlığı sorgulanmalı.
- Reset, meltdown zaman çizelgesi, gerçek cam kırılma ve çarpışma, uzaktan oyuncu davranışı, ışık performansı ve ses izinleri çevrimdışı doğrulanmadı.
- Geçmişte açığa çıkmış şifreli köprü anahtarları güvenilir sayılmamalı; anahtarlar yenilenmeden otomatik köprüye komut göndermek önerilmez.

## Sonraki adımlar
Kullanıcı köprüyü ve Studio'yu açtığını söyledikten sonra önce güvenlik/anahtar durumunu teyit et; kullanıcıya yedek aldır, doğru projeyi ve kayıt durumunu salt okunur incele. Sonra kullanıcıya cam adayını göster; uygun bulunursa küçük ve geri alınabilir adımlarla Studio'ya deneme kurulumu ve olay/reset testleri yap. Bu dosya herhangi bir canlı kurulum talimatı çalıştırmaz.
