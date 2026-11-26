// SEARCH: BFS, DFS, IDS (the 3 required-style algorithms) + Dijkstra used ONLY as a reference check
// ---- search algorithms: each returns {steps:[{n,fr,ex,note}], path} ----
function bfs(s,g){const st=[],q=[[s,[s]]],inF=new Set([s]),ex=new Set();
 while(q.length){const[n,p]=q.shift();inF.delete(n);ex.add(n);st.push({n,fr:q.map(x=>x[0]),ex:[...ex],note:"FIFO queue"});
  if(n===g)return{steps:st,path:p};
  for(const[m]of adj[n])if(!ex.has(m)&&!inF.has(m)){q.push([m,[...p,m]]);inF.add(m)}}
 return{steps:st,path:null}}
function dfs(s,g){const st=[],S=[[s,[s]]],ex=new Set();
 while(S.length){const[n,p]=S.pop();if(ex.has(n))continue;ex.add(n);
  st.push({n,fr:S.map(x=>x[0]).filter(x=>!ex.has(x)),ex:[...ex],note:"LIFO stack"});
  if(n===g)return{steps:st,path:p};
  for(const[m]of[...adj[n]].reverse())if(!ex.has(m))S.push([m,[...p,m]])}
 return{steps:st,path:null}}
function ids(s,g){const st=[];
 for(let L=0;L<=N.length;L++){const seen=[];
  const rec=(n,p,l)=>{seen.push(n);st.push({n,fr:p.slice(0,-1),ex:[...new Set(seen)],note:"depth limit "+L+" (frontier = current path)"});
   if(n===g)return p;if(l===0)return"cut";let c=false;
   for(const[m]of adj[n]){if(p.includes(m))continue;const r=rec(m,[...p,m],l-1);if(r==="cut")c=true;else if(r)return r}
   return c?"cut":null};
  const r=rec(s,[s],L);if(Array.isArray(r))return{steps:st,path:r};if(r===null)break}
 return{steps:st,path:null}}
const ALG={bfs,dfs,ids};
function dijkstra(s,g){const d={},pr={},done=new Set();N.forEach(n=>d[n]=Infinity);d[s]=0;
 while(true){let u=null;for(const n of N)if(!done.has(n)&&(u===null||d[n]<d[u]))u=n;if(u===null||d[u]===Infinity)break;done.add(u);
  for(const[v,c]of adj[u])if(d[u]+c<d[v]){d[v]=d[u]+c;pr[v]=u}}
 const p=[g];while(p[0]!==s)p.unshift(pr[p[0]]);return{cost:d[g],path:p}}

