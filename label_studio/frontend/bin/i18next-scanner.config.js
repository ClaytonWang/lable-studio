const path = require('path');

Object.assign(process.env, {
  LSF_DIR: path.join(__dirname, '../../../../label-studio-frontend'),
  DM_DIR: path.join(__dirname, '../../../../dm2'),
});
require('dotenv').config({
  override: true,
});

const tasks = {
  ls: 'src/**/*.{js,jsx}',
  dm2: path.join(process.env.DM_DIR, 'src/**/*.{js,jsx}'),
  lsf: path.join(process.env.LSF_DIR, 'src/**/*.{js,jsx}'),
};

module.exports = {
  input: Object.values(tasks),
  output: './',
  options: {
    debug: true,
    func: {
      list: ['t'],
      extensions: ['.js', '.jsx']
    },
    lngs: ['zh-CN', 'en-US'],
    ns: Object.keys(tasks),
    defaultLng: 'zh-CN',
  }
};