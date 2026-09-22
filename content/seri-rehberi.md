# Fındık'ın Meslek Macerası — Seri Rehberi

Bu dosya dizinin "kutsal kitabı"dır. n8n workflow'undaki tüm prompt'lar buradaki kurallara göre yazılır. Bir şey değişecekse önce burası güncellenir.

---

## 1. Dizi Özeti

| | |
| :--- | :--- |
| **Ad** | Fındık'ın Meslek Macerası |
| **Hedef kitle** | 3–7 yaş (okul öncesi ve 1. sınıf) |
| **Format** | YouTube Shorts, dikey 9:16, **45–60 saniye** (10 sahne × 5 sn = 50 sn) |
| **Dil** | Türkçe |
| **Platform ayarı** | YouTube → "Çocuklara özel" (made for kids) |
| **Görsel stil** | 3D Pixar tarzı animasyon, sıcak renkler, yumuşak ışık |
| **Üretim** | Yarı otonom: bölüm n8n'de elle başlatılır, bitmiş video Drive'daki `final` klasörüne düşer |

**Tek cümlelik fikir:** Meraklı minik tilki Fındık, sihirli sırt çantasıyla her bölümde başka bir mesleğin dünyasına gider, küçük bir sorun yaşar, o meslekten biri ona yol gösterir ve Fındık yeni bir şey öğrenir.

---

## 2. Ana Karakter: Fındık

**Kişilik:** 6 yaşında bir çocuk gibi. Çok meraklı, bol soru soruyor, bazen aceleci davranıp küçük hatalar yapıyor ama hatasını hemen kabul ediyor ve düzeltmek istiyor. Hiçbir zaman kaba, korkutucu ya da tehlikeli davranışı özendiren biri değil.

**Görünüş (Türkçe):** Yumuşak, kabarık turuncu tüylü; göğsü, yanakları ve ağzının çevresi krem-beyaz; kabarık kuyruğunun ucu krem-beyaz; iri yuvarlak zümrüt yeşili gözlü, koyu kahve burunlu minik bir tilki yavrusu. İki ayağı üzerinde yürüyor. Boynunda bir ucu önden sarkan kırmızı örgü bir atkı, sırtında kapağında yeşil yaprak olan sarı bir çanta var.

**Resmî görseller:**
- Karakter sayfası (ön, yan, arka): [assets/findik-karakter-sayfasi.png](../assets/findik-karakter-sayfasi.png)
- Referans görsel (ön görünüm 576x1024): [assets/findik-referans.png](../assets/findik-referans.png). Drive'daki `ai-powered-video/fındık referans` klasörüne yüklenir; workflow her sahnede Fındık'ı bu görsele göre çizer.

### Karakter Kartı (görsel prompt'larına AYNEN eklenecek blok)

Bu metin her görsel prompt'una kelimesi kelimesine eklenir. Değiştirilmez, kısaltılmaz; yoksa Fındık sahneden sahneye farklı görünür.

```
Findik, a small cute anthropomorphic baby fox cub with soft fluffy bright orange fur, cream-white chest, cheeks and muzzle, big pointed ears, a big fluffy tail with a cream-white tip, big round emerald-green eyes, small dark brown nose, wearing a red knitted scarf with one end hanging down the front and a small yellow backpack with a green leaf patch on the flap, standing upright on two legs, child-sized
```

