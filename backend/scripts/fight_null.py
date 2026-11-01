import sys, duckdb
from collections import defaultdict
from math import comb
con = duckdb.connect(sys.argv[1], read_only=True)
teams = {(m,p):t for m,p,t in con.execute("select match_id, participant_id, team_id from participants").fetchall()}
ev = defaultdict(list)
for m,ts,v in con.execute("select match_id, ts_ms, victim_id from events where type='CHAMPION_KILL' and victim_id is not null and victim_id>0 order by match_id, ts_ms").fetchall():
    ev[m].append((ts,v))
def null_p(n):
    # first team has 1 kill; remaining n-1 kills coin flips; P(win | not tie)
    w=l=0
    for k in range(n):  # k additional kills for first team
        a=1+k; b=n-a; pr=comb(n-1,k)
        if a>b: w+=pr
        elif a<b: l+=pr
    return w/(w+l) if w+l else 0
obs=defaultdict(lambda:[0,0]); rest=[0,0]; rest_by=defaultdict(lambda:[0,0]); second=[0,0]
for m,ks in ev.items():
    g=[];cur=[]
    for e in ks:
        if cur and e[0]-cur[-1][0]>20000: g.append(cur);cur=[]
        cur.append(e)
    if cur:g.append(cur)
    for f in g:
        if len(f)<3: continue
        side=[300-teams.get((m,e[1]),100) for e in f]
        c100=side.count(100); c200=len(side)-c100
        if c100==c200: continue
        win=100 if c100>c200 else 200
        n=len(f)
        obs[n][0]+= side[0]==win; obs[n][1]+=1
        r=sum(1 for s in side[1:] if s==side[0]); rest[0]+=r; rest[1]+=n-1
        b=min(n,6); rest_by[b][0]+=r; rest_by[b][1]+=n-1
        second[0]+= side[1]==side[0]; second[1]+=1
tot_o=sum(v[0] for v in obs.values()); tot_n=sum(v[1] for v in obs.values())
exp=sum(null_p(n)*v[1] for n,v in obs.items())
print("fights",tot_n,"obs",tot_o/tot_n,"null expected",exp/tot_n)
for b in range(3,7):
    ns=[n for n in obs if (n==b if b<6 else n>=6)]
    o=sum(obs[n][0] for n in ns); t=sum(obs[n][1] for n in ns); e=sum(null_p(n)*obs[n][1] for n in ns)
    print(b,t,round(o/t,3),"null",round(e/t,3),"rest-kills share",round(rest_by[b][0]/rest_by[b][1],3))
print("share of later kills by first-kill team",rest[0]/rest[1], "n",rest[1])
print("second kill same team",second[0]/second[1])
