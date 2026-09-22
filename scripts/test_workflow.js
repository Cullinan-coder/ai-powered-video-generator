// Code node'larını sahte n8n verisiyle çalıştırır.  Kullanım:  node scripts/test_workflow.js [src/workflow.json]
const fs = require('fs');
const wf = JSON.parse(fs.readFileSync(process.argv[2] || 'src/workflow.json', 'utf8'));
const code = (n) => wf.nodes.find((x) => x.name === n).parameters.jsCode;
const lines = fs.readFileSync('content/sezon-1.csv', 'utf8').trim().split('\n');
const parseCsv = (l) => { const o = []; let c = '', q = false; for (const ch of l) { if (ch === '"') q = !q; else if (ch === ',' && !q) { o.push(c); c = ''; } else c += ch; } o.push(c.replace(/\r$/, '')); return o; };
const head = parseCsv(lines[0]); const ep = Object.fromEntries(parseCsv(lines[1]).map((v, i) => [head[i], v]));
const run = (src, ctx) => new Function(...Object.keys(ctx), src)(...Object.values(ctx));
const store = {};
const mk = (nodeData, input, runIndex = 0, json) => ({
  $: (n) => ({ first: () => ({ json: nodeData[n] }), item: { json: nodeData[n] } }),
  $input: { first: () => ({ json: input[0] }), all: () => input.map((j) => ({ json: j })) },
  $json: json, $runIndex: runIndex, $getWorkflowStaticData: () => store,
});
// Referans Kontrol
const rk = code('Referans Kontrol');
console.log('ref', JSON.stringify(run(rk, mk({}, [{ id: 'a', name: 'not.txt', mimeType: 'text/plain' }, { id: 'F1', name: 'findik.png', mimeType: 'image/png' }]))));
try { run(rk, mk({}, [{}])); } catch (e) { console.log('ref empty throws:', e.message); }
// Senaryo
const scenes = Array.from({ length: 10 }, (_, i) => ({ no: i + 1, anlatim: `Sahne ${i + 1} için "kısa" anlatım 🦊`, sahne_prompt: 'Findik looks around', hareket_prompt: 'slow push in', yardimci_var: i % 2 === 0 }));
const nd = { 'İlk Bölümü Al': ep, 'Referans Kontrol': { url: 'https://drive.google.com/uc?export=download&id=F1' } };
let out = run(code('Senaryoyu Ayrıştır'), mk(nd, [{ choices: [{ message: { content: JSON.stringify({ sahneler: scenes }) } }] }]));
console.log('items', out.length, 'valid', out[0].json.valid, 'keys', Object.keys(out[0].json).join(','));
console.log('s1', out[0].json.narration, '| s10', out[9].json.narration);
console.log('req', out[2].json.image_request.model, out[2].json.image_request.task_type, out[2].json.image_request.input.image);
console.log('prompt', out[2].json.image_request.input.prompt.slice(0, 160), '...');
out = run(code('Senaryoyu Ayrıştır'), mk(nd, [{ choices: [{ message: { content: '{"sahneler":[]}' } }] }]));
console.log('invalid', JSON.stringify(out));
// Kontrol
const chk = code('Görsel Kontrol');
for (const st of ['processing', 'completed', 'failed', 'failed', 'failed', 'failed']) {
  try { console.log(st, '->', run(chk, mk({ 'Sahne Döngüsü': { scene: 3 } }, [], 0, { data: { status: st } })).json.route); } catch (e) { console.log(st, 'throws:', e.message.slice(0, 60)); }
}
// Topla + kurgu
const items = Array.from({ length: 10 }, (_, i) => ({ scene: 10 - i, narration: `n${10 - i}`, video_url: `v${10 - i}`, image_url: 'i', episode: { id: 1, bolum: 1, meslek: 'İtfaiyeci' } }));
const col = run(code('Bölümü Topla'), mk({}, items))[0].json;
console.log('collect', col.scenes.map((s) => s.video_url).join(','), '|', col.narration_text);
const r = run(code('Kurgu Hazırla'), mk({ 'Bölümü Topla': col, 'Ses Dosyasını Yükle': { id: 'abc' } }, []))[0].json.render;
console.log('render', r.duration, 's,', r.elements.length, 'element:', [...new Set(r.elements.map((e) => e.type))].join('/'));
