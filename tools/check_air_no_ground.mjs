#!/usr/bin/env node
// Compatibility entry point: verify each fighter's actual clean flight cells.
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const result=spawnSync('python3',['tools/check_ninja_jumps.py','--static'],{cwd:root,stdio:'inherit'});
if(result.error)throw result.error;
process.exit(result.status??1);
