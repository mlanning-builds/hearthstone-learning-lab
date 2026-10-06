"""Notebook-only presentation; no extra packages beyond Jupyter's IPython."""
from html import escape
import time


class Progress:
    def __init__(self):
        self.handle=None
        self.last_update=0

    def __call__(self, state):
        from IPython.display import HTML, display
        now=time.monotonic()
        done,total=state['completed'],state['total']
        if done not in (state['resumed'],total) and now-self.last_update<0.2 and state['status']=='running':
            return
        self.last_update=now
        new=done-state['resumed']; elapsed=state['elapsed']
        speed=new/elapsed if elapsed>0 else 0
        eta=(total-done)/speed if speed else None
        timing=f'{speed:.1f} games/sec · {elapsed:.1f}s elapsed'
        if eta is not None and done<total: timing+=f' · about {eta:.0f}s remaining'
        status={'complete':'Complete','running':'Playing random matches','interrupted':'Interrupted — progress saved','failed':'Stopped on an error — progress saved'}[state['status']]
        html=f'''<div style="padding:18px;border:1px solid #63758b;border-radius:10px;max-width:760px">
        <strong>{escape(status)}</strong><span style="float:right">{done} / {total} games</span>
        <progress value="{done}" max="{total}" style="width:100%;height:24px;margin:12px 0" aria-label="Completed games"></progress>
        <div>{timing}</div><small>{state['resumed']} games loaded from a previous run · random players · no learning yet</small></div>'''
        if self.handle is None: self.handle=display(HTML(html),display_id=True)
        else: self.handle.update(HTML(html))


def show_summary(experiment):
    from IPython.display import HTML, display
    s=experiment['summary']
    metrics=[('Games completed',s['games']),('First-player wins',s['first_player_wins']),
             ('Second-player wins',s['second_player_wins']),('Draws',s['draws']),
             ('Reached turn limit',s['turn_limit_games']),('Mean turns',s['mean_turns'])]
    rows=''.join(f'<tr><td style="padding:7px 24px 7px 0">{escape(k)}</td><td><b>{v}</b></td></tr>' for k,v in metrics)
    display(HTML('<h3>Random-play baseline</h3><table>'+rows+'</table><p>These are simulator checks, not trained-model results or a deck ranking.</p>'))
