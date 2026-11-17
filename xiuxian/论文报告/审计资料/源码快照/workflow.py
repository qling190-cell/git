"""Video 2026-10-26: fixed realms, ordered tasks, shared parent pages."""
WORKFLOW_VERSION=5
TRIBUTE_NAMES=('落日城','战争之门','斗技场','传承之地','不灭城')
PALACE_TASKS=('palace_lamp','palace_cultivate','palace_court','palace_garden')
DAILY_GROUPS=[
    ('mortal','人间',['travel','sect_deadland','sect_herbs','practice','sect_exchange','freegift','signin','fishing_mortal']),
    ('heaven','仙界',['guard','quiz','gamble','jade','lecture','forbidden','duel','tower','treasure','hunt','demon','smallworld','sword','transfer']),
    ('void','虚空',['battle_exchange','night','familycare','family','observatory','stars','star_forbidden','raid','provisions','gifts','pond']),
    ('yuanji','元极',list(PALACE_TASKS)),
]
FINISH_GROUPS=[
    ('mortal','人间',['travel','sect_deadland','sect_herbs']),
    ('heaven','仙界',['forbidden','treasure','hunt','smallworld']),
    ('void','虚空',['night','family']),
    ('yuanji','元极',['palace_cultivate','palace_court']),
]
PARENTS={
    'travel':'mortal_nav','mortal_sect':'mortal_nav',
    'practice':'mortal_sect','sect_deadland':'mortal_sect','sect_herbs':'mortal_sect','sect_exchange':'mortal_sect',
    'island':'heaven_nav','teaching':'island','market':'island','hall':'island','forbidden':'island',
    'market_shop':'market','gamble':'market','heaven_arena':'heaven_nav','sword':'heaven_nav',
    'heaven_travel':'heaven_nav','tower':'heaven_travel','secrets':'heaven_travel','smallworld':'heaven_travel',
    'immortal_home':'void_nav','ancestral':'immortal_home','family':'immortal_home',
    'food_shop':'immortal_home','diplomacy':'immortal_home','journey':'void_nav','battle_exchange':'journey',
    'stars':'void_nav','observatory':'stars','star_orbit':'stars',
    'palace_map':'yuanji_nav',
}
TASK_ENTRY={
    'travel':'travel','sect_deadland':'mortal_sect','sect_herbs':'mortal_sect','practice':'mortal_sect',
    'sect_exchange':'mortal_sect','freegift':'mortal_nav','signin':'mortal_nav','fishing_mortal':'travel',
    'guard':'teaching','quiz':'teaching','transfer':'teaching','gamble':'market','jade':'market',
    'lecture':'hall','forbidden':'forbidden','duel':'heaven_arena','sword':'heaven_nav',
    'tower':'heaven_travel','treasure':'secrets','hunt':'secrets','demon':'secrets','smallworld':'heaven_travel',
    'battle_exchange':'journey','night':'journey','familycare':'immortal_home','family':'immortal_home',
    'raid':'immortal_home','provisions':'immortal_home','gifts':'immortal_home','pond':'immortal_home',
    'observatory':'stars','stars':'stars','star_orbit':'stars','star_forbidden':'stars',
    'palace_lamp':'palace_map','palace_garden':'palace_map','palace_cultivate':'palace_map','palace_court':'palace_map',
}

def shared_parent(task,following):
    if task not in TASK_ENTRY or following not in TASK_ENTRY:return None
    first=[];page=TASK_ENTRY[task]
    while page:
        first.append(page);page=PARENTS.get(page)
    page=TASK_ENTRY[following]
    while page:
        if page in first:return None if page.endswith('_nav') else page
        page=PARENTS.get(page)
    return None
