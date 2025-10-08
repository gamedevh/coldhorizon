
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160/build/three.module.js';
import {PointerLockControls} from 'https://cdn.jsdelivr.net/npm/three@0.160/examples/jsm/controls/PointerLockControls.js';

// ----- DOM -----
const canvas = document.getElementById('c');
const overlay = document.getElementById('overlay');
const startBtn = document.getElementById('startBtn');
const invPanel = document.getElementById('inventory');
const invList = document.getElementById('invList');
const craftingDiv = document.getElementById('crafting');
const messagesDiv = document.getElementById('messages');

if (!canvas) console.error('Canvas #c not found');
if (!startBtn) console.error('Start button #startBtn not found');

// ----- Renderer/Scene/Camera -----
const renderer = new THREE.WebGLRenderer({canvas, antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x20242a);
const camera = new THREE.PerspectiveCamera(70, innerWidth/innerHeight, 0.05, 500);

// ----- Lighting -----
const hemi = new THREE.HemisphereLight(0xaaccff, 0x334455, 0.25);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 1.1);
sun.position.set(10,30,10);
sun.castShadow = true;
sun.shadow.camera.near = 0.5;
sun.shadow.camera.far = 200;
scene.add(sun);

// ----- Ground -----
const groundGeo = new THREE.PlaneGeometry(500, 500);
const groundMat = new THREE.MeshPhongMaterial({color:0x24303f});
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI/2;
ground.receiveShadow = true;
scene.add(ground);

// ----- Player / Controls -----
// IMPORTANT: use renderer.domElement for pointer lock target (more reliable than document.body)
const controls = new PointerLockControls(camera, renderer.domElement);
let velocity = new THREE.Vector3();
let direction = new THREE.Vector3();
let onGround = false;
let speed = 6.0;
let sprint = 1.7;
let gravity = 22.0;
let jumpImpulse = 8.5;

camera.position.set(0, 1.7, 0);
scene.add(controls.getObject());

function lock() {
  console.log('Attempting pointer lock...');
  controls.lock();
}
function unlock() {
  overlay.classList.remove('hidden');
}
controls.addEventListener('lock', ()=>{
  console.log('Pointer lock acquired');
  overlay.classList.add('hidden');
});
controls.addEventListener('unlock', ()=>{
  console.log('Pointer lock released');
  unlock();
});

// Button + canvas to start
startBtn?.addEventListener('click', (e)=>{ e.preventDefault(); lock(); });
canvas.addEventListener('click', ()=>{ if (!controls.isLocked) lock(); });

