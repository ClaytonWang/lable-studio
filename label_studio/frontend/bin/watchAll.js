const runAll = require("npm-run-all");

runAll(["watch", "watch:dm", "watch:lsf"], {
  parallel: true,
  stdout: process.stdout,
  printLabel: true
});