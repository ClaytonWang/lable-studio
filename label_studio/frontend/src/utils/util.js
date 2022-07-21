import { find, get, startsWith } from 'lodash';

const TEMPLATES = [
  {
    class: 'intent-classification-for-dialog',
    label: 'Intent Classification for Dialog',
    desc: '对话-意图分类',
  },
  {
    class: 'conversational-ai-response-generation',
    label: 'Conversational AI - Response Generation',
    desc: '对话生成',
  },
];
const getTemplateClass = (config) => {
  try {
    const cfg = get(config, 'label_config', toString(config));
    const classNames = cfg.match(/className="([^"]+)"/)[1].split(/\s+/);
    const templateClass = classNames.find(item => startsWith(item, 'template-')).replace(/^template-/, '');

    return templateClass;
  } catch (error) {
    return '';
  }
};
const getTemplate = (config) => {
  const templateClass = getTemplateClass(config);

  return templateClass ? find(TEMPLATES, {
    class: templateClass,
  }, null) : null;
};
const getTemplateLabel = (config, withBracket = false) => {
  const template = getTemplate(config);
  
  if (!template) {
    return '';
  }
  return withBracket ? `(${t(template.label)})` : t(template.label);
};

export const template = {
  get: getTemplate,
  class: getTemplateClass,
  label: getTemplateLabel,
};
