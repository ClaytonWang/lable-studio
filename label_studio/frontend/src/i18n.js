import i18next from "i18next";
import zhCN from './i18n/zh-CN/translation.json';
import enUS from './i18n/en-US/translation.json';

// 注册全局变量
window.i18next = i18next;
window.t = i18next.t;

// 初始化
const resources = {
  'zh-CN': {
    translation: zhCN,
  },
  'en-US': {
    translation: enUS,
  },
};

i18next.init({
  resources,
  lngs: ["zh-CN", "en-US"],
  lng: "zh-CN",
  debug: process.env.NODE_ENV === "development",
});
