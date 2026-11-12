const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1200,height:1260},deviceScaleFactor:1.5});
pg.on('pageerror',e=>console.log('ERR',e.message));
await pg.goto('file:///home/user/new/stories/render.html');await pg.waitForTimeout(800);await pg.screenshot({path:'render.png'});await b.close();})();
