const path = require('path');
const runAll = require("npm-run-all");

Object.assign(process.env, {
  LSF_DIR: path.join(__dirname, '../../../../label-studio-frontend'),
  DM_DIR: path.join(__dirname, '../../../../dm2'),
  LSF_WORK: path.join(__dirname, '../dist/lsf'),
  DM_WORK: path.join(__dirname, '../dist/dm'),
  NODE_ENV: 'production',
  BUILD_NO_HASH: true,
  BUILD_NO_CHUNKS: true,
  BUILD_MODULE: true,
});
require('dotenv').config({
  override: true,
});

(async () => {
  await runAll(["watch", "watch:dm", "watch:lsf"], {
    parallel: true,
    stdout: process.stdout,
    stderr: process.stderr,
    printLabel: true
  });
})();
