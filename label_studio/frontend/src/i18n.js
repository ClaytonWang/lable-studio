import i18next from "i18next";
import jqueryI18next from "jquery-i18next";
import zhCN from "./i18n/zh-CN/translation.json";
import enUS from "./i18n/en-US/translation.json";
import Formatter from './i18n/formatter';

const STORAGE_KEY = 'i18n-locale';

// 0. 注册全局变量
i18next.switchLocale = () => {
  const next = i18next.language === 'zh-CN' ? 'en-US' : 'zh-CN';

  i18next.changeLanguage(next).then(() => {
    window.localStorage.setItem(STORAGE_KEY, next);
    window.location.reload();
  });
};
window.i18next = i18next;
window.t = i18next.t;

// 1. 初始化多语言
Formatter.init(window.t, window.t);
const options = (() => {
  const resources = {
    "zh-CN": {
      translation: zhCN,
    },
    "en-US": {
      translation: enUS,
    },
  };
  const res = {
    resources,
    lngs: ["zh-CN", "en-US"],
    lng: "zh-CN",
    debug: process.env.NODE_ENV === "development",
  };
  const storageLang = window.localStorage.getItem(STORAGE_KEY);

  if (storageLang && res.lngs.indexOf(storageLang) > -1) {
    res.lng = storageLang;
  }
  return res;
})();

i18next.init(options);

// 2. 翻译python模版中的多语言
jqueryI18next.init(i18next, $);
$(() => {
  $("body").localize();
});
