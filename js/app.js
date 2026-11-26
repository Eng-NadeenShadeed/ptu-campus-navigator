// UI: map drawing, controls, step-by-step animation, comparison table, Arabic/English switch

Object.assign(NAME,{J_South:["South Junction","التقاطع الجنوبي"],J_NE:["North-East Junction","التقاطع الشمالي الشرقي"],J_Mid:["Central Junction","التقاطع الأوسط"],J_West:["West Junction","التقاطع الغربي"],J_East:["East Junction","التقاطع الشرقي"],J_SE:["South-East Junction","التقاطع الجنوبي الشرقي"]});
let lang="ar",ALGO="bfs",R=null,idx=-1,timer=null,nextPick="s";
const L=(a,e)=>lang==="ar"?a:e,D=n=>NAME[n][lang==="ar"?1:0],$=id=>document.getElementById(id),NS="http://www.w3.org/2000/svg",Y0=195,VH=690;
const mk=(t,a,x)=>{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(x!=null)e.textContent=x;return e};
const PL=N.filter(n=>!/^J_/.test(n)),sel={s:$("s"),g:$("gsel")};
const ICO={Mosque:"🕌",Stadium:"⚽",Bank:"🏦",Cafeteria:"☕",Parking_East:"P",Parking_Student:"P",South_Gate:"🚪",Main_Gate:"🚪"};
const ADESC={bfs:["يفحص الأقرب أولاً باستخدام طابور. يجد المسار بأقل عدد من الخطوات.","Expands the shallowest place first using a queue. It finds the route with the fewest moves."],dfs:["يتعمق في طريق واحد قدر الإمكان ثم يتراجع باستخدام مكدّس. سريع البداية لكن المسار قد يطول.","Follows one road as deep as it can, then backs up, using a stack. Quick to start, but the route can be long."],ids:["يكرّر بحثاً محدود العمق بحدود 0، 1، 2، … فيجمع ذاكرة DFS الصغيرة ونتيجة BFS بأقل خطوات.","Repeats depth-limited searches with limits 0, 1, 2, … keeping DFS’s small memory and BFS’s fewest-moves result."]};
const TRIPS=[["South_Gate","G_Library"],["Main_Gate","D_Registration"],["Parking_Student","Stadium"],["Mosque","S_Culture"],["B_OldEng","Parking_East"],["F_ContEd","Cafeteria"]];
$("nn").textContent=$("nn2").textContent=N.length;$("ne").textContent=$("ne2").textContent=E.length;
// map layers
const svg=$("map"),gE=mk("g",{id:"edges"}),gP=mk("g"),gN=mk("g"),nEl={};svg.append(gE,gP,gN);
E.forEach(([a,b,c])=>{const[x1,y1]=P[a],[x2,y2]=P[b];gE.append(mk("line",{x1,y1,x2,y2,class:"edge"}),mk("text",{x:(x1+x2)/2,y:(y1+y2)/2+3,class:"cost"},c))});
N.forEach(n=>{const[x,y]=P[n],g=mk("g",{class:"node",transform:`translate(${x} ${y})`,tabindex:0,role:"button"}),t=LET[n]||ICO[n];
 g.append(mk("circle",{r:18,class:"ring"}));
 if(t)g.append(mk("rect",{x:-17,y:-17,width:34,height:34,rx:10,class:"box"}),mk("text",{class:LET[n]?"let":"ico",y:6},t));else g.append(mk("circle",{r:7,class:"dot"}));
 g.onmouseenter=g.onfocus=()=>tip(n);g.onmouseleave=g.onblur=()=>$("tip").hidden=true;g.onclick=()=>pick(n);
 g.onkeydown=e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();pick(n)}};gN.append(g);nEl[n]=g});
