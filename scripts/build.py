#!/usr/bin/env python3
"""Статические сертификаты из CSV. Запуск: python scripts/build.py --base-url https://USER.github.io/REPO"""
import argparse,csv,datetime,html,json,re,shutil
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--base-url',default='http://localhost:8000');args=p.parse_args();base=args.base_url.rstrip('/')
if urlparse(base).scheme not in ('http','https') or not urlparse(base).netloc:raise ValueError('Нужен абсолютный http(s) base-url')
rows=[];seen=set()
with (ROOT/'data/graduates.csv').open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f)
 if reader.fieldnames!=['first_name','last_name','course','date','code','example']:raise ValueError('Неверные заголовки CSV')
 for r in reader:
  if None in r: raise ValueError('Лишние колонки CSV: заключите поля с запятой в двойные кавычки')
  r={k:v.strip() if v is not None else '' for k,v in r.items()}
  if not all(r.values()):raise ValueError('Пустое поле в CSV')
  if not re.fullmatch(r'[A-Za-z0-9_-]{24,64}',r['code']) or r['code'] in seen:raise ValueError('Код должен быть уникальным, 24–64 символа A–Z a–z 0–9 _ -')
  if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',r['date']): raise ValueError('Дата должна быть ГГГГ-ММ-ДД')
  seen.add(r['code']);datetime.date.fromisoformat(r['date'])
  if r['example'] not in ('true','false'):raise ValueError('example должен быть true/false')
  for key in ('first_name','last_name','course'):
   if len(r[key])>200:raise ValueError('Слишком длинное поле '+key)
  r['example']=r['example']=='true';rows.append(r)
