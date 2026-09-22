"""n8n workflow'unu (src/workflow.json) üretir.

Kullanım:  python scripts/build_workflow.py src/workflow.json
Tüm gizli değerler yer tutucu (YOUR_...) olarak yazılır; gerçek değerler n8n'deki Ayarlar node'una girilir.
"""
import json, uuid, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "src/workflow.json"

nodes, conns = [], {}

def node(name, type_, ver, pos, params, **extra):
    n = {"parameters": params, "id": str(uuid.uuid4()), "name": name, "type": type_,
         "typeVersion": ver, "position": pos}
    n.update(extra)
    nodes.append(n)
    return name

def link(src, dst, out=0, inp=0):
    outs = conns.setdefault(src, {"main": []})["main"]
    while len(outs) <= out:
        outs.append([])
    outs[out].append({"node": dst, "type": "main", "index": inp})

def cond(left, op_type, operation, right=None, single=False):
    c = {"id": str(uuid.uuid4()), "leftValue": left,
         "operator": {"type": op_type, "operation": operation}}
    if single:
        c["operator"]["singleValue"] = True
    else:
        c["rightValue"] = right
    return {"conditions": {"options": {"version": 2, "leftValue": "", "caseSensitive": True,
                                       "typeValidation": "loose"},
                           "combinator": "and", "conditions": [c]},
            "looseTypeValidation": True, "options": {}}

def wait(amount, unit):
    return {"amount": amount, "unit": unit}

def http(method, url, headers, body=None, file_response=False):
    p = {"method": method, "url": url, "sendHeaders": True,
         "headerParameters": {"parameters": [{"name": k, "value": v} for k, v in headers]},
         "options": {}}
    if method == "GET":
        del p["method"]
    if body is not None:
        p.update({"sendBody": True, "contentType": "raw", "rawContentType": "application/json",
                  "body": body})
    if file_response:
        p["options"] = {"response": {"response": {"responseFormat": "file"}}}
    return p

def sticky(name, pos, w, h, color, text):
    node(name, "n8n-nodes-base.stickyNote", 1, pos,
         {"content": text, "height": h, "width": w, "color": color})

K = "$('Ayarlar').first().json"
PIAPI = [("X-API-Key", "={{ " + K + "['PiAPI Key'] }}")]
CREATO = [("Authorization", "=Bearer {{ " + K + "['Creatomate API Key'] }}"),
          ("Content-Type", "application/json")]
SCENE = "$('Sahne Döngüsü').item.json"

# ---------------------------------------------------------------- 1. Senaryo
node("Elle Başlat", "n8n-nodes-base.manualTrigger", 1, [0, -120], {})
node("Her Gün 07:00", "n8n-nodes-base.scheduleTrigger", 1.2, [0, 120],
     {"rule": {"interval": [{"triggerAtHour": 7}]}}, disabled=True)

def s(name, value, type_="string"):
    return {"id": str(uuid.uuid4()), "name": name, "value": value, "type": type_}

node("Ayarlar", "n8n-nodes-base.set", 3.4, [220, 0], {"assignments": {"assignments": [
    s("PiAPI Key", "YOUR_PIAPI_KEY"),
    s("ElevenLabs API Key", "YOUR_ELEVENLABS_KEY"),
    s("Creatomate API Key", "YOUR_CREATOMATE_KEY"),
    s("ElevenLabs Voice ID", "RXCCWbOxP7Hisa63Xsv5"),
    s("Google Sheet ID", "YOUR_GOOGLE_SHEET_ID"),
    s("Google Sheet Sekme ID", "0"),
    s("Drive Ses Klasor ID", "YOUR_SESLER_FOLDER_ID"),
    s("Drive Final Klasor ID", "YOUR_FINAL_FOLDER_ID"),
    s("Drive Referans Klasor ID", "YOUR_REFERANS_FOLDER_ID"),
    s("Kling Mode", "std"),
    s("Kling Version", "1.6"),
    s("Minimum PiAPI Bakiye USD", "3.5"),
]}, "options": {}})

DRIVE = {"__rl": True, "mode": "list", "value": "My Drive"}
def folder(key):
    return {"__rl": True, "value": "={{ " + K + "['" + key + "'] }}", "mode": "id"}

def share(fid):
    return {"operation": "share", "fileId": {"__rl": True, "mode": "id", "value": fid},
            "permissionsUi": {"permissionsValues": {"role": "reader", "type": "anyone"}},
            "options": {}}

SHEET_ID = {"__rl": True, "value": "={{ " + K + "['Google Sheet ID'] }}", "mode": "id"}
# Belge ID ifadeyle geldiği için "From list" yüklenemez; sekmeyi ID (URL'deki gid) ile ver.
SHEET_TAB = {"__rl": True, "value": "={{ " + K + "['Google Sheet Sekme ID'] }}", "mode": "id"}