function tip(n){const t=$("tip");t.hidden=false;t.style.left=P[n][0]/776*100+"%";t.style.top=(P[n][1]-Y0)/VH*100+"%";t.innerHTML=`<b>${NAME[n][0]}</b><span dir="rtl">${NAME[n][1]}</span>`}
const val=k=>sel[k].value;
function fill(){["s","g"].forEach(k=>{const v=sel[k].value;sel[k].replaceChildren();PL.slice().sort((a,b)=>D(a).localeCompare(D(b),lang)).forEach(n=>sel[k].add(new Option((LET[n]?LET[n]+" · ":"")+D(n),n)));sel[k].value=v||(k==="s"?"South_Gate":"G_Library")})}
function lists(){$("dir").replaceChildren();["A_Main","B_OldEng","C_Sports","D_Registration","E_Sciences","F_ContEd","G_Library","H_NewEng","L_Graduate","S_Culture","Mosque","Stadium","Bank","Cafeteria"].forEach(n=>{const b=document.createElement("button");b.innerHTML=`<b>${LET[n]||ICO[n]}</b><span>${D(n)}</span><small>${NAME[n][lang==="ar"?0:1]}</small>`;b.onmouseenter=()=>nEl[n].classList.add("hl");b.onmouseleave=()=>nEl[n].classList.remove("hl");b.onclick=()=>{pick(n);$("navigator").scrollIntoView()};$("dir").append(b)});
 $("quick").replaceChildren();TRIPS.forEach(([a,b])=>{const q=document.createElement("button");q.textContent=D(a)+(lang==="ar"?" ← ":" → ")+D(b);q.onclick=()=>{sel.s.value=a;sel.g.value=b;refresh()};$("quick").append(q)})}
function pick(n){if(nextPick==="s"){sel.s.value=n;nextPick="g"}else{sel.g.value=n;nextPick="s"}refresh()}
function hint(){$("hint").textContent=nextPick==="s"?L("اضغط على مبنى لتعيين البداية.","Tap a building to set the start."):L("البداية: "+D(val("s"))+". اضغط الآن على الوجهة.","Start: "+D(val("s"))+". Now tap your destination.")}
document.querySelectorAll("#alg button").forEach(b=>b.onclick=()=>{ALGO=b.dataset.a;document.querySelectorAll("#alg button").forEach(x=>x.setAttribute("aria-pressed",x===b));reset()});
const chips=(el,a,c)=>$(el).replaceChildren(...a.map(x=>Object.assign(document.createElement("span"),{textContent:D(x),className:c||""})));
function paint(){const stp=idx>=0?R.steps[idx]:null,s=val("s"),g=val("g"),fin=R&&idx===R.steps.length-1;
 N.forEach(n=>{const c=nEl[n].classList;c.toggle("ex",!!stp&&stp.ex.includes(n));c.toggle("fr",!!stp&&stp.fr.includes(n));c.toggle("cur",!!stp&&stp.n===n);c.toggle("s",n===s);c.toggle("g",n===g);nEl[n].setAttribute("aria-label",D(n))});
 svg.classList.toggle("edges",$("ed").checked||!!R);gP.replaceChildren();
 if(fin&&R.path)R.path.forEach((n,i)=>{if(!i)return;const a=P[R.path[i-1]],b=P[n],c=adj[R.path[i-1]].find(y=>y[0]===n)[1];gP.append(mk("line",{x1:a[0],y1:a[1],x2:b[0],y2:b[1],class:"pc"}),mk("line",{x1:a[0],y1:a[1],x2:b[0],y2:b[1],class:"pl"}),mk("text",{x:(a[0]+b[0])/2,y:(a[1]+b[1])/2-8,class:"pt"},c))});
 $("ad").textContent=ADESC[ALGO][lang==="ar"?0:1];$("run").textContent=timer?L("إيقاف مؤقت","Pause"):L("شغّل البحث","Run search");$("stp").textContent=L("الخطوة التالية","Next step");$("rs").textContent=L("إعادة","Reset");
 if(stp){$("i1").textContent=L(`الخطوة ${idx+1} من ${R.steps.length} · في الانتظار:`,`Step ${idx+1} of ${R.steps.length} · Frontier:`);chips("fr",stp.fr);chips("ex",stp.ex,"n")}else{$("i1").textContent=L("في الانتظار:","Frontier:");chips("fr",[]);chips("ex",[])}
 const ar=lang==="ar";$("res").replaceChildren();
 if(fin&&R.path){const p=R.path,m=cost(p);$("m2").textContent=m;$("m3").textContent=R.steps.length;$("m4").textContent=Math.ceil(m/80);
  p.forEach((n,i)=>{if(!i)return;const li=document.createElement("li"),c=adj[p[i-1]].find(y=>y[0]===n)[1];li.innerHTML=`<span>${D(p[i-1])} ${ar?"←":"→"} ${D(n)}</span><b>${c} ${L("م","m")}</b>`;$("res").append(li)})}
 else{["m2","m3","m4"].forEach(i=>$(i).textContent="–");if(!stp){const li=document.createElement("li");li.textContent=L("اختر البداية والوجهة ثم شغّل البحث.","Choose a start and goal, then run the search.");$("res").append(li)}}
 hint();liveMsg(stp,fin)}