**Stil bloğu (her görsel prompt'unun sonuna eklenir):**

```
3D Pixar-style animation, soft warm lighting, vibrant friendly colors, child-friendly, cinematic composition, vertical 9:16 frame
```

**Negatif prompt:**

```
text, letters, words, logos, brand names, watermark, scary, dark, horror, violence, weapons, blood, injury, realistic photo, human-like fox, extra limbs, distorted face, different outfit, missing scarf, missing backpack
```

---

## 3. Dünyası ve Sabit Unsurlar

- **Fındık'ın odası:** Her bölüm burada başlar. Ağaç kovuğundan yapılmış, sıcak renkli, pencereden orman görünen küçük bir oda.
- **Sihirli çanta:** Fındık "Çanta çanta, bizi götür!" deyince çanta parlar ve Fındık'ı altın renkli yaprakların arasında o günün meslek yerine götürür.
- **Işınlanma efekti:** Altın rengi parıltılar ve uçuşan sonbahar yaprakları. Her bölümde aynıdır.

### Sabit Cümleler (her bölümde aynı, çocuklar ezberlesin diye)

| Yer | Cümle |
| :--- | :--- |
| **Açılış** | Merhaba, ben Fındık! Bugün hangi mesleği tanıyacağız? Çanta çanta, bizi götür! |
| **Kapanış** | Bugün öğrendim ki *(mesaj)*. Bir sonraki macerada görüşürüz! |

---

## 4. Meslek Karakterleri

- Her bölümde bir meslek sahibi insan karakter vardır. Adı Türkçedir (Ayşe, Mehmet, Zeynep...).
- Kadın ve erkek karakterler dengeli dağılır. Meslekler cinsiyetle eşleştirilmez (kadın itfaiyeci, erkek hemşire olabilir).
- Görünüşü bölüm içinde sabit kalsın diye, her bölümün İngilizce karakter tarifi `sezon-1.csv` dosyasındaki `yardimci_karakter_prompt` sütununda durur ve o bölümün tüm sahnelerine eklenir.
- Meslek karakteri her zaman nazik, sabırlı ve güven verici davranır. Asla bağırmaz, azarlamaz, korkutmaz.

---

## 5. Bölüm Şablonu (10 sahne × 5 saniye)

| Sahne | Bölüm | Ne olur | Anlatım örneği (1. bölüm) |
| :---: | :--- | :--- | :--- |
| 1 | Açılış | Fındık odasında, kameraya el sallar | Merhaba, ben Fındık! Bugün hangi mesleği tanıyacağız? |
| 2 | Yolculuk | Çanta parlar, yapraklar uçuşur | Çanta çanta, bizi götür! |
| 3 | Varış | Fındık meslek yerine gelir, etrafına şaşkınlıkla bakar | Vay canına, burası bir itfaiye istasyonu! |
| 4 | Tanışma | Meslek sahibi gülümseyerek selam verir | Merhaba Fındık, ben itfaiyeci Ayşe. |
| 5 | Meslek tanıtımı | Meslek sahibi işini ve aletini gösterir | Biz yangınları söndürür, insanlara yardım ederiz. |
| 6 | Sorun | Fındık küçük bir hata yapmak üzeredir | Fındık yerde parlak bir kibrit kutusu gördü. |
| 7 | Öğretme | Meslek sahibi nazikçe doğrusunu anlatır | Dur Fındık, kibrit ve ateş oyuncak değildir. |
| 8 | Çözüm | Fındık doğru davranışı yapar | Fındık kibriti hemen bir büyüğe verdi. |
| 9 | Bilgi | Günün bilgisi söylenir | Yangın görürsek hemen bir büyüğe söyler, 112'yi ararız. |
| 10 | Kapanış | Fındık kameraya el sallar | Bugün öğrendim ki ateş oyuncak değil. Görüşürüz! |

**Anlatım kuralları:**
- Her satır bir sahnedir ve **en fazla 10 kelime** olur (5 saniyede rahatça okunur).
- Kısa, basit ve somut cümleler kurulur. Soyut kavram, deyim ya da ironi kullanılmaz.
- Emoji ve tırnak işareti kullanılmaz (metin sese dönüştürülüyor).
- Mesaj pozitif cümleyle verilir ("ateşle oynama" yerine "ateş oyuncak değil" gibi).

---

## 6. İçerik Kuralları (Çocuk Güvenliği)

Bunlar pazarlığa açık değildir. Her üretilen metin ve görsel bunlara uymalıdır.

1. **Taklit edilebilir tehlikeli davranış gösterilmez.** Sorun sahnesinde Fındık tehlikeli bir şeye *yaklaşır* ama asla yapmaz (kibrit yakılmaz, prize dokunulmaz).
2. Korkutucu sahne, karanlık ortam, yaralanma, kan, silah ya da şiddet olmaz.
3. Gerçek marka, logo ya da ürün adı geçmez.
4. Yanlış bilgi verilmez. Her bölümün bilgisi basit ama doğrudur.
5. Utandırma, alay ya da cezalandırma olmaz. Hata yapmak normaldir, önemli olan düzeltmektir.
6. Görsellerde yazı olmaz (yapay zekâ yazıyı bozuk çiziyor). Videolarda altyazı kullanılmaz.

---

## 7. Ses

| Rol | Özellik |
| :--- | :--- |
| **Anlatıcı** | Sıcak, sakin, masal anlatır gibi. Yavaş ve net diksiyon. |
| **Fındık** (ileride) | Neşeli, çocuksu ses. İlk aşamada tüm metni tek anlatıcı okur, ikinci aşamada Fındık'ın cümleleri ayrı sesle okunur. |

---

## 8. YouTube Bilgileri Şablonu

- **Başlık:** `Fındık'ın Meslek Macerası | Bölüm {bolum}: {meslek} | Çocuklar İçin Eğitici Masal`
- **Açıklama:**

  ```
  Meraklı minik tilki Fındık bugün {meslek} ile tanışıyor! Bu bölümde {deger_aciklama}.

  Bugünün bilgisi: {bilgi}

  Fındık'ın Meslek Macerası, çocukların meslekleri tanırken güzel davranışlar öğrendiği kısa bir animasyon dizisidir.

  #çocukmasalları #meslekler #eğiticivideo #Shorts
  ```

- **Etiketler:** çocuk masalı, meslekler, eğitici çizgi film, okul öncesi, Fındık, {meslek}
- **Kitle:** Çocuklara özel ✅
- **Oynatma listesi:** Fındık'ın Meslek Macerası — 1. Sezon
