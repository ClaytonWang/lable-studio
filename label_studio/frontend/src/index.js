import i18next from "i18next";
import resourcesToBackend from "i18next-resources-to-backend";

// 多语言
const initI18n = async () => {
  // 全局变量注册
  window.i18next = i18next;
  window.t = i18next.t;
  // 多语言初始化
  await i18next
    .use(
      resourcesToBackend((language, namespace, callback) => {
        import(`./i18n/${language}/${namespace}.json`)
          .then((resources) => {
            callback(null, resources);
          })
          .catch((error) => {
            callback(error, null);
          });
      }),
    )
    .init({
      lngs: ["zh-CN", "en-US"],
      lng: "zh-CN",
      fallbackLng: false,
      debug: process.env.NODE_ENV === "development",
    });
};

initI18n().then(() => {
  import("./app/App");
});
