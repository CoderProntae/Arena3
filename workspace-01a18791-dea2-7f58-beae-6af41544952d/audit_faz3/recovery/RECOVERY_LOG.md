# KURTARMA KAYDI — Studio Çökmesi Sonrası Geri Yükleme
Tarih: 28 Ekim 2026 (aynı oturum)

## Ne oldu
- Pozlanmış hareket çakışması denetimi (Edit'te 677 MeshPart'ın hepsini aynı anda
  PreciseConvexDecomposition'a çeviren ağır script) 180 sn araç zaman aşımına girdi;
  ardından Studio çöktü.
- Studio yeniden açıldığında dosya FAZ 2 öncesi bir kayda geri dönmüş bulundu.

## Kayıp tespit (envanter karşılaştırması)
- MeshPart: 677 -> 539 (eksik 138)
  - FAZ2 geometrisi: 4x RADIAL_HATCH (24), TURBINE_ROTOR (4), BULKHEAD_REV05_TURBINE_PORT (9),
    REAR_TURBINE_PLENUM_01 (11), CROWN_AND_DECK_01 (11), SIDE_DIAG_OPEN_AND_FRONT_SEAL_03 (4), 4x PLAQUE
  - FAZ3 geometrisi: COOLANT_PIPING_RING_01 (42), PISTON_REAR_SERVICE_BAYS_01 (26), FOREBAY_CONTAINMENT_HALL_01 (7)
- Script'ler tamamen eksik: Faz2_ChamberAndTurbine, Faz3_PipingAndServiceBays
- Eski sürüme dönmüş script'ler (yedekleri recovery/ altında):
  ReactorPilot_SixHeads (+3 bayt, eski cyan zamanlaması), CORE_PROTOCOL_Server (-137 bayt, eski Z-fight değerleri),
  ReactorPilot_CustomVapor (-2678 bayt, lockstep lazer senkronu yok)
- ServerStorage'da __STUDIO_QA_SWITCH eksik

## Geri yükleme (kaynak: workspace kopyaları = bilinen son iyi)
1. Geri dönmüş 3 script script_read ile yedeklendi (recovery/backup_*.lua)
2. multi_edit ile 5 script kuruldu (bayt boyları birebir: 65619 / 62117 / 13467 / 79015 / 141209)
3. FAZ2 kaynağı Edit'te çalıştırıldı -> konsol: [FAZ2] ... active!
4. FAZ3 kaynağı Edit'te çalıştırıldı -> konsol: [FAZ3-REV4] ... active! (75 static 3D MeshParts)
5. __STUDIO_QA_SWITCH BindableFunction yeniden oluşturuldu

## Doğrulama (Edit)
- Toplam MeshPart 677 = STATIC 285 + MOVING 392 (çökme öncesi ile aynı)
- Model ağacı farkı: 0 (tüm isimler + parça sayıları eşleşti)
- 19 hareketli pivot birebir aynı; CollisionFidelity 677xDefault; CanCollide 677xfalse; CanQuery 476/201
- Edit'te CORE_PROTOCOL_V2_WORLD kopyası yok (temiz)

## BEKLEYEN
- [x] Kullanıcı Ctrl+S (kurtarılan hâl kaydedildi)
- [x] Play boot kontrolü (çökme öncesi referansla birebir aynı)
- [x] Denetime hafif yöntemle devam edildi ve TAMAMLANDI — bkz. ../DENETIM_RAPORU_FAZ4_ONCESI.md
- [x] Zemin yarığı mühürlendi (STATIC/DENETIM_MUHUR_ZEMIN_01); SL-03 şüphesi yakın çekimle çürütüldü
- [x] Mühür için bir kez daha Ctrl+S (kaydedildi — denetim kapandı)

studio_id (yeni oturum): 71a30cd4-967b-4208-af00-1da3ea43bcff
