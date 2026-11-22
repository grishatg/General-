const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});const p=await b.newPage({viewport:{width:1000,height:1300}});
for (const n of ['v7']) for (const [s,v] of [['closed','front'],['open','open'],['closed','back'],['closed','base']]){
 await p.goto(`http://127.0.0.1:${process.env.PORT||8770}/view.html?f=${n}_${s}&v=${v}`); await p.waitForFunction(()=>document.title==='done',null,{timeout:120000});
 await p.screenshot({path:`${process.argv[2]}/${n}_${v}.png`});}
await b.close();})();
