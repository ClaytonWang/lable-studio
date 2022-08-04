import { useMemo } from 'react';
import { get, map, template } from 'lodash';
import { ConfigureControl } from '@/pages/CreateProject/Config/Config';
import { Template } from '@/pages/CreateProject/Config/Template';
import "./ProjectTag.less";

const tpl = `<View className="template-intent-classification-for-dialog">
<Paragraphs name="dialogue" value="$dialogue" layout="dialogue" />
<Choices name="intent" toName="dialogue" choice="multiple" showInLine="true">
  <% list.forEach(item => { %>
  <Choice value="<%= item %>"/>  
  <% }) %>
</Choices>
</View>`;
const createLabelConfig  = (list) => {
  return template(tpl)({ list });
};

const ProjectTag = ({ value, onChange }) => {
  const {
    template,
    control,
  } = useMemo(() => {
    const str = createLabelConfig(value);
    const template = new Template({ config: str });
    const control = get(template, ['controls', 0]);

    template.onConfigUpdate = () => {
      console.log(control, control.children);

      const res = map(control.children, item => item.getAttribute("value"));

      onChange(res);
    };
    return {
      template,
      control,
    };
  }, [value]);

  return (
    <div className="project-tag">
      <ConfigureControl control={control} template={template} />
    </div>
  );
};

export {
  ProjectTag
};
