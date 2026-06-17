#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, json, time, logging, signal, re, sqlite3
import requests
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s [MAX] %(levelname)s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("max")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cbt_core import *
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
MAX_TOKEN = os.getenv("MAX_BOT_TOKEN","")
MAX_API = "https://platform-api.max.ru"
if not MAX_TOKEN: log.error("MAX_BOT_TOKEN not found!"); sys.exit(1)
UID_MAP = {int(os.getenv("MAX_BOT_ADMIN_ID", "0")): int(os.getenv("ADMIN_TG_ID", "0"))}  # заменить в .env
def tu(u): return UID_MAP.get(u,u)
MAXM = 3900; _running = True; st = {}

def api(p,method="GET",data=None,params=None):
    h = {"Authorization":MAX_TOKEN,"Content-Type":"application/json"}
    r = requests.request(method,f"{MAX_API}{p}",headers=h,json=data,params=params,timeout=35)
    return r.json() if r.status_code in (200,201) else None

def tx(uid,text,buttons=None):
    body = {"text":text[:3990],"format":"markdown","notify":False}
    if buttons:
        rows = [[{"type":"message","text":b,"payload":b} for b in row] for row in buttons]
        body["attachments"] = [{"type":"inline_keyboard","payload":{"buttons":rows}}]
    return api(f"/messages?user_id={uid}","POST",body)

def chk(uid,items,header,btns=None):
    if not items: tx(uid,header+"\n\n-",buttons=btns); return
    chunks = []; cur = [header]
    for item in items:
        e = item if isinstance(item,str) else item[0]+"\n"+item[1]
        if len("\n\n".join(cur+[e]))>MAXM:
            chunks.append("\n\n".join(cur)); cur=[e]
        else: cur.append(e)
    if cur: chunks.append("\n\n".join(cur))
    for i,c in enumerate(chunks): tx(uid,c,buttons=btns if i==0 else None)

def dr(days): n=datetime.now(); return n-timedelta(days=days),n
def pd(s):
    for f in ("%d.%m.%Y","%d.%m.%Y %H:%M","%Y-%m-%d","%d/%m/%Y","%d-%m-%Y"):
        try: return datetime.strptime(s.strip(),f)
        except: pass
    return None
fd = lambda d: d.strftime("%d.%m.%Y") if hasattr(d,"strftime") else str(d)
fds = lambda s: fd(datetime.strptime(s,"%Y-%m-%d")) if s else "-"

def dbq(q,p=()):
    conn=sqlite3.connect(DB_FILE); c=conn.cursor(); c.execute(q,p); r=c.fetchall(); conn.commit(); conn.close()
    return r
def dbq1(q,p=()):
    conn=sqlite3.connect(DB_FILE); c=conn.cursor(); c.execute(q,p); r=c.fetchone(); conn.commit(); conn.close()
    return r

def kb_main():
    return [["KPT Dnevnik","Plany na den"],["Dostizheniya","Pomosh"],["/start"]]
def kb_cbt():
    return [["Novaya zapis","Moi zapisi"],["Redaktirovat","Udalit zapis"],["Export Excel"],["Glavnoe menu"]]
def kb_fill():
    return [["Situaciya","Mysl"],["Podtverzhdeniya","Oproverzheniya"],["Emociya","Telo"],["Povedenie","Izmenit datu"],["Zavershit"],["Nazad v KPT","Glavnoe menu"]]
def kb_edit():
    return [["Data/vremya","Situaciya"],["Mysl","Podtverzhdeniya"],["Oproverzheniya","Emociya"],["Telo","Povedenie"],["Udalit zapis"],["Nazad v KPT","Glavnoe menu"]]
def kb_records():
    return [["3 dnya L","Nedelya L"],["Mesac L","Svoi L"],["Nazad v KPT","Glavnoe menu"]]
def kb_records_edit():
    return [["3 dnya R","Nedelya R"],["Mesac R","Svoi R"],["Nazad v KPT","Glavnoe menu"]]
def kb_records_del():
    return [["3 dnya X","Nedelya X"],["Mesac X","Svoi X"],["Nazad v KPT","Glavnoe menu"]]
def kb_cancel():
    return [["Nazad","Glavnoe menu"]]
def kb_confirm_del():
    return [["Da udalit"],["Nazad","Glavnoe menu"]]
def kb_plans():
    return [["Novyj plan","Moi plany"],["Redaktirovat plan","Otmetit vypolnenie"],["Export Excel","Udalit plan"],["Glavnoe menu"]]
def kb_plan_view():
    return [["Segodnya","Zavtra"],["Vybrat datu","Posledn nedelya"],["Za vse vremya"],["Nazad v plany","Glavnoe menu"]]
def kb_plan_edit():
    return [["Segodnya R","Zavtra R"],["Vybrat datu R","Nedelya R"],["Nazad v plany","Glavnoe menu"]]
def kb_plan_date():
    return [["Segodnya","Zavtra"],["Vybrat datu"],["Nazad v plany","Glavnoe menu"]]
def kb_plan_fill():
    return [["Gotovo"],["Nazad v plany","Glavnoe menu"]]
def kb_plan_items():
    return [["Dobavit punkt","Redaktirovat punkt"],["Udalit punkt"],["Nazad v plany","Glavnoe menu"]]
def kb_plan_mark():
    return [["Segodnya O","Zavtra O"],["Vybrat datu O","Nedelya O"],["Vse O"],["Nazad v plany","Glavnoe menu"]]
