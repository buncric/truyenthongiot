const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
function visit(dir){for(const item of fs.readdirSync(dir,{withFileTypes:true})){if(['node_modules','.git','luu-tru','project-goc'].includes(item.name))continue;const p=path.join(dir,item.name);if(item.isDirectory())visit(p);else if(/\.(cjs|js)$/.test(p)){const r=spawnSync(process.execPath,['--check',p],{encoding:'utf8'});if(r.status!==0){console.error(r.stderr);process.exitCode=1;}}}}
visit(process.cwd());
