"""src/workflow.json'u, yerel n8n'deki mevcut Ayarlar değerleri, credential'lar ve elle düzeltilmiş
Sheets node ayarlarıyla birleştirip local/workflow.local.json olarak yazar (git'e girmez).
n8n veritabanı yalnızca okunur.

Kullanım:  python scripts/make_local.py [n8n-workflow-id]
Workflow ID verilmezse adı "Fındık'ın Meslek Macerası" olan workflow kullanılır.
"""
import sqlite3, json, os, sys
db = os.path.expanduser('~/.n8n/database.sqlite')
con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
if len(sys.argv) > 1:
    row = con.execute('select nodes from workflow_entity where id=?', (sys.argv[1],)).fetchone()
else:
    row = con.execute("select nodes from workflow_entity where name=? order by updatedAt desc", ("Fındık'ın Meslek Macerası",)).fetchone()
old = json.loads(row[0])
old_by_name = {n['name']: n for n in old}
old_vals = {a['name']: a['value'] for a in old_by_name['Ayarlar']['parameters']['assignments']['assignments']}

wf = json.load(open('src/workflow.json', encoding='utf-8'))
kept, creds = [], []
for n in wf['nodes']:
    if n['name'] == 'Ayarlar':
        for a in n['parameters']['assignments']['assignments']:
            v = old_vals.get(a['name'])
            if v not in (None, '') and not str(v).startswith('YOUR_'):
                a['value'] = v; kept.append(a['name'])
    o = old_by_name.get(n['name'])
    # Kullanıcının n8n'de elle düzelttiği node'ların ayarlarını aynen koru
    if o and n['name'] in ('Bölümleri Oku', 'Tabloyu Güncelle'):
        n['parameters'] = o['parameters']; kept.append(n['name'] + ' (ayarlar)')
    if o and o.get('credentials'):
        n['credentials'] = o['credentials']; creds.append(n['name'])
os.makedirs('local', exist_ok=True)
json.dump(wf, open('local/workflow.local.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('korunan değerler:', kept); print('korunan credential:', creds)
