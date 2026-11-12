const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1920}});
for(let i=1;i<=4;i++){await pg.goto(`file:///home/user/new/stories/s${i}.html`);await pg.waitForTimeout(600);await pg.screenshot({path:`story${i}.png`});}
await b.close();})();