REF_JS = r"""// Drive'daki referans klasöründen Fındık'ın görselini seçer (PNG/JPEG/WebP).
const files = $input.all()
  .map((i) => i.json)
  .filter((f) => f.id && (String(f.mimeType || '').startsWith('image/') || /\.(png|jpe?g|webp)$/i.test(f.name || '')));
if (!files.length) {
  throw new Error("Referans klasöründe görsel bulunamadı. Fındık'ın referans görselini Drive'daki referans klasörüne yükle.");
}
const f = files[0];
return [{ json: { id: f.id, name: f.name, url: `https://drive.google.com/uc?export=download&id=${f.id}` } }];"""

BALANCE_JS = r"""// PiAPI bakiyesi bir bölüme yetmiyorsa hiçbir şey üretmeden durur.
const info = $json.data ?? $json;
const usd = Number(info.equivalent_in_usd);
const min = Number($('Ayarlar').first().json['Minimum PiAPI Bakiye USD'] || 3.5);
if (!Number.isFinite(usd)) {
  throw new Error('PiAPI bakiyesi okunamadı. PiAPI Key doğru mu? Yanıt: ' + JSON.stringify($json).slice(0, 200));
}
if (usd < min) {
  throw new Error(`PiAPI bakiyesi yetersiz: $${usd.toFixed(2)} (bir bölüm için en az $${min}). piapi.ai üzerinden kredi yükle.`);
}
return [{ json: { piapi_usd: usd } }];"""

node("PiAPI Bakiye", "n8n-nodes-base.httpRequest", 4.2, [440, 0],
     http("GET", "https://api.piapi.ai/account/info", PIAPI))
node("Bakiye Kontrol", "n8n-nodes-base.code", 2, [660, 0], {"jsCode": BALANCE_JS})

node("Referans Görseli Bul", "n8n-nodes-base.googleDrive", 3, [880, 0], {
    "resource": "fileFolder", "searchMethod": "query",
    "queryString": "trashed = false",
    "filter": {"folderId": folder("Drive Referans Klasor ID"), "whatToSearch": "files"},
    "limit": 10, "options": {"fields": ["id", "name", "mimeType"]}}, alwaysOutputData=True)
node("Referans Kontrol", "n8n-nodes-base.code", 2, [1100, 0], {"jsCode": REF_JS})
node("Referans Paylaşım İzni", "n8n-nodes-base.googleDrive", 3, [1320, 0], share("={{ $json.id }}"))

node("Bölümleri Oku", "n8n-nodes-base.googleSheets", 4.5, [440, 0],
     {"documentId": SHEET_ID, "sheetName": SHEET_TAB,
      "filtersUI": {"values": [{"lookupColumn": "production", "lookupValue": "for production"}]},
      "options": {}}, alwaysOutputData=True)
node("İlk Bölümü Al", "n8n-nodes-base.limit", 1, [660, 0], {"maxItems": 1})
node("Bölüm Var mı?", "n8n-nodes-base.if", 2.2, [880, 0],
     cond("={{ String($json.id ?? '') }}", "string", "notEmpty", single=True))

