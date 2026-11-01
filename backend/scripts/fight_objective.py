import sys, duckdb
from collections import defaultdict
con = duckdb.connect(sys.argv[1], read_only=True)
P = {(m,p):(t,pos) for m,p,t,pos in con.execute("select match_id, participant_id, team_id, position from participants").fetchall()}
ev = defaultdict(list)
for m,ts,ty,v,mt,tid in con.execute("select match_id, ts_ms, type, victim_id, monster_type, team_id from events where type in ('CHAMPION_KILL','ELITE_MONSTER_KILL') order by match_id, ts_ms").fetchall():
    ev[m].append((ts,ty,v,mt,tid))
# near-objective fights: objective killed within [start-10s, end+60s]; who got first kill -> took objective?
fk=defaultdict(lambda:[0,0]); jg=defaultdict(lambda:[0,0]); jgall=[0,0]
for m,es in ev.items():
    ks=[e for e in es if e[1]=='CHAMPION_KILL' and e[2]]
    g=[];cur=[]
    for e in ks:
        if cur and e[0]-cur[-1][0]>20000: g.append(cur);cur=[]
        cur.append(e)
    if cur:g.append(cur)
    for f in g:
        if len(f)<3: continue
        first_victim=P.get((m,f[0][2]),(100,''))
        fkteam=300-first_victim[0]
        # fight result
        side=[300-P.get((m,e[2]),(100,''))[0] for e in f]
        c1=side.count(100); c2=len(side)-c1
        if c1!=c2:
            win=100 if c1>c2 else 200
            if first_victim[1]=='JUNGLE':
                jgall[0]+= (win!=first_victim[0]); jgall[1]+=1
        for e in es:
            if e[1]=='ELITE_MONSTER_KILL' and f[0][0]-10000<=e[0]<=f[-1][0]+60000 and e[3] in ('DRAGON','HORDE','RIFTHERALD','BARON_NASHOR'):
                fk[e[3]][0]+= e[4]==fkteam; fk[e[3]][1]+=1
                if first_victim[1]=='JUNGLE':
                    jg[e[3]][0]+= e[4]!=first_victim[0]; jg[e[3]][1]+=1
                break
for k,(w,n) in fk.items(): print(k,"first-kill team takes obj",round(w/n,3),n)
for k,(w,n) in jg.items(): print(k,"jungler died first -> enemy takes obj",round(w/n,3),n)
print("jungler died first -> his team loses fight",jgall[0]/jgall[1],jgall[1])
