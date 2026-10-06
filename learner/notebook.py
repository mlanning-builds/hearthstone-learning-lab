"""Dependency-free notebook presentation of real training and evaluation results."""
from html import escape
import time


def learning_curve(evaluations):
    if not evaluations: return '<p>Initial evaluation is running.</p>'
    width,height=620,230; left,top=52,20; plot_w,plot_h=540,160
    maximum=max(1,max(e['trained_games'] for e in evaluations))
    points=[(left+e['trained_games']/maximum*plot_w,top+(1-e['win_rate'])*plot_h) for e in evaluations]
    svg=[f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Monitoring win rate against random play versus training games" style="width:100%;max-width:720px;color:inherit">']
    for percent in (0,25,50,75,100):
        y=top+(1-percent/100)*plot_h
        svg.append(f'<line x1="{left}" y1="{y}" x2="{left+plot_w}" y2="{y}" stroke="#8291a4" opacity="0.35"/><text x="{left-8}" y="{y+4}" text-anchor="end" fill="currentColor" font-size="11">{percent}%</text>')
    path=' '.join(f'{x:.2f},{y:.2f}' for x,y in points)
    svg.append(f'<polyline points="{path}" fill="none" stroke="#3185de" stroke-width="2.5"/>')
    for (x,y),e in zip(points,evaluations):
        svg.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#3185de"><title>{e["trained_games"]} training games: {e["wins"]}/{e["games"]} wins</title></circle>')
    svg.extend([f'<text x="{left}" y="200" font-size="11" fill="currentColor">0</text>',
                f'<text x="{left+plot_w}" y="200" text-anchor="end" font-size="11" fill="currentColor">{maximum:,}</text>',
                '<text x="325" y="220" text-anchor="middle" font-size="12" fill="currentColor">Completed training games</text></svg>'])
    return ''.join(svg)


class TrainingProgress:
    def __init__(self): self.handle=None; self.last=0; self.phase=None

    def __call__(self,state):
        from IPython.display import HTML, display
        now=time.monotonic()
        phase=state['phase']; done=state['completed']; total=max(done,state['total'])
        if phase==self.phase and now-self.last<0.3 and phase not in ('complete','failed','interrupted'): return
        self.last=now; self.phase=phase
        names=dict(training='Learning from game outcomes',evaluation='Checking against random play',
                   final_test='Testing on separate decks',complete='Training complete',
                   interrupted='Paused — latest completed game saved',failed='Stopped on an error — checkpoint preserved')
        elapsed=state['elapsed']; fresh=done-state['resumed']
        speed=fresh/elapsed if elapsed>0 else 0
        extra=''
        if phase in ('evaluation','final_test'):
            extra=f'<p>{state["phase_done"]} / {state["phase_total"]} evaluation games (no learning updates)</p>'
        timing=f'{elapsed:.1f}s elapsed · {speed:.1f} training games/sec including evaluations'
        html=f'''<div style="padding:18px;border:1px solid #8291a4;border-radius:10px;max-width:760px">
        <strong>{escape(names[phase])}</strong><p>{done:,} / {total:,} training games · {state['resumed']:,} resumed</p>
        <progress value="{done}" max="{total}" style="width:100%;height:24px" aria-label="Training games completed"></progress>
        {extra}<small>{timing}</small><h4>Monitoring win rate vs random play</h4>{learning_curve(state['evaluations'])}
        <small>Monitoring games use separate decks. Points are noisy measurements, not guaranteed improvement.</small></div>'''
        if self.handle is None: self.handle=display(HTML(html),display_id=True)
        else: self.handle.update(HTML(html))


def show_results(run):
    from IPython.display import HTML, display
    state=run['state']; final=state['final_tests'][str(state['completed'])]
    rows=[]
    for name,result in [('Fresh test vs random',final['versus_random']),('Fresh test vs initial model',final['versus_initial'])]:
        lo,hi=result['win_interval']
        rows.append(f'<tr><td>{name}</td><td>{result["wins"]} / {result["games"]}</td><td>{result["losses"]}</td><td>{result["draws"]}</td><td>{result["win_rate"]:.1%}</td><td>{lo:.0%}–{hi:.0%}</td></tr>')
    html='<h3>Separate test results</h3><table><thead><tr><th>Opponent</th><th>Wins / games</th><th>Losses</th><th>Draws</th><th>Win rate</th><th>95% conservative bounds</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>'
    html+='<p>Bounds account for initiative-swapped game pairs. They can be wide on small samples. These tests do not update or select the model.</p>'
    history=''.join(f'<tr><td>{e["trained_games"]:,}</td><td>{e["wins"]}/{e["games"]}</td><td>{e["win_rate"]:.1%}</td><td>{e["draws"]}</td></tr>' for e in state['evaluations'])
    html+='<h3>Monitoring history</h3><table><tr><th>Training games</th><th>Wins / games</th><th>Win rate</th><th>Draws</th></tr>'+history+'</table>'
    display(HTML(html))
    print(f"Saved {state['completed']:,} training games and learned model weights in:\n{run['directory']}")


def show_parameter_changes(run,limit=12):
    from .policy import FEATURE_NAMES
    initial=run['initial'].weights; trained=run['policy'].weights
    changes=sorted(zip(FEATURE_NAMES,initial,trained),key=lambda x:abs(x[2]-x[1]),reverse=True)
    print('Largest learned parameter changes (not a ranking of card strength):')
    for name,before,after in changes[:limit]: print(f'{name:48} {before:+.3f} → {after:+.3f}')
