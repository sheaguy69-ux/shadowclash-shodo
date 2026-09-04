import json,sys,pathlib
name=sys.argv[1]; pick=int(sys.argv[2])
hook=("const _o=spriteFrameIndex; globalThis.__AL={}; "
      "spriteFrameIndex=function(p,F){const i=_o(p,F); "
      "if(p===player1&&!p.isGrounded&&typeof i==='number'){const k=p.state+'#'+i; __AL[k]=(__AL[k]||0)+1;} return i;}; return 'hooked'")
air=[]
# neutral jump, and jump + each attack at two heights
for atk in [None,'KeyF','KeyJ','KeyG','KeyH']:
    for delay in [0.18,0.45]:
        air.append({"key":"KeyW","hold":0.08})
        if atk: air.append({"wait":delay}); air.append({"key":atk,"hold":0.06})
        air.append({"wait":1.1})
# directional air attacks
for d in ['KeyD','KeyA','KeyS']:
    for atk in ['KeyF','KeyG','KeyH']:
        air.append({"key":"KeyW","hold":0.08})
        air.append({"wait":0.22})
        air.append({"down":d}); air.append({"key":atk,"hold":0.06}); air.append({"wait":0.5}); air.append({"up":d})
        air.append({"wait":0.9})
# forward/back jumps (jumpDir), and a wall jump attempt
for d in ['KeyD','KeyA']:
    air.append({"down":d}); air.append({"key":"KeyW","hold":0.08}); air.append({"wait":1.2}); air.append({"up":d})
air.append({"down":"KeyA"}); air.append({"wait":1.4}); air.append({"key":"KeyW","hold":0.08}); air.append({"wait":0.4})
air.append({"key":"KeyW","hold":0.08}); air.append({"wait":1.2}); air.append({"up":"KeyA"})
# take a hit in the air: park p2 close and let it swing
air.append({"eval":"player2.x=player1.x+70; cpuMode=true; return 'cpu'"})
for _ in range(6):
    air.append({"key":"KeyW","hold":0.08}); air.append({"wait":1.3})
steps=[{"wait":1.2},{"key":"Space"},{"wait":0.6},
 {"eval":f"gameMode='training'; cpuMode=false; p1Pick={pick}; p2Pick=5; stagePick='bamboo'; attractMode=false; startNewGame(); return 'boot'"},
 {"wait":3.2},
 {"eval":"moveListOpen=false; player1.x=420; player2.x=760; player1.hp=9999; player2.hp=9999; return player1.spec.name"},
 {"eval":hook}] + air + [
 {"eval":"const m=SPRITES[player1.spec.name.toLowerCase()].frames; const rev={}; for(const k in m){(rev[m[k]]=rev[m[k]]||[]).push(k);} const o={}; for(const k in __AL){const [s,i]=k.split('#'); o[k]={n:__AL[k],names:(rev[+i]||[]).join(',')};} return JSON.stringify({f:player1.spec.name,hits:o});","label":"AIRLOG"}]
pathlib.Path(f'/tmp/air_{name}.json').write_text(json.dumps(steps))
print(len(steps))
