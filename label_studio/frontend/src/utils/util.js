import { find, get, startsWith } from 'lodash';

const INTENT_VIEW  = `<View className="template-intent-classification-for-dialog">
<Paragraphs name="dialogue" value="$dialogue" layout="dialogue" />
<Choices name="intent" toName="dialogue" choice="multiple" showInLine="true">
  <Choice value="升级"/>
  <Choice value="不知情"/>
  <Choice value="外呼"/>
</Choices>
</View>`;

const RESPONSE_VIEW = `<View className="template-conversational-ai-response-generation">
<Paragraphs name="chat" value="$dialogue" layout="dialogue"/>
<Header value="意图标签"/>
<Choices readonly="true" name="intent" toName="chat" choice="multiple" showInLine="true">
  <Choice value="升级"/>
  <Choice value="不知情"/>
  <Choice value="外呼"/>
</Choices>
<Header value="提供对话"/>
<TextArea name="response" toName="chat" rows="4" editable="true" maxSubmissions="100"/>
</View>`;

const CORRECTION_VIEW = `<View className="template-round-correction">
<Paragraphs name="chat" value="$dialogue" layout="dialogue"/>
<Header value="意图标签"/>
<Choices readonly="true" name="intent" toName="chat" choice="multiple" showInLine="true">
  <Choice value="升级"/>
  <Choice value="不知情"/>
  <Choice value="外呼"/>
</Choices>
<Header value="提供对话"/>
<TextArea name="response" toName="chat" rows="4" editable="true" maxSubmissions="100"/>
</View>`;

const CLEAN_VIEW = `<View className="template-intelligent-clean">
<Paragraphs name="chat" value="$dialogue" layout="dialogue"/>
<Header value="意图标签"/>
<Choices readonly="true" name="intent" toName="chat" choice="multiple" showInLine="true">
  <Choice value="升级"/>
  <Choice value="不知情"/>
  <Choice value="外呼"/>
</Choices>
<Header value="提供对话"/>
<TextArea name="response" toName="chat" rows="4" editable="true" maxSubmissions="100"/>
</View>`;

const TEMPLATE_TYPES = [
  {
    label: t("intention"),
    apiKey: "intent-classification",
    config: INTENT_VIEW,
  },
  {
    label: t("generation"),
    apiKey: "conversational-generation",
    config: RESPONSE_VIEW,
  },
  {
    label: t("round-correction"),
    apiKey: "round-correction",
    config: CORRECTION_VIEW,
  },
  {
    label: t("intelligent-clean"),
    apiKey: "intelligent-clean",
    config: CLEAN_VIEW,
  },
];

const TEMPLATES = [
  {
    class: 'intent-classification-for-dialog',
    label: 'Intent Classification for Dialog',
    desc: t("intention"),
  },
  {
    class: 'conversational-ai-response-generation',
    label: 'Conversational AI - Response Generation',
    desc: t("round-correction"),
  },
  {
    class: 'round-correction',
    label: t("round-correction"),
    desc: t("round-correction"),
  },
  {
    class: 'intelligent-clean',
    label: t("intelligent-clean"),
    desc: t("intelligent-clean"),
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

const getConfigByApikey = (key) => {
  const item = find(TEMPLATE_TYPES, { apiKey: key });

  return item?.config;
};

export const template = {
  get: getTemplate,
  class: getTemplateClass,
  label: getTemplateLabel,
  TEMPLATE_TYPES,
  getConfigByApikey,
};
