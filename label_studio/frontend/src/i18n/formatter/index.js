import { t } from 'i18next';
import { map, forEach, isArray } from 'lodash';

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
    } else if (key === 'ls_export_formats') {
      return formatExportFormats(data, ...options);
    }
    return data;
  } catch (error) {
    return data;
  }
};

const formatExportFormats = (data) => {
  return map(data, item => {
    return {
      ...item,
      description: t(`export_${item.title}`, item.description),
    };
  });
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
