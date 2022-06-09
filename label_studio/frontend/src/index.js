import './app/App';

// 多语言处理
(() => {
  if (typeof window.t !== 'function') {
    window.t = (key, defaultMessage) => {
      return defaultMessage || key || 'T';
    };
  }
})();