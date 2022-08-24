import React, { useState } from 'react';
import { Col, Form, Input, Row, Select, Tag } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { Modal } from "@/components/Modal/Modal";
import { Space } from "@/components/Space/Space";
import { Button } from "@/components/Button/Button";
const { Option } = Select;

export default ({ onCancel }) => {
  const [modelType, setModelType]=useState("tip_learn");

  const handleChange = (value) => {
    setModelType(value);
  };

  return (
    <div className="evaluate">
      <Modal.Header>
        <span><PlusOutlined />新增训练</span>
      </Modal.Header>
      <Form className="content">
        <Row>
          <Col span={8}>
            <Form.Item label="模型集名称">
              <Row>
                <Col span={modelType==="tip_learn"?12:24}>
                  <Select defaultValue="tip_learn" onChange={handleChange}>
                    <Option value="tip_learn">提示学习</Option>
                    <Option value="other">其他</Option>
                  </Select>
                </Col>
                <Col span={modelType==="tip_learn"?12:0}>
                  <Input />
                </Col>
              </Row>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item label="当前版本">
              <Input disabled />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item label="新模型版本">
              <Input disabled />
            </Form.Item>
          </Col>
        </Row>
        <Row>
          <Col span={8}>
            <Form.Item label="总任务数">
              <Input disabled />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item label="当前正确任务数">
              <Input disabled />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item label="当前准确率">
              <Input disabled />
            </Form.Item>
          </Col>
        </Row>
        <Row>
          <Col span={8}>
            <Form.Item label="项目名称">
              <Input disabled />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item label="新模型训练任务数" tooltip={{ title: t('next_train_task_count', '前80%的任务将参与新模型训练') }}>
              <Input disabled />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item label="新模型评估任务数" tooltip={{ title: t('next_evaluate_task_count', '后20%的任务将参与新模型准确率评估') }}>
              <Input disabled />
            </Form.Item>
          </Col>
        </Row>
        <Row>
          <Col>
            <Form.Item label="当前模型标签">
              <Space>
                <Tag>升级</Tag>
                <Tag>不知情</Tag>
              </Space>
            </Form.Item>
          </Col>
        </Row>
      </Form>
      <Modal.Footer>
        <Space align="end">
          <Button size="compact" onClick={onCancel}>{t("Cancel")}</Button>
          <Button size="compact" look="primary" type="submit">
            {t("record_train", "立即训练")}
          </Button>
        </Space>
      </Modal.Footer>
    </div>
  );
};
