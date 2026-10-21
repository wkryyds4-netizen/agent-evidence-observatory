import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const sha = x => crypto.createHash('sha256').update(x).digest('hex');
const decode = (s, n) => {
  if (typeof s !== 'string' || !/^[A-Za-z0-9_-]+$/.test(s)) throw Error('encoding');
  const b = Buffer.from(s, 'base64url');
  if (b.length !== n || b.toString('base64url') !== s) throw Error('length/canonical encoding');
  return b;
};
function verifyRow(row) {
  const digest = typeof row.text === 'string' ? sha(Buffer.from(row.text,'utf8')) : null;
  const out = {
    text_hash_matches: digest !== null && digest === row.sha256,
    signature_status: 'unsigned',
    fingerprint_matches: null,
    signed_core_fields_match: null,
    signed_text_room_key_match: null,
    core_binding_differences: [],
  };
  if (!row.public_key && !row.signature && !row.signed_payload) return out;
  try {
    const pub=decode(row.public_key,32), sig=decode(row.signature,64);
    if (typeof row.signed_payload !== 'string') throw Error('payload');
    const key=crypto.createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),pub]),format:'der',type:'spki'});
    out.signature_status=crypto.verify(null,Buffer.from(row.signed_payload,'utf8'),key,sig)?'valid':'invalid';
    out.fingerprint_matches=sha(pub)===row.author;
    const payload=JSON.parse(row.signed_payload);
    const cmd=payload.command;
    out.signed_core_fields_match=!!cmd && ['text','room','page','kind','public_key'].every(k=>cmd[k]===row[k]);
    out.signed_text_room_key_match=!!cmd && ['text','room','public_key'].every(k=>cmd[k]===row[k]);
    out.core_binding_differences=cmd?['text','room','page','kind','public_key'].filter(k=>cmd[k]!==row[k]):['command_missing'];
  } catch {
    out.signature_status='unverifiable_under_checked_format';
  }
  return out;
}
function selfTest(){
  const {publicKey,privateKey}=crypto.generateKeyPairSync('ed25519');
  const pub=publicKey.export({format:'der',type:'spki'}).subarray(-32);
  const row={text:'fixture',room:'r',page:'p',kind:'note',public_key:pub.toString('base64url')};
  row.author=sha(pub);
  row.signed_payload=JSON.stringify({version:1,service:'fixture-only',command:{...row}});
  row.signature=crypto.sign(null,Buffer.from(row.signed_payload),privateKey).toString('base64url');
  row.sha256=sha(Buffer.from(row.text));
  const good=verifyRow(row);
  const tampered=verifyRow({...row,text:'changed'});
  const alteredSig=Buffer.from(decode(row.signature,64));alteredSig[0]^=1;
  const bad=verifyRow({...row,signature:alteredSig.toString('base64url')});
  const passed=good.signature_status==='valid' && good.fingerprint_matches && good.text_hash_matches && good.signed_core_fields_match &&
    tampered.signature_status==='valid' && !tampered.text_hash_matches && !tampered.signed_core_fields_match && bad.signature_status==='invalid';
  if(!passed)throw Error('signature verifier self-test failed');
  return {passed,checks:['valid Ed25519','changed archive text breaks hash/core binding','changed signature rejected'],external_identity_created:false};
}
const args=process.argv.slice(2);
if(args.length===1 && args[0]==='--self-test') {
  console.log(JSON.stringify(selfTest(),null,2));
  process.exit(0);
}
if(args.length!==4 || args[0]!=='--input' || args[2]!=='--out') {
  console.error('Usage: node code/verify_public_partition.mjs --input INPUT.jsonl --out OUTPUT.json\n       node code/verify_public_partition.mjs --self-test');
  process.exit(2);
}
const input=path.resolve(args[1]);
if(fs.statSync(input).size>16*1024*1024) throw Error('Partition exceeds reviewed 16 MiB bound');
const raw=fs.readFileSync(input);
const rows=raw.toString('utf8').trim().split(/\r?\n/).map(JSON.parse);
const eligible=rows.filter(r=>['event','message'].includes(r.type)&&!r.hidden&&r.visibility==='public'&&r.archive_eligible===true);
const records=eligible.map((row,i)=>({line_index:rows.indexOf(row)+1,archive_id:row.id,kind:row.kind,created_at:row.created_at,...verifyRow(row)}));
const status=Object.fromEntries([...new Set(records.map(r=>r.signature_status))].map(k=>[k,records.filter(r=>r.signature_status===k).length]));
const result={
  verifier:'Node.js built-in crypto.verify Ed25519 over exact supplied signed_payload bytes; no network',
  self_test:selfTest(),input_sha256:sha(raw),row_count:rows.length,eligible_message_count:eligible.length,
  imported_count:eligible.filter(r=>r.kind==='imported').length,
  signature_status_counts:status,
  text_hash_matches:records.filter(r=>r.text_hash_matches).length,
  fingerprint_matches:records.filter(r=>r.fingerprint_matches===true).length,
  signed_core_fields_match:records.filter(r=>r.signed_core_fields_match===true).length,
  signed_text_room_key_match:records.filter(r=>r.signed_text_room_key_match===true).length,
  core_binding_difference_counts:Object.fromEntries(['text','room','page','kind','public_key','command_missing'].map(k=>[k,records.filter(r=>r.core_binding_differences.includes(k)).length])),
  records,
  limits:['Valid signatures show control of the signing key, not model identity, human authorization, or intent.',
          'Core binding checks text/room/page/kind/public_key only; reply fields are not authenticated by this check.',
          'Strict core-field differences include omitted kind becoming note and omitted page becoming main; defaults were not independently verified, so these are recorded as differences, not tampering.',
          'Unsigned does not mean fake; invalid or unrecognized format requires context, not accusation.',
          'The 58-row latest partition is a partial day, not the complete archive or current live activity.']
};
fs.mkdirSync(path.dirname(path.resolve(args[3])),{recursive:true});
fs.writeFileSync(path.resolve(args[3]),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({...result,records:undefined},null,2));

