import { each, isArray, map } from 'lodash';
import { template } from '@/utils/util';

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
    switch (key) {
      case 'with_template':
        return formatWithTemplate(data, ...options);
      case 'dm_columns':
        return formatDMColumns(data, ...options);
      case 'ls_export_formats':
        return formatExportFormats(data, ...options);
      case 'dm_actions':
        return formatDMActions(data, ...options);
      case 'ls_validate_config':
        return formatValidateConfig(data, ...options);
      default:
        return data;
    }
  } catch (error) {
    console.log('i18n.format.error', error);
    return data;
  }
};

const formatWithTemplate = (key, ...options) => {
  return Formatter.trans(`${window._projectClass}.${key}`, Formatter.trans(key, ...options));
};

const validatei18n = {
  non_field_errors: [
    ['These labels still exist in annotations','error_label_still_in'],
    ['annotations', 'annotations'],
  ],
};
const formatValidateConfig = (data) => {
  if (data.error) {
    const response = data.response;

    response.detail = Formatter.trans(response.detail);
    each(response.validation_errors, (list, key) => {
      if (validatei18n[key]) {
        response.validation_errors[key] = list.map(item => {
          each(validatei18n[key], cfg => {
            item = item.replace(cfg[0], Formatter.trans(cfg[1]));
          });
          return item;
        });
      }
    });
  }

  return data;
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

    each(data.columns, item => {
      if (item.id) {
        item.title = formatWithTemplate(item.id, item.title);
        item.help = formatWithTemplate(`${item.id}_help`, '');
      }
    });
  }
  return data;
};

export default Formatter;