def kb_ach():
    return [["Dobavit odno","Dobavit neskolko"],["Moi dostizheniya","Redaktirovat dostizh"],["Udalit dostizh","Udalit vse"],["Export Excel"],["Glavnoe menu"]]
def kb_ach_fill():
    return [["Gotovo","Udalit vse"],["Nazad v dostizh","Glavnoe menu"]]

FILL = {"Situaciya":"situation","Mysl":"thought","Podtverzhdeniya":"confirmation","Oproverzheniya":"refutation","Emociya":"emotion","Telo":"body_reaction","Povedenie":"behavior_reaction","Izmenit datu":"created_at"}
EDIT_F = {"Data/vremya":"created_at","Situaciya":"situation","Mysl":"thought","Podtverzhdeniya":"confirmation","Oproverzheniya":"refutation","Emociya":"emotion","Telo":"body_reaction","Povedenie":"behavior_reaction"}
IDX = {'created_at':2,'situation':3,'thought':4,'confirmation':8,'refutation':9,'emotion':5,'body_reaction':6,'behavior_reaction':7}
PER_D = {"3 dnya L":3,"Nedelya L":7,"Mesac L":30,"3 dnya R":3,"Nedelya R":7,"Mesac R":30,"3 dnya X":3,"Nedelya X":7,"Mesac X":30}