SYSTEM_PROMPT = """Sen 3-7 yaş çocuklar için kısa animasyon dizisi yazan deneyimli bir çocuk kitabı yazarı ve okul öncesi eğitimcisisin. Dizinin adı Fındık'ın Meslek Macerası. Ana karakter Fındık: 6 yaşında bir çocuk kadar meraklı, turuncu minik bir tilki. Sırtındaki sihirli sarı çanta onu her bölümde başka bir mesleğin dünyasına götürür.

Görevin: Sana verilen bölüm bilgilerinden 10 sahnelik, her sahnesi 5 saniye süren bir bölüm senaryosu yazmak.

SAHNE AKIŞI (bu sırayı bozma):
1. Açılış: Fındık odasında izleyiciye el sallar.
2. Yolculuk: sihirli çanta parlar, Fındık altın yapraklar arasında yolculuk eder.
3. Varış: Fındık meslek yerine gelir ve şaşkınlıkla etrafına bakar.
4. Tanışma: meslek sahibi Fındık'ı gülümseyerek karşılar ve kendini tanıtır.
5. Meslek tanıtımı: meslek sahibi işini ve bir aletini gösterir.
6. Sorun: Fındık verilen sorunu yaşar ya da küçük bir hata yapmak üzeredir.
7. Öğretme: meslek sahibi nazikçe doğrusunu anlatır.
8. Çözüm: Fındık doğru davranışı yapar.
9. Bilgi: günün bilgisi basitçe söylenir.
10. Kapanış: Fındık izleyiciye el sallar.

ANLATIM KURALLARI:
- Her sahnenin anlatımı Türkçe ve EN FAZLA 10 kelime. Tek cümle ya da iki kısa cümle.
- 3-7 yaş çocuğun anlayacağı basit, somut kelimeler kullan. Deyim, soyut kavram ve ironi kullanma.
- Mesajı olumlu cümleyle ver.
- Emoji ve tırnak işareti kullanma; metin sese dönüştürülecek.
- Meslek sahibi her zaman nazik, sabırlı ve güven vericidir; bağırmaz, azarlamaz, korkutmaz.
- Fındık hata yapmaya yaklaşır ama tehlikeli davranışı asla gerçekten yapmaz. Korkutucu, üzücü veya şiddet içeren hiçbir şey yazma.
- Verilen bilgiyi değiştirme, yanlış bilgi ekleme.

GÖRSEL ALANLAR (İngilizce yaz):
- sahne_prompt: sahnede ne olduğunu anlatan tek cümlelik İngilizce görsel tarif. Karakterlere isimleriyle değin (Findik ve meslek sahibinin adı), ama görünüşlerini, kıyafetlerini veya mekânı TARİF ETME; bunları sistem otomatik ekleyecek. Yazı, tabela veya harf içeren nesne isteme.
- hareket_prompt: 5 saniyelik klipte neyin nasıl hareket edeceğini anlatan kısa İngilizce tarif. Örnek: Findik waves happily, slow camera push in.
- yardimci_var: meslek sahibi o sahnede görünüyorsa true, görünmüyorsa false.

ÖRNEK ANLATIM (1. bölüm, itfaiyeci):
1 Merhaba, ben Fındık! Bugün hangi mesleği tanıyacağız?
2 Çanta çanta, bizi götür!
3 Vay canına, burası bir itfaiye istasyonu!
4 Merhaba Fındık, ben itfaiyeci Ayşe.
5 Biz yangınları söndürür, insanlara yardım ederiz.
6 Fındık yerde parlak bir kibrit kutusu gördü.
7 Dur Fındık, kibrit ve ateş oyuncak değildir.
8 Fındık kibriti hemen bir büyüğe verdi.
9 Yangın görürsek bir büyüğe söyler, 112'yi ararız.
10 Bugün öğrendim ki ateş oyuncak değil. Görüşürüz!

ÇIKTI: Sadece şu yapıda geçerli bir JSON nesnesi döndür, başka hiçbir şey yazma:
{"sahneler":[{"no":1,"anlatim":"...","sahne_prompt":"...","hareket_prompt":"...","yardimci_var":false}]}
sahneler dizisinde tam 10 sahne olmalı."""

EP = "$('İlk Bölümü Al').first().json"
USER_PROMPT = ("=Bölüm {{ " + EP + ".bolum }}: {{ " + EP + ".baslik }}\n"
               "Meslek: {{ " + EP + ".meslek }}\n"
               "Meslek sahibi: {{ " + EP + ".yardimci_karakter }}\n"
               "Kategori: {{ " + EP + ".kategori }}\n"
               "Verilecek değer: {{ " + EP + ".deger }}\n"
               "Sorun (6. sahne): {{ " + EP + ".sorun }}\n"
               "Günün bilgisi (9. sahne): {{ " + EP + ".bilgi }}\n"
               "Kapanış mesajı: Bugün öğrendim ki {{ " + EP + ".kapanis_mesaji }}")

node("Senaryo Yaz", "@n8n/n8n-nodes-langchain.openAi", 1.8, [1100, 0], {
    "modelId": {"__rl": True, "mode": "list", "value": "gpt-4o-mini", "cachedResultName": "GPT-4O-MINI"},
    "messages": {"values": [{"content": SYSTEM_PROMPT, "role": "system"}, {"content": USER_PROMPT}]},
    "simplify": False, "jsonOutput": True, "options": {"temperature": 0.8}})

