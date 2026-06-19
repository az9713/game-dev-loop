// Dev-only: extract the engine block from an HTML file and run its self-play harness.
// Usage: node .realm_runtest.cjs <html> [seeds] [turns]
const fs=require("fs"), path=require("path"), os=require("os");
const html=fs.readFileSync(process.argv[2],"utf8");
const a=html.indexOf("// ENGINE-START"), b=html.indexOf("// ENGINE-END");
if(a<0||b<0){ console.error("engine markers not found"); process.exit(2); }
const code=html.slice(a,b);
const tmp=path.join(os.tmpdir(),"realm_engine_extract.cjs");
fs.writeFileSync(tmp,code);
const m=require(tmp);
(async()=>{
  const r=await m.runHarness(parseInt(process.argv[3]||"200",10), parseInt(process.argv[4]||"40",10));
  console.log(r.summary);
  process.exit(r.ok?0:1);
})();
