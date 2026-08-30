import random, html
import gradio as gr
from questions import QUESTIONS

CHAPTER_NAMES={3:'Chapter 3 — Fractions',4:'Chapter 4 — Decimals',5:'Chapter 5 — Addition & Subtraction',6:'Chapter 6 — Multiplication',9:'Chapter 9 — Geometrical Shapes & Solids',10:'Chapter 10 — Symmetry'}
PRACTICE_QUOTAS={3:6,4:8,5:10,6:10,9:7,10:9}
EXAM_QUOTAS={3:4,4:5,5:6,6:6,9:4,10:5}

def build_test(mode):
    quotas=PRACTICE_QUOTAS if mode=='practice' else EXAM_QUOTAS
    selected=[]
    for ch,quota in quotas.items():
        pool=[q for q in QUESTIONS if q['chapter']==ch]
        random.shuffle(pool)
        if mode=='exam': pool.sort(key=lambda q:0 if q['difficulty']=='hard' else 1)
        selected.extend(pool[:min(quota,len(pool))])
    random.shuffle(selected)
    return selected

def new_state(mode): return {'mode':mode,'questions':build_test(mode),'index':0,'score':0,'answered':False,'mistakes':[]}

def buttons(q,enabled=True):
    return [gr.update(value=q['options'][i],visible=i<len(q['options']),interactive=enabled) if i<len(q['options']) else gr.update(value='',visible=False,interactive=False) for i in range(4)]

def render(q):
    fig=q.get('figure') or ''
    return f"""<div class="card"><div class="tags"><span>{CHAPTER_NAMES[q['chapter']]}</span><span>{html.escape(q['topic'])}</span><span>{'Harder' if q['difficulty']=='hard' else 'Medium'}</span></div><div class="question">{html.escape(q['prompt'])}</div>{fig}</div>"""

def start(label):
    mode='practice' if 'Practice' in label else 'exam'; s=new_state(mode); q=s['questions'][0]
    note='🟢 **Balanced Practice Test — 50 questions**' if mode=='practice' else '🔴 **Exam Prep Test — 30 questions, slightly harder**'
    return s,note,f'### Question 1 of {len(s["questions"])}',render(q),'',gr.update(value='',visible=False),'### Score: **0**',*buttons(q,True),gr.update(visible=False),gr.update(visible=False)

def answer(idx,s):
    if not s or s['answered']: return s,'',gr.update(),*[gr.update() for _ in range(4)],gr.update(),gr.update()
    q=s['questions'][s['index']]; s['answered']=True
    if idx==q['answer']:
        s['score']+=1; fb=f'<div class="ok"><b>Correct!</b><br>{html.escape(q["explanation"])}</div>'
    else:
        s['mistakes'].append({'question':q['prompt'],'your':q['options'][idx],'correct':q['options'][q['answer']],'why':q['explanation'],'chapter':CHAPTER_NAMES[q['chapter']]})
        fb=f'<div class="bad"><b>Not quite.</b><br><b>Correct answer:</b> {html.escape(q["options"][q["answer"]])}<br>{html.escape(q["explanation"])}</div>'
    return s,fb,f'### Score: **{s["score"]}**',*buttons(q,False),gr.update(visible=True),gr.update(visible=False)

def sheet(s):
    total=len(s['questions']); pct=round(100*s['score']/total); out=[f'# Result Sheet',f'## Score: **{s["score"]} / {total} ({pct}%)**']
    if not s['mistakes']: out+=['','## Excellent — no incorrect answers!']
    else:
        out+=['',f'## Questions to revise: {len(s["mistakes"])}']
        for i,m in enumerate(s['mistakes'],1): out += ['',f'### {i}. {m["question"]}',f'**{m["chapter"]}**',f'- Your answer: **{m["your"]}**',f'- Correct answer: **{m["correct"]}**',f'- Why: {m["why"]}']
    return '\n'.join(out)

def next_q(s):
    n=s['index']+1
    if n>=len(s['questions']):
        hidden=[gr.update(value='',visible=False,interactive=False) for _ in range(4)]
        return s,'','','',gr.update(value=sheet(s),visible=True),f'### Final Score: **{s["score"]} / {len(s["questions"])}**',*hidden,gr.update(visible=False),gr.update(visible=True)
    s['index']=n;s['answered']=False;q=s['questions'][n]
    return s,f'### Question {n+1} of {len(s["questions"])}',render(q),'',gr.update(value='',visible=False),f'### Score: **{s["score"]}**',*buttons(q,True),gr.update(visible=False),gr.update(visible=False)

CSS=""".card{max-width:850px;margin:auto;padding:22px;border:1px solid #dbe3ea;border-radius:18px;background:#f8fafc}.tags{display:flex;gap:8px;flex-wrap:wrap}.tags span{padding:5px 10px;border-radius:999px;background:#e0e7ff;font-weight:600;font-size:13px}.question{font-size:23px;font-weight:700;line-height:1.4;margin:16px 0}.ok,.bad{padding:16px;border-radius:14px;font-size:17px}.ok{background:#ecfdf5}.bad{background:#fff7ed}.answer-button{min-height:60px!important;font-size:17px!important;white-space:normal!important}"""
with gr.Blocks(theme=gr.themes.Soft(),css=CSS,title='Class IV Mathematics — Exam Prep') as demo:
    state=gr.State(None)
    gr.Markdown('# 📚 Class IV Mathematics — Exam Prep')
    gr.Markdown('Chapters 3, 4, 5, 6, 9 & 10')
    mode=gr.Radio(['🟢 Balanced Practice Test — 50 Questions','🔴 Exam Prep Test — 30 Questions'],value='🟢 Balanced Practice Test — 50 Questions',label='Choose your test')
    start_btn=gr.Button('Start / Restart Test',variant='primary')
    note=gr.Markdown(); progress=gr.Markdown(); question=gr.HTML(); feedback=gr.HTML(); result=gr.Markdown(visible=False); score=gr.Markdown()
    with gr.Row(): b0=gr.Button('',visible=False,elem_classes='answer-button'); b1=gr.Button('',visible=False,elem_classes='answer-button')
    with gr.Row(): b2=gr.Button('',visible=False,elem_classes='answer-button'); b3=gr.Button('',visible=False,elem_classes='answer-button')
    next_btn=gr.Button('Next Question',variant='primary',visible=False); again=gr.Button('Choose a mode and start again',visible=False)
    start_out=[state,note,progress,question,feedback,result,score,b0,b1,b2,b3,next_btn,again]
    start_btn.click(start,mode,start_out); again.click(start,mode,start_out)
    ans_out=[state,feedback,score,b0,b1,b2,b3,next_btn,again]
    for i,b in enumerate([b0,b1,b2,b3]): b.click(lambda s,idx=i:answer(idx,s),state,ans_out)
    next_out=[state,progress,question,feedback,result,score,b0,b1,b2,b3,next_btn,again]
    next_btn.click(next_q,state,next_out)
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860
    )