PARSE_JS = r"""// Senaryoyu doğrular ve her sahne için görsel isteğini hazırlar.
// Karakter kartı content/seri-rehberi.md ile birebir aynı olmalı.
const CHARACTER = 'Findik, a small cute anthropomorphic baby fox cub with soft fluffy bright orange fur, cream-white chest, cheeks and muzzle, big pointed ears, a big fluffy tail with a cream-white tip, big round emerald-green eyes, small dark brown nose, wearing a red knitted scarf with one end hanging down the front and a small yellow backpack with a green leaf patch on the flap, standing upright on two legs, child-sized';
const STYLE = '3D Pixar-style animation, soft warm lighting, vibrant friendly colors, child-friendly, cinematic composition, vertical 9:16 frame';
const ROOM = 'inside a cozy warm tree-hollow bedroom with a round wooden window showing a green forest, soft morning sunlight';
const TRAVEL = 'surrounded by swirling golden sparkles and flying autumn leaves, magical glowing light';

const ep = $('İlk Bölümü Al').first().json;
const ref = $('Referans Kontrol').first().json.url;

const fail = (msg) => {
  if ($runIndex >= 2) throw new Error('Senaryo 3 denemede geçerli üretilemedi: ' + msg);
  return [{ json: { valid: false, error: msg } }];
};

const clean = (t) => String(t ?? '')
  .replace(/["“”«»]/g, '')
  .replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/gu, '')
  .replace(/\s+/g, ' ')
  .trim();

let data = $input.first().json.choices?.[0]?.message?.content;
if (typeof data === 'string') {
  try {
    data = JSON.parse(data.replace(/^```(json)?/, '').replace(/```$/, '').trim());
  } catch (e) {
    return fail('JSON okunamadı');
  }
}
const sahneler = Array.isArray(data?.sahneler) ? data.sahneler : [];
if (sahneler.length !== 10) return fail(`10 yerine ${sahneler.length} sahne geldi`);

// Açılış, yolculuk ve kapanış her bölümde aynı kalır.
const fixed = {
  1: {
    anlatim: 'Merhaba, ben Fındık! Bugün hangi mesleği tanıyacağız?',
    sahne_prompt: 'Findik smiles and waves happily at the viewer',
    hareket_prompt: 'Findik waves happily at the camera, gentle slow camera push in',
    mekan: ROOM,
    yardimci_var: false,
  },
  2: {
    anlatim: 'Çanta çanta, bizi götür!',
    sahne_prompt: 'Findik excitedly holds the straps of the glowing magical yellow backpack',
    hareket_prompt: 'the backpack glows brightly, golden sparkles and autumn leaves swirl around Findik',
    mekan: TRAVEL,
    yardimci_var: false,
  },
  10: { anlatim: `Bugün öğrendim ki ${clean(ep.kapanis_mesaji)}. Görüşürüz!` },
};

const episode = {
  id: ep.id,
  bolum: ep.bolum,
  meslek: ep.meslek,
};

const items = [];
for (let i = 0; i < 10; i++) {
  const no = i + 1;
  const s = { ...sahneler[i], ...(fixed[no] || {}) };
  const narration = clean(s.anlatim);
  const words = narration.split(' ').filter(Boolean).length;
  if (!narration) return fail(`Sahne ${no} anlatımı boş`);
  if (words > 14) return fail(`Sahne ${no} anlatımı çok uzun (${words} kelime)`);
  if (!clean(s.sahne_prompt)) return fail(`Sahne ${no} görsel tarifi boş`);

  const helper = s.yardimci_var === true || s.yardimci_var === 'true';
  const setting = s.mekan || ep.mekan_prompt;
  const prompt = [
    CHARACTER,
    helper ? ep.yardimci_karakter_prompt : null,
    clean(s.sahne_prompt),
    setting ? `Setting: ${setting}` : null,
    STYLE,
  ].filter(Boolean).join('. ');

  // Fındık her sahnede Drive'daki referans görsele göre çizilir (Flux Kontext).
  const image_request = {
    model: 'Qubico/flux1-dev-advanced',
    task_type: 'kontext',
    input: {
      prompt: `Keep the fox character from the reference image exactly the same: same face, same orange fur, same red knitted scarf and yellow backpack with the green leaf. New scene: ${prompt}`,
      image: ref,
      width: 576,
      height: 1024,
      steps: 28,
    },
  };

  items.push({
    json: {
      valid: true,
      scene: no,
      narration,
      image_request,
      video_prompt: clean(s.hareket_prompt) || 'gentle natural movement, slow camera push in',
      episode,
    },
  });
}

// Görsel/video tekrar deneme sayaçlarını sıfırla.
$getWorkflowStaticData('global').retries = {};
return items;"""

node("Senaryoyu Ayrıştır", "n8n-nodes-base.code", 2, [1320, 0], {"jsCode": PARSE_JS})
node("Senaryo Geçerli mi?", "n8n-nodes-base.if", 2.2, [1540, 0],
     cond("={{ $json.valid }}", "boolean", "true", single=True))

# ---------------------------------------------------------------- 2. Sahne döngüsü
node("Sahne Döngüsü", "n8n-nodes-base.splitInBatches", 3, [1760, 0],
     {"batchSize": 1, "options": {}})

