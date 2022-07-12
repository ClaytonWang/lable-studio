import { useCallback, useContext, useEffect, useRef } from 'react';
import { Button } from '../../components';
import { Form, Label, TextArea, Toggle } from '../../components/Form';
import { MenubarContext } from '../../components/Menubar/Menubar';
import { ProjectContext } from '../../providers/ProjectProvider';

export const InstructionsSettings = () => {
  const { project, fetchProject } = useContext(ProjectContext);
  const pageContext = useContext(MenubarContext);
  const formRef = useRef();

  useEffect(() => {
    pageContext.setProps({ formRef });
  }, [formRef]);

  const updateProject = useCallback(() => {
    fetchProject(project.id, true);
  }, [project]);

  return (
    <div style={{ width: 480 }}>
      <Form ref={formRef} action="updateProject" formData={{ ...project }} params={{ pk: project.id }} onSubmit={updateProject}>
        <Form.Row columnCount={1}>
          <Label text={t("Labeling Instructions")} large/>
          <div style={{ paddingLeft: 16 }}>
            <Toggle label={t("Show before labeling", "展示标注前数据")} name="show_instruction"/>
          </div>
          <div style={{ color: "rgba(0,0,0,0.4)", paddingLeft: 16 }}>
            {t("write_label_help")}
          </div>
        </Form.Row>

        <Form.Row columnCount={1}>
          <TextArea name="expert_instruction" style={{ minHeight: 128 }}/>
        </Form.Row>

        <Form.Actions>
          <Form.Indicator>
            <span case="success">{t("Saved!")}</span>
          </Form.Indicator>
          <Button type="submit" look="primary" style={{ width: 120 }}>{t("Save")}</Button>
        </Form.Actions>
      </Form>
    </div>
  );
};

InstructionsSettings.title = t("Instructions");
InstructionsSettings.path = "/instruction";
