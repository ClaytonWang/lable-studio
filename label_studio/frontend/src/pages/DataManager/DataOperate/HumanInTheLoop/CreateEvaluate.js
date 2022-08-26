import React, { useCallback,useContext,useEffect,useState } from 'react';
import { Col, Form, Input, Row,Select } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { Modal } from "@/components/Modal/Modal";
import { Space } from "@/components/Space/Space";
import { Button } from "@/components/Button/Button";
import { useProject } from "@/providers/ProjectProvider";
import { ApiContext } from '@/providers/ApiProvider';
const { Option } = Select;

const tip_learn = {
  id: 'tip_learn',
  title: "提示学习",
};


export default ({ onCancel }) => {
  const api = useContext(ApiContext);
  const [currModel, setCurrModel] = useState(tip_learn);
  const [trainModalData, setTrainModalData] = useState({});
  const [trainModels, setTrainModels]=useState([]);
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
    },[project,currModel]);


  const handleChange = (value, option) => {
    setCurrModel(option.model);
  };

  useEffect(() => {
    getTrainModel().then(data => {
      const rlst = data ?? [];

      rlst.unshift(tip_learn);
      setTrainModels(data ?? []);
    });
  }, []);

  useEffect(() => {
    getTrainInit().then(data => {
      setTrainModalData(data);
    });
  }, [currModel]);
  return (
    <div className="evaluate">
      <Modal.Header><span><PlusOutlined />新增评估</span></Modal.Header>
      <Form className="content">
        <Row>
          <Col span={12}>
            <Form.Item label="模型集名称">
              <Row>
                <Col span={currModel.id==="tip_learn"?12:24}>
                  <Select defaultValue="tip_learn" onChange={handleChange}>
                    {trainModels.map((model) => (
                      <Option key={model.id} model={ model}>{model.title}</Option>
                    ))}
                  </Select>
                </Col>
                <Col span={currModel.id==="tip_learn"?12:0}>
                  <Input placeholder='请输入新模型名称' title='请输入新模型名称' />
                </Col>
              </Row>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item label="项目名称">
              <Input disabled />
            </Form.Item>
          </Col>
        </Row>
        <Row>
          <Col span={12}>
            <Form.Item label="总任务数">
              <Input disabled />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item label="当前正确任务数">
              <Input disabled />
            </Form.Item>
          </Col>
        </Row>
        <Row>
          <Col span={12}>
            <Form.Item label="当前正确率">
              <Input disabled />
            </Form.Item>
          </Col>
        </Row>
      </Form>
      <Modal.Footer>
        <Space align="end">
          <Button size="compact" onClick={onCancel}>{t("Cancel")}</Button>
          <Button size="compact" look="primary" type="submit">
            {t("record_evaluate", "记录评估")}
          </Button>
        </Space>
      </Modal.Footer>
    </div>
  );
};