node("Görsel Üret", "n8n-nodes-base.httpRequest", 4.2, [2000, -400],
     http("POST", "https://api.piapi.ai/api/v1/task", PIAPI,
          "={{ JSON.stringify(" + SCENE + ".image_request) }}"))
node("Görseli Bekle", "n8n-nodes-base.wait", 1.1, [2200, -400], wait(1, "minutes"))
node("Görsel Durumu", "n8n-nodes-base.httpRequest", 4.2, [2400, -400],
     http("GET", "=https://api.piapi.ai/api/v1/task/{{ $json.data.task_id }}", PIAPI))

def check_js(kind, label, max_fail, max_poll):
    return (r"""// PiAPI görev durumunu yorumlar: done = hazır, retry = hata aldı tekrar üret, wait = beklemeye devam.
const data = $json.data || {};
const status = String(data.status || '').toLowerCase();
const scene = $('Sahne Döngüsü').item.json.scene;
const store = $getWorkflowStaticData('global');
store.retries = store.retries || {};
const bump = (k) => (store.retries[k] = (store.retries[k] || 0) + 1);

let route = 'wait';
if (status === 'completed') {
  route = 'done';
} else if (status === 'failed') {
  if (bump(`KIND-fail-${scene}`) > MAXFAIL) {
    throw new Error(`Sahne ${scene}: LABEL MAXFAIL denemede üretilemedi. ${JSON.stringify(data.error || {})}`);
  }
  route = 'retry';
} else if (bump(`KIND-poll-${scene}`) > MAXPOLL) {
  throw new Error(`Sahne ${scene}: LABEL MAXPOLL kontrolde hazır olmadı (durum: ${status || 'bilinmiyor'})`);
}
return { json: { ...$json, route } };"""
            .replace("KIND", kind).replace("LABEL", label)
            .replace("MAXFAIL", str(max_fail)).replace("MAXPOLL", str(max_poll)))

node("Görsel Kontrol", "n8n-nodes-base.code", 2, [2600, -400],
     {"mode": "runOnceForEachItem", "jsCode": check_js("img", "görsel", 3, 30)})
node("Görsel Hazır mı?", "n8n-nodes-base.if", 2.2, [2800, -400],
     cond("={{ $json.route }}", "string", "equals", "done"))
node("Görsel Hatalı mı?", "n8n-nodes-base.if", 2.2, [3000, -260],
     cond("={{ $json.route }}", "string", "equals", "retry"))
node("Görseli Tekrar Bekle", "n8n-nodes-base.wait", 1.1, [3200, -160], wait(30, "seconds"))

KLING_NEG = ("blurry motion, distorted faces, extra limbs, morphing, flickering, "
             "scary, dark, text, watermark, bad quality")
VIDEO_BODY = ("={{ JSON.stringify({ model: 'kling', task_type: 'video_generation', input: { "
              "prompt: " + SCENE + ".video_prompt, "
              "negative_prompt: '" + KLING_NEG + "', "
              "cfg_scale: 0.5, duration: 5, "
              "mode: " + K + "['Kling Mode'], "
              "version: " + K + "['Kling Version'], "
              "image_url: $('Görsel Kontrol').item.json.data.output.image_url "
              "} }) }}")
node("Video Üret", "n8n-nodes-base.httpRequest", 4.2, [3200, -560],
     http("POST", "https://api.piapi.ai/api/v1/task", PIAPI, VIDEO_BODY))
node("Videoyu Bekle", "n8n-nodes-base.wait", 1.1, [3400, -560], wait(3, "minutes"))
node("Video Durumu", "n8n-nodes-base.httpRequest", 4.2, [3600, -560],
     http("GET", "=https://api.piapi.ai/api/v1/task/{{ $json.data.task_id }}", PIAPI))
node("Video Kontrol", "n8n-nodes-base.code", 2, [3800, -560],
     {"mode": "runOnceForEachItem", "jsCode": check_js("vid", "video", 3, 40)})
node("Video Hazır mı?", "n8n-nodes-base.if", 2.2, [4000, -560],
     cond("={{ $json.route }}", "string", "equals", "done"))
node("Video Hatalı mı?", "n8n-nodes-base.if", 2.2, [4200, -420],
     cond("={{ $json.route }}", "string", "equals", "retry"))
node("Videoyu Tekrar Bekle", "n8n-nodes-base.wait", 1.1, [4400, -320], wait(1, "minutes"))

