import React, { useCallback, useMemo, useState } from 'react';
import { useHistory } from 'react-router';
import { get } from 'lodash';
import { Button, ToggleItems } from '../../components';
import { Modal } from '../../components/Modal/Modal';
import { Space } from '../../components/Space/Space';
import { useAPI } from '../../providers/ApiProvider';
import { Select } from '@/components/Form';
import { template } from '../../utils/util';
import { cn } from '../../utils/bem';
import { ConfigPage } from './Config/Config';
import "./CreateProject.styl";
import { ImportPage } from './Import/Import';
import { useImportPage } from './Import/useImportPage';
import { useDraftProject } from './utils/useDraftProject';
import { Radio } from 'antd';

// 1期需求：创建项目时，默认的模版
// const DEFAULT_CONFIG = `<View className="template-intent-classification-for-dialog">
// <Paragraphs name="dialogue" value="$dialogue" layout="dialogue" />
// <Choices name="intent" toName="dialogue" choice="multiple" showInLine="true">
//   <Choice value="升级"/>
//   <Choice value="不知情"/>
//   <Choice value="外呼"/>
// </Choices>
// </View>`;

const ProjectName = ({ templateType, setTemplateType, templateTypes, name, setName, onSaveName, onSubmit, error, description, setDescription, modelId, setModelId, existModels, getModels, show = true }) => {
  const [modelTrain, setTodelTrain] = useState('TRAIN_NEW');

  return !show ? null : (
    <form className={cn("project-name")} onSubmit={e => { e.preventDefault(); onSubmit(); }}>
      <div className="field field--wide">
        <label htmlFor="project_name">{t("Project Name")}</label>
        <input name="name" id="project_name" value={name} onChange={e => setName(e.target.value)} onBlur={onSaveName} />
        {error && <span className="error">{error}</span>}
      </div>
      <div className="field field--wide">
        <label htmlFor="project_description">{t("Description")}</label>
        <textarea
          name="description"
          id="project_description"
          placeholder={t("create_project_desc", "项目描述")}
          rows="4"
          value={description}
          onChange={e => setDescription(e.target.value)}
        />
      </div>
      <div className="field field--wide">
        <label htmlFor="template_type">{t("choose_template_type", "选择项目类型")}</label>
        <Select
          name="template_type"
          id="template_type"
          value={templateType}
          onChange={e => {
            setModelId('');//清空老的model id
            setTemplateType(e.target.value);
            if (modelTrain !== "TRAIN_NEW") {
              getModels(e.target.value);
            }
          }}
          options={templateTypes.filter(item => {
            return item.apiKey === 'intent-classification'
              || item.apiKey === 'conversational-generation';
          }).map(item => ({
            label: item.label,
            value: item.apiKey,
          }))}
        />
      </div>
      <div className="field field--wide">
        <label htmlFor="model_id">模型训练</label>
        <Radio.Group
          value={modelTrain}
          onChange={(e) => {
            setTodelTrain(e.target.value);
            if (e.target.value !== "TRAIN_NEW") {
              getModels(templateType);
            }
          }}
        >
          <Space direction="vertical" style={{ justifyContent: "flex-start" }}>
            <Radio value='TRAIN_NEW'>训练新模型</Radio>
            <Radio value='TRAIN_EXIST'>训练已有模型</Radio>
          </Space>
        </Radio.Group>

      </div>
      {existModels && modelTrain === "TRAIN_EXIST" && (
        <div className="field field--wide">
          <label htmlFor="model_id">选择模型</label>
          <Select
            name="model_id"
            id="model_id"
            value={modelId}
            onChange={e => setModelId(e.target.value)}
            options={existModels.map(item => ({
              label: item.title + " " + item.version,
              value: item.id,
            }))}
          />
        </div>
      )}
    </form>
  );
};

