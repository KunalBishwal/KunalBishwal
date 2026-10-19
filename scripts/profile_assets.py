#!/usr/bin/env python3
"""Generate Kunal's self-hosted GitHub profile SVG assets.

Purpose-built implementation inspired by the terminal banner, radar visualisations,
and generated stat cards in https://github.com/emmi-lili/emmi-lili. This script does
not reuse upstream personal images or project artwork and uses only Python stdlib.
"""
from __future__ import annotations
import argparse, html, json, os, urllib.request
from pathlib import Path
import math

THEMES = {
 "dark": {"bg":"#0d1117","panel":"#111827","panel2":"#151d2e","border":"#30363d","text":"#dbe4f0","muted":"#8b9bb4","accent":"#a99bff","blue":"#60a5fa","green":"#6ee7b7","grid":"#253149","title":"#f5f7ff"},
 "light":{"bg":"#f7f8fc","panel":"#ffffff","panel2":"#eef2fb","border":"#d7ddec","text":"#273149","muted":"#67728b","accent":"#715be8","blue":"#1875c9","green":"#16865d","grid":"#dce2ee","title":"#171a2b"}
}
LANG_COLORS={"TypeScript":"#3178c6","JavaScript":"#f1e05a","Python":"#3572A5","HTML":"#e34c26","CSS":"#563d7c","Java":"#b07219","C++":"#f34b7d","C":"#555555","Jupyter Notebook":"#DA5B0B","Shell":"#89e051","Go":"#00ADD8","Rust":"#dea584","SQL":"#e38c00"}
FONT="ui-sans-serif,-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"

def e(value): return html.escape(str(value), quote=True)
def text(x,y,value,size,color,weight=400,anchor="start",extra=""):
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}" {extra}>{e(value)}</text>'
def svg(w,h,label):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{e(label)}" font-family="{FONT}">'
def save(path,content):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(content,encoding="utf-8")

def banner(theme):
    c=THEMES[theme]; W,H=1200,360
    s=[svg(W,H,"Kunal Bishwal terminal-style profile banner")]
    s += [f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{c["bg"]}"/><stop offset="1" stop-color="{c["panel2"]}"/></linearGradient><linearGradient id="glow"><stop stop-color="{c["accent"]}"/><stop offset="1" stop-color="{c["blue"]}"/></linearGradient><pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="{c["grid"]}" stroke-width="1"/></pattern></defs>',
           f'<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/><rect width="{W}" height="{H}" rx="18" fill="url(#grid)"/>',
           f'<rect x="22" y="20" width="1156" height="320" rx="14" fill="{c["panel"]}" stroke="{c["border"]}"/><path d="M22 63H1178" stroke="{c["border"]}"/>']
    for x,col in zip((43,59,75),("#ff6b6b","#f5c451","#42d392")): s.append(f'<circle cx="{x}" cy="42" r="5" fill="{col}"/>')
    s += [text(94,46,"profile.sh — KUNALBISHWAL",12,c["muted"],600),text(1150,46,"LIVE / PROFILE",10,c["accent"],600,"end")]
    s += [text(52,91,"kunal@github",12,c["green"],600),text(146,91,":~$ whoami",12,c["text"],500),
          text(52,137,"KUNAL BISHWAL",33,c["title"],750),text(52,166,"Full-stack engineering  /  Applied AI",16,c["accent"],600),
          text(52,196,"SRM Institute of Science and Technology  ·  Class of 2027",12,c["muted"])]
    rows=[("FOCUS","Full-stack products + practical AI"),("BUILD","React · Next.js · TypeScript · Node.js"),("APPLIED AI","Python · Computer Vision · LLMs"),("STACK","PostgreSQL · Docker · AWS")]
    for i,(key,value) in enumerate(rows):
        y=231+i*25; s += [text(52,y,key,10,c["blue"],700,extra='letter-spacing="1.2"'),text(145,y,value,12,c["text"])]
    s += [f'<rect x="397" y="250" width="7" height="14" rx="1" fill="{c["accent"]}"><animate attributeName="opacity" values="1;0;1" dur="1.15s" repeatCount="indefinite"/></rect>',
          f'<rect x="765" y="82" width="385" height="232" rx="10" fill="{c["panel2"]}" stroke="{c["border"]}"/>',
          text(787,108,"// system map",11,c["muted"],600),text(1128,108,"v1.0",10,c["green"],600,"end")]
    for x,y,w,col in [(788,132,160,c["accent"]),(788,151,224,c["blue"]),(788,170,118,c["green"]),(788,189,194,c["muted"]),(788,208,143,c["accent"])]:
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="5" rx="2.5" fill="{col}" opacity=".84"/>')
    pts=[(820,268),(895,244),(970,273),(1040,231),(1100,266),(1005,297),(905,292)]
    for a,b in [(0,1),(1,2),(2,3),(3,4),(2,5),(5,6),(6,0),(1,6),(3,5)]:
        x1,y1=pts[a];x2,y2=pts[b];s.append(f'<path d="M{x1} {y1}L{x2} {y2}" stroke="url(#glow)" stroke-width="1.5" opacity=".65"/>')
    for i,(x,y) in enumerate(pts):
        col=c["accent"] if i%2==0 else c["blue"]
        s.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{col}"><animate attributeName="r" values="4;6;4" dur="{2.1+i*.17}s" repeatCount="indefinite"/></circle>')
    s += [text(52,318,"BUILD  /  LEARN  /  SHIP",10,c["muted"],600,extra='letter-spacing="2"'),text(1147,318,"GITHUB.COM/KUNALBISHWAL",10,c["muted"],600,"end"),"</svg>"]
    return "".join(s)

