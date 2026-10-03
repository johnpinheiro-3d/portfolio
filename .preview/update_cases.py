from pathlib import Path
import re
import shutil
import json

root = Path(__file__).resolve().parent.parent
data = {
 'bike-itau': ('Facilitar o uso do app e o acesso às informações.', 'Aplicativo mobile', 'Redesign de interface', ['Visão geral','Esboço','Wireframes','Identidade visual','Interface final']),
 'casas-bahia': ('Simplificar a página de produto e explorar sua visualização em 3D.', 'Web e realidade aumentada', 'Redesign de página de produto', ['Desafio','Esboço','Wireframes','Realidade aumentada','Identidade visual','Interface final']),
 'cashforce': ('Organizar a captura de leads com a entrega de um e-book.', 'Desktop e mobile', 'Landing page e formulário', ['Desafio','Esboço','Wireframes','Identidade visual','Interface final']),
 'hi-rez': ('Facilitar a descoberta e o acesso aos jogos no site.', 'Interface web', 'Redesign da página de jogos', ['Desafio','Personas','Esboço','Wireframes','Tipografia','Interface final']),
 'rede-otaku': ('Reunir as funções importantes para quem assiste a animes.', 'Aplicativo mobile', 'Pesquisa, interface e protótipo', ['Interface','Desafio','Método','Pesquisa','Personas','Esboço','Arquitetura','Wireframes','Identidade visual','Logo e ícones','Interface final'])
}
assets = root/'assets'/'personas'
assets.mkdir(exist_ok=True)
baseline = {}
for slug,(goal,platform,scope,labels) in data.items():
 path = root/f'projeto-{slug}.html'
 s = path.read_text(encoding='utf-8')
 baseline[path.name] = {
  'images': len(re.findall(r'<img\b',s)),
  'videos': len(re.findall(r'<video\b',s)),
  'quotes': re.findall(r'<blockquote>(.*?)</blockquote>',s,re.S),
  'sources': re.findall(r'<(?:video|source)\b[^>]*src="([^"]+)"',s)
 }
 s = s.replace('<body>', '<body class="case-study">')
 s = re.sub(r'refinement.css\?v=\d+', 'refinement.css?v=9', s)
 s = s.replace('</head>', '<link rel="stylesheet" href="assets/case-layout.css?v=1">\n</head>')
 summary = '\n    <dl class="case-overview">' + ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k,v in [('Objetivo',goal),('Plataforma',platform),('Escopo',scope)]) + '</dl>'
 s = re.sub(r'(<p class="case-lead">.*?</p>)', lambda m:m[0]+summary, s, count=1)
 sections = list(re.finditer(r'<section class="case-block">.*?</section>', s, re.S))
 chunks = [m[0] for m in sections]
 if slug == 'rede-otaku':
  chunks[1],chunks[2] = chunks[2],chunks[1]
  chunks[0] = chunks[0].replace('<section class="case-block">', '<section class="case-block">\n    <div class="case-block__inner"><h2>A interface em perspectiva</h2><p>Uma prévia das telas antes de acompanhar a pesquisa e o desenvolvimento do aplicativo.</p></div>')
 assert len(chunks)==len(labels), (slug,len(chunks),len(labels))
 new_chunks=[]
 for i,chunk in enumerate(chunks,1):
  chunk=chunk.replace('<section class="case-block">', f'<section class="case-block" id="etapa-{i}" aria-labelledby="titulo-etapa-{i}">',1)
  chunk=chunk.replace('<h2>', f'<h2 id="titulo-etapa-{i}">',1)
  new_chunks.append(chunk)
 s=s[:sections[0].start()]+'\n  '.join(new_chunks)+s[sections[-1].end():]
 outline='<nav class="case-outline" aria-label="Etapas do projeto"><ul>'+''.join(f'<li><a href="#etapa-{i}">{label}</a></li>' for i,label in enumerate(labels,1))+'<li><a href="#prototipo">Protótipo interativo</a></li></ul></nav>\n\n  '
 s=s.replace('<section class="case-block"',outline+'<section class="case-block"',1)
 s=s.replace('<section class="case-proto">','<section class="case-proto" id="prototipo">')
 if slug in ['hi-rez','rede-otaku']:
  index=[0]
  def portrait(m):
   i=index[0]; index[0]+=1
   modifier='hi-rez' if slug=='hi-rez' else ['luiza','gabriel'][i]
   name=f'{slug}-{i}.png'
   shutil.copyfile(root/'.preview'/f'projeto-{slug}-{i}.png', assets/name)
   img=re.sub(r'src="[^"]+"',f'src="assets/personas/{name}"',m[1])
   return '<div class="case-persona">\n      <div class="case-persona__portrait case-persona__portrait--'+modifier+'">'+img+'</div>'
  s=re.sub(r'<div class="case-persona">\s*(<img[^>]+>)',portrait,s)
  # Persona cards contain a portrait and a text block. Group the complete cards.
  pattern=r'(<div class="case-persona">.*?</blockquote>\s*</div>\s*</div>\s*){2}'
  s,n=re.subn(pattern,lambda m:'<div class="case-personas">\n'+m[0]+'</div>\n  ',s,flags=re.S)
  assert n==1,slug
 s=s.replace('Entregar | Prototipação — Tipografia + paleta de cores','Tipografia e paleta de cores')
 s=s.replace('Prototipação — Tipografia + paleta de cores','Tipografia e paleta de cores')
 s=s.replace('Tipografia + paleta de cores</h2>','Tipografia e paleta de cores</h2>')
 if slug=='rede-otaku':
  s=s.replace('1) Descobrir | A pesquisa','Pesquisa com usuários').replace('2) Definir | Entendendo o problema','Necessidades e personas').replace('3) Desenvolver | Design','Esboços da interface').replace('4) Entregar | Prototipação','Tipografia e paleta de cores')
  s=re.sub(r'((?:<div class="case-quote">.*?</div>\s*){4})',lambda m:'<div class="case-quotes">'+m[1]+'</div>\n',s,flags=re.S)
  # Split the 22 existing videos by user journey, without removing any clip.
  match=re.search(r'<div class="case-video-grid">((?:<div class="case-video-item case-video-item--portrait">.*?</div>)+)</div>',s,re.S)
  assert match
  videos=re.findall(r'<div class="case-video-item case-video-item--portrait">.*?</div>',match[1],re.S)
  assert len(videos)==22
  groups=[('Primeiros passos',0,4),('Descoberta e reprodução',4,11),('Menu e perfil',11,16),('Amigos e comunidade',16,22)]
  organized='\n'.join('<h3 class="case-sub">'+title+'</h3>\n<div class="case-video-grid">'+''.join(videos[a:b])+'</div>' for title,a,b in groups)
  s=s[:match.start()]+organized+s[match.end():]
 if slug=='cashforce':
  s=s.replace('<div class="case-sub">Mobile</div>','<div class="case-sub">Versão mobile e formulários</div>')
  s=s.replace('<div class="case-row case-row--h300"><img', '<div class="case-row case-row--h300"><img',1)
  # Name the final pair separately from the capture forms.
  marker='<div class="case-row case-row--h300"><img'
  pos=s.rfind(marker)
  if pos!=-1: s=s[:pos]+'<div class="case-sub">Confirmação do cadastro</div>\n    '+s[pos:]
 tool='Figma' if slug in ['bike-itau','cashforce'] else 'Adobe XD'
 s=s.replace('direto no Figma ou Adobe XD.',f'no {tool}.')
 path.write_text(s,encoding='utf-8')
(root/'.preview'/'case-baseline.json').write_text(json.dumps(baseline,ensure_ascii=False),encoding='utf-8')
print('Cinco páginas reorganizadas; quatro retratos enquadrados; 22 vídeos agrupados.')