SAVE_JS = r"""// Sahnenin bilgilerini üretilen video ile birlikte döngüye geri verir.
const scene = $('Sahne Döngüsü').item.json;
const out = $json.data?.output || {};
const video_url = out.video_url
  || out.works?.[0]?.video?.resource_without_watermark
  || out.works?.[0]?.video?.resource;
if (!video_url) throw new Error(`Sahne ${scene.scene}: video adresi bulunamadı`);

const { image_request, ...rest } = scene;
return {
  json: {
    ...rest,
    image_url: $('Görsel Kontrol').item.json.data.output.image_url,
    video_url,
  },
};"""
node("Sahneyi Kaydet", "n8n-nodes-base.code", 2, [4200, -700],
     {"mode": "runOnceForEachItem", "jsCode": SAVE_JS})

# ---------------------------------------------------------------- 3. Ses ve kurgu
COLLECT_JS = r"""// Döngüden çıkan 10 sahneyi tek bir bölüm kaydında toplar.
const scenes = $input.all().map((i) => i.json).sort((a, b) => a.scene - b.scene);
if (scenes.length !== 10) throw new Error(`10 sahne bekleniyordu, ${scenes.length} geldi`);

return [{
  json: {
    ...scenes[0].episode,
    scenes: scenes.map(({ scene, narration, image_url, video_url }) => ({
      scene, narration, image_url, video_url,
    })),
    narration_text: scenes.map((s) => s.narration).join(' '),
  },
}];"""
node("Bölümü Topla", "n8n-nodes-base.code", 2, [2000, 400], {"jsCode": COLLECT_JS})

VOICE_BODY = ("={{ JSON.stringify({ text: $json.narration_text, model_id: 'eleven_multilingual_v2', "
              "voice_settings: { stability: 0.6, similarity_boost: 0.75, style: 0.2, "
              "use_speaker_boost: true, speed: 0.9 } }) }}")
node("Seslendir", "n8n-nodes-base.httpRequest", 4.2, [2200, 400],
     http("POST", "=https://api.elevenlabs.io/v1/text-to-speech/{{ " + K + "['ElevenLabs Voice ID'] }}?output_format=mp3_44100_128",
          [("xi-api-key", "={{ " + K + "['ElevenLabs API Key'] }}"),
           ("Content-Type", "application/json")],
          VOICE_BODY, file_response=True))

BOLUM = "$('Bölümü Topla').first().json"

node("Ses Dosyasını Yükle", "n8n-nodes-base.googleDrive", 3, [2400, 400],
     {"name": "=bolum-{{ " + BOLUM + ".bolum }}-seslendirme.mp3", "driveId": DRIVE,
      "folderId": folder("Drive Ses Klasor ID"), "options": {}})
node("Ses Paylaşım İzni", "n8n-nodes-base.googleDrive", 3, [2600, 400], share("={{ $json.id }}"))

RENDER_JS = r"""// Creatomate için kurguyu (RenderScript) hazırlar: 10 klip + seslendirme.
const ep = $('Bölümü Topla').first().json;
const voiceId = $('Ses Dosyasını Yükle').first().json.id;
const voiceUrl = `https://drive.google.com/uc?export=download&id=${voiceId}`;
const SCENE_SECONDS = 5;
const total = ep.scenes.length * SCENE_SECONDS;

const elements = ep.scenes.map((s, i) => ({
  name: `Video-${i + 1}`,
  type: 'video',
  track: 1,
  time: i * SCENE_SECONDS,
  duration: SCENE_SECONDS,
  source: s.video_url,
  fit: 'cover',
  volume: '0%',
}));

elements.push({ name: 'Voice', type: 'audio', track: 2, time: 0.3, source: voiceUrl });


return [{
  json: {
    render: { output_format: 'mp4', width: 1080, height: 1920, frame_rate: 30, duration: total, elements },
  },
}];"""
node("Kurgu Hazırla", "n8n-nodes-base.code", 2, [2800, 400], {"jsCode": RENDER_JS})
node("Videoyu Birleştir", "n8n-nodes-base.httpRequest", 4.2, [3000, 400],
     http("POST", "https://api.creatomate.com/v2/renders", CREATO,
          "={{ JSON.stringify($json.render) }}"))
node("Kurguyu Bekle", "n8n-nodes-base.wait", 1.1, [3200, 400], wait(1, "minutes"))
node("Kurgu Durumu", "n8n-nodes-base.httpRequest", 4.2, [3400, 400],
     http("GET", "=https://api.creatomate.com/v2/renders/{{ $('Videoyu Birleştir').first().json.id }}", CREATO))
node("Kurgu Hazır mı?", "n8n-nodes-base.if", 2.2, [3600, 400],
     cond("={{ $json.status }}", "string", "equals", "succeeded"))
node("Kurgu Hatalı mı?", "n8n-nodes-base.if", 2.2, [3800, 560],
     cond("={{ $json.status }}", "string", "equals", "failed"))