export const CreateProject = ({ onClose }) => {
  const [step, setStep] = React.useState("name"); // name | import | config
  const [waiting, setWaitingStatus] = React.useState(false);
  const [modelId, setModelId] = useState("");
  const [existModels, setExistModels] = useState(null);

  const project = useDraftProject();
  const history = useHistory();
  const api = useAPI();

  const [templateType, setTemplateType] = React.useState(get(template.TEMPLATE_TYPES, [0, 'apiKey'], ''));
  const [name, setName] = React.useState("");
  const [error, setError] = React.useState();
  const [description, setDescription] = React.useState("");
  const [config, setConfig] = React.useState("<View></View>");

  const templateConfig = useMemo(() => {
    return template.getConfigByApikey(templateType);
  }, [templateType]);

  React.useEffect(() => { setError(null); }, [name]);

  const { columns, uploading, uploadDisabled, finishUpload, pageProps } = useImportPage(project);

  const rootClass = cn("create-project");
  const tabClass = rootClass.elem("tab");
  const steps = {
    name: <span className={tabClass.mod({ disabled: !!error })}>{t("Project Name")}</span>,
    import: <span className={tabClass.mod({ disabled: uploadDisabled })}>{t("Data Import", "数据导入")}</span>,
    config: t("Labeling Setup", "标注设置"),
  };

  // name intentionally skipped from deps:
  // this should trigger only once when we got project loaded
  React.useEffect(() => {
    project && !name && setName(project.title);
  }, [project]);

  const projectBody = React.useMemo(() => {
    return {
      title: name,
      description,
      label_config: config,
      template_type: templateType,
      model_id: modelId,
    };
  }, [name, description, config, templateType, modelId]);


  const getModels = useCallback(async (tpl_type) => {
    const response = await api.callApi("modelManager", {
      params: {
        template_type: tpl_type,
      },
    });

    if (response !== null && response.results) {
      const models = response.results?.filter((i) => { return i.version !== "1.0"; });

      setExistModels(models);
      if (models.length > 0)
        setModelId(models[0].id);
    }

  }, []);

  const onCreate = React.useCallback(async () => {
    const imported = await finishUpload();

    if (!imported) return;

    setWaitingStatus(true);
    const response = await api.callApi('updateProject', {
      params: {
        pk: project.id,
      },
      body: projectBody,
    });

    setWaitingStatus(false);

    if (response !== null) {
      history.push(`/projects/${response.id}/data`);
    }
  }, [project, projectBody, finishUpload]);

  const onSaveName = async () => {
    if (error) return;
    const res = await api.callApi('updateProjectRaw', {
      params: {
        pk: project.id,
      },
      body: {
        title: name,
      },
    });

    if (res.ok) return;
    const err = await res.json();

    setError(err.validation_errors?.title);
  };

  const onDelete = React.useCallback(async () => {
    setWaitingStatus(true);
    if (project) await api.callApi('deleteProject', {
      params: {
        pk: project.id,
      },
    });
    setWaitingStatus(false);
    history.replace("/projects");
    onClose?.();
  }, [project]);

  return (
    <Modal onHide={onDelete} fullscreen visible bare closeOnClickOutside={false}>
      <div className={rootClass}>
        <Modal.Header>
          <h1>{t("Create Project")}</h1>
          <ToggleItems items={steps} active={step} onSelect={setStep} />

          <Space>
            <Button look="danger" size="compact" onClick={onDelete} waiting={waiting}>{t('Delete')}</Button>
            <Button look="primary" size="compact" onClick={onCreate} waiting={waiting || uploading} disabled={!project || uploadDisabled || error}>{t("Save")}</Button>
          </Space>
        </Modal.Header>
        <ProjectName
          name={name}
          setName={setName}
          error={error}
          onSaveName={onSaveName}
          onSubmit={onCreate}
          description={description}
          setDescription={setDescription}
          show={step === "name"}
          templateTypes={template.TEMPLATE_TYPES}
          templateType={templateType}
          setTemplateType={setTemplateType}
          modelId={modelId}
          setModelId={setModelId}
          existModels={existModels}
          getModels={getModels}
        />
        <ImportPage project={project} show={step === "import"} {...pageProps} />
        <ConfigPage key={templateType} project={project} onUpdate={setConfig} show={step === "config"} columns={columns} pageReadonly={false} config={templateConfig} modelId={modelId} />
      </div>
    </Modal>
  );
};
