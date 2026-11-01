import sys, duckdb
from collections import defaultdict
con = duckdb.connect(sys.argv[1], read_only=True)
teams = {(m,p):t for m,p,t in con.execute("select match_id, participant_id, team_id from participants").fetchall()}
ev = defaultdict(list)
for m,ts,v in con.execute("select match_id, ts_ms, victim_id from events where type='CHAMPION_KILL' and victim_id is not null and victim_id>0 order by match_id, ts_ms").fetchall():
    ev[m].append((ts,v))
allf=0; rest=[0,0]; sec=[0,0]; restmore=[0,0,0]; ties=0
for m,ks in ev.items():
    g=[];cur=[]
    for e in ks:
        if cur and e[0]-cur[-1][0]>20000: g.append(cur);cur=[]
        cur.append(e)
    if cur:g.append(cur)
    for f in g:
        if len(f)<3: continue
        allf+=1
        side=[300-teams.get((m,e[1]),100) for e in f]
        if side.count(100)*2==len(side): ties+=1
        r=sum(1 for s in side[1:] if s==side[0]); o=len(side)-1-r
        rest[0]+=r; rest[1]+=len(side)-1
        sec[0]+=side[1]==side[0]; sec[1]+=1
        restmore[0 if r>o else 1 if r<o else 2]+=1
print("all fights incl ties",allf,"ties",ties, ties/allf)
print("later kills share first team (no tie filter)",rest[0]/rest[1])
print("second kill same team",sec[0]/sec[1])
print("remaining kills: first team more / fewer / equal", [x/allf for x in restmore])