def handle(uid,t):
    global st
    s = st.get(uid,{})

    # ---- Start / Main Menu ----
    if t=="/start":
        st[uid]={}
        tx(uid,"KPT Dnevnik\n\nZapisej: "+str(get_records_count(tu(uid))),buttons=kb_main())
        return
    if t=="Glavnoe menu": st[uid]={}; tx(uid,"Glavnoe menu",buttons=kb_main()); return
    if t=="Pomosh":
        st[uid]={}
        tx(uid,"Pomosh\nKPT Dnevnik, Plany, Dostizheniya",buttons=kb_main())
        return
    if t=="KPT Dnevnik": st[uid]={}; tx(uid,"KPT Dnevnik",buttons=kb_cbt()); return
    if t=="Nazad v KPT": st[uid]={}; tx(uid,"KPT Dnevnik",buttons=kb_cbt()); return
    if t=="Nazad v plany": st[uid]={'sec':'plans'}; tx(uid,"Plany",buttons=kb_plans()); return
    if t=="Nazad v dostizh": st[uid]={'sec':'ach'}; tx(uid,"Dostizheniya",buttons=kb_ach()); return

    # ---- New Record ----
    if t=="Novaya zapis":
        now=now_str()
        st[uid]={'state':'fill','data':{'created_at':display_to_db(now)}}
        tx(uid,"Novaya zapis!\n"+now+"\nPole:",buttons=kb_fill())
        return
    if t in FILL and s.get('state')=='fill':
        field=FILL[t]
        pr={"created_at":"Data: DD-MM-YYYY HH:MM","situation":"Situaciya:","thought":"Mysl:",
            "confirmation":"Podtverzhdeniya:","refutation":"Oproverzheniya:","emotion":"Emociya:",
            "body_reaction":"Telo:","behavior_reaction":"Povedenie:"}
        s['cf']=field; s['state']='val'; st[uid]=s
        tx(uid,pr.get(field,"?"),buttons=kb_cancel())
        return
    if t=="Zavershit" and s.get('state') in ('fill','val'):
        data=s.get('data',{})
        if data and data.get('situation'):
            rid=save_record(tu(uid),data)
            tx(uid,"Zapis #"+str(rid)+" sohranena!",buttons=kb_cbt())
        else: tx(uid,"Situaciya obyazatelna!",buttons=kb_fill())
        st[uid]={}; return
    if s.get('state')=='val':
        field=s.get('cf'); data=s.get('data',{})
        if t=="Nazad": st[uid]={'state':'fill','data':data}; tx(uid,".",buttons=kb_fill()); return
        if t=="Glavnoe menu": st[uid]={}; tx(uid,"Menu",buttons=kb_main()); return
        if field=='created_at':
            try: data[field]=display_to_db(t.strip())
            except: tx(uid,"Format: DD-MM-YYYY HH:MM",buttons=kb_cancel()); return
        else: data[field]=t.strip()
        st[uid]={'state':'fill','data':data}
        d=data
        tx(uid,"Zapis:\n"+db_to_display(d.get('created_at',''))+"\n"+str(d.get('situation','X')),buttons=kb_fill())
        return

    # ---- Records List ----
    if t=="Moi zapisi": st[uid]={'state':'recs'}; tx(uid,"Period:",buttons=kb_records()); return
    if s.get('state')=='recs':
        if t in PER_D:
            days=PER_D[t]; start,end=dr(days); recs=get_records_by_period(tu(uid),start,end)
            lb={3:"3d",7:"7d",30:"30d"}.get(days,"")
            if not recs: tx(uid,"Net.",buttons=kb_cbt()); st[uid]={}; return
            items=["#"+str(r[0])+" "+db_to_display(r[2])+"\n"+str(r[3] or '-') for r in recs]
            chk(uid,items,"Zapisi ("+str(len(recs))+"):",btns=kb_cbt())
            st[uid]={}; return
        if "Svoi L" in t: st[uid]={'state':'recs_custom'}; tx(uid,"DD-MM-YYYY DD-MM-YYYY:",buttons=kb_cancel()); return
        if t=="Nazad v KPT": st[uid]={}; tx(uid,"KPT",buttons=kb_cbt()); return
        return
    if s.get('state')=='recs_custom':
        if t=="Nazad": st[uid]={'state':'recs'}; tx(uid,".",buttons=kb_records()); return
        parts=t.split()
        if len(parts)<2: tx(uid,"DD-MM-YYYY DD-MM-YYYY:",buttons=kb_cancel()); return
        try: sd=datetime.strptime(parts[0],"%d-%m-%Y").date(); ed=datetime.strptime(parts[1],"%d-%m-%Y").date()
        except: tx(uid,"Error.",buttons=kb_cancel()); return
        recs=get_records_by_period(tu(uid),sd,ed)
        if not recs: tx(uid,"Net.",buttons=kb_cbt())
        else: chk(uid,["#"+str(r[0])+" "+db_to_display(r[2]) for r in recs],str(len(recs))+" zapisey",btns=kb_cbt())
        st[uid]={}; return

    # ---- Edit ----
    if t=="Redaktirovat": st[uid]={'state':'es'}; tx(uid,"Period:",buttons=kb_records_edit()); return
    if s.get('state')=='es':
        if t in PER_D:
            days=PER_D[t]; start,end=dr(days); recs=get_records_by_period(tu(uid),start,end)
            if not recs: tx(uid,"Net.",buttons=kb_cbt()); st[uid]={}; return
            valid_ids={r[0] for r in recs}
            lines=["#"+str(r[0])+" "+db_to_display(r[2]) for r in recs[:15]]
            tx(uid,str(len(recs))+" z\n"+"\n".join(lines)+"\nID:",buttons=kb_cancel())
            st[uid]={'state':'eid','valid_ids':valid_ids}; return
        if "Svoi R" in t: st[uid]={'state':'es_custom'}; tx(uid,"DD-MM-YYYY DD-MM-YYYY:",buttons=kb_cancel()); return
        if t=="Nazad v KPT": st[uid]={}; tx(uid,"KPT",buttons=kb_cbt()); return
        return
    if s.get('state')=='es_custom':
        if t=="Nazad": st[uid]={'state':'es'}; tx(uid,".",buttons=kb_records_edit()); return
        parts=t.split()
        if len(parts)<2: tx(uid,"...",buttons=kb_cancel()); return
        try: sd=datetime.strptime(parts[0],"%d-%m-%Y").date(); ed=datetime.strptime(parts[1],"%d-%m-%Y").date()
        except: tx(uid,".",buttons=kb_cancel()); return
        recs=get_records_by_period(tu(uid),sd,ed)
        if not recs: tx(uid,"Net.",buttons=kb_cbt()); st[uid]={}; return
        lines=["#"+str(r[0]) for r in recs[:15]]
        tx(uid,str(len(recs))+"\n"+"\n".join(lines)+"\nID:",buttons=kb_cancel())
        st[uid]={'state':'eid','valid_ids':{r[0] for r in recs}}; return
    if s.get('state')=='eid':
        if t=="Nazad": st[uid]={'state':'es'}; tx(uid,".",buttons=kb_records_edit()); return
        try: rid=int(t)
        except: tx(uid,"ID.",buttons=kb_cancel()); return
        rec=get_record_by_id(rid,tu(uid))
        if not rec: tx(uid,"Ne najdena.",buttons=kb_cancel()); return
        st[uid]={'state':'editing','record_id':rid}
        tx(uid,"Red #"+str(rid)+"\n"+format_record(rec)+"\nPole:",buttons=kb_edit())
        return
    if s.get('state')=='editing':
        if t in EDIT_F:
            field=EDIT_F[t]; rec=get_record_by_id(s['record_id'],tu(uid))
            old=rec[IDX[field]] if rec else ''
            s['ef']=field; s['state']='ev'; st[uid]=s
            if field=='created_at': tx(uid,"Bylo: "+str(db_to_display(old) if old else '-')+"\nNovoe (DD-MM-YYYY HH:MM):",buttons=kb_cancel())
            else: tx(uid,"Bylo: "+str(old or '-')+"\nNovoe:",buttons=kb_cancel())
            return
        if t=="Udalit zapis": delete_record(s['record_id'],tu(uid)); tx(uid,"#"+str(s['record_id'])+" udalena!",buttons=kb_cbt()); st[uid]={}; return
        if t=="Nazad v KPT": st[uid]={}; tx(uid,"KPT",buttons=kb_cbt()); return
        return
    if s.get('state')=='ev':
        if t=="Nazad": rid=s['record_id']; rec=get_record_by_id(rid,tu(uid)); st[uid]={'state':'editing','record_id':rid}; tx(uid,"#"+str(rid)+"\n"+format_record(rec),buttons=kb_edit()); return
        field=s.get('ef'); val=t.strip()
        if field=='created_at':
            try: val=display_to_db(val)
            except: tx(uid,"Format: DD-MM-YYYY HH:MM",buttons=kb_cancel()); return
        update_record(s['record_id'],tu(uid),field,val)
        tx(uid,"Obnovleno!",buttons=kb_edit()); st[uid]={'state':'editing','record_id':s['record_id']}; return

    # ---- Delete Record ----
    if t=="Udalit zapis": st[uid]={'state':'ds'}; tx(uid,"Period:",buttons=kb_records_del()); return
    if s.get('state')=='ds':
        if t in PER_D:
            days=PER_D[t]; start,end=dr(days); recs=get_records_by_period(tu(uid),start,end)
            if not recs: tx(uid,"Net.",buttons=kb_cbt()); st[uid]={}; return
            lines=["#"+str(r[0]) for r in recs[:15]]
            tx(uid,str(len(recs))+"\n"+"\n".join(lines)+"\nID:",buttons=kb_cancel())
            st[uid]={'state':'di','valid_ids':{r[0] for r in recs}}; return
        if "Svoi X" in t: st[uid]={'state':'ds_custom'}; tx(uid,"DD-MM-YYYY DD-MM-YYYY:",buttons=kb_cancel()); return
        if t=="Nazad v KPT": st[uid]={}; tx(uid,"KPT",buttons=kb_cbt()); return
        return

    if s.get('state')=='ds_custom':
        if t=="Nazad": st[uid]={'state':'ds'}; tx(uid,".",buttons=kb_records_del()); return
        parts=t.split()
        if len(parts)<2: tx(uid,"...",buttons=kb_cancel()); return
        try: sd=datetime.strptime(parts[0],"%d-%m-%Y").date(); ed=datetime.strptime(parts[1],"%d-%m-%Y").date()
        except: tx(uid,".",buttons=kb_cancel()); return
        recs=get_records_by_period(tu(uid),sd,ed)
        if not recs: tx(uid,"Net.",buttons=kb_cbt()); st[uid]={}; return
        lines=["#"+str(r[0]) for r in recs[:15]]
        tx(uid,str(len(recs))+"\n"+"\n".join(lines)+"\nID:",buttons=kb_cancel())
        st[uid]={'state':'di','valid_ids':{r[0] for r in recs}}; return
    if s.get('state')=='di':
        if t=="Nazad": st[uid]={'state':'ds'}; tx(uid,".",buttons=kb_records_del()); return
        try: rid=int(t)
        except: tx(uid,"ID.",buttons=kb_cancel()); return
        rec=get_record_by_id(rid,tu(uid))
        if not rec: tx(uid,"Net.",buttons=kb_cancel()); return
        st[uid]={'state':'dc','record_id':rid}
        tx(uid,"Udalit #"+str(rid)+"?\n"+format_record(rec)+"\nDa?",buttons=kb_confirm_del())
        return
    if s.get('state')=='dc':
        if t=="Da udalit": delete_record(s['record_id'],tu(uid)); tx(uid,"#"+str(s['record_id'])+" udalena!",buttons=kb_cbt())
        elif t=="Nazad": tx(uid,"Otmeneno.",buttons=kb_cbt())
        st[uid]={}; return

    # ==== PLANS ====
    if t=="Plany na den": st[uid]={'sec':'plans'}; tx(uid,"Plany",buttons=kb_plans()); return
    if t=="Novyj plan": st[uid]={'state':'pn'}; tx(uid,"Den?",buttons=kb_plan_date()); return
    if s.get('state')=='pn':
        if t=="Segodnya": d=date.today()
        elif t=="Zavtra": d=date.today()+timedelta(1)
        elif t=="Vybrat datu": st[uid]={'state':'pn_dt'}; tx(uid,"DD-MM-YYYY:",buttons=kb_cancel()); return
        elif t in ("Nazad v plany","Nazad"): st[uid]={'sec':'plans'}; tx(uid,"Plany",buttons=kb_plans()); return
        else: return
        if check_plan_exists(tu(uid),d)[0]: tx(uid,"Est!",buttons=[["Redaktirovat plan","Glavnoe menu"]]); st[uid]={'sec':'plans'}; return
        pid=get_or_create_plan(tu(uid),d)
        st[uid]={'state':'pf','pid':pid}
        tx(uid,"Plan na "+fd(d)+" sozdan!\nPishi:",buttons=kb_plan_fill())
        return
    if s.get('state')=='pn_dt':
        if t=="Nazad": st[uid]={'state':'pn'}; tx(uid,".",buttons=kb_plan_date()); return
        try: d=datetime.strptime(t.strip(),"%d.%m.%Y").date()
        except: tx(uid,"DD-MM-YYYY",buttons=kb_cancel()); return
        if check_plan_exists(tu(uid),d)[0]: tx(uid,"Est!",buttons=[["Redaktirovat plan","Glavnoe menu"]]); st[uid]={'sec':'plans'}; return
        pid=get_or_create_plan(tu(uid),d)
        st[uid]={'state':'pf','pid':pid}
        tx(uid,"Plan na "+fd(d)+" sozdan!\nPishi:",buttons=kb_plan_fill())
        return
    if s.get('state')=='pf':
        pid=s.get('pid')
        if t=="Gotovo": cnt=len(get_plan_items(pid)); tx(uid,"Sohranen! "+str(cnt)+" p.",buttons=[["Moi plany","Otmetit vypolnenie"],["Novyj plan","Glavnoe menu"]]); st[uid]={'sec':'plans'}; return
        if t in ("Nazad v plany","Glavnoe menu"): st[uid]={'sec':'plans'}; tx(uid,"Plany",buttons=kb_plans()); return
        if pid:
            for l in t.split("\n"):
                if l.strip(): add_plan_item(pid,l.strip())
            tx(uid,"Dobavleno!",buttons=[["Gotovo"],["Nazad v plany","Glavnoe menu"]])
        return

    if t=="Moi plany": st[uid]={'state':'pv'}; tx(uid,"Period:",buttons=kb_plan_view()); return
    if s.get('state')=='pv':
        if t=="Segodnya": d=date.today()
        elif t=="Zavtra": d=date.today()+timedelta(1)
        elif t=="Vybrat datu": st[uid]={'state':'pv_dt'}; tx(uid,"DD-MM-YYYY:",buttons=kb_cancel()); return
        elif t=="Posledn nedelya":
            pls=get_plans_by_period(tu(uid),date.today()-timedelta(7),date.today())
            if not pls: tx(uid,"Net.",buttons=kb_plan_view()); return
            its=[p['plan_date']+" - "+str(len(p.get('items',[])))+" tasks" for p in pls]
            chk(uid,its,"Nedelya:",btns=[["Nazad v plany","Glavnoe menu"]])
            st[uid]={'sec':'plans'}; return
        elif t=="Za vse vremya":
            pls=get_plans_by_period(tu(uid),date(2000,1,1),date.today())
            if not pls: tx(uid,"Net.",buttons=kb_plan_view()); return
            its=[p['plan_date']+" - "+str(len(p.get('items',[])))+" tasks" for p in pls]
            chk(uid,its,"Vse:",btns=[["Nazad v plany","Glavnoe menu"]])
            st[uid]={'sec':'plans'}; return
        elif t in ("Nazad v plany","Nazad"): st[uid]={'sec':'plans'}; tx(uid,"Plany",buttons=kb_plans()); return
        else: return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); its=get_plan_items(pid)
            lines=["Plan na "+fd(d)+":"]
            for it in its: lines.append("  "+("OK" if it[2] else "[ ]")+" #"+str(it[0])+" "+it[1])
            tx(uid,"\n".join(lines),buttons=kb_plan_items())
            st[uid]={'state':'pvi','pid':pid}
        else: tx(uid,"Net.",buttons=kb_plan_view())
        return
    if s.get('state')=='pv_dt':
        if t=="Nazad": st[uid]={'state':'pv'}; tx(uid,".",buttons=kb_plan_view()); return
        try: d=datetime.strptime(t.strip(),"%d.%m.%Y").date()
        except: tx(uid,"DD-MM-YYYY",buttons=kb_cancel()); return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); its=get_plan_items(pid)
            lines=["Plan:"]
            for it in its: lines.append("  "+("OK" if it[2] else "[ ]")+" #"+str(it[0])+" "+it[1])
            tx(uid,"\n".join(lines),buttons=kb_plan_items())
            st[uid]={'state':'pvi','pid':pid}
        else: tx(uid,"Net.",buttons=kb_plan_view())
        return

    # ---- Plan Items CRUD ----
    if s.get('state')=='pvi':
        pid=s.get('pid')
        if t=="Dobavit punkt": st[uid]={'state':'pvi_add','pid':pid}; tx(uid,"Tekst:",buttons=kb_cancel()); return
        if t=="Redaktirovat punkt": st[uid]={'state':'pvi_ed_sel','pid':pid}; tx(uid,"#ID:",buttons=kb_cancel()); return
        if t=="Udalit punkt": st[uid]={'state':'pvi_del','pid':pid}; tx(uid,"#ID:",buttons=kb_cancel()); return
        if t in ("Nazad v plany","Nazad"): st[uid]={'sec':'plans'}; tx(uid,"Plany",buttons=kb_plans()); return
        return
    if s.get('state')=='pvi_add':
        if t in ("Nazad","Glavnoe menu"): st[uid]={'sec':'plans'}; tx(uid,"Plany",buttons=kb_plans()); return
        add_plan_item(s['pid'],t); tx(uid,"+!",buttons=[["Dobavit punkt"],["Nazad v plany","Glavnoe menu"]]); return
    if s.get('state')=='pvi_ed_sel':
        if t in ("Nazad","Glavnoe menu"): st[uid]={'state':'pvi','pid':s['pid']}; tx(uid,".",buttons=kb_plan_items()); return
        try: iid=int(t.strip().lstrip('#')); st[uid]={'state':'pvi_ed_val','pid':s['pid'],'iid':iid}; tx(uid,"Novyj tekst:",buttons=kb_cancel())
        except: tx(uid,"#ID.",buttons=kb_cancel())
        return
    if s.get('state')=='pvi_ed_val':
        if t in ("Nazad","Glavnoe menu"): st[uid]={'state':'pvi','pid':s['pid']}; tx(uid,".",buttons=kb_plan_items()); return
        dbq('UPDATE plan_items SET text=? WHERE id=?',(t,s['iid'])); tx(uid,"Obnovleno!",buttons=kb_plan_items()); st[uid]={'state':'pvi','pid':s['pid']}; return
    if s.get('state')=='pvi_del':
        if t in ("Nazad","Glavnoe menu"): st[uid]={'sec':'plans'}; tx(uid,"Plany",buttons=kb_plans()); return
        try: iid=int(t.strip().lstrip('#')); delete_plan_item(iid); tx(uid,"#"+str(iid)+" udalen!",buttons=kb_plan_items()); st[uid]={'state':'pvi','pid':s['pid']}
        except: tx(uid,"#ID.",buttons=kb_cancel())
        return

    # ---- Edit Plan (redirect) ----
    if t=="Redaktirovat plan": st[uid]={'state':'pe'}; tx(uid,"Den?",buttons=kb_plan_edit()); return
    if s.get('state')=='pe':
        if t=="Segodnya R": d=date.today()
        elif t=="Zavtra R": d=date.today()+timedelta(1)
        elif t=="Vybrat datu R": st[uid]={'state':'pe_dt'}; tx(uid,"DD-MM-YYYY:",buttons=kb_cancel()); return
        elif t=="Nedelya R":
            pls=get_plans_by_period(tu(uid),date.today()-timedelta(7),date.today())
            if not pls: tx(uid,"Net.",buttons=kb_plan_edit()); return
            its=[p['plan_date'] for p in pls]
            chk(uid,its,"Vyberi:",btns=[["Nazad v plany","Glavnoe menu"]])
            st[uid]={'state':'pe_dt'}; return
        elif t in ("Nazad v plany","Nazad"): st[uid]={'sec':'plans'}; tx(uid,"Plany",buttons=kb_plans()); return
        else: return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); its=get_plan_items(pid)
            lines=["R "+fd(d)+":"]; [lines.append("  #"+str(it[0])+" "+it[1]) for it in its]
            tx(uid,"\n".join(lines),buttons=kb_plan_items()); st[uid]={'state':'pvi','pid':pid}
        else: tx(uid,"Net.",buttons=kb_plan_edit()); return
    if s.get('state')=='pe_dt':
        if t=="Nazad": st[uid]={'state':'pe'}; tx(uid,".",buttons=kb_plan_edit()); return
        try: d=datetime.strptime(t.strip(),"%d.%m.%Y").date()
        except: tx(uid,"DD-MM-YYYY",buttons=kb_cancel()); return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); its=get_plan_items(pid)
            lines=["R:"]; [lines.append("  #"+str(it[0])+" "+it[1]) for it in its]
            tx(uid,"\n".join(lines),buttons=kb_plan_items()); st[uid]={'state':'pvi','pid':pid}
        else: tx(uid,"Net.",buttons=kb_plan_edit()); return

    # ---- Delete Plan ----
    if t=="Udalit plan": st[uid]={'state':'pdel'}; tx(uid,"Den?",buttons=kb_plan_edit()); return
    if s.get('state')=='pdel':
        if t=="Segodnya R": d=date.today()
        elif t=="Zavtra R": d=date.today()+timedelta(1)
        elif t=="Vybrat datu R": st[uid]={'state':'pdel_dt'}; tx(uid,"DD-MM-YYYY:",buttons=kb_cancel()); return
        elif t=="Nedelya R":
            pls=get_plans_by_period(tu(uid),date.today()-timedelta(7),date.today())
            if not pls: tx(uid,"Net.",buttons=kb_plan_edit()); return
            its=[p['plan_date'] for p in pls]
            chk(uid,its,"Vyberi:",btns=[["Nazad v plany","Glavnoe menu"]])
            st[uid]={'state':'pdel_dt'}; return
        elif t in ("Nazad v plany","Nazad"): st[uid]={'sec':'plans'}; tx(uid,"Plany",buttons=kb_plans()); return
        else: return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); delete_plan(pid)
            tx(uid,"Plan na "+fd(d)+" udalen!",buttons=kb_plans())
        else: tx(uid,"Net.",buttons=kb_plan_edit())
        st[uid]={'sec':'plans'}; return
    if s.get('state')=='pdel_dt':
        if t=="Nazad": st[uid]={'state':'pdel'}; tx(uid,".",buttons=kb_plan_edit()); return
        try: d=datetime.strptime(t.strip(),"%d.%m.%Y").date()
        except: tx(uid,"DD-MM-YYYY",buttons=kb_cancel()); return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); delete_plan(pid)
            tx(uid,"Plan na "+fd(d)+" udalen!",buttons=kb_plans())
        else: tx(uid,"Net.",buttons=kb_plan_edit())
        st[uid]={'sec':'plans'}; return

    # ---- Mark Done ----
    if t=="Otmetit vypolnenie": st[uid]={'state':'po'}; tx(uid,"Den?",buttons=kb_plan_mark()); return
    if s.get('state')=='po':
        if t=="Segodnya O": d=date.today()
        elif t=="Zavtra O": d=date.today()+timedelta(1)
        elif t=="Vybrat datu O": st[uid]={'state':'po_dt'}; tx(uid,"DD-MM-YYYY:",buttons=kb_cancel()); return
        elif t=="Nedelya O":
            pls=get_plans_by_period(tu(uid),date.today()-timedelta(7),date.today())
            if not pls: tx(uid,"Net.",buttons=kb_plan_mark()); return
            its=[p['plan_date'] for p in pls]
            chk(uid,its,"Vyberi:",btns=[["Nazad v plany","Glavnoe menu"]])
            st[uid]={'state':'po_dt'}; return
        elif t=="Vse O":
            pls=get_plans_by_period(tu(uid),date(2000,1,1),date.today())
            if not pls: tx(uid,"Net.",buttons=kb_plan_mark()); return
            its=[p['plan_date'] for p in pls]
            chk(uid,its,"Vyberi:",btns=[["Nazad v plany","Glavnoe menu"]])
            st[uid]={'state':'po_dt'}; return
        elif t in ("Nazad v plany","Nazad"): st[uid]={'sec':'plans'}; tx(uid,"Plany",buttons=kb_plans()); return
        else: return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); its=get_plan_items(pid)
            lines=["O "+fd(d)+":"]
            for it in its: lines.append("  "+("OK" if it[2] else "[ ]")+" #"+str(it[0])+" "+it[1])
            lines.append("\n#ID to toggle:")
            tx(uid,"\n".join(lines),buttons=[["Gotovo"],["Nazad v plany","Glavnoe menu"]])
            st[uid]={'state':'po_tg','pid':pid}
        else: tx(uid,"Net.",buttons=kb_plan_mark())
        return
    if s.get('state')=='po_tg':
        pid=s.get('pid')
        if t=="Gotovo": st[uid]={'sec':'plans'}; tx(uid,"Plany",buttons=kb_plans()); return
        if t in ("Nazad v plany","Glavnoe menu"): st[uid]={'sec':'plans'}; tx(uid,"Plany",buttons=kb_plans()); return
        try:
            iid=int(t.strip().lstrip('#'))
            toggle_plan_item(iid)
        except: tx(uid,"#ID",buttons=[["Gotovo"],["Nazad v plany","Glavnoe menu"]]); return
        its=get_plan_items(pid)
        lines=["O:"]
        for it in its: lines.append("  "+("OK" if it[2] else "[ ]")+" #"+str(it[0])+" "+it[1])
        lines.append("\n#ID:")
        tx(uid,"\n".join(lines),buttons=[["Gotovo"],["Nazad v plany","Glavnoe menu"]])
        st[uid]={'state':'po_tg','pid':pid}
        return
    if s.get('state')=='po_dt':
        if t=="Nazad": st[uid]={'state':'po'}; tx(uid,".",buttons=kb_plan_mark()); return
        try: d=datetime.strptime(t.strip(),"%d.%m.%Y").date()
        except: tx(uid,"DD-MM-YYYY",buttons=kb_cancel()); return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); its=get_plan_items(pid)
            lines=["O:"]
            for it in its: lines.append("  "+("OK" if it[2] else "[ ]")+" #"+str(it[0])+" "+it[1])
            lines.append("\n#ID:")
            tx(uid,"\n".join(lines),buttons=[["Gotovo"],["Nazad v plany","Glavnoe menu"]])
            st[uid]={'state':'po_tg','pid':pid}
        else: tx(uid,"Net.",buttons=kb_plan_mark())
        return

    # ==== ACHIEVEMENTS ====
    if t=="Dostizheniya": st[uid]={'sec':'ach'}; tx(uid,"Dostizheniya ("+str(count_achievements(tu(uid)))+")",buttons=kb_ach()); return
    if t=="Dobavit odno": st[uid]={'state':'ach_add'}; tx(uid,"Napishi dostizhenie:",buttons=kb_cancel()); return
    if s.get('state')=='ach_add':
        if t in ("Nazad","Nazad v dostizh"): st[uid]={'sec':'ach'}; tx(uid,"Dostizheniya",buttons=kb_ach()); return
        if t=="Glavnoe menu": st[uid]={}; tx(uid,"Menu",buttons=kb_main()); return
        add_achievement(tu(uid),t)
        tx(uid,"Dobavleno! Vsego: "+str(count_achievements(tu(uid))),buttons=[["Dobavit odno","Moi dostizheniya"],["Nazad v dostizh","Glavnoe menu"]])
        st[uid]={'sec':'ach'}; return
    if t=="Dobavit neskolko": st[uid]={'state':'ach_multi','achs':[]}; tx(uid,"Pishi kazhdoe s novoy stroki. Gotovo -> knopka:",buttons=kb_ach_fill()); return
    if s.get('state')=='ach_multi':
        if t=="Gotovo":
            achs=s.get('achs',[])
            for a in achs:
                if a.strip(): add_achievement(tu(uid),a.strip())
            tx(uid,"Dobavleno "+str(len(achs))+"! Vsego: "+str(count_achievements(tu(uid))),buttons=kb_ach())
            st[uid]={'sec':'ach'}; return
        if t=="Udalit vse":
            all_a=get_achievements_all(tu(uid))
            for a in all_a: delete_achievement(a[0])
            tx(uid,"Vse udaleno!",buttons=kb_ach())
            st[uid]={'sec':'ach'}; return
        if t in ("Nazad v dostizh","Nazad"): st[uid]={'sec':'ach'}; tx(uid,"Dostizheniya",buttons=kb_ach()); return
        if t=="Glavnoe menu": st[uid]={}; tx(uid,"Menu",buttons=kb_main()); return
        achs=s.get('achs',[])
        for l in t.split("\n"):
            if l.strip(): achs.append(l.strip())
        st[uid]['achs']=achs
        tx(uid,"Prislano: "+str(len(achs))+". Eshche ili Gotovo:",buttons=kb_ach_fill())
        return
    if t=="Moi dostizheniya":
        data=get_achievements_all(tu(uid))
        if not data: tx(uid,"Net.",buttons=kb_ach())
        else: chk(uid,[str(a[0])+". "+a[1] for a in data],"Dostizheniya:",btns=[["Dobavit odno","Nazad v dostizh","Glavnoe menu"]])
        st[uid]={'sec':'ach'}; return
    if t=="Udalit dostizh": st[uid]={'state':'ach_del'}; tx(uid,"#ID:",buttons=kb_cancel()); return
    if s.get('state')=='ach_del':
        if t in ("Nazad","Nazad v dostizh"): st[uid]={'sec':'ach'}; tx(uid,"Dostizheniya",buttons=kb_ach()); return
        try: iid=int(t.strip().lstrip('#')); delete_achievement(iid); tx(uid,"Udaleno!",buttons=kb_ach())
        except: tx(uid,"#ID.",buttons=kb_cancel()); return
        st[uid]={'sec':'ach'}; return
    if t=="Udalit vse":
        all_a=get_achievements_all(tu(uid))
        for a in all_a: delete_achievement(a[0])
        tx(uid,"Vse udaleno ("+str(len(all_a))+")!",buttons=kb_ach())
        st[uid]={'sec':'ach'}; return
    if t=="Redaktirovat dostizh": st[uid]={'state':'ach_ed_sel'}; tx(uid,"#ID:",buttons=kb_cancel()); return
    if s.get('state')=='ach_ed_sel':
        if t in ("Nazad","Nazad v dostizh"): st[uid]={'sec':'ach'}; tx(uid,"Dostizheniya",buttons=kb_ach()); return
        try: iid=int(t.strip().lstrip('#')); st[uid]={'state':'ach_ed_val','iid':iid}; tx(uid,"Novyj tekst:",buttons=kb_cancel())
        except: tx(uid,"#ID.",buttons=kb_cancel())
        return
    if s.get('state')=='ach_ed_val':
        if t in ("Nazad","Nazad v dostizh","Glavnoe menu"): st[uid]={'sec':'ach'}; tx(uid,"Dostizheniya",buttons=kb_ach()); return
        update_achievement(s['iid'],t); tx(uid,"Obnovleno!",buttons=kb_ach()); st[uid]={'sec':'ach'}; return

    # ==== EXPORT ====
    if t=="Export Excel": st[uid]={'state':'ex'}; tx(uid,"Chto?",buttons=[["KPT zapisi","Plany"],["Dostizheniya"],["Nazad","Glavnoe menu"]]); return
    if s.get('state')=='ex':
        if t=="KPT zapisi": et="cbt"
        elif t=="Plany": et="plans"
        elif t=="Dostizheniya":
            data=get_achievements_all(tu(uid))
            chk(uid,[str(a[0])+". "+a[1] for a in data],"Dostizheniya:",btns=[["Nazad","Glavnoe menu"]])
            st[uid]={'sec':'ach'}; return
        else: return
        st[uid]={'state':'ex_days','et':et}; tx(uid,"Skolko dney?",buttons=[["3","7","30"],["Nazad","Glavnoe menu"]])
        return
    if s.get('state')=='ex_days':
        try: d=int(t.strip())
        except: tx(uid,"3,7,30",buttons=kb_cancel()); return
        if d not in (3,7,30): tx(uid,"3,7,30",buttons=kb_cancel()); return
        et=s.get('et','cbt')
        if et=='cbt':
            start,end=dr(d); recs=get_records_by_period(tu(uid),start,end)
            if not recs: tx(uid,"Net."); return
            its=[("#"+str(r[0])+" "+db_to_display(r[2]),str(r[3] or '-')+"\n"+str(r[4] or '-')) for r in recs]
            chk(uid,its,"KPT ("+str(len(recs))+"):",btns=[["Nazad","Glavnoe menu"]])
        elif et=='plans':
            pls=get_plans_by_period(tu(uid),date.today()-timedelta(d),date.today()+timedelta(1))
            if not pls: tx(uid,"Net."); return
            its=[]
            for p in pls:
                for it in p.get("items",[]): its.append(p['plan_date']+"  "+("OK" if it.get('is_done') else "[ ]")+" "+it['text'])
            chk(uid,its,"Plany:",btns=[["Nazad","Glavnoe menu"]])
        st[uid]={}; return

    # ---- Fallback ----
    # If nothing matched, check for export answer
    if s.get('state')=='ex_custom':
        pass  # handled above

    tx(uid,"?",buttons=kb_main())