def radar(data_path,theme):
    data=json.loads(data_path.read_text(encoding="utf-8"))
    axes=[(a["label"],float(a["value"])) for a in data["axes"]]; title=data.get("title","Engineering focus")
    c=THEMES[theme]; W,H=620,405; cx,cy=310,202; radius=125; n=len(axes)
    s=[svg(W,H,title),f'<rect width="100%" height="100%" rx="12" fill="{c["bg"]}"/>',text(W/2,27,title,16,c["title"],700,"middle")]
    def point(rad,i):
        angle=-math.pi/2+i*2*math.pi/n
        return cx+rad*math.cos(angle),cy+rad*math.sin(angle)
    for k in range(1,6):
        pts=[point(radius*k/5,i) for i in range(n)]
        s.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" fill="none" stroke="{c["grid"]}" stroke-width="1"/>')
    for i,(label,value) in enumerate(axes):
        x,y=point(radius,i); s.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{c["grid"]}"/>')
    shape=[point(radius*max(0,min(100,v))/100,i) for i,(_,v) in enumerate(axes)]
    points=" ".join(f"{x:.1f},{y:.1f}" for x,y in shape)
    s.append(f'<polygon points="{points}" fill="{c["accent"]}" fill-opacity=".20" stroke="{c["accent"]}" stroke-width="2.5" stroke-linejoin="round"><animate attributeName="fill-opacity" values=".12;.27;.12" dur="5s" repeatCount="indefinite"/></polygon>')
    for i,(label,value) in enumerate(axes):
        x,y=point(radius+30,i); angle=-math.pi/2+i*2*math.pi/n
        anchor="middle" if abs(math.cos(angle))<.23 else ("start" if math.cos(angle)>0 else "end")
        px,py=shape[i]; s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.7" fill="{c["blue"]}" stroke="{c["bg"]}" stroke-width="1"/>')
        s.append(text(f"{x:.1f}",f"{y:.1f}",label,11,c["text"],600,anchor))
        s.append(text(f"{x:.1f}",f"{y+14:.1f}",value,10,c["muted"],400,anchor))
    return "".join(s)+"</svg>"

def api(path,token):
    req=urllib.request.Request("https://api.github.com"+path,headers={"User-Agent":"KunalProfileAssets/1.0","Accept":"application/vnd.github+json"})
    if token: req.add_header("Authorization","Bearer "+token)
    with urllib.request.urlopen(req,timeout=25) as res: return json.loads(res.read().decode("utf-8"))

def fetch_profile(user,token):
    profile=api(f"/users/{user}",token); repos=[]; page=1
    while True:
        batch=api(f"/users/{user}/repos?per_page=100&page={page}&type=owner&sort=pushed",token)
        repos.extend(batch)
        if len(batch)<100: break
        page+=1
    owned=[r for r in repos if not r.get("fork") and not r.get("archived")]
    languages={}
    for repo in owned:
        try:
            path=repo["languages_url"].replace("https://api.github.com","")
            for name,count in api(path,token).items(): languages[name]=languages.get(name,0)+int(count)
        except Exception: continue
    return profile,repos,owned,languages

def frame(w,h,c,label,body):
    return svg(w,h,label)+f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{c["panel"]}" stroke="{c["border"]}"/>'+body+"</svg>"

