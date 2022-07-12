const path = require('path');
const fse = require('fs/promises');
const _ = require('lodash');

const zhPath = path.resolve(__dirname, '../src/i18n/zh-CN/translation.json');
const enPath = path.resolve(__dirname, '../src/i18n/en-US/translation.json');

const zhCN = require(zhPath);
const enUS = require(enPath);

const tocsv = async () => {
  let str = 'key\tzh-CN\ten-US';
  const res = {};
  _.forEach(zhCN, (v, key) => {
    str += `\n${key}\t${v}\t${enUS[key]}`;
  });
  const filePath = path.join(__dirname, '../src/i18n/translation.csv');
  await fse.writeFile(filePath, str, 'utf-8');
};

const merge = async () => {
  const filePath = path.join(__dirname, '../src/i18n/label_studio_i18n.csv');
  const data = await fse.readFile(filePath, 'utf-8').then(txt => {
    const [ title, ...list ] = txt.replace(/^\uFEFF/, '').split('\n').map(item => item.split('\t'));
    const res = [];
    for (const item of list) {
      const map = {};
      for (let i=0; i<title.length; i++) {
        map[title[i]] = item[i];
      }
      res.push(map);
    }
    return res;
  });

  // console.log("🚀 ~ file: i18n.js ~ line 35 ~ data ~ data", data)

  for (const item of data) {
    const { key, 'zh-CN': zh, 'en-US': en } = item;
    if (zh && zhCN[key]) {
      zhCN[key] = zh;
    }
    if (en && enUS[key]) {
      enUS[key] = en;
    }
  }
  await fse.writeFile(zhPath, JSON.stringify(zhCN, null, 2), 'utf-8');
  await fse.writeFile(enPath, JSON.stringify(enUS, null, 2), 'utf-8');
};

const OPERATE = process.argv[2];
if (OPERATE === 'tocsv') {
  tocsv();
} else if (OPERATE === 'merge') {
  merge();
} else {
  console.log('Please set operate param: in [tocsv, merge]');
}

module.exports.tocsv = tocsv;
module.exports.merge = merge;
