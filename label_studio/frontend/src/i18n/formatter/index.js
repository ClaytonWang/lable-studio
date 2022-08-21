import { each, get, isArray, map } from 'lodash';

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
      case 'dm_data':
        return formatDMData(data, ...options);
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

const formatDMData = (data, apiMethod) => {
  if (apiMethod === 'tasks') {
    switch (window._projectClass) {
      case 'conversational-ai-response-generation':
        each(data?.tasks, item => {
          item.auto_label = get([].concat(item.auto_label), [0], '');
          item.manual_label = get([].concat(item.manual_label), [0], '');
        });
        break;
      case 'intent-classification-for-dialog':
        each(data?.tasks, item => {
          item.auto_label = [].concat(item.auto_label).join(',');
          item.manual_label = [].concat(item.manual_label).join(',');
        });
        break;
    }
  }
  return data;
};

export default Formatter;
