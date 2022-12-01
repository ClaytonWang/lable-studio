import "codemirror/lib/codemirror.css";
import "codemirror/theme/material.css";
import "codemirror/mode/javascript/javascript.js";
import React, { useCallback, useContext, useEffect, useState } from 'react';
import { UnControlled as CodeMirror } from 'react-codemirror2';
import { Col, Form, Input, Row, Select, Tag } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { Modal } from "@/components/Modal/Modal";
import { Space } from "@/components/Space/Space";
import { Button } from "@/components/Button/Button";
import { useProject } from "@/providers/ProjectProvider";
import { ApiContext } from '@/providers/ApiProvider';
const { Option } = Select;

const tip_learn = {
  id: '',
  title: "请选择模型",
  model_title: '',
  version:'',
};

const formatJSON = (json) => {
  if (!json) return '';
  return JSON.stringify(json);
};

let newModelConfig = null;

export default ({ onCancel,onSubmit }) => {
  const api = useContext(ApiContext);
  const [currModel, setCurrModel] = useState(tip_learn);
  const [trainModalData, setTrainModalData] = useState({});
  const [trainModels, setTrainModels] = useState([]);
  const [ipnutStatus, setIpnutStatus] = useState('');
  const [modelLabels, setModelLabels] = React.useState([]);
  const [modelConfig, setModelConfig] = React.useState('');

  const { project } = useProject();

  const getTrainModel = useCallback(
    async () => {
      if (!project.id) {
        return {};
      }
      return await api.callApi("modelTrainModel", {
        params: {
          project_id:project.id,
        },
      });
    }, [project,currModel]);

  const getTrainInit = useCallback(
    async () => {
      if (!project.id) {
        return {};
      }
      return await api.callApi("modelTrainInit", {
        params: {
          project_id: project.id,
          model_id: currModel.id===tip_learn.id?'':currModel.id,
          operate:'train',
        },
      });
    }, [project, currModel]);

  const getModelConfig = useCallback(async () => {
    return await api.callApi("modelConfig", {});
  },[]);


  const handleChange = (value, option) => {
    setCurrModel(option.model);
    if (option.model.id !== tip_learn.id) {
      getModelLabels(option.model.id);
    }
    if (option.model.id) {
      setIpnutStatus("");
    } else {
      setIpnutStatus("error");
    }

  };

  useEffect(() => {
    getTrainModel().then(data => {
      let rlst = data ?? [];

      rlst = rlst.filter(v => v.title.indexOf("普通") !== -1).sort((a, b) => { return a.id-b.id; });
      rlst.unshift(tip_learn);
      setTrainModels(rlst ?? []);
    });
  }, []);

  useEffect(() => {
    getModelConfig().then(data => {
      setModelConfig(data);
    });
    getTrainInit().then(data => {
      setTrainModalData(data);
    });
  }, [currModel]);

  const submitData = () => {
    if (!currModel.id && !currModel.model_title) {
      setIpnutStatus('error');
      return;
    }
    trainModalData.model_id = !currModel.id ? null : currModel.id;
    let model_params = modelConfig;

    if (newModelConfig) model_params = newModelConfig;
    onSubmit('train',{ ...trainModalData,model_title:currModel.model_title,model_params });
  };

  const getModelLabels = useCallback(async (model_id) => {
    if(!model_id) return [];
    const data = await api.callApi("modelLabel", {
      params: {
        model_id,
      },
    });

    setModelLabels(data);
  }, []);

  return (
    <div className="evaluate">
      <Modal.Header>
        <span><PlusOutlined />人在环路</span>
      </Modal.Header>
      <Form
        initialValues={trainModalData}
        colon={false}
        className="content">
        <Row>
          <Col span={8}>
            <Form.Item label="模型集名称">
              <Select defaultValue="" status={ipnutStatus} onChange={handleChange}>
                {trainModels.map((model) => (
                  <Option key={model.id} model={ model}>{model.title + model.version}</Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item label="当前版本" >
              <Input disabled value={trainModalData.version}/>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item label="新模型版本">
              <Input disabled value={trainModalData.new_version}/>
            </Form.Item>
          </Col>
        </Row>
        {
          modelLabels.length>0  && (
            <Row>
              <Col span={24}>
                <Form.Item label="当前模型标签">
                  <Space>
                    {
                      modelLabels && modelLabels.map(tag => {
                        return (
                          <Tag key={tag}>{tag}</Tag>
                        );
                      })
                    }
                  </Space>
                </Form.Item>
              </Col>
            </Row>
          )
        }
        <Row>
          <Col span={16} >
            <Form.Item label="模型配置">
              <div style={{ display: "json" }}>
                <CodeMirror
                  name="code"
                  id="model_edit_code"
                  value={formatJSON(modelConfig)}
                  options={{ mode: {
                    name: "javascript",
                    json: true,
                    statementIndent: 2,
                  }, theme: "default", lineNumbers: true,
                  }}
                  onChange={(editor, data, value) => {
                    newModelConfig = value;
                  }}
                />
              </div>
            </Form.Item>
          </Col>
        </Row>
      </Form>
      <Modal.Footer>
        <Space align="end">
          <Button size="compact" onClick={onCancel}>{t("Cancel")}</Button>
          <Button size="compact" look="primary" onClick={ submitData}>
            {t("record_train", "立即训练")}
          </Button>
        </Space>
      </Modal.Footer>
    </div>
  );
};
