// SPDX-License-Identifier: CC-BY-SA-4.0
// Renders the studio's blank-template starter for the default name MyApp.
// Usage: node render_starter.js <website>/assets/js/builder.js <out-dir>
const fs=require('fs');const src=fs.readFileSync(process.argv[2],'utf8');
const a=src.indexOf('function generateBlankTemplate(appName) {');const b=src.indexOf('setHCode(hCode);',a);
const body=src.slice(a,b)+'return {h:hCode,cpp:cppCode};}';
const f=new Function(body+'\nreturn generateBlankTemplate;')();const r=f('MyApp');
fs.writeFileSync(process.argv[3]+'/MyApp.h',r.h);fs.writeFileSync(process.argv[3]+'/MyApp.cpp',r.cpp);
