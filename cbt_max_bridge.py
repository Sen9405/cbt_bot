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
MAX_API = "https://platform-api2.max.ru"

# Кастомный SSL контекст для сертификата Минцифры
import ssl
from urllib3.poolmanager import PoolManager
from requests.adapters import HTTPAdapter
_CA_BUNDLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'max_ca_chain.pem')
_ctx = ssl.create_default_context(cafile=_CA_BUNDLE)
class _SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = _ctx
        return super().init_poolmanager(*args, **kwargs)
_SESSION = requests.Session()
_SESSION.mount('https://', _SSLAdapter())
if not MAX_TOKEN: log.error("MAX_BOT_TOKEN not found!"); sys.exit(1)
UID_MAP = {int(os.getenv("MAX_BOT_ADMIN_ID", "102726510")): int(os.getenv("ADMIN_TG_ID", "144288459"))}
def tu(u): return UID_MAP.get(u,u)
MAXM = 3900; _running = True; st = {}

def api(p,method="GET",data=None,params=None):
    h = {"Authorization":MAX_TOKEN,"Content-Type":"application/json"}
    url = f"{MAX_API}{p}"
    if method == "GET":
        r = _SESSION.get(url, headers=h, params=params, timeout=35)
    else:
        r = _SESSION.post(url, headers=h, json=data, params=params, timeout=35)
    if r.status_code in (200,201):
        return r.json()
    log.warning(f"API {p} -> {r.status_code}: {r.text[:200]}")
    
def tx(uid,text,buttons=None):
    body = {"text":text[:3990],"format":"markdown","notify":False}
    if buttons:
        rows = [[{"type":"message","text":b,"payload":b} for b in row] for row in buttons]
        body["attachments"] = [{"type":"inline_keyboard","payload":{"buttons":rows}}]
    r = api(f"/messages?user_id={uid}","POST",body)
    if r: log.info(f"-> MAX#{uid}: ok")
    else: log.warning(f"-> MAX#{uid}: FAIL")
    return r

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

def make_kb(rows):
    return [list(row) for row in rows]

def kb_main():
    return make_kb([["🧠 КПТ Дневник","📋 Планы на день"],["🏆 Достижения","❓ Помощь"],["🔄 /start"]])
def kb_cbt():
    return make_kb([["📝 Новая запись","📋 Мои записи"],["✏️ Редактировать","🗑 Удалить запись"],["📊 Выгрузить"],["🏠 Главное меню"]])
def kb_fill():
    return make_kb([["📍 Ситуация","💭 Мысль"],["✅ Подтверждения","❌ Опровержения"],["😌 Эмоция","🔹 Тело"],["🔹 Поведение","📅 Дата"],["✅ Завершить"],["◀️ Назад","🏠 Главное меню"]])
def kb_edit():
    return make_kb([["📅 Дата/время","📍 Ситуация"],["💭 Мысль","✅ Подтверждения"],["❌ Опровержения","😌 Эмоция"],["🔹 Тело","🔹 Поведение"],["🗑 Удалить запись"],["◀️ Назад","🏠 Главное меню"]])
def kb_records():
    return make_kb([["3 дня 📋","Неделя 📋"],["Месяц 📋","Свой период 📋"],["◀️ Назад","🏠 Главное меню"]])
def kb_records_edit():
    return make_kb([["3 дня ✏️","Неделя ✏️"],["Месяц ✏️","Свой период ✏️"],["◀️ Назад","🏠 Главное меню"]])
def kb_records_del():
    return make_kb([["3 дня 🗑","Неделя 🗑"],["Месяц 🗑","Свой период 🗑"],["◀️ Назад","🏠 Главное меню"]])
def kb_cancel():
    return make_kb([["◀️ Назад","🏠 Главное меню"]])
def kb_confirm_del():
    return make_kb([["✅ Да, удалить"],["◀️ Назад","🏠 Главное меню"]])
def kb_confirm_del_all():
    return make_kb([["✅ Да, удалить всё"],["❌ Нет, отменить"]])
def kb_plans():
    return make_kb([["📝 Новый план","📋 Мои планы"],["✏️ Редактировать","✅ Отметить выполнение"],["📊 Выгрузить","🗑 Удалить план"],["🏠 Главное меню"]])
def kb_plan_view():
    return make_kb([["📅 Сегодня","📅 Завтра"],["📅 Выбрать дату","📅 Неделя"],["📅 За всё время"],["◀️ Назад","🏠 Главное меню"]])
def kb_plan_edit():
    return make_kb([["📅 Сегодня ✏️","📅 Завтра ✏️"],["📅 Выбрать дату ✏️","📅 Неделя ✏️"],["◀️ Назад","🏠 Главное меню"]])
def kb_plan_date():
    return make_kb([["📅 Сегодня","📅 Завтра"],["📅 Выбрать дату"],["◀️ Назад","🏠 Главное меню"]])
def kb_plan_fill():
    return make_kb([["✅ Готово"],["◀️ Назад","🏠 Главное меню"]])
def kb_plan_items():
    return make_kb([["➕ Добавить пункт","✏️ Редактировать пункт"],["🗑 Удалить пункт"],["◀️ Назад","🏠 Главное меню"]])
def kb_plan_mark():
    return make_kb([["📅 Сегодня ✅","📅 Завтра ✅"],["📅 Выбрать дату ✅","📅 Неделя ✅"],["📅 Всё ✅"],["◀️ Назад","🏠 Главное меню"]])
def kb_ach():
    return make_kb([["➕ Добавить одно","➕ Несколько"],["📋 Мои достижения","✏️ Редактировать"],["🗑 Удалить","🗑 Удалить все"],["📊 Выгрузить"],["🏠 Главное меню"]])
def kb_ach_fill():
    return make_kb([["✅ Готово","🗑 Удалить всё"],["◀️ Назад","🏠 Главное меню"]])

