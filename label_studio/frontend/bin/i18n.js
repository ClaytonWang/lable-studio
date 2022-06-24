const path = require('path');
const fse = require('fs/promises');
const _ = require('lodash');
const zhCN = require('../src/i18n/zh-CN/translation.json');
const enUS = require('../src/i18n/en-US/translation.json');

const toCsv = () => {
  let str = 'key\tzh-CN\ten-US';
  const res = {};
  _.forEach(zhCN, (v, key) => {
    str += `\n${key}\t${v}\t${enUS[key]}`;
  });
  const filePath = path.join(__dirname, '../src/i18n/translation.csv');
  fse.writeFile(filePath, str, 'utf-8');
};

toCsv();

module.exports.toCsv = toCsv;