def process_update(upd):
    ut = upd.get("update_type","")
    uid = None; text = ""
    if ut == "message_created":
        msg = upd.get("message",{}) or {}
        snd = msg.get("sender",{}) or upd.get("user",{})
        uid = snd.get("user_id")
        text = ((msg.get("body",{}) or {}).get("text","")).strip()
    elif ut == "bot_started":
        uid = upd.get("user",{}).get("user_id")
        text = "/start"
    elif ut == "message_callback":
        uid = upd.get("user",{}).get("user_id")
        cb = upd.get("callback",{}) or {}
        text = cb.get("payload","") or cb.get("text","")
    else:
        return
    if not uid or not text: return
    log.info(f"<- MAX#{uid}: {text[:50]}")
    try:
        handle(uid, text)
    except Exception as e:
        import traceback; traceback.print_exc()
        log.error(f"Error: {e}")
        tx(uid, "Error. Try again.", buttons=kb_main())

def poll():
    last_update_id = 0
    while _running:
        try:
            data = api("/get_updates", params={"last_update_id": last_update_id, "timeout": 30})
            if data and isinstance(data, list):
                for upd in data:
                    uid = upd.get("update_id",0)
                    if uid > last_update_id: last_update_id = uid
                    process_update(upd)
        except requests.exceptions.Timeout:
            pass
        except Exception as e:
            log.error(f"Poll error: {e}")
            time.sleep(5)

def main():
    signal.signal(signal.SIGTERM, lambda *a: setattr(sys.modules[__name__], '_running', False))
    signal.signal(signal.SIGINT, lambda *a: setattr(sys.modules[__name__], '_running', False))
    log.info("Starting MAX bridge...")
    poll()
    log.info("Stopped.")

if __name__ == "__main__":
    main()
