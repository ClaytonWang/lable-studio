import { forEach, isArray, map } from 'lodash';

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
    } else if (key === 'dm_actions') {
      return formatDMActions(data, ...options);
    }
    return data;
  } catch (error) {
    return data;
  }
};

const formatDMActions = (data) => {
  return map(data, item => {
    return {
      ...item,
      title: Formatter.trans(item.id, item.title),
      dialog: {
        ...item.dialog,
        text: Formatter.trans(`${item.id}_dialog`, item.dialog.text),
      },
    };
  });
};

const formatExportFormats = (data) => {
  return map(data, item => {
    return {
      ...item,
      description: Formatter.trans(`export_${item.title}`, item.description),
    };
  });
};

const formatDMColumns = (data) => {
  if (isArray(data?.columns)) {
    forEach(data.columns, item => {
      if (item.id) {
        item.title = Formatter.trans(item.id, item.title);
        item.help = Formatter.trans(`${item.id}_help`, '');
      }
    });
  }
  return data;
};

export default Formatter;
