import { useCallback, useContext, useEffect, useState } from 'react';
import { Button } from '../../../components';
import { Description } from '../../../components/Description/Description';
import { Divider } from '../../../components/Divider/Divider';
import { ErrorWrapper } from '../../../components/Error/Error';
import { InlineError } from '../../../components/Error/InlineError';
import { Form, Input, Label, Select, TextArea, Toggle } from '../../../components/Form';
import { FormResponseContext } from '../../../components/Form/FormContext';
import { modal } from '../../../components/Modal/Modal';
import { useAPI } from '../../../providers/ApiProvider';
import { ProjectContext } from '../../../providers/ProjectProvider';
import { MachineLearningList } from './MachineLearningList';
import './MachineLearningSettings.styl';

export const MachineLearningSettings = () => {
  const api = useAPI();
  const { project, fetchProject, updateProject } = useContext(ProjectContext);
  const [mlError, setMLError] = useState();
  const [backends, setBackends] = useState([]);
  const [versions, setVersions] = useState([]);

  const resetMLVersion = useCallback(async (e) => {
    e.preventDefault();
    e.stopPropagation();

    await updateProject({
      model_version: null,
    });
  }, [api, project]);

  const fetchBackends = useCallback(async () => {
    const models = await api.callApi('mlBackends', {
      params: {
        project: project.id,
      },
    });


    if (models) setBackends(models);
  }, [api, project, setBackends]);

  const fetchMLVersions = useCallback(async () => {
    const modelVersions = await api.callApi("modelVersions", {
      params: {
        pk: project.id,
      },
    });

    var versions = [];

    for (const [key, value] of Object.entries(modelVersions)) {
      versions.push({
        value: key,
        label: key + " (" + value + " predictions)",
      });
    }

    setVersions(versions);
  }, [api, project.id]);

  const showMLFormModal = useCallback((backend) => {
    const action = backend ? "updateMLBackend" : "addMLBackend";

    console.log({ backend });
    const modalProps = {
      title: `${backend ? 'Edit' : 'Add'} model`,
      style: { width: 760 },
      closeOnClickOutside: false,
      body: (
        <Form
          action={action}
          formData={{ ...(backend ?? {}) }}
          params={{ pk: backend?.id }}
          onSubmit={async (response) => {
            if (!response.error_message) {
              await fetchBackends();
              modalRef.close();
            }
          }}
        >
          <Input type="hidden" name="project" value={project.id}/>

          <Form.Row columnCount={2}>
            <Input name="title" label="Title" placeholder="ML Model"/>
            <Input name="url" label="URL" required/>
          </Form.Row>

          <Form.Row columnCount={1}>
            <TextArea name="description" label="Description" style={{ minHeight: 120 }}/>
          </Form.Row>

          <Form.Row columnCount={1}>
            <Toggle
              name="is_interactive"
              label="Use for interactive preannotations"
            />
          </Form.Row>

          <Form.Actions>
            <Button type="submit" look="primary" onClick={() => setMLError(null)}>
              {t("Validate and Save", "校验并保存")}
            </Button>
          </Form.Actions>

          <Form.ResponseParser>{response => (
            <>
              {response.error_message && (
                <ErrorWrapper error={{
                  response: {
                    detail: `Failed to ${backend ? 'save' : 'add new'} ML backend.`,
                    exc_info: response.error_message,
                  },
                }}/>
              )}
            </>
          )}</Form.ResponseParser>

          <InlineError/>
        </Form>
      ),
    };

    const modalRef = modal(modalProps);
  }, [project, fetchBackends, mlError]);

  useEffect(() => {
    if (project.id) {
      fetchBackends();
      fetchMLVersions();
    }
  }, [project]);

  return (
    <>
      <Description style={{ marginTop: 0, maxWidth: 680 }}>
        {t("ml_add_desc")}
      </Description>
      <Button onClick={() => showMLFormModal()}>
        {t("Add Model")}
      </Button>

      <Divider height={32}/>

      <Form action="updateProject"
        formData={{ ...project }}
        params={{ pk: project.id }}
        onSubmit={() => fetchProject()}
        autosubmit
      >
        <Form.Row columnCount={1}>
          <Label text={t("ML-Assisted Labeling")} large/>

          <div style={{ paddingLeft: 16 }}>
            <Toggle
              label={t("ml_start_after")}
              name="start_training_on_annotation_update"
            />
          </div>

          <div style={{ paddingLeft: 16 }}>
            <Toggle
              label={t("ml_retrieve_auto")}
              name="evaluate_predictions_automatically"
            />
          </div>

          <div style={{ paddingLeft: 16 }}>
            <Toggle
              label={t("ml_show_quickview")}
              name="show_collab_predictions"
            />
          </div>
        </Form.Row>

        {versions.length > 1 && (
          <Form.Row columnCount={1}>
            <Label
              text="Model Version"
              description="Model version allows you to specify which prediction will be shown to the annotators."
              style={{ marginTop: 16 }}
              large
            />

            <div style={{ display: 'flex', alignItems: 'center', width: 400, paddingLeft: 16 }}>
              <div style={{ flex: 1, paddingRight: 16 }}>
                <Select
                  name="model_version"
                  defaultValue={null}
                  options={[
                    ...versions,
                  ]}
                  placeholder="No model version selected"
                />
              </div>

              <Button onClick={resetMLVersion}>
                Reset
              </Button>
            </div>

          </Form.Row>
        )}
      </Form>

      <MachineLearningList
        onEdit={(backend) => showMLFormModal(backend)}
        fetchBackends={fetchBackends}
        backends={backends}
      />
    </>
  );
};

MachineLearningSettings.title = t("Machine Learning");
MachineLearningSettings.path = "/ml";
