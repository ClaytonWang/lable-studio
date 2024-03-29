const path = require('path');
const fs = require("fs/promises");
const runAll = require("npm-run-all");
var git = require('git-rev-sync');
const gitlog = require("gitlog").default;

Object.assign(process.env, {
  LSF_DIR: path.join(__dirname, '../../../../label-studio-frontend'),
  DM_DIR: path.join(__dirname, '../../../../dm2'),
});
require('dotenv').config({
  override: true,
});

const DIST = path.join(__dirname, '../dist');
const DM = process.env.DM_DIR;
const DM_DIST = path.join(DM, 'build/static');
const LSF = process.env.LSF_DIR;
const LSF_DIST = path.join(LSF, 'build/static');
const LICENSE_path = path.join(__dirname, '../lib/index.js.LICENSE.txt');

const createGitVersionJson = async (dir, filePath) => {
  const branch = git.branch(dir);
  const [ commit ] = gitlog({
    repo: dir,
    number: 1,
  });
  const json = {
    "message": commit.subject,
    "commit": commit.hash,
    branch,
    "date": commit.authorDate,
  };
  await fs.writeFile(filePath, JSON.stringify(json, null, 2), 'utf8');
};

(async () => {
  // 0. 删除dist文件夹
  await fs.rm(DIST, {
    recursive: true,
  });
  // 1. Build
  await runAll(["build:production", "build:dm", "build:lsf"], {
    stdout: process.stdout,
    printLabel: true
  });
  // 2. Copy文件
  await fs.cp(DM_DIST, path.join(DIST, 'dm'), { recursive: true });
  await fs.cp(LSF_DIST, path.join(DIST, 'lsf'), { recursive: true });
  await fs.cp(LICENSE_path, path.join(DIST, 'react-app/index.js.LICENSE.txt'));
  // 3. 生成version文件
  await createGitVersionJson(DM_DIST, path.join(DIST, 'dm/version.json'));
  await createGitVersionJson(LSF_DIST, path.join(DIST, 'lsf/version.json'));
})();