FILL = {"📍 Ситуация":"situation","💭 Мысль":"thought","✅ Подтверждения":"confirmation","❌ Опровержения":"refutation","😌 Эмоция":"emotion","🔹 Тело":"body_reaction","🔹 Поведение":"behavior_reaction","📅 Дата":"created_at"}
EDIT_F = {"📅 Дата/время":"created_at","📍 Ситуация":"situation","💭 Мысль":"thought","✅ Подтверждения":"confirmation","❌ Опровержения":"refutation","😌 Эмоция":"emotion","🔹 Тело":"body_reaction","🔹 Поведение":"behavior_reaction"}
IDX = {'created_at':2,'situation':3,'thought':4,'confirmation':8,'refutation':9,'emotion':5,'body_reaction':6,'behavior_reaction':7}
PER_D = {"3 дня 📋":3,"Неделя 📋":7,"Месяц 📋":30,"3 дня ✏️":3,"Неделя ✏️":7,"Месяц ✏️":30,"3 дня 🗑":3,"Неделя 🗑":7,"Месяц 🗑":30}

# Prompt messages for fill fields
FILL_PR = {
    "created_at":"📅 **Дата/время** (ДД-ММ-ГГГГ ЧЧ:ММ):",
    "situation":"📍 **Ситуация:** Что произошло? Где? С кем?",
    "thought":"💭 **Мысль:** Что подумал(а)?",
    "confirmation":"✅ **Подтверждения:** Факты за мысль",
    "refutation":"❌ **Опровержения:** Факты против мысли",
    "emotion":"😌 **Эмоция:** Тревога, гнев, грусть?",
    "body_reaction":"🔹 **Тело:** Ощущения?",
    "behavior_reaction":"🔹 **Поведение:** Что сделал(а)?",
}

