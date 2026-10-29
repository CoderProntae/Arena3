# FAZ 4 ÖNCESİ DENETİM RAPORU — Boşluk/Mühür + İçiçe Geçme
Tarih: 28 Ekim 2026 | Oyun: AEGIS_Reactor.rbxlx | Durum: **DENETİM TAMAM**

---

## 1) Önce çökme ve kurtarma (özet)

Denetimin ilk sürümü, Edit içinde 677 parçayı aynı anda PreciseConvexDecomposition'a
çeviren ağır bir script çalıştırdı; bu Studio'yu çökertti ve dosya yeniden açıldığında
FAZ 2 öncesi bir kayda dönmüş çıktı. **Bu benim hatamdı, özür dilerim.**
O yöntem bir daha kullanılmayacak (aşağıdaki tüm işler Play tarafında, parçalı ve hafif yapıldı).

**Kayıp tespit (envanter karşılaştırması):**
- 138 MeshPart eksik (677 → 539): tüm FAZ2 geometrisi (4 radyal kapak, türbin rotoru,
  REV05 türbin portu, plenum, crown/deck, yan diyagonal, 4 plaka) + tüm FAZ3 geometrisi
  (soğutma boru halkası, piston servis yuvaları, forebay holü)
- Silinmiş script'ler: Faz2_ChamberAndTurbine, Faz3_PipingAndServiceBays
- Eski sürüme dönmüş 3 script: ReactorPilot_SixHeads, CORE_PROTOCOL_Server, ReactorPilot_CustomVapor

**Geri yükleme (kaynak: workspace'teki onaylı kopyalar):**
- 5 script birebir aynı bayt boylarıyla yeniden kuruldu (65619 / 62117 / 13467 / 79015 / 141209);
  geri dönmüş sürümler `audit_faz3/recovery/` altında yedekte.
- FAZ2 + FAZ3 kaynakları Edit'te yeniden çalıştırılarak geometri inşa edildi.
- Doğrulama: **677/677 MeshPart, model ağacı farkı 0, 19 hareketli pivot birebir**,
  Play açılışı çökme öncesiyle aynı (COLD, pilot READY_REAL_3D_NO_2D_EFFECTS, dünya 1370 parça).
- Bu hâli **Ctrl+S ile kaydettin** ✅

## 2) BOŞLUK / MÜHÜR DENETİMİ — "oyuncu hiçbir yerde boşluk görmesin"

Yöntem: Play içinde 8 iç noktadan 600'er yönlü küresel ışın probu (Precise çarpışma,
saydam katmanları atlayan yinelemeli atış), zemin+tavan dikey ışın ızgaraları,
kesit (transect) ışınları ve 20+ kamera görseli.

| Bölge | Sonuç |
|---|---|
| Kontrol odası (0,28,56) | 0/600 kaçış ✅ |
| Reaktör çekirdeği (0,26.5,2.7) | 0/600 ✅ |
| Oda ön / üst / alt noktaları | 0-1/600 (tek kaçış aşağıdaki yarık) |
| Sol + sağ servis yuvası içi | 0/600 ✅ |
| Plenum içi (fan arkası) | 0/600 ✅ (fan aralığından bakınca görülen şey plenum duvarı, boşluk değil) |
| Zemin ızgarası (567 nokta) | **2 delik: x=0, z 12–14** ❌ → düzeltildi |
| Tavan ızgarası | 0 delik ✅ |

**Bulunan tek kusur ve düzeltme:**
- CROWN_DECK zemininin tam ortasında (x=0, z 12–14, genişlik <0.5 stud) iki zemin
  diliminin birleşim yerinde kıl yarık: düz aşağı bakınca altındaki boşluğa açılıyordu.
- Düzeltme: `STATIC/DENETIM_MUHUR_ZEMIN_01` — deck renginde metal mühür plakası
  (1.8 × 0.3 × 4.6, üst yüzeyi zemin yüzeyinin 0.02 altında; FAZ2/FAZ3 yeniden
  inşalarından etkilenmez, istenirse tek tıkla silinir).