def stats_card(user,profile,owned,languages,projects,theme):
    c=THEMES[theme]; stars=sum(int(r.get("stargazers_count",0)) for r in owned); forks=sum(int(r.get("forks_count",0)) for r in owned)
    tiles=[(f"{stars:,}","Stars earned"),(f"{profile.get('public_repos',0):,}","Public repos"),(f"{profile.get('followers',0):,}","Followers"),(f"{len(owned):,}","Original repos"),(f"{forks:,}","Forks received"),(f"{len(languages):,}","Languages used")]
    w,h=500,196; out=[text(22,31,user,15,c["accent"],700),text(478,31,"GITHUB / AT A GLANCE",9,c["muted"],600,"end",'letter-spacing="1"'),f'<line x1="22" y1="45" x2="478" y2="45" stroke="{c["border"]}"/>']
    for i,(value,label) in enumerate(tiles):
        x=26+(i%3)*155; y=83+(i//3)*70
        out += [text(x,y,value,25,c["title"],700),text(x,y+19,label,10,c["muted"],500)]
    out.append(text(22,181,f"{len(projects)} featured projects · auto-refreshed by GitHub Actions",9,c["muted"]))
    return frame(w,h,c,f"{user} GitHub statistics","".join(out))

def project_card(repo,entry,theme):
    c=THEMES[theme]; w,h=420,146; name=repo.get("name",entry["repo"]); desc=entry.get("description") or repo.get("description") or "Project by Kunal Bishwal"
    words=desc.split(); lines=[]; current=""
    for word in words:
        trial=(current+" "+word).strip()
        if len(trial)>54 and current: lines.append(current); current=word
        else: current=trial
    if current: lines.append(current)
    lines=lines[:2]
    if len(words)>sum(len(line.split()) for line in lines) and lines: lines[-1]=lines[-1].rstrip(" .")+"…"
    out=[text(18,28,"▱",16,c["accent"],700),text(40,29,name,14,c["title"],700),text(402,28,f"★ {repo.get('stargazers_count',0)}",10,c["muted"],500,"end")]
    for i,line in enumerate(lines): out.append(text(18,57+i*17,line,11,c["text"]))
    lang=repo.get("language") or "Software"; color=LANG_COLORS.get(lang,c["blue"])
    out += [f'<circle cx="23" cy="120" r="4" fill="{color}"/>',text(34,124,lang,10,c["muted"],500),text(402,124,f"Forks {repo.get('forks_count',0)}",10,c["muted"],500,"end"),f'<line x1="18" y1="137" x2="402" y2="137" stroke="{c["border"]}"/>']
    return frame(w,h,c,f"Featured project {name}","".join(out))

def language_card(languages,theme):
    c=THEMES[theme]; top=sorted(languages.items(),key=lambda item:-item[1])[:7]; total=sum(v for _,v in top) or 1
    w,h=500,238; out=[text(22,28,"Languages across public repositories",14,c["title"],700)]
    for i,(name,count) in enumerate(top):
        y=58+i*24; pct=count/total*100; color=LANG_COLORS.get(name,c["accent"])
        out += [text(22,y,name,11,c["text"],600),text(478,y,f"{pct:.1f}%",10,c["muted"],500,"end"),
                f'<rect x="22" y="{y+6}" width="456" height="5" rx="2.5" fill="{c["border"]}"/>',
                f'<rect x="22" y="{y+6}" width="{456*pct/100:.1f}" height="5" rx="2.5" fill="{color}"/>']
    out.append(text(22,h-12,"Computed from GitHub language-byte totals; refreshed automatically",9,c["muted"]))
    return frame(w,h,c,"GitHub language composition","".join(out))

def main():
    parser = argparse.ArgumentParser(description="Generate Kunal's terminal-style profile banner.")
    parser.add_argument("--out", type=Path, default=Path("assets"))
    parser.add_argument("--banner-only", action="store_true",
                        help="generate only the custom banners; stats and charts are handled by cards.py and radar.py")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = args.out if args.out.is_absolute() else root / args.out
    for theme in ("dark", "light"):
        save(out / f"banner-{theme}.svg", banner(theme))
    if args.banner_only:
        print("Generated dark and light terminal-style banners.")
        return

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    projects_path = root / "assets/projects.json"
    projects = json.loads(projects_path.read_text(encoding="utf-8"))["projects"]
    profile, repos, owned, languages = fetch_profile("KunalBishwal", token)
    by_name = {r["name"].lower(): r for r in repos}
    found = [(by_name[item["repo"].lower()], item) for item in projects
             if item["repo"].lower() in by_name]
    for theme in ("dark", "light"):
        save(out / f"radar-{theme}.svg", radar(root / "assets/skills.json", theme))
        save(out / f"radar-stack-{theme}.svg", radar(root / "assets/stack.json", theme))
        save(out / f"card-stats-{theme}.svg",
             stats_card("KunalBishwal", profile, owned, languages, projects, theme))
        save(out / f"card-languages-{theme}.svg", language_card(languages, theme))
        for repo, item in found:
            save(out / f"card-{repo['name']}-{theme}.svg", project_card(repo, item, theme))
    print(f"Generated profile SVGs: {len(found)} project cards, {len(languages)} languages.")

if __name__ == "__main__":
    main()
