# GitHub'a yükleme ve başvuru kontrolü

## ÖNCE YEREL TEST

1. Python 3.10–3.12 kurulu olsun.
2. `start_windows.bat` dosyasına çift tıkla; ilk seferde Python paketleri/YOLO ağırlığı indirilebilir.
3. Gerçek kişi takibini denemek için kullanma hakkına sahip olduğun videoyu `data/input/sample_video.mp4` olarak ekle veya `python main.py --input ...` çalıştır.
4. `python -m pip install -r requirements-dev.txt` ve `python -m pytest -q` çalıştır.
5. GitHub'da **Actions** sekmesinden testleri gözlemle; kırmızıysa önce düzelt.

## GITHUB (MEVCUT DEPOYA EKLE)

**GitHub'a kaynak kod paketini yükle; eski `.git` klasörünü arşivden taşımadık.**

Önerilen güvenli yöntem: var olan repoyu `git clone https://github.com/alieraykalayci5-hash/python-vision-tracking-engine.git` ile indir. Bu paketteki dosyaları klonun içine kopyala. Sonra:

```
git status
git add .
git status
git commit -m "Add tests, CLI, Windows launcher and gated-assignment fixes"
git push origin HEAD
```

`git status` çıktısında `.venv`, `*.pt`, büyük videolar ve `cpp/build` OLMAMALI. `.gitignore` zaten engelliyor ama GitHub'da daha önce takip edilen dosyalar ayrıca kaldırılmalıdır. Özel dosyalar, başkasına ait görüntüler ve izin verilmemiş model ağırlıklarını yükleme.

## BAŞVURU

1. Deponun herkese açık olduğunu, çalışan testleri ve ana bakımcı rolünü doğrula.
2. `docs/APPLICATION_NOTES.md` metnini gerçek katılıma ve güncel GitHub verilerine göre düzenle.
3. `https://openai.com/form/codex-for-oss/` üzerinden, ChatGPT e-postan ve kendi Organization ID'n ile başvur.
4. Kabul garantisi veya kesin yanıt süresi yok. Sırf başvuru için sahte katkı/indirme/yıldız üretme.