node("Kurgu Hatası", "n8n-nodes-base.stopAndError", 1, [4000, 500],
     {"errorMessage": "=Creatomate kurgusu başarısız oldu: {{ $json.error_message || 'bilinmeyen hata' }}"})

# ---------------------------------------------------------------- 4. Drive (final)
node("Videoyu İndir", "n8n-nodes-base.httpRequest", 4.2, [3800, 300],
     {"url": "={{ $json.url }}",
      "options": {"response": {"response": {"responseFormat": "file"}}}})
node("Videoyu Arşivle", "n8n-nodes-base.googleDrive", 3, [4000, 300],
     {"name": "=Bölüm {{ " + BOLUM + ".bolum }} - {{ " + BOLUM + ".meslek }}.mp4", "driveId": DRIVE,
      "folderId": folder("Drive Final Klasor ID"), "options": {}})
SHEET_COLS = ["id", "bolum", "baslik", "meslek", "yardimci_karakter", "yardimci_karakter_prompt",
              "mekan_prompt", "kategori", "deger", "sorun", "bilgi", "kapanis_mesaji",
              "production", "publishing", "final_output", "youtube_url"]
node("Tabloyu Güncelle", "n8n-nodes-base.googleSheets", 4.5, [4200, 300], {
    "operation": "update", "documentId": SHEET_ID, "sheetName": SHEET_TAB,
    "columns": {
        "mappingMode": "defineBelow",
        "value": {
            "id": "={{ " + BOLUM + ".id }}",
            "production": "done",
            "final_output": "=https://drive.google.com/file/d/{{ $json.id }}/view",
        },
        "matchingColumns": ["id"],
        "schema": [{"id": c, "displayName": c, "required": False, "defaultMatch": c == "id",
                    "display": True, "type": "string", "canBeUsedToMatch": True,
                    "removed": c not in ("id", "production", "final_output")}
                   for c in SHEET_COLS],
    },
    "options": {}})
# ---------------------------------------------------------------- Bağlantılar
link("Elle Başlat", "Ayarlar")
link("Her Gün 07:00", "Ayarlar")
link("Ayarlar", "PiAPI Bakiye")
link("PiAPI Bakiye", "Bakiye Kontrol")
link("Bakiye Kontrol", "Referans Görseli Bul")
link("Referans Görseli Bul", "Referans Kontrol")
link("Referans Kontrol", "Referans Paylaşım İzni")
link("Referans Paylaşım İzni", "Bölümleri Oku")
link("Bölümleri Oku", "İlk Bölümü Al")
link("İlk Bölümü Al", "Bölüm Var mı?")
link("Bölüm Var mı?", "Senaryo Yaz", 0)
link("Senaryo Yaz", "Senaryoyu Ayrıştır")
link("Senaryoyu Ayrıştır", "Senaryo Geçerli mi?")
link("Senaryo Geçerli mi?", "Sahne Döngüsü", 0)
link("Senaryo Geçerli mi?", "Senaryo Yaz", 1)

link("Sahne Döngüsü", "Bölümü Topla", 0)   # done
link("Sahne Döngüsü", "Görsel Üret", 1)    # loop
link("Görsel Üret", "Görseli Bekle")
link("Görseli Bekle", "Görsel Durumu")
link("Görsel Durumu", "Görsel Kontrol")
link("Görsel Kontrol", "Görsel Hazır mı?")
link("Görsel Hazır mı?", "Video Üret", 0)
link("Görsel Hazır mı?", "Görsel Hatalı mı?", 1)
link("Görsel Hatalı mı?", "Görsel Üret", 0)
link("Görsel Hatalı mı?", "Görseli Tekrar Bekle", 1)
link("Görseli Tekrar Bekle", "Görsel Durumu")
link("Video Üret", "Videoyu Bekle")
link("Videoyu Bekle", "Video Durumu")
link("Video Durumu", "Video Kontrol")
link("Video Kontrol", "Video Hazır mı?")
link("Video Hazır mı?", "Sahneyi Kaydet", 0)
link("Video Hazır mı?", "Video Hatalı mı?", 1)
link("Video Hatalı mı?", "Video Üret", 0)
link("Video Hatalı mı?", "Videoyu Tekrar Bekle", 1)
link("Videoyu Tekrar Bekle", "Video Durumu")
link("Sahneyi Kaydet", "Sahne Döngüsü")