// ----- Input -----
const key = {};
window.addEventListener('keydown', e=>{
  if (e.code === 'Tab'){ e.preventDefault(); invPanel.classList.toggle('hidden'); renderInventory(); return; }
  key[e.code] = true;
});
window.addEventListener('keyup', e=> key[e.code] = false);
window.addEventListener('resize', ()=>{
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

// ----- Resource Nodes -----
const NODE_KIND = {TREE:'Tree', ROCK:'Rock', ORE:'Ore'};
const nodes = [];
const nodeGeo = new THREE.CapsuleGeometry(0.4, 0.6, 4, 8);
const nodeMats = {
  [NODE_KIND.TREE]: new THREE.MeshStandardMaterial({color:0x3a8540}),
  [NODE_KIND.ROCK]: new THREE.MeshStandardMaterial({color:0x71767a}),
  [NODE_KIND.ORE]:  new THREE.MeshStandardMaterial({color:0x8b6f3e})
};

function spawnNodes(count=80){
  for (let i=0;i<count;i++){
    const kind = [NODE_KIND.TREE, NODE_KIND.ROCK, NODE_KIND.ORE][(Math.random()*3)|0];
    const mesh = new THREE.Mesh(nodeGeo, nodeMats[kind]);
    mesh.position.set( (Math.random()-0.5)*220, 0.9, (Math.random()-0.5)*220 );
    mesh.castShadow = true;
    mesh.userData.kind = kind;
    mesh.userData.hp = (kind===NODE_KIND.TREE?30:kind===NODE_KIND.ROCK?40:50);
    scene.add(mesh);
    nodes.push(mesh);
  }
}
spawnNodes();

// ----- Raycaster for interact -----
const raycaster = new THREE.Raycaster();
function tryInteract(){
  raycaster.set(camera.getWorldPosition(new THREE.Vector3()), camera.getWorldDirection(new THREE.Vector3()));
  const hits = raycaster.intersectObjects(nodes, false);
  if (hits.length && hits[0].distance < 3){
    const m = hits[0].object;
    m.userData.hp -= 10;
    spawnFloatingText('-10');
    if (m.userData.hp <= 0){
      giveResource(m.userData.kind);
      scene.remove(m);
      const idx = nodes.indexOf(m);
      if (idx>=0) nodes.splice(idx,1);
    }
  } else {
    pushMsg('Nothing to harvest.');
  }
}
window.addEventListener('keydown', e=>{
  if (e.code==='KeyE') tryInteract();
});

// ----- Floating Text -----
function spawnFloatingText(text){
  const el = document.createElement('div');
  el.className='msg';
  el.textContent = text;
  messagesDiv.appendChild(el);
  setTimeout(()=>el.remove(), 1200);
}

// ----- Inventory / Crafting -----
const inv = new Map([['berry',2],['water',1]]);
function add(item, qty=1){
  inv.set(item, (inv.get(item)||0)+qty);
  pushMsg(`+${qty} ${item}`);
  if (!invPanel.classList.contains('hidden')) renderInventory();
}
function has(item, qty=1){ return (inv.get(item)||0) >= qty; }
function remove(item, qty=1){
  if (!has(item,qty)) return false;
  inv.set(item, inv.get(item)-qty);
  if (inv.get(item)<=0) inv.delete(item);
  return true;
}
function giveResource(kind){
  if (kind===NODE_KIND.TREE) add('wood',3);
  else if (kind===NODE_KIND.ROCK) add('stone',3);
  else add('ore',2);
}
const RECIPES = {
  hatchet: { cost:{wood:2, stone:1}, gives:{hatchet:1} },
  pickaxe: { cost:{wood:2, stone:2}, gives:{pickaxe:1} },
  spear:   { cost:{wood:3}, gives:{spear:1} },
  tea:     { cost:{berry:2, water:1}, gives:{tea:1} }
};
function craft(name, qty=1){
  const r = RECIPES[name]; if (!r) return false;
  for (const [k,v] of Object.entries(r.cost)){
    if (!has(k, v*qty)) { pushMsg('Missing '+k); return false; }
  }
  for (const [k,v] of Object.entries(r.cost)) remove(k, v*qty);
  for (const [k,v] of Object.entries(r.gives)) add(k, v*qty);
  pushMsg(`Crafted ${name} x${qty}`);
  renderInventory();
  return true;
}
function renderInventory(){
  invList.innerHTML = '';
  [...inv.entries()].sort().forEach(([k,v])=>{
    const li = document.createElement('li'); li.textContent = `${k} x${v}`; invList.appendChild(li);
  });
  craftingDiv.innerHTML='';
  Object.keys(RECIPES).forEach(name=>{
    const b = document.createElement('button'); b.textContent = name;
    b.onclick=()=>craft(name,1);
    craftingDiv.appendChild(b);
  });
}
function pushMsg(t){
  const el = document.createElement('div'); el.className='msg'; el.textContent = t;
  messagesDiv.appendChild(el);
  setTimeout(()=>el.remove(), 1600);
}

// ----- Game Loop -----
let last = performance.now();
function step(now){
  const dt = Math.min(0.05, (now - last)/1000); last = now;

  // Day/Night simple rotate
  sun.position.applyAxisAngle(new THREE.Vector3(1,0,0), dt * (Math.PI*2/360));
  const dot = Math.max(0, sun.position.normalize().y);
  hemi.intensity = 0.15 + 0.35 * dot;
  sun.intensity = 0.2 + 1.0 * dot;

  // Movement
  const directionZ = Number(key['KeyS']) - Number(key['KeyW']);
  const directionX = Number(key['KeyD']) - Number(key['KeyA']);
  const norm = Math.hypot(directionX, directionZ) || 1;
  const nx = directionX / norm, nz = directionZ / norm;
  const mult = (key['ShiftLeft']||key['ShiftRight']) ? sprint : 1.0;
  if (controls.isLocked){
    const forward = new THREE.Vector3();
    controls.getDirection(forward);
    forward.y=0; forward.normalize();
    const right = new THREE.Vector3().crossVectors(new THREE.Vector3(0,1,0), forward).negate();
    const move = new THREE.Vector3().addScaledVector(forward, -nz).addScaledVector(right, nx);
    const moveSpeed = speed * mult;
    controls.moveRight(move.x * moveSpeed * dt);
    controls.moveForward(move.z * moveSpeed * dt);

    // Gravity & jump (simple ground plane at y=1.7 for camera)
    const obj = controls.getObject();
    let y = obj.position.y;
    const grounded = y <= 1.7;
    if (grounded){ y = 1.7; velocity.y = 0; onGround = true; }
    else { velocity.y -= gravity * dt; onGround = false; }
    if (onGround && key['Space']) { velocity.y = jumpImpulse; onGround = false; }
    obj.position.y = y + velocity.y * dt;
  }

  renderer.render(scene, camera);
  requestAnimationFrame(step);
}
requestAnimationFrame(step);

// Prevent default browser scroll/focus issues for game keys
window.addEventListener('keydown', e=>{
  if (['Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code)) e.preventDefault();
});