function liveMsg(stp,fin){const lv=$("live"),n=R?R.steps.length:0;
 lv.textContent=fin?(R.path?L("انتهى البحث: وُجد المسار بـ "+(R.path.length-1)+" انتقالات. اضغط «إعادة» للبدء من جديد.","Search finished: route found in "+(R.path.length-1)+" moves. Press Reset to start over."):L("انتهى البحث: لا يوجد مسار.","Search finished: no route.")):stp?L("يفحص الآن: "+D(stp.n)+" ("+(idx+1)+"/"+n+")","Expanding now: "+D(stp.n)+" ("+(idx+1)+"/"+n+")"):L("جاهز. اضغط «الخطوة التالية» أو «شغّل البحث».","Ready. Press “Next step” or “Run search”.");
 lv.classList.remove("f");void lv.offsetWidth;lv.classList.add("f")}
function reset(){clearInterval(timer);timer=null;R=null;idx=-1;paint()}
function step(){if(!R){R=ALG[ALGO](val("s"),val("g"));idx=-1}if(idx<R.steps.length-1){idx++;paint();return true}clearInterval(timer);timer=null;paint();return false}
$("stp").onclick=step;$("rs").onclick=reset;$("ed").onchange=paint;
$("run").onclick=()=>{if(timer){clearInterval(timer);timer=null;paint();return}if(R&&idx===R.steps.length-1)reset();timer=setInterval(step,1100-$("sp").value*100);paint()};
$("sw").onclick=()=>{const t=val("s");sel.s.value=val("g");sel.g.value=t;refresh()};
["s","g"].forEach(k=>sel[k].onchange=refresh);
function table(){const s=val("s"),g=val("g"),ref=dijkstra(s,g);let h=`<tr><th>${L("الخوارزمية","Algorithm")}</th><th>${L("الانتقالات","Moves")}</th><th>${L("الأمتار","Metres")}</th><th>${L("حالات فُحصت","Expanded")}</th><th>${L("الأقصر؟","Cheapest?")}</th></tr>`;
 for(const k of["bfs","dfs","ids"]){const r=ALG[k](s,g),c=cost(r.path),y=c===ref.cost;h+=`<tr><td><b>${k.toUpperCase()}</b></td><td>${r.path.length-1}</td><td>${c}</td><td>${r.steps.length}</td><td class="${y?"ok":"no"}">${y?L("نعم","yes"):L("لا","no")}</td></tr>`}
 h+=`<tr><td colspan="5" class="note">${L("أقصر مسار مرجعي","Reference cheapest route")}: ${ref.cost} ${L("م","m")} — ${ref.path.map(D).join(lang==="ar"?" ← ":" → ")}</td></tr>`;$("cmp").innerHTML=h}
function refresh(){reset();table()}
function setLang(l){lang=l;const h=document.documentElement;h.lang=l;h.dir=l==="ar"?"rtl":"ltr";$("lg").textContent=l==="ar"?"EN":"عربي";fill();lists();refresh()}
$("lg").onclick=()=>setLang(lang==="ar"?"en":"ar");
setLang("ar");
