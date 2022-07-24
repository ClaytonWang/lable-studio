import { Form, InputNumber, Select, Tag } from 'antd';
import { Modal } from "@/components/Modal/Modal";
import { Space } from "@/components/Space/Space";
import { Button } from "@/components/Button/Button";

const formItemLayout = {
  labelCol: { span: 4 },
  wrapperCol: { span: 20 },
};

const ResponseGeneration = ({ close }) => {
  return (
    <>
      <Modal.Header>
      对话生成(普通)
      </Modal.Header>
      <Form
        {...formItemLayout}
      >
        <Form.Item
          label="生成回答数量"
        >
          <InputNumber />
        </Form.Item>
        <Form.Item
          label="选择模型"
        >
          <Select />
        </Form.Item>
        <Form.Item
          label="所选标签模型"
        >
          <Space size="small">
            <Tag>升级</Tag>
            <Tag>不知情</Tag>
            <Tag>套餐</Tag>
          </Space>
        </Form.Item>
      </Form>
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
          >
            立即生成
          </Button>
        </Space>
      </Modal.Footer>
    </>
  );
};

export default ResponseGeneration;