def handle(uid,t):
    global st
    s = st.get(uid,{})
    sec = s.get('sec','')
    state = s.get('state','')

    # ==== GLOBAL NAVIGATION ====
    if t=="/start":
        st[uid]={}
        tx(uid,"🧠 **КПТ-Терапия Бот**\n\nЗаписей: "+str(get_records_count(tu(uid))),buttons=kb_main())
        return
    if t=="🏠 Главное меню":
        st[uid]={}
        tx(uid,"🏠 **Главное меню**\n\nВыбери раздел:",buttons=kb_main())
        return
    if t=="🔄 /start":
        st[uid]={}
        tx(uid,"🔄 Начинаем заново\nВыбери раздел:",buttons=kb_main())
        return

    # ==== HELP ====
    if t=="❓ Помощь":
        tx(uid,
            "❓ **Помощь**\n\n"
            "🧠 **КПТ Дневник**\n"
            "📝 **Новая запись** — заполнить ситуацию, мысли, подтверждения/опровержения, эмоции, реакции\n"
            "📋 **Мои записи** — просмотр записей за период\n"
            "✏️ **Редактировать** — изменить существующую запись\n"
            "🗑 **Удалить запись** — удалить запись по ID с подтверждением\n"
            "📊 **Выгрузить** — выгрузка данных\n\n"
            "📋 **Планы на день**\n"
            "📝 **Новый план** — создать план на сегодня/завтра/свою дату\n"
            "📋 **Мои планы** — просмотр планов\n"
            "✏️ **Редактировать план** — добавить/удалить/переименовать пункты\n"
            "✅ **Отметить выполнение** — отметить пункты как выполненные\n"
            "🗑 **Удалить план** — удалить план на дату\n"
            "📊 **Выгрузить** — выгрузка планов\n\n"
            "🏆 **Мои достижения**\n"
            "➕ **Добавить одно** — добавить одно достижение\n"
            "📝 **Добавить несколько** — добавить список достижений\n"
            "📋 **Мои достижения** — просмотр всех достижений\n"
            "✏️ **Редактировать** — изменить текст достижения\n"
            "🗑 **Удалить** — удалить достижение\n"
            "📊 **Выгрузить** — выгрузка достижений\n\n"
            "**Формат даты:** `ДД-ММ-ГГГГ ЧЧ:ММ`\n"
            "Например: `23-04-2026 15:30`\n"
            "Для планов достаточно `ДД-ММ-ГГГГ`",
            buttons=kb_main())
        return

    # ==== CBT DIARY SECTION ====
    if t=="🧠 КПТ Дневник":
        st[uid]={}
        tx(uid,"🧠 **КПТ Дневник**\n\nВыбери действие:",buttons=kb_cbt())
        return

    # -- New Record --
    if t=="📝 Новая запись":
        now=now_str()
        st[uid]={'state':'fill','data':{'created_at':display_to_db(now)}}
        tx(uid,"✅ **Новая запись**\n📅 "+now+"\n\nВыбери поле:",buttons=kb_fill())
        return

    if state=='fill' and t in FILL:
        field=FILL[t]
        prompts={"created_at":"📅 **Дата/время** (ДД-ММ-ГГГГ ЧЧ:ММ):","situation":"📍 **Ситуация:** Что произошло?","thought":"💭 **Мысль:** Что подумал?","confirmation":"✅ **Подтверждения:**","refutation":"❌ **Опровержения:**","emotion":"😌 **Эмоция:**","body_reaction":"🔹 **Тело:**","behavior_reaction":"🔹 **Поведение:**"}
        st[uid]['cf']=field; st[uid]['state']='val'
        tx(uid,prompts.get(field,"✏️ Введи:"),buttons=kb_cancel())
        return

    if t=="✅ Завершить" and state in ('fill','val'):
        data=s.get('data',{})
        if data.get('situation'):
            rid=save_record(tu(uid),data)
            tx(uid,"✅ **Запись #"+str(rid)+" сохранена!**",buttons=kb_cbt())
        else: tx(uid,"⚠️ **Ситуация** обязательна!",buttons=kb_fill())
        st[uid]={}; return

    if state=='val':
        field=s.get('cf'); data=s.get('data',{})
        if t=="◀️ Назад": st[uid]={'state':'fill','data':data}; tx(uid,"📝 Продолжить:",buttons=kb_fill()); return
        if field=='created_at':
            try: data[field]=display_to_db(t.strip())
            except: tx(uid,"❌ Формат: ДД-ММ-ГГГГ ЧЧ:ММ",buttons=kb_cancel()); return
        else: data[field]=t.strip()
        d=data
        st[uid]={'state':'fill','data':data}
        tx(uid,"📝 **Запись:**\n📅 "+db_to_display(d.get('created_at',''))+"\n📍 "+str(d.get('situation','-')),buttons=kb_fill())
        return

    # -- View Records --
    if t=="📋 Мои записи": st[uid]={'state':'recs'}; tx(uid,"📅 **Период:**",buttons=kb_records()); return

    if state=='recs':
        if t=="◀️ Назад": st[uid]={}; tx(uid,"🧠 КПТ",buttons=kb_cbt()); return
        if t in PER_D:
            days=PER_D[t]; start,end=dr(days); recs=get_records_by_period(tu(uid),start,end)
            if not recs: tx(uid,"❌ Нет записей.",buttons=kb_cbt()); st[uid]={}; return
            items=["#"+str(r[0])+" "+db_to_display(r[2])+"\n"+str(r[3] or '-') for r in recs]
            chk(uid,items,"📋 **Записей: "+str(len(recs))+"**",btns=kb_cbt())
            st[uid]={}; return
        if "Свой" in t: st[uid]={'state':'recs_custom'}; tx(uid,"📅 **ДД-ММ-ГГГГ ДД-ММ-ГГГГ:**",buttons=kb_cancel()); return
        return

    if state=='recs_custom':
        if t=="◀️ Назад": st[uid]={'state':'recs'}; tx(uid,"📅 Период:",buttons=kb_records()); return
        parts=t.split()
        if len(parts)<2: tx(uid,"❌ ДД-ММ-ГГГГ ДД-ММ-ГГГГ:",buttons=kb_cancel()); return
        try: sd=datetime.strptime(parts[0],"%d-%m-%Y").date(); ed=datetime.strptime(parts[1],"%d-%m-%Y").date()
        except: tx(uid,"❌ Неверный формат.",buttons=kb_cancel()); return
        recs=get_records_by_period(tu(uid),sd,ed)
        if not recs: tx(uid,"❌ Нет записей.",buttons=kb_cbt())
        else: chk(uid,["#"+str(r[0])+" "+db_to_display(r[2]) for r in recs],"📋 **"+str(len(recs))+" записей**",btns=kb_cbt())
        st[uid]={}; return

    # -- Edit Record --
    if t=="✏️ Редактировать" and sec!='plans' and sec!='ach':
        st[uid]={'state':'es'}; tx(uid,"📅 **Период:**",buttons=kb_records_edit()); return

    if state=='es':
        if t=="◀️ Назад": st[uid]={}; tx(uid,"🧠 КПТ",buttons=kb_cbt()); return
        if t in PER_D:
            days=PER_D[t]; start,end=dr(days); recs=get_records_by_period(tu(uid),start,end)
            if not recs: tx(uid,"❌ Нет записей.",buttons=kb_cbt()); st[uid]={}; return
            lines=["#"+str(r[0])+" "+db_to_display(r[2]) for r in recs[:15]]
            tx(uid,"✏️ **"+str(len(recs))+" записей**\n\n"+"\n".join(lines)+"\n\n**ID записи:**",buttons=kb_cancel())
            st[uid]={'state':'eid','valid_ids':{r[0] for r in recs}}; return
        if "Свой" in t: st[uid]={'state':'es_custom'}; tx(uid,"📅 ДД-ММ-ГГГГ ДД-ММ-ГГГГ:",buttons=kb_cancel()); return
        return

    if state=='es_custom':
        if t=="◀️ Назад": st[uid]={'state':'es'}; tx(uid,"📅 Период:",buttons=kb_records_edit()); return
        parts=t.split()
        if len(parts)<2: tx(uid,"❌",buttons=kb_cancel()); return
        try: sd=datetime.strptime(parts[0],"%d-%m-%Y").date(); ed=datetime.strptime(parts[1],"%d-%m-%Y").date()
        except: tx(uid,"❌",buttons=kb_cancel()); return
        recs=get_records_by_period(tu(uid),sd,ed)
        if not recs: tx(uid,"❌ Нет.",buttons=kb_cbt()); st[uid]={}; return
        lines=["#"+str(r[0]) for r in recs[:15]]
        tx(uid,"✏️ **"+str(len(recs))+"**\n"+"\n".join(lines)+"\n**ID:**",buttons=kb_cancel())
        st[uid]={'state':'eid','valid_ids':{r[0] for r in recs}}; return

    if state=='eid':
        if t=="◀️ Назад": st[uid]={'state':'es'}; tx(uid,"📅",buttons=kb_records_edit()); return
        try: rid=int(t)
        except: tx(uid,"❌ **ID** (цифра).",buttons=kb_cancel()); return
        rec=get_record_by_id(rid,tu(uid))
        if not rec: tx(uid,"❌ #"+str(rid)+" не найдена.",buttons=kb_cancel()); return
        st[uid]={'state':'editing','record_id':rid}
        tx(uid,"✏️ **#"+str(rid)+"**\n\n"+format_record(rec)+"\n**Поле:**",buttons=kb_edit())
        return

    if state=='editing':
        if t in EDIT_F:
            field=EDIT_F[t]; rec=get_record_by_id(s['record_id'],tu(uid))
            old=rec[IDX[field]] if rec else ''
            st[uid]['ef']=field; st[uid]['state']='ev'
            if field=='created_at': tx(uid,"📅 **Было:** "+str(db_to_display(old) if old else '-')+"\n✏️ **Новое (ДД-ММ-ГГГГ ЧЧ:ММ):**",buttons=kb_cancel())
            else: tx(uid,"📝 **Было:** "+str(old or '-')+"\n✏️ **Новое:**",buttons=kb_cancel())
            return
        if t=="🗑 Удалить запись": 
            rid = s.get('record_id')
            if rid: delete_record(rid, tu(uid)); tx(uid,"✅ #"+str(rid)+" удалена!",buttons=kb_cbt())
            else: tx(uid,"❌ Нет записи для удаления.",buttons=kb_cbt())
            st[uid]={}; return
        if t=="◀️ Назад": st[uid]={}; tx(uid,"🧠 КПТ",buttons=kb_cbt()); return
        return

    if state=='ev':
        if t=="◀️ Назад": rid=s['record_id']; rec=get_record_by_id(rid,tu(uid)); st[uid]={'state':'editing','record_id':rid}; tx(uid,"✏️ #"+str(rid)+"\n"+format_record(rec),buttons=kb_edit()); return
        field=s.get('ef'); val=t.strip()
        if field=='created_at':
            try: val=display_to_db(val)
            except: tx(uid,"❌ Формат ДД-ММ-ГГГГ ЧЧ:ММ",buttons=kb_cancel()); return
        update_record(s['record_id'],tu(uid),field,val)
        tx(uid,"✅ **Обновлено!**",buttons=kb_edit())
        st[uid]={'state':'editing','record_id':s['record_id']}; return

    # -- Delete Record --
    if t=="🗑 Удалить запись":
        st[uid]={'state':'ds'}; tx(uid,"🗑 **Период:**",buttons=kb_records_del()); return

    if state=='ds':
        if t=="◀️ Назад": st[uid]={}; tx(uid,"🧠 КПТ",buttons=kb_cbt()); return
        if t in PER_D:
            days=PER_D[t]; start,end=dr(days); recs=get_records_by_period(tu(uid),start,end)
            if not recs: tx(uid,"❌ Нет записей.",buttons=kb_cbt()); st[uid]={}; return
            lines=["#"+str(r[0]) for r in recs[:15]]
            tx(uid,"🗑 **"+str(len(recs))+"**\n"+"\n".join(lines)+"\n**ID для удаления:**",buttons=kb_cancel())
            st[uid]={'state':'di','valid_ids':{r[0] for r in recs}}; return
        if "Свой" in t: st[uid]={'state':'ds_custom'}; tx(uid,"📅 ДД-ММ-ГГГГ ДД-ММ-ГГГГ:",buttons=kb_cancel()); return
        return

    if state=='di':
        if t=="◀️ Назад": st[uid]={'state':'ds'}; tx(uid,"🗑 Период:",buttons=kb_records_del()); return
        try: rid=int(t)
        except: tx(uid,"❌ ID.",buttons=kb_cancel()); return
        rec=get_record_by_id(rid,tu(uid))
        if not rec: tx(uid,"❌ Не найдена.",buttons=kb_cancel()); return
        st[uid]={'state':'dc','record_id':rid}
        tx(uid,"🗑 **Удалить #"+str(rid)+"?**\n"+format_record(rec)+"\n\n**Подтвердить?**",buttons=kb_confirm_del())
        return

    if state=='dc':
        if t=="✅ Да, удалить": delete_record(s['record_id'],tu(uid)); tx(uid,"✅ #"+str(s['record_id'])+" удалена!",buttons=kb_cbt())
        elif t=="◀️ Назад": tx(uid,"❌ Отменено.",buttons=kb_cbt())
        st[uid]={}; return

    if state=='ds_custom':
        if t=="◀️ Назад": st[uid]={'state':'ds'}; tx(uid,"🗑",buttons=kb_records_del()); return
        parts=t.split()
        if len(parts)<2: tx(uid,"❌",buttons=kb_cancel()); return
        try: sd=datetime.strptime(parts[0],"%d-%m-%Y").date(); ed=datetime.strptime(parts[1],"%d-%m-%Y").date()
        except: tx(uid,"❌",buttons=kb_cancel()); return
        recs=get_records_by_period(tu(uid),sd,ed)
        if not recs: tx(uid,"❌ Нет.",buttons=kb_cbt()); st[uid]={}; return
        lines=["#"+str(r[0]) for r in recs[:15]]
        tx(uid,"🗑 **"+str(len(recs))+"**\n"+"\n".join(lines)+"\n**ID:**",buttons=kb_cancel())
        st[uid]={'state':'di','valid_ids':{r[0] for r in recs}}; return

    # ==== PLANS ====
    if t=="📋 Планы на день":
        st[uid]={'sec':'plans'}; tx(uid,"📋 **Планы на день**",buttons=kb_plans()); return

    if sec=='plans' and t=="✏️ Редактировать":
        st[uid]={'state':'pe'}; tx(uid,"📅 **День:**",buttons=kb_plan_edit()); return

    # -- New Plan --
    if sec=='plans' and t=="📝 Новый план":
        st[uid]={'sec':'plans','state':'pn'}; tx(uid,"📅 **На какой день?**",buttons=kb_plan_date()); return

    if state=='pn':
        if t=="📅 Сегодня": d=date.today()
        elif t=="📅 Завтра": d=date.today()+timedelta(1)
        elif t=="📅 Выбрать дату": st[uid]={'sec':'plans','state':'pn_dt'}; tx(uid,"📅 **ДД-ММ-ГГГГ:**",buttons=kb_cancel()); return
        elif t=="◀️ Назад": st[uid]={'sec':'plans'}; tx(uid,"📋 Планы",buttons=kb_plans()); return
        else: return
        if check_plan_exists(tu(uid),d)[0]: tx(uid,"⚠️ **План уже есть!**",buttons=[["✏️ Редактировать","🏠 Главное меню"]]); st[uid]={'sec':'plans'}; return
        pid=get_or_create_plan(tu(uid),d)
        st[uid]={'sec':'plans','state':'pf','pid':pid}
        tx(uid,"📝 **План на "+fd(d)+"**\nПиши пункты:",buttons=kb_plan_fill())
        return

    if state=='pn_dt':
        if t=="◀️ Назад": st[uid]={'sec':'plans','state':'pn'}; tx(uid,"📅",buttons=kb_plan_date()); return
        try: d=datetime.strptime(t.strip(),"%d.%m.%Y").date()
        except: tx(uid,"❌ **ДД.ММ.ГГГГ**",buttons=kb_cancel()); return
        if check_plan_exists(tu(uid),d)[0]: tx(uid,"⚠️ Есть!",buttons=[["✏️ Редактировать","🏠 Главное меню"]]); st[uid]={'sec':'plans'}; return
        pid=get_or_create_plan(tu(uid),d)
        st[uid]={'sec':'plans','state':'pf','pid':pid}
        tx(uid,"📝 **План на "+fd(d)+"**\nПункты:",buttons=kb_plan_fill())
        return

    # -- Plan fill --
    if state=='pf':
        pid=s.get('pid')
        if t=="✅ Готово":
            cnt=len(get_plan_items(pid))
            tx(uid,"✅ **Сохранён!** Пунктов: "+str(cnt),buttons=[["📋 Мои планы","✅ Отметить выполнение"],["📝 Новый план","🏠 Главное меню"]])
            st[uid]={'sec':'plans'}; return
        if t in ("◀️ Назад","🏠 Главное меню"): st[uid]={'sec':'plans'}; tx(uid,"📋 Планы",buttons=kb_plans()); return
        if pid:
            for l in t.split("\n"):
                if l.strip(): add_plan_item(pid,l.strip())
            tx(uid,"✅ Добавлено!",buttons=[["✅ Готово"],["◀️ Назад","🏠 Главное меню"]])
        return

    # -- View Plans --
    if sec=='plans' and t=="📋 Мои планы":
        st[uid]={'sec':'plans','state':'pv'}; tx(uid,"📅 **Период:**",buttons=kb_plan_view()); return

    if state=='pv':
        if t=="📅 Сегодня": d=date.today()
        elif t=="📅 Завтра": d=date.today()+timedelta(1)
        elif t=="📅 Выбрать дату": st[uid]={'sec':'plans','state':'pv_dt'}; tx(uid,"📅 **ДД.ММ.ГГГГ:**",buttons=kb_cancel()); return
        elif t=="📅 Неделя":
            pls=get_plans_by_period(tu(uid),date.today()-timedelta(7),date.today())
            if not pls: tx(uid,"📭 **Нет планов.**",buttons=kb_plan_view()); return
            its=[p['plan_date']+" — ✅"+str(sum(1 for i in p.get('items',[]) if i['is_done']))+"/"+str(len(p.get('items',[]))) for p in pls]
            chk(uid,its,"📋 **Неделя:**",btns=[["📝 Новый план","◀️ Назад","🏠 Главное меню"]])
            st[uid]={'sec':'plans'}; return
        elif t=="📅 За всё время":
            pls=get_plans_by_period(tu(uid),date(2000,1,1),date.today())
            if not pls: tx(uid,"📭 **Нет.**",buttons=kb_plan_view()); return
            its=[p['plan_date']+" — ✅"+str(sum(1 for i in p.get('items',[]) if i['is_done']))+"/"+str(len(p.get('items',[]))) for p in pls]
            chk(uid,its,"📋 **Все планы:**",btns=[["📝 Новый план","◀️ Назад","🏠 Главное меню"]])
            st[uid]={'sec':'plans'}; return
        elif t=="◀️ Назад": st[uid]={'sec':'plans'}; tx(uid,"📋 Планы",buttons=kb_plans()); return
        else: return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); its=get_plan_items(pid)
            lines=["📅 **План на "+fd(d)+":**"]
            for it in its: lines.append("  ✅ #"+str(it[0])+" "+it[1] if it[2] else "  ⬜ #"+str(it[0])+" "+it[1])
            tx(uid,"\n".join(lines),buttons=kb_plan_items())
            st[uid]={'sec':'plans','state':'pvi','pid':pid}
        else: tx(uid,"❌ **Нет плана на "+fd(d)+".**",buttons=kb_plan_view())
        return

    if state=='pv_dt':
        if t=="◀️ Назад": st[uid]={'sec':'plans','state':'pv'}; tx(uid,"📅",buttons=kb_plan_view()); return
        try: d=datetime.strptime(t.strip(),"%d.%m.%Y").date()
        except: tx(uid,"❌ ДД.ММ.ГГГГ",buttons=kb_cancel()); return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); its=get_plan_items(pid)
            lines=["📅:"]
            for it in its: lines.append("  ✅ #"+str(it[0])+" "+it[1] if it[2] else "  ⬜ #"+str(it[0])+" "+it[1])
            tx(uid,"\n".join(lines),buttons=kb_plan_items())
            st[uid]={'sec':'plans','state':'pvi','pid':pid}
        else: tx(uid,"❌ Нет.",buttons=kb_plan_view())
        return

    # -- Plan Items CRUD --
    if state=='pvi':
        pid=s.get('pid')
        if t=="➕ Добавить пункт": st[uid]={'sec':'plans','state':'pvi_add','pid':pid}; tx(uid,"✏️ **Текст:**",buttons=kb_cancel()); return
        if t=="✏️ Редактировать пункт": st[uid]={'sec':'plans','state':'pvi_ed_sel','pid':pid}; tx(uid,"✏️ **#ID:**",buttons=kb_cancel()); return
        if t=="🗑 Удалить пункт": st[uid]={'sec':'plans','state':'pvi_del','pid':pid}; tx(uid,"🗑 **#ID:**",buttons=kb_cancel()); return
        if t=="◀️ Назад": st[uid]={'sec':'plans'}; tx(uid,"📋 Планы",buttons=kb_plans()); return
        return

    if state=='pvi_add':
        if t in ("◀️ Назад","🏠 Главное меню"): 
            pid = s.get('pid')
            if pid: st[uid]={'sec':'plans','state':'pvi','pid':pid}; tx(uid,"📋",buttons=kb_plan_items())
            else: st[uid]={'sec':'plans'}; tx(uid,"📋",buttons=kb_plans())
            return
        add_plan_item(s['pid'],t); tx(uid,"✅ Добавлено!",buttons=[["➕ Ещё"],["◀️ Назад","🏠 Главное меню"]]); return

    if state=='pvi_ed_sel':
        if t in ("◀️ Назад","🏠 Главное меню"): st[uid]={'sec':'plans','state':'pvi','pid':s['pid']}; tx(uid,".",buttons=kb_plan_items()); return
        try: iid=int(t.strip().lstrip('#')); st[uid]={'sec':'plans','state':'pvi_ed_val','pid':s['pid'],'iid':iid}; tx(uid,"✏️ **Новый текст:**",buttons=kb_cancel())
        except: tx(uid,"❌ #ID",buttons=kb_cancel())
        return

    if state=='pvi_ed_val':
        if t in ("◀️ Назад","🏠 Главное меню"): st[uid]={'sec':'plans','state':'pvi','pid':s['pid']}; tx(uid,".",buttons=kb_plan_items()); return
        dbq('UPDATE plan_items SET text=? WHERE id=?',(t,s['iid'])); tx(uid,"✅ **Обновлено!**",buttons=kb_plan_items()); st[uid]={'sec':'plans','state':'pvi','pid':s['pid']}; return

    if state=='pvi_del':
        if t in ("◀️ Назад","🏠 Главное меню"): st[uid]={'sec':'plans'}; tx(uid,"📋",buttons=kb_plans()); return
        try: iid=int(t.strip().lstrip('#')); delete_plan_item(iid); tx(uid,"✅ #"+str(iid)+" удалён!",buttons=kb_plan_items()); st[uid]={'sec':'plans','state':'pvi','pid':s['pid']}
        except: tx(uid,"❌ #ID.",buttons=kb_cancel())
        return

    # -- Edit Plan (redirect to items) --
    if state=='pe':
        if t=="📅 Сегодня ✏️": d=date.today()
        elif t=="📅 Завтра ✏️": d=date.today()+timedelta(1)
        elif t=="📅 Выбрать дату ✏️": st[uid]={'sec':'plans','state':'pe_dt'}; tx(uid,"📅 ДД.ММ.ГГГГ:",buttons=kb_cancel()); return
        elif t=="📅 Неделя ✏️":
            pls=get_plans_by_period(tu(uid),date.today()-timedelta(7),date.today())
            if not pls: tx(uid,"❌ Нет.",buttons=kb_plan_edit()); return
            its=[p['plan_date'] for p in pls]
            chk(uid,its,"📋 Выбери:",btns=[["◀️ Назад","🏠 Главное меню"]])
            st[uid]={'sec':'plans','state':'pe_dt'}; return
        elif t=="◀️ Назад": st[uid]={'sec':'plans'}; tx(uid,"📋",buttons=kb_plans()); return
        else: return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); its=get_plan_items(pid)
            lines=["✏️ **"+fd(d)+":**"]
            for it in its: lines.append("  #"+str(it[0])+" "+it[1])
            tx(uid,"\n".join(lines),buttons=kb_plan_items()); st[uid]={'sec':'plans','state':'pvi','pid':pid}
        else: tx(uid,"❌ Нет.",buttons=kb_plan_edit())
        return

    if state=='pe_dt':
        if t=="◀️ Назад": st[uid]={'sec':'plans','state':'pe'}; tx(uid,"📅",buttons=kb_plan_edit()); return
        try: d=datetime.strptime(t.strip(),"%d.%m.%Y").date()
        except: tx(uid,"❌",buttons=kb_cancel()); return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); its=get_plan_items(pid)
            lines=["✏️:"]
            for it in its: lines.append("  #"+str(it[0])+" "+it[1])
            tx(uid,"\n".join(lines),buttons=kb_plan_items()); st[uid]={'sec':'plans','state':'pvi','pid':pid}
        else: tx(uid,"❌ Нет.",buttons=kb_plan_edit())
        return

    # -- Delete Plan --
    if sec=='plans' and t=="🗑 Удалить план":
        st[uid]={'sec':'plans','state':'pdel'}; tx(uid,"📅 **День:**",buttons=kb_plan_edit()); return

    if state=='pdel':
        if t=="📅 Сегодня ✏️": d=date.today()
        elif t=="📅 Завтра ✏️": d=date.today()+timedelta(1)
        elif t=="📅 Выбрать дату ✏️": st[uid]={'sec':'plans','state':'pdel_dt'}; tx(uid,"📅 ДД.ММ.ГГГГ:",buttons=kb_cancel()); return
        elif t=="📅 Неделя ✏️":
            pls=get_plans_by_period(tu(uid),date.today()-timedelta(7),date.today())
            if not pls: tx(uid,"❌ Нет.",buttons=kb_plan_edit()); return
            its=[p['plan_date'] for p in pls]
            chk(uid,its,"🗑 Выбери:",btns=[["◀️ Назад","🏠 Главное меню"]])
            st[uid]={'sec':'plans','state':'pdel_dt'}; return
        elif t=="◀️ Назад": st[uid]={'sec':'plans'}; tx(uid,"📋",buttons=kb_plans()); return
        else: return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); delete_plan(pid)
            tx(uid,"🗑 **План на "+fd(d)+" удалён!**",buttons=kb_plans())
        else: tx(uid,"❌ Нет.",buttons=kb_plan_edit())
        st[uid]={'sec':'plans'}; return

    if state=='pdel_dt':
        if t=="◀️ Назад": st[uid]={'sec':'plans','state':'pdel'}; tx(uid,"📅",buttons=kb_plan_edit()); return
        try: d=datetime.strptime(t.strip(),"%d.%m.%Y").date()
        except: tx(uid,"❌",buttons=kb_cancel()); return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); delete_plan(pid)
            tx(uid,"🗑 **Удалён!**",buttons=kb_plans())
        else: tx(uid,"❌ Нет.",buttons=kb_plan_edit())
        st[uid]={'sec':'plans'}; return

    # -- Mark Done --
    if sec=='plans' and t=="✅ Отметить выполнение":
        st[uid]={'sec':'plans','state':'po'}; tx(uid,"📅 **День:**",buttons=kb_plan_mark()); return

    if state=='po':
        if t=="📅 Сегодня ✅": d=date.today()
        elif t=="📅 Завтра ✅": d=date.today()+timedelta(1)
        elif t=="📅 Выбрать дату ✅": st[uid]={'sec':'plans','state':'po_dt'}; tx(uid,"📅 ДД.ММ.ГГГГ:",buttons=kb_cancel()); return
        elif t=="📅 Неделя ✅":
            pls=get_plans_by_period(tu(uid),date.today()-timedelta(7),date.today())
            if not pls: tx(uid,"❌ Нет.",buttons=kb_plan_mark()); return
            its=[p['plan_date'] for p in pls]
            chk(uid,its,"📋 Выбери:",btns=[["◀️ Назад","🏠 Главное меню"]])
            st[uid]={'sec':'plans','state':'po_dt'}; return
        elif t=="📅 Всё ✅":
            pls=get_plans_by_period(tu(uid),date(2000,1,1),date.today())
            if not pls: tx(uid,"❌ Нет.",buttons=kb_plan_mark()); return
            its=[p['plan_date'] for p in pls]
            chk(uid,its,"📋 Выбери:",btns=[["◀️ Назад","🏠 Главное меню"]])
            st[uid]={'sec':'plans','state':'po_dt'}; return
        elif t=="◀️ Назад": st[uid]={'sec':'plans'}; tx(uid,"📋",buttons=kb_plans()); return
        else: return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); its=get_plan_items(pid)
            lines=["📋 **"+fd(d)+":**"]
            for it in its: lines.append("  ✅ #"+str(it[0])+" "+it[1] if it[2] else "  ⬜ #"+str(it[0])+" "+it[1])
            lines.append("\n**Введи #ID для отметки:**")
            tx(uid,"\n".join(lines),buttons=[["✅ Готово"],["◀️ Назад","🏠 Главное меню"]])
            st[uid]={'sec':'plans','state':'po_tg','pid':pid}
        else: tx(uid,"❌ **Нет плана.**",buttons=kb_plan_mark())
        return

    if state=='po_tg':
        pid=s.get('pid')
        if t=="✅ Готово": st[uid]={'sec':'plans'}; tx(uid,"📋",buttons=kb_plans()); return
        if t in ("◀️ Назад","🏠 Главное меню"): st[uid]={'sec':'plans'}; tx(uid,"📋",buttons=kb_plans()); return
        try:
            iid=int(t.strip().lstrip('#'))
            toggle_plan_item(iid)
        except Exception:
            tx(uid,"❌ #ID",buttons=kb_confirm_del())
            return
        its = get_plan_items(pid)
        lines = ["📋:"]
        for it in its:
            lines.append("  ✅ #" + str(it[0]) + " " + it[1] if it[2] else "  ⬜ #" + str(it[0]) + " " + it[1])
        lines.append("")
        lines.append("#ID:")
        tx(uid, "\n".join(lines), buttons=kb_plan_items())
        st[uid] = {"sec": "plans", "state": "po_tg", "pid": pid}
        return


    if state=='po_dt':
        if t=="◀️ Назад": st[uid]={'sec':'plans','state':'po'}; tx(uid,"📅",buttons=kb_plan_mark()); return
        try: d=datetime.strptime(t.strip(),"%d.%m.%Y").date()
        except: tx(uid,"❌",buttons=kb_cancel()); return
        if check_plan_exists(tu(uid),d)[0]:
            pid=get_or_create_plan(tu(uid),d); its=get_plan_items(pid)
            lines=["📋:"]
            for it in its: lines.append("  ✅ #"+str(it[0])+" "+it[1] if it[2] else "  ⬜ #"+str(it[0])+" "+it[1])
            lines.append("")
            lines.append("#ID:")
            tx(uid,"\n".join(lines),buttons=kb_plan_items())
            st[uid]={'sec':'plans','state':'po_tg','pid':pid}
        else: tx(uid,"❌ Нет.",buttons=kb_plan_mark())
        return

    # ==== ACHIEVEMENTS ====
    if t=="🏆 Достижения":
        st[uid]={'sec':'ach'}; tx(uid,"🏆 **Достижения** ("+str(count_achievements(tu(uid)))+")",buttons=kb_ach()); return

    if sec=='ach' and t=="➕ Добавить одно":
        st[uid]={'sec':'ach','state':'ach_add'}; tx(uid,"✏️ **Напиши достижение:**",buttons=kb_cancel()); return
    if state=='ach_add':
        if t in ("◀️ Назад","🏠 Главное меню"): st[uid]={'sec':'ach'}; tx(uid,"🏆",buttons=kb_ach()); return
        add_achievement(tu(uid),t)
        tx(uid,"✅ **Добавлено!** ("+str(count_achievements(tu(uid)))+")",buttons=kb_ach())
        st[uid]={'sec':'ach'}; return

    if sec=='ach' and t=="➕ Несколько":
        st[uid]={'sec':'ach','state':'ach_multi','achs':[]}; tx(uid,"✏️ **Пиши каждое с новой строки.**\n✅ **Готово** когда закончишь:",buttons=kb_ach_fill()); return
    if state=='ach_multi':
        if t=="✅ Готово":
            achs=s.get('achs',[])
            for a in achs:
                if a.strip(): add_achievement(tu(uid),a.strip())
            tx(uid,"✅ **Добавлено "+str(len(achs))+"!** Всего: "+str(count_achievements(tu(uid))),buttons=kb_ach())
            st[uid]={'sec':'ach'}; return
        if t=="🗑 Удалить всё":
            for a in get_achievements_all(tu(uid)): delete_achievement(a[0], tu(uid))
            tx(uid,"🗑 **Всё удалено!**",buttons=kb_ach())
            st[uid]={'sec':'ach'}; return
        if t in ("◀️ Назад","🏠 Главное меню"): st[uid]={'sec':'ach'}; tx(uid,"🏆",buttons=kb_ach()); return
        achs=s.get('achs',[])
        for l in t.split("\n"):
            if l.strip(): achs.append(l.strip())
        st[uid]['achs']=achs
        tx(uid,"✅ **В списке: "+str(len(achs))+"**\nПиши ещё или нажми ✅ Готово:",buttons=kb_ach_fill())
        return

    if sec=='ach' and t=="📋 Мои достижения":
        data=get_achievements_all(tu(uid))
        if not data: tx(uid,"📭 **Нет достижений.**",buttons=kb_ach())
        else: chk(uid,[str(a[0])+". "+a[1] for a in data],"🏆 **Достижения:**",btns=kb_ach())
        st[uid]={'sec':'ach'}; return

    if sec=='ach' and t=="🗑 Удалить":
        st[uid]={'sec':'ach','state':'ach_del'}; tx(uid,"🗑 **#ID:**",buttons=kb_cancel()); return
    if state=='ach_del':
        if t in ("◀️ Назад","🏠 Главное меню"): st[uid]={'sec':'ach'}; tx(uid,"🏆",buttons=kb_ach()); return
        try: iid=int(t.strip().lstrip("#'")); delete_achievement(iid, tu(uid)); tx(uid,"✅ **Удалено!**",buttons=kb_ach())
        except: tx(uid,"❌ #ID.",buttons=kb_cancel()); return
        st[uid]={'sec':'ach'}; return

    if sec=='ach' and t=="🗑 Удалить все":
        st[uid]={'sec':'ach','state':'ach_confirm_del_all'}
        tx(uid,"⚠️ **Точно удалить все достижения?**\n\nЭто действие нельзя отменить.",buttons=kb_confirm_del_all())
        return

    if state=='ach_confirm_del_all':
        if t=="✅ Да, удалить всё":
            for a in get_achievements_all(tu(uid)): delete_achievement(a[0])
            tx(uid,"🗑 **Всё удалено!**",buttons=kb_ach())
            st[uid]={'sec':'ach'}; return
        if t=="❌ Нет, отменить":
            st[uid]={'sec':'ach'}
            tx(uid,"❌ Отменено.",buttons=kb_ach())
            return
        tx(uid,"⚠️ **Точно удалить все?**",buttons=kb_confirm_del_all())
        return

    if sec=='ach' and t=="✏️ Редактировать":
        st[uid]={'sec':'ach','state':'ach_ed_sel'}; tx(uid,"✏️ **#ID:**",buttons=kb_cancel()); return
    if state=='ach_ed_sel':
        if t in ("◀️ Назад","🏠 Главное меню"): st[uid]={'sec':'ach'}; tx(uid,"🏆",buttons=kb_ach()); return
        try: iid=int(t.strip().lstrip("#'")); st[uid]={'sec':'ach','state':'ach_ed_val','iid':iid}; tx(uid,"✏️ **Новый текст:**",buttons=kb_cancel())
        except: tx(uid,"❌ #ID.",buttons=kb_cancel())
        return
    if state=='ach_ed_val':
        if t in ("◀️ Назад","🏠 Главное меню"): st[uid]={'sec':'ach'}; tx(uid,"🏆",buttons=kb_ach()); return
        update_achievement(s['iid'],t); tx(uid,"✅ **Обновлено!**",buttons=kb_ach())
        st[uid]={'sec':'ach'}; return

    # ==== EXPORT ====
    if t in ("📊 Выгрузить","📊 Выгрузить Excel"):
        st[uid]={'state':'ex'}; tx(uid,"📊 **Что выгрузить?**",buttons=make_kb([["🧠 КПТ записи","📋 Планы"],["🏆 Достижения"],["◀️ Назад","🏠 Главное меню"]])); return
    if state=='ex':
        if t=="🧠 КПТ записи": et="cbt"
        elif t=="📋 Планы": et="plans"
        elif t=="🏆 Достижения":
            data=get_achievements_all(tu(uid))
            chk(uid,[str(a[0])+". "+a[1] for a in data],"🏆",btns=make_kb([["◀️ Назад","🏠 Главное меню"]]))
            st[uid]={'sec':'ach'}; return
        elif t=="◀️ Назад": st[uid]={}; tx(uid,"🏠",buttons=kb_main()); return
        else: return
        st[uid]={'state':'ex_days','et':et}; tx(uid,"📅 **Сколько дней:**",buttons=make_kb([["3 дня","7 дней","30 дней"],["◀️ Назад","🏠 Главное меню"]]))
        return
    if state=='ex_days':
        if t=="◀️ Назад": st[uid]={}; tx(uid,"🏠",buttons=kb_main()); return
        m={"3 дня":3,"7 дней":7,"30 дней":30}
        d=m.get(t)
        if not d:
            try: d=int(t.strip())
            except: tx(uid,"❌ 3, 7 или 30",buttons=kb_cancel()); return
        if d not in (3,7,30): tx(uid,"❌ 3, 7, 30",buttons=kb_cancel()); return
        et=s.get('et','cbt')
        if et=='cbt':
            start,end=dr(d); recs=get_records_by_period(tu(uid),start,end)
            if not recs: tx(uid,"❌ Нет.",buttons=kb_cbt()); return
            its=[("#"+str(r[0])+" "+db_to_display(r[2]),str(r[3] or '-')+"\n"+str(r[4] or '-')) for r in recs]
            chk(uid,its,"🧠 **КПТ ("+str(len(recs))+"):**",btns=kb_cbt())
        elif et=='plans':
            pls=get_plans_by_period(tu(uid),date.today()-timedelta(d),date.today()+timedelta(1))
            if not pls: tx(uid,"❌ Нет.",buttons=kb_plans()); return
            its=[]
            for p in pls:
                for it in p.get("items",[]): its.append(p['plan_date']+"  "+("✅" if it.get('is_done') else "⬜")+" "+it['text'])
            chk(uid,its,"📋 **Планы:**",btns=kb_plans())
        st[uid]={}; return

    # ---- Fallback ----
    tx(uid, "❓ Неизвестная команда. Выбери из меню:", buttons=kb_main())