- Sonrası doğrulama: zemin ızgarası **0 delik**, 7/7 kontrol ışını mühre çarpıyor. ✅

**Çürütülen şüphe:** SL-03 plakası geniş açıda ters okunuyor gibi görünmüştü;
karşıdan yakın çekimde düzgün okunuyor (SL-04 ile aynı). Kusur yok, dokunulmadı.

## 3) İÇİÇE GEÇME (CLIPPING) DENETİMİ — özellikle hareketli parçalar

Yöntem: 4 pozda (kapalı / kapaklar açık / yarı strok / tam strok) 392 hareketli parçaya
çakışma sorgusu + kafa çevrelerinde halka boşluk probları + yuva kesit ışınları +
Play ve Edit'te pozlanmış görsel kontroller (tam strok önden/diyagonal/alttan,
zemin + yan duvar kapağı yakın çekimleri, 3 ayrı yuvanın içinden çekimler).

**Sonuç: Görünür içiçe geçme YOK.** Sayısal sorgulardaki "çakışmaların" tamamı iki sınıfa giriyor:
1. **Tasarım içi yuvalanma:** kafalar yuva deliklerinin, kademeler kılavuzlarının,
   kapak yaprakları kanallarının içinde eşmerkezli oturuyor. Kesit ışınları katman
   sırasını doğruladı (duvar r≈5.9 → kılavuz kafesi r≈3.9 → kafa gövdesi r≈2.1,
   arada net boşluklar). Tam strokta kafalar kapı açıklıklarından merkezli geçiyor;
   kafa-kafa en küçük yatay boşluk **>9 stud**.
2. **Ölçüm artığı:** FAZ2/FAZ3'ün ortak-batch mesh'leri (tüm yuvalar/tüm sektörler tek
   MeshPart) dışbükey parçalamada hafif şiştiği için sorgular temas varmış gibi
   sayıyor; görsellerde karşılık gelen hiçbir kırpılma yok.

Ayrıca tek tek bakılanlar:
- **Rotor:** kanat ucu yarıçapı tasarımda 3.588; plenum iç yarıçapı en dar halkada 3.64,
  tünelde 3.92 → boşluk 0.05–0.33 stud. Dar ama **temas yok**; görsellerde merkezli dönüyor.
- **Duvar kapak kuyrukları:** tam açıkken kendileri için yapılan duvar ceplerine giriyor (tasarım).
- **Statik-statik:** boru↔flanş, çerçeve↔deck gibi birleşimlerin hepsi tasarlanmış
  bağlantılar; dünya parçalarıyla (kontrol odası/koridorlar) paylaşılan sınırlar temiz.

Hareket için **hiçbir parçanın yeri değiştirilmedi** — gerekmiyordu.

## 4) Yapılan değişikliklerin tam listesi

1. 5 script yeniden kuruldu (kurtarma; içerik onaylı kopyalarla birebir).
2. FAZ2 + FAZ3 geometrisi kendi kaynaklarından yeniden inşa edildi (kurtarma).
3. `__STUDIO_QA_SWITCH` yeniden oluşturuldu (kurtarma).
4. **`DENETIM_MUHUR_ZEMIN_01` eklendi** (bu denetimin tek düzeltmesi; geri alınabilir).

Onaylı GLB modellerden hiçbiri yeniden şekillendirilmedi; hiçbir pivot/konum değiştirilmedi.
Tüm kanıtlar: `audit_faz3/` (ışın verileri, poz sonuçları, 30+ ekran görüntüsü `captures/`).

## 5) Bekleyenler

- [ ] **Ctrl+S** — mühür plakası şu an sadece açık Edit oturumunda; kaydetmen gerekiyor.
- [ ] FAZ 3 nihai kabulü (önceden açıktı, hâlâ senden onay bekliyor).
- [ ] Sır rotasyonu sorusu (önceden açık).
- Bunlar bitince FAZ 4'e (hasar) geçilebilir — sen söylemeden başlamıyorum.
