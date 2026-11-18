from itertools import combinations
from collections import Counter
import json,time
n=16
raw=0
canon=set()
profiles=Counter()
rotation_fixed=[0]*n
reflection_fixed=[0]*n
start=time.monotonic()
for ones in combinations(range(n),8):
    occupied=set(ones)
    if sum((i+1)%n in occupied for i in ones)!=4: continue
    remaining=[i for i in range(n) if i not in occupied]
    for twos in combinations(remaining,4):
        two=set(twos)
        g=tuple(1 if i in occupied else 2 if i in two else 4 for i in range(n))
        if sum((g[i],g[(i+1)%n]) in ((2,4),(4,2)) for i in range(n)) != 4: continue
        if any((g[i],g[(i+1)%n],g[(i+2)%n]) == (1,4,1) for i in range(n)): continue
        raw+=1
        rots=[g[s:]+g[:s] for s in range(n)]
        rev=g[::-1]
        refs=[rev[s:]+rev[:s] for s in range(n)]
        for i,t in enumerate(rots): rotation_fixed[i]+=t==g
        for i,t in enumerate(refs): reflection_fixed[i]+=t==g
        c=min(rots+refs)
        if c not in canon:
            canon.add(c)
            r=sum(t==g for t in rots)
            f=sum(t==g for t in refs)
            profiles[(r,f)]+=1
out={'rooted_gap_sequences':raw,'dihedral_orbits':len(canon),'profiles':[{'rotation_stabilizer':r,'reflection_stabilizer':f,'orbits':c} for (r,f),c in sorted(profiles.items())], 'rotation_fixed_counts':rotation_fixed,'reflection_fixed_counts':reflection_fixed,'burnside_orbits':sum(rotation_fixed+reflection_fixed)//32,'seconds':round(time.monotonic()-start,3)}
print(json.dumps(out,indent=2))
