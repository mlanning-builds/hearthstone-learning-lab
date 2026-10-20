"""Pinned Choose One forms, constructed before summon entry; unvalidated."""
FORMS={
 'AT_042':(('AT_042t','AT_042t2'),'OG_044c'),
 'BRM_010':(('BRM_010t','BRM_010t2'),'OG_044b'),
 'DED_001':(('DED_001at','DED_001bt'),'DED_001c'),
 'EX1_165':(('EX1_165t1','EX1_165t2'),'OG_044a'),
 'GIL_188':(('GIL_188t','GIL_188t2'),'GIL_188t3'),
 'ICC_051':(('ICC_051t','ICC_051t2'),'ICC_051t3'),
 'UNG_101':(('UNG_101t','UNG_101t2'),'UNG_101t3'),
 'TRL_343':(('TRL_343at2','TRL_343bt2','TRL_343ct2','TRL_343dt2'),'TRL_343et1'),
}
CHOICES={cid:[('Form '+str(i+1),'none',[]) for i,_ in enumerate(forms)] for cid,(forms,combined) in FORMS.items()}
RULES={cid:('none',[]) for cid in FORMS}
RULES['OG_044']=('none',[])
GENERATED_IDS=frozenset(RULES)
FIXED_TOKEN_IDS=frozenset(form for forms,combined in FORMS.values() for form in forms+(combined,))
TOKEN_RULES={cid:('none',[]) for cid in FIXED_TOKEN_IDS}
SPELL_DAMAGE_VALUES={'TRL_343ct2':1,'TRL_343et1':1}


def resolve(cid,choices):
 if cid not in FORMS:return cid
 forms,combined=FORMS[cid]
 return combined if choices==(-1,) else forms[choices[0]]
