import fs from 'node:fs';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
const tasks=JSON.parse(fs.readFileSync('agent/tasks.json','utf8'));
assert.equal(tasks.project,'Dutch Learning');
assert.equal(tasks.policy.auto_merge,false);
assert.ok(tasks.tasks.length>0);
const ids=new Set();
for(const t of tasks.tasks){
 assert.ok(t.id&&t.title&&Array.isArray(t.acceptance)&&t.acceptance.length);
 assert.ok(['todo','in_progress','blocked','done','unverified'].includes(t.status));
 assert.ok(!ids.has(t.id),'duplicate task '+t.id);ids.add(t.id);
}
for(const path of ['dutch-auth.js']){
 execFileSync('node',['--check',path],{stdio:'inherit'});
}
console.log('Agent task schema and auth JavaScript syntax: PASS');
