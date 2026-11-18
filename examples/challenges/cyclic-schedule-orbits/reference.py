from functools import lru_cache
from math import gcd
import json,time


def rooted_count(n):
    target=n//4
    total=0
    for first in (1,2,4):
        for second in (1,2,4):
            counts={1:n//2,2:n//4,4:n//4}
            counts[first]-=1;counts[second]-=1
            if min(counts.values())<0:continue
            @lru_cache(None)
            def dp(a,b,c,previous,last,aa,bc):
                if aa>target or bc>target:return 0
                if a+b+c==0:
                    if (previous,last,first)==(1,4,1) or (last,first,second)==(1,4,1):return 0
                    return int(aa+int(last==first==1)==target and bc+int({last,first}=={2,4})==target)
                result=0
                for value,left in ((1,a),(2,b),(4,c)):
                    if left==0 or (previous,last,value)==(1,4,1):continue
                    result+=dp(a-(value==1),b-(value==2),c-(value==4),last,value,
                               aa+int(last==value==1),bc+int({last,value}=={2,4}))
                return result
            total+=dp(counts[1],counts[2],counts[4],first,second,int(first==second==1),int({first,second}=={2,4}))
            dp.cache_clear()
    return total


def reflection_count(n,shift):
    unseen=set(range(n));cycles=[]
    while unseen:
        i=min(unseen);orbit=sorted({i,(shift-i)%n});cycles.append(orbit);unseen.difference_update(orbit)
    word=[None]*n
    def assign(index,a,b,c):
        if index==len(cycles):
            if a or b or c:return 0
            if sum(word[i]==word[(i+1)%n]==1 for i in range(n))!=n//4:return 0
            if sum({word[i],word[(i+1)%n]}=={2,4} for i in range(n))!=n//4:return 0
            if any((word[i],word[(i+1)%n],word[(i+2)%n])==(1,4,1) for i in range(n)):return 0
            return 1
        cycle=cycles[index];size=len(cycle);total=0
        for value,left in ((1,a),(2,b),(4,c)):
            if left<size:continue
            for j in cycle:word[j]=value
            total+=assign(index+1,a-size*(value==1),b-size*(value==2),c-size*(value==4))
            for j in cycle:word[j]=None
        return total
    return assign(0,n//2,n//4,n//4)


def solve(n):
    divisors=[d for d in range(1,n+1) if n%d==0 and (n//2)%d==0 and (n//4)%d==0]
    fixed={d:rooted_count(n//d) for d in divisors}
    reflections={d:(reflection_count(n//d,0),reflection_count(n//d,1)) for d in divisors}
    exact={};weighted={};profiles=[]
    for d in sorted(divisors,reverse=True):
        exact[d]=fixed[d]-sum(v for h,v in exact.items() if h%d==0)
        full_sum=d*(n//d//2)*sum(reflections[d])
        weighted[d]=full_sum-sum(v for h,v in weighted.items() if h%d==0)
        reflective=weighted[d]//d
        assert weighted[d]%d==0
        rotation_orbit_size=n//d
        assert reflective%rotation_orbit_size==0
        assert (exact[d]-reflective)%(2*rotation_orbit_size)==0
        profiles.extend([{'r':d,'f':0,'orbits':(exact[d]-reflective)//(2*rotation_orbit_size)},
                         {'r':d,'f':d,'orbits':reflective//rotation_orbit_size}])
    fixed_rotations=sum(fixed.get(n//gcd(n,s),0) for s in range(n))
    fixed_reflections=n//2*sum(reflections[1])
    total=(fixed_rotations+fixed_reflections)//(2*n)
    assert sum(p['orbits'] for p in profiles)==total
    return {'gap_length':n,'bit_length':3*n,'rooted_gap_sequences':fixed[1],
            'labelled_binary_schedules':3*fixed[1],'dihedral_orbits':total,
            'profiles':sorted(profiles,key=lambda x:(x['r'],x['f'])),
            'period_divisibility_counts':fixed,'reflection_class_counts':reflections,
            'rotation_fixed_sum':fixed_rotations,'reflection_fixed_sum':fixed_reflections,
            'exact_rotational_stabilizer_word_counts':exact}

if __name__=='__main__':
    import sys
    start=time.monotonic()
    result=solve(int(sys.argv[1]) if len(sys.argv)>1 else 24)
    result['seconds']=round(time.monotonic()-start,3)
    print(json.dumps(result,indent=2))