link("Bölümü Topla", "Seslendir")
link("Seslendir", "Ses Dosyasını Yükle")
link("Ses Dosyasını Yükle", "Ses Paylaşım İzni")
link("Ses Paylaşım İzni", "Kurgu Hazırla")
link("Kurgu Hazırla", "Videoyu Birleştir")
link("Videoyu Birleştir", "Kurguyu Bekle")
link("Kurguyu Bekle", "Kurgu Durumu")
link("Kurgu Durumu", "Kurgu Hazır mı?")
link("Kurgu Hazır mı?", "Videoyu İndir", 0)
link("Kurgu Hazır mı?", "Kurgu Hatalı mı?", 1)
link("Kurgu Hatalı mı?", "Kurgu Hatası", 0)
link("Kurgu Hatalı mı?", "Kurguyu Bekle", 1)

link("Videoyu İndir", "Videoyu Arşivle")
link("Videoyu Arşivle", "Tabloyu Güncelle")

# ---------------------------------------------------------------- Notlar
sticky("Not: Başlangıç", [-80, -560], 1140, 500, 5,
"""## 🦊 Fındık'ın Meslek Macerası — Otomatik Bölüm Üretici

**Yarı otonom mod:** Bölümleri sen `Seneryo/sezon-1` tablosuna yazarsın, workflow'u **Elle Başlat** ile çalıştırırsın. `production = for production` olan **ilk** bölüm üretilir, bitmiş video `final` klasörüne düşer. Başka hiçbir yere yüklenmez.

**İlk kurulum:**
1. **Ayarlar** node'unu doldur (API anahtarları, `Seneryo/sezon-1` Sheet ID, `sesler`, `final` ve `fındık referans` klasör ID'leri).
2. OpenAI, Google Sheets ve Google Drive node'larına credential bağla.
3. **Elle Başlat** → Test workflow.

Tam otomatiğe geçmek istersen **Her Gün 07:00** node'unu aktif et.

**Bakiye koruması:** Başta PiAPI bakiyesi kontrol edilir; `Minimum PiAPI Bakiye USD` altındaysa workflow hiçbir şey üretmeden durur.

**Karakter tutarlılığı:** Workflow her çalıştığında `fındık referans` klasöründeki PNG'yi alır ve her sahnede Fındık'ı bu görsele göre çizer (Flux Kontext). Klasörde tek bir PNG tut.

Tüm dizi kuralları: `content/seri-rehberi.md`""")

sticky("Not: Senaryo", [1080, -240], 640, 420, 4,
"""### 1. Senaryo
OpenAI 10 sahnelik senaryoyu JSON olarak yazar. **Senaryoyu Ayrıştır** bunu doğrular (10 sahne, en fazla 14 kelime), açılış/kapanış cümlelerini sabitler ve karakter kartını görsel prompt'larına **kodla** ekler. Geçersizse en fazla 3 kez yeniden yazdırır.""")

sticky("Not: Sahneler", [1960, -900], 2600, 860, 6,
"""### 2. Sahne döngüsü (her sahne sırayla)
Flux ile görsel → Kling ile 5 sn video. Her görev bitene kadar beklenir; hata alan görev en fazla 3 kez yeniden üretilir, sonra workflow durur (boşa para yakmamak için). Kling modu ve versiyonu **Ayarlar**'dan değişir (`std` ≈ $0.26/klip).""")

sticky("Not: Kurgu", [1960, 160], 2140, 560, 3,
"""### 3. Ses ve kurgu
ElevenLabs tüm anlatımı tek parça seslendirir, ses `sesler` klasörüne yüklenir. Creatomate 10 klibi ve sesi 1080x1920 tek videoda birleştirir; şablon gerekmez.""")

sticky("Not: Drive", [3960, 160], 480, 400, 7,
"""### 4. Drive
Bitmiş video `final` klasörüne `Bölüm N - Meslek.mp4` adıyla kaydedilir. Tabloda bölüm `done` olur, `final_output` sütununa video linki yazılır.""")

FIXED = {"Elle Başlat", "Her Gün 07:00", "Ayarlar", "PiAPI Bakiye", "Bakiye Kontrol", "Referans Görseli Bul",
         "Referans Kontrol", "Referans Paylaşım İzni", "Not: Başlangıç"}
for n in nodes:
    if n["name"] not in FIXED:
        n["position"] = [n["position"][0] + 1100, n["position"][1]]

wf = {"name": "Fındık'ın Meslek Macerası", "nodes": nodes, "connections": conns,
      "pinData": {}, "settings": {"executionOrder": "v1"},
      "meta": {"templateCredsSetupCompleted": False}}

# Doğrulama
names = {n["name"] for n in nodes}
assert len(names) == len(nodes), "yinelenen node adı"
for src, c in conns.items():
    assert src in names, src
    for outs in c["main"]:
        for t in outs:
            assert t["node"] in names, t["node"]

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)
print(f"{len(nodes)} node, {sum(len(o) for c in conns.values() for o in c['main'])} bağlantı yazıldı")