out=ROOT/'_site'
if out.exists():shutil.rmtree(out)
out.mkdir();shutil.copytree(ROOT/'assets',out/'assets');(out/'.nojekyll').touch();shutil.copy(ROOT/'code-generator.html',out/'code-generator.html')
def esc(s):return html.escape(str(s),quote=True)
def page(title,body,prefix='',url='',image='',dataset=''):
 return f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Моноид</title><meta name="description" content="{esc(title)}"><meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(('Демонстрационный пример. Не подтверждает обучение. ' if title.startswith('ПРИМЕР') else '')+'Сертификат курса Safety Evals. Проверка по уникальному коду.')}"><meta property="og:url" content="{esc(url)}"><meta property="og:image" content="{esc(image or base+'/assets/course-preview.png')}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><link rel="canonical" href="{esc(url)}"><link rel="stylesheet" href="{prefix}assets/site.css"><link rel="icon" href="{prefix}assets/logo/icon.svg"><script defer src="{prefix}assets/certificate.js"></script></head><body class="cert-page" {dataset}><nav class="cert-nav" aria-label="Навигация"><a class="brand" href="{prefix}index.html">Моноид</a><div><a href="{prefix}index.html">О курсе</a> · <a href="{prefix}verify.html">Проверить сертификат</a></div></nav><main class="cert-main">{body}<footer class="cert-foot">Моноид · Safety Evals · <a href="{prefix}verify.html">Реестр сертификатов</a></footer></main></body></html>'''
def font(size):
 for path in [Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf')]:
  if path.exists():return ImageFont.truetype(str(path),size)
 raise RuntimeError('Установите fonts-dejavu-core для PNG')
def wrapped(draw,text,y,size,width=1060):
 f=font(size);line=''
 for word in text.split():
  # Длинное слово также переносим посимвольно.
  if draw.textlength(word,font=f)>width:
   if line:draw.text((70,y),line,font=f,fill='#222');y+=size+14;line=''
   for ch in word:
    if draw.textlength(line+ch,font=f)>width:draw.text((70,y),line,font=f,fill='#222');y+=size+14;line=''
    line+=ch
  elif draw.textlength((line+' '+word).strip(),font=f)>width:
   draw.text((70,y),line,font=f,fill='#222');y+=size+14;line=word
  else:line=(line+' '+word).strip()
 if line:draw.text((70,y),line,font=f,fill='#222');y+=size+14
 return y
preview=Image.new('RGB',(1200,630),'#f5f5f3');preview_draw=ImageDraw.Draw(preview)
wrapped(preview_draw,'Моноид',100,48)
wrapped(preview_draw,'Safety Evals',220,64)
wrapped(preview_draw,'Курс по оценке LLM и агентных систем',350,32)
wrapped(preview_draw,'Программа курса и реестр сертификатов',440,26)
preview.save(out/'assets/course-preview.png',optimize=True)
for r in rows:
 code=r['code'];folder=out/'certificate'/code;folder.mkdir(parents=True)
 name=r['first_name']+' '+r['last_name'];url=base+'/certificate/'+code+'/'
 dt=datetime.date.fromisoformat(r['date']);date=dt.strftime('%d.%m.%Y');title=('ПРИМЕР — ' if r['example'] else '')+name+' — '+r['course']
 im=Image.new('RGB',(1200,630),'#f5f5f3');d=ImageDraw.Draw(im);d.rectangle((30,30,1170,600),fill='white',outline='#cccccc',width=2);d.rectangle((30,30,1170,38),fill='#222')
 y=wrapped(d,'Моноид / СЕРТИФИКАТ'+(' · ПРИМЕР' if r['example'] else ''),65,26)
 y=wrapped(d,name,y+22,48 if len(name)<40 else 30)
 y=wrapped(d,r['course'],y+12,30 if len(r['course'])<80 else 20)
 y=wrapped(d,'Дата выдачи: '+date,y+20,22)
 y=wrapped(d,'ID: '+code,y+6,19)
 if y>545:raise ValueError('Текст не помещается в PNG; сократите имя/название курса')
 d.text((70,568),'Демонстрационная запись — не подтверждает обучение' if r['example'] else 'Проверка подлинности по коду на странице курса',font=font(18),fill='#666');im.save(folder/'certificate.png',optimize=True)
 sample='<aside class="sample">ПРИМЕР. Тестовые данные: этот сертификат не подтверждает прохождение курса.</aside>' if r['example'] else ''
 status='Демонстрационная запись' if r['example'] else 'Запись найдена в реестре'
 body=f'''{sample}<article class="cert-sheet"><div class="eyebrow">Сертификат об окончании курса</div><h1>{esc(name)}</h1><p>Завершил(а) курс</p><h2>{esc(r['course'])}</h2><p>Оценка LLM и агентных систем: подходы, бенчмарки и методология.</p><span class="status {"status-example" if r["example"] else ""}">{status}</span><dl class="cert-details"><div><dt>Дата выдачи</dt><dd>{date}</dd></div><div><dt>Код сертификата</dt><dd><code>{code}</code></dd></div><div><dt>Организатор</dt><dd>Моноид</dd></div></dl></article><div class="actions"><a id="linkedin" href="https://www.linkedin.com/profile/add" target="_blank" rel="noopener noreferrer">Добавить в LinkedIn</a><button id="copy" class="secondary">Скопировать ссылку</button><a class="secondary" href="certificate.png" download>Скачать PNG</a><button id="print" class="secondary">Печать / PDF</button></div><p id="share-status" role="status"></p><p class="hint">Публичная ссылка на этот сертификат доступна без регистрации. Проверка означает наличие записи в опубликованном реестре организатора.</p>'''
 if r['example']:
  body=re.sub(r'<a id="linkedin".*?</a>','<button class="secondary" disabled>LinkedIn недоступен для примера</button>',body)
 dataset=f'data-course="{esc(r["course"])}" data-year="{dt.year}" data-month="{dt.month}" data-code="{code}"'
 (folder/'index.html').write_text(page(title,body,'../../',url,url+'certificate.png',dataset),encoding='utf-8')
(out/'registry.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
verify='''<div class="eyebrow">Реестр выпускников</div><h1>Проверить сертификат</h1><p>Введите уникальный код со страницы сертификата.</p><form id="verify-form" class="verify-form"><label for="code">Код сертификата</label><input id="code" name="code" required maxlength="64" autocomplete="off" spellcheck="false" placeholder="Вставьте код"><button type="submit">Проверить</button></form><div id="verify-result" class="verify-result" role="status" aria-live="polite"></div><p class="hint">Записи с пометкой «Пример» демонстрационные и не подтверждают обучение. Реестр публикуется организатором курса.</p>'''
(out/'verify.html').write_text(page('Проверить сертификат',verify,url=base+'/verify.html'),encoding='utf-8')
source=(ROOT/'index.html').read_text()
source=re.sub(r'<meta\b(?=[^>]*property="og:url")[^>]*>',lambda m:'<meta property="og:url" content="'+esc(base+'/')+'">',source)
source=re.sub(r'<link\b(?=[^>]*rel="canonical")[^>]*>',lambda m:'<link rel="canonical" href="'+esc(base+'/')+'">',source)
source=source.replace('</head>','<meta property="og:image" content="'+esc(base+'/assets/course-preview.png')+'"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:description" content="Курс Safety Evals: подходы, бенчмарки и методология оценки LLM и агентных систем."></head>')
(out/'index.html').write_text(source,encoding='utf-8')
(out/'404.html').write_text(page('Страница не найдена',f'<h1>Страница не найдена</h1><p><a href="{esc(base)}/verify.html">Проверить код сертификата</a></p>',prefix=base+'/',url=base+'/404.html'),encoding='utf-8')
print(f'OK: {len(rows)} certificates; base={base}; output={out}')
