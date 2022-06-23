import { forEach, isArray } from 'lodash';

const Formatter = {
  trans: window.t,
  init: (transFunc, parent) => {
    Formatter.trans = transFunc;
    if (parent) {
      Object.assign(parent, {
        format,
      });
    }
  },
};

const format = (key, data, ...options) => {
  try {
    if (key === 'dm_columns') {
      return formatDMColumns(data, ...options);
    }
    return data;
  } catch (error) {
    return data;
  }
};

const formatDMColumns = (data) => {
  if (isArray(data?.columns)) {
    forEach(data.columns, item => {
      if (item.id) {
        item.title = t(item.id, item.title);
        item.help = t(`${item.id}_help`, item.help);
      }
    });
  }

  return data;
};

export default Formatter;