def process_update(upd):
    ut = upd.get("update_type","")
    uid = None; text = ""
    if ut == "message_created":
        msg = upd.get("message",{}) or {}
        snd = msg.get("sender",{}) or upd.get("user",{})
        uid = snd.get("user_id")
        body = (msg.get("body",{}) or {})
        text = body.get("text","")
        if isinstance(text,str): text = text.strip()
    elif ut == "bot_started":
        uid = upd.get("user",{}).get("user_id")
        text = "/start"
    elif ut == "message_callback":
        uid = upd.get("user",{}).get("user_id")
        cb = upd.get("callback",{}) or {}
        text = cb.get("payload","") or cb.get("text","")
        if isinstance(text,str): text = text.strip()
    else:
        return
    if not uid or not text: return
    log.info(f"<- MAX#{uid}: {text[:80]}")
    try:
        handle(uid, text)
    except Exception as e:
        import traceback; traceback.print_exc()
        log.error(f"Error: {e}")
        tx(uid, "Произошла ошибка. Попробуй ещё раз.", buttons=kb_main())

def poll():
    marker = None
    while _running:
        try:
            params = {"timeout": 30, "limit": 100, "types": "message_created,message_callback,bot_started"}
            if marker is not None:
                params["marker"] = marker
            data = api("/updates", params=params)
            if data and isinstance(data, dict):
                marker = data.get("marker") or marker
                updates = data.get("updates", [])
                for upd in updates:
                    process_update(upd)
            elif data and isinstance(data, list):
                for upd in data:
                    process_update(upd)
        except requests.exceptions.Timeout:
            pass
        except Exception as e:
            log.error(f"Poll error: {e}")
            time.sleep(5)

def main():
    signal.signal(signal.SIGTERM, lambda *a: setattr(sys.modules[__name__], '_running', False))
    signal.signal(signal.SIGINT, lambda *a: setattr(sys.modules[__name__], '_running', False))
    log.info("🚀 CBT-MAX Bridge запущен")
    log.info(f"   MAX API: {MAX_API}")
    log.info(f"   DB: {DB_FILE}")
    me = api("/me")
    if me:
        log.info(f"✅ Бот авторизован: {me.get('name', '?')} (@{me.get('username', '?')})")
    else:
        log.error("❌ Не удалось подключиться к MAX")
    poll()
    log.info("Stopped.")

if __name__ == "__main__":
    main()
