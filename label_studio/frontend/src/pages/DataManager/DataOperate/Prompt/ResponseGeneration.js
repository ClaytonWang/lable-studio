import { Form, InputNumber } from 'antd';
import { Modal } from "@/components/Modal/Modal";
import { Space } from "@/components/Space/Space";
import { Button } from "@/components/Button/Button";
import { TagList } from "@/components/TagList/TagList";
import { PromptTemplate } from "@/components/PromptTemplate/PromptTemplate";

const formItemLayout = {
  labelCol: { span: 4 },
  wrapperCol: { span: 20 },
};

const ResponseGeneration = ({ close, project }) => {
  return (
    <>
      <Modal.Header>
      对话生成(0样本)
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
          label="提示学习"
        >
          <PromptTemplate project={project} />
        </Form.Item>
        <Form.Item
          name="tags"
          label="标签"
        >
          <TagList />
        </Form.Item>
      </Form>
      <Modal.Footer>
        <Space align="end">
          <Button
            size="compact"
            onClick={close}
          >
            {t("Cancel")}
          </Button>
          <Button
            size="compact"
            look="primary"
          >
            {t("ceate_rightnow", "立即生成")}
          </Button>
        </Space>
      </Modal.Footer>
    </>
  );
};

export default ResponseGeneration;
