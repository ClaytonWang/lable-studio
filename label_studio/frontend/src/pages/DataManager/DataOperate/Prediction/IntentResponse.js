import React, { useCallback, useEffect, useState } from 'react';
import { Col, Form, Row, Tag } from 'antd';
import { Modal } from "@/components/Modal/Modal";
import { Space } from "@/components/Space/Space";
import { Button } from "@/components/Button/Button";
import { Select } from '@/components/Form';
import { useProject } from '@/providers/ProjectProvider';
import { ConfigureControl } from '@/pages/CreateProject/Config/Config';
import { Template } from '@/pages/CreateProject/Config/Template';
import { useAPI } from '@/providers/ApiProvider';

const { confirm } = Modal;

const formItemLayout = {
  labelCol: { span: 5 },
  wrapperCol: { span: 19 },
};

const IntentResponse = ({ close, execLabel }) => {
  const { project } = useProject();
  const [template, setCurrentTemplate] = useState(null);
  const [config, _setConfig] = React.useState("");
  const [execModel, setExecModel] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [execModelList, setExecModelList] = React.useState([]);
  const [modelLabels, setModelLabels] = React.useState([]);
  const api = useAPI();

  const setConfig = useCallback(config => {
    _setConfig(config);
  }, [_setConfig]);

  const setTemplate = useCallback(config => {
    const tpl = new Template({ config });

    tpl.onConfigUpdate = setConfig;
    setConfig(config);
    setCurrentTemplate(tpl);
  }, [setConfig, setCurrentTemplate]);

  const getModelLabels = useCallback(async (model_id) => {
    if (model_id) {
      const data = await api.callApi("modelLabel", {
        params: {
          model_id,
        },
      });

      setModelLabels(data);
    }
    setExecModel(model_id);

  }, []);

  const getModelList = useCallback(async () => {
    const data = await api.callApi("modelList", {
      params: {
        type: 'intention',
      },
    });

    setExecModelList([{ id:'',title:'请选择模型',version:'',value:'' },...data]);

  }, []);

  useEffect(() => {
    if (project.label_config) {
      setTemplate(project.label_config);
    }
    getModelList();
  }, []);

  const saveConfig = useCallback(async () => {
    setLoading(true);
    const res = await api.callApi("updateProjectRaw", {
      params: {
        pk: project.id,
      },
      body: {
        label_config: config,
      },
    });

    if (res.ok) {
      execLabel({ model_id: execModel });
      return true;
    }
    const error = await res.json();

    setLoading(false);
    return error;
  }, [project, config, execModel]);

  const exec = () => {
    let changedLabels = [];
    const labels = project?.parsed_label_config?.intent?.labels ?? [];

    template.controls.map(ctl => {
      changedLabels = Array.from(ctl.children).map(c => {
        return c.getAttribute("value");
      });
    });

    if (!execModel) {
      return;
    }

    //判断新旧标签是否相同
    const isSame = labels.length === changedLabels.length
      && (labels.filter(t => !changedLabels.includes(t))).length === 0
      && (changedLabels.filter(t => !labels.includes(t))).length === 0;

    if (!isSame) {
      confirm({
        title: "警告",
        body: "模型标签和已设置标签不一致是否继续标注?",
        buttonLook: "destructive",
        onOk: () => {
          //go exec
          saveConfig();
        },
        okText: "继续标注",
        cancelText: "返回修改",
      });
    } else {
      //go exec
      saveConfig();
    }
  };

  return (
    <>
      <Modal.Header>
        预标注(普通)
      </Modal.Header>
      <Form
        {...formItemLayout}
        layout="horizontal"
        name="form_in_modal"
        className='modal_form'
      >
        <Form.Item
          label="选择模型"
          validateStatus={execModel ? 'success' : 'error'}
          help={!execModel ? "请选择模型" : ''}
        >
          <div style={{ width: 300 }}>
            <Select
              options={execModelList?.map(v => {
                return { label: v.title + v.version, value: v.id };
              })}
              onChange={(e) => {
                getModelLabels(e.target.value);
              }} />
          </div>
        </Form.Item>
        <Form.Item
          label="所选模型标签"
        >
          <Space size="small">
            {
              modelLabels && modelLabels.map(tag => {
                return (
                  <Tag key={tag}>{tag}</Tag>
                );
              })
            }
          </Space>
          {
            modelLabels.length > 0 && <div style={{ color: 'red', marginTop: 10 }}>注:所选模型标签和已设置标签</div>
          }
        </Form.Item>
      </Form>
      {template && template.controls.map(control => {
        return (
          <Row key={control.getAttribute("name")} className={'configure-row'}>
            <Col span={5} className={'ant-form-item-label'}>
              <label>已设置标签</label>
            </Col>
            <Col span={19} >
              <ConfigureControl control={control} template={template} />
            </Col>
          </Row>
        );
      })}
      <Modal.Footer>
        <Space align="end">
          <Button
            size="compact"
            onClick={close}
          >
            取消
          </Button>
          <Button
            size="compact"
            look="primary"
            onClick={exec}
            waiting={ loading }
            disabled={!execModel}
          >
            立即标注
          </Button>
        </Space>
      </Modal.Footer>
    </>
  );
};

export default IntentResponse;
