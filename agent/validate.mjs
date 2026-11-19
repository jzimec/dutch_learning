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
const config=JSON.parse(fs.readFileSync('agent/runner-config.json','utf8'));
assert.equal(config.auto_merge,false);
assert.equal(config.auto_push,false);
assert.equal(config.mode,'supervised');
assert.ok(config.max_tasks_per_run>=1 && config.max_tasks_per_run<=3);
assert.ok(config.max_runtime_minutes>=1 && config.max_runtime_minutes<=60);
assert.ok(config.max_budget_usd>0 && config.max_budget_usd<=10);
assert.ok(config.protected_paths.includes('index.html'));
assert.ok(config.protected_paths.includes('.github/workflows/**'));
console.log('Agent queue, safety configuration and auth syntax: PASS');
