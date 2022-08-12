import { Col, Form, Input, Row } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { Modal } from "@/components/Modal/Modal";
import { Space } from "@/components/Space/Space";
import { Button } from "@/components/Button/Button";

export default ({ onCancel }) => {
  return (
    <div className="evaluate">
      <Modal.Header><span><PlusOutlined />新增评估</span></Modal.Header>
      <Form className="content">
        <Row>
          <Col span={12}>
            <Form.Item label="模型名称">
              <Input />
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
