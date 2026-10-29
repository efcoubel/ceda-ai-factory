#!/usr/bin/env node
// Reads Firestore documents for diagnosis, never from a production project.
// Usage: node firestore-read.mjs --env <environment> --collection <path> [--where field,op,value]... [--order field[,desc]] [--limit n]
// The environment is a key of tools.database.config.projects in the nearest .ai-factory/profile.json.
// "local" (or a project set to "emulator") needs FIRESTORE_EMULATOR_HOST, which `firebase emulators:exec` sets.
// firebase-admin is resolved from the current directory, so run it from the functions folder.
import { createRequire } from 'node:module';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';

function fail(message) {
  console.error(message);
  process.exit(2);
}

function findProfile(start) {
  let dir = resolve(start);
  for (;;) {
    const candidate = join(dir, '.ai-factory', 'profile.json');
    if (existsSync(candidate)) {
      return candidate;
    }
    const parent = dirname(dir);
    if (parent === dir) {
      fail('No .ai-factory/profile.json found above the current directory.');
    }
    dir = parent;
  }
}

function parseArgs(argv) {
  const args = { where: [] };
  for (let i = 0; i < argv.length; i += 2) {
    const name = argv[i].replace(/^--/, '');
    const value = argv[i + 1];
    if (value === undefined) {
      fail(`Missing value for --${name}.`);
    }
    if (name === 'where') {
      args.where.push(value);
    } else {
      args[name] = value;
    }
  }
  return args;
}

function parseValue(raw) {
  try {
    return JSON.parse(raw);
  } catch {
    return raw;
  }
}

const args = parseArgs(process.argv.slice(2));
if (!args.env || !args.collection) {
  fail('Usage: node firestore-read.mjs --env <environment> --collection <path> [--where field,op,value]... [--order field[,desc]] [--limit n]');
}

const config = JSON.parse(readFileSync(findProfile(process.cwd()), 'utf8')).tools?.database?.config ?? {};
const projects = config.projects ?? {};
const productionEnvs = config.production_environments ?? ['production'];
const productionIds = productionEnvs.map((env) => projects[env]).filter(Boolean);
const project = projects[args.env];

if (productionEnvs.includes(args.env)) {
  fail(`Refused: "${args.env}" is a production environment.`);
}
if (project === undefined) {
  fail(`Unknown environment "${args.env}" (known: ${Object.keys(projects).join(', ')}).`);
}

const emulator = project === 'emulator';
if (emulator && !process.env.FIRESTORE_EMULATOR_HOST) {
  fail('Refused: the emulator is not running (FIRESTORE_EMULATOR_HOST is not set). Use firebase emulators:exec.');
}
const projectId = emulator ? (config.emulator_project ?? 'demo-local') : project;
if (productionIds.includes(projectId)) {
  fail(`Refused: project "${projectId}" belongs to a production environment.`);
}
if (productionIds.includes(process.env.GOOGLE_CLOUD_PROJECT)) {
  fail(`Refused: GOOGLE_CLOUD_PROJECT points to the production project "${process.env.GOOGLE_CLOUD_PROJECT}".`);
}
if (!emulator) {
  delete process.env.FIRESTORE_EMULATOR_HOST;
}

const require = createRequire(join(process.cwd(), 'noop.js'));
const { initializeApp } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');

initializeApp({ projectId });
let query = getFirestore().collection(args.collection);
for (const clause of args.where) {
  const [field, op, ...rest] = clause.split(',');
  query = query.where(field, op, parseValue(rest.join(',')));
}
if (args.order) {
  const [field, direction] = args.order.split(',');
  query = query.orderBy(field, direction === 'desc' ? 'desc' : 'asc');
}
query = query.limit(Number(args.limit ?? 20));

const snapshot = await query.get();
console.log(JSON.stringify(snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() })), null, 2));
