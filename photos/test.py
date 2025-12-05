import sys
import math
def func():
    data = sys.stdin.read().strip().split()
    
    it = iter(data)
    n = int(next(it))
    k = int(next(it))
    k = min(k,n)
    pts = [(float(next(it)),float(next(it))) for _ in range(n)]
    
    # k-means
    centers = [list(pts[i]) for i in range(k)]
    
    assign = [0] * n
    for _ in range(100):
        for i,(x,y) in enumerate(pts):
            best_c, best_d = 0, float('inf')
            for c in range(k):
                cx, cy = centers[c]
                d = (x - cx) * (x - cx) + (y - cy) * (y - cy)
                if d < best_d:
                    best_d, best_c = d, c
            assign[i] = best_c
                
        
        sums = [[0.0,0.0,0] for _ in range(k)]
        for (x,y) , c in zip(pts, assign):
            s = sums[c]
            s[0] += x 
            s[1] += y 
            s[2] += 1 
        new_centers = [centers[c][:] for c in range(k)]
        for c in range(k):
            cnt = sums[c][2]
            if cnt > 0:
                new_centers[c][0] == sums[c][0] / cnt
                new_centers[c][1] == sums[c][1] / cnt
        max_shift = 0.0
        for c in range(k):
            dx = new_centers[c][0] - centers[c][0]
            dy = new_centers[c][1] - centers[c][1]
            max_shift = max(max_shift, math.hypot(dx,dy))
        centers = new_centers
        
        if max_shift <= 1e-6:
                break
    
    clusters = [[] for _ in range(k)]
    for i, c in enumerate(assign):
        clusters[c].append(i)
        
    dist = [[0.0]*n for _ in range(n)]
    for i in range(n):
        x1, y1 = pts[i]
        for j in range(i+1, n):
            x2, y2 = pts[j]
            d = math.hypot(x1-x2, y1-y2)
            dist[i][j] = dist[j][i] = d
    
    s_cluster = [0.0] * k 
    for c in range(k):
        idxs = clusters[c]
        m = len(idxs)
        if m <= 1:
            s_cluster[c] =0.0
            continue
        s_sum = 0.0
        for i in idxs:
            a_i = sum(dist[i][j] for j in idxs if j!=i)/(m-1)
            b_i = min((sum(dist[i][j] for j in clusters[t]) / len(clusters[t])
                     for t in range(k) if t!=c and len(clusters[t]) > 0),default=0.0
                     )
            denom = max(a_i,b_i)
            s_sum += 0.0 if denom == 0.0 else (b_i - a_i) /denom
        s_cluster[c] = s_sum/m
        
    worst = min(range(k), key = lambda c: s_cluster[c])
    
    cx, cy = centers[worst]
    print(f"{cx:.2f}，{cy:.2f}")
    # please define the python3 input here. For example: a,b = map(int, input().strip().split())
    # please finish the function body here.
    # please define the python3 output here. For example: print().

if __name__ == "__main__":
    func()