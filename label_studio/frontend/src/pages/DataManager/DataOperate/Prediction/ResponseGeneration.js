import { useCallback } from 'react';
import { Form, InputNumber, Select } from 'antd';
import { map } from 'lodash';
import { Modal } from "@/components/Modal/Modal";
import { Space } from "@/components/Space/Space";
import { Button } from "@/components/Button/Button";
import { PromptTemplate } from "@/components/PromptTemplate/PromptTemplate";

const formItemLayout = {
  labelCol: { span: 4 },
  wrapperCol: { span: 20 },
};

const ResponseGeneration = ({ close, execLabel, loading, project }) => {
  const onFinish = useCallback((values) => {
    execLabel(values);
  }, [execLabel]);

  return (
    <>
      <Modal.Header>
      对话生成(普通)
      </Modal.Header>
      <Form
        {...formItemLayout}
        onFinish={onFinish}
      >
        <Form.Item
          name="generate_count"
          label="生成回答数量"
          rules={[{ required: true, message: t('tip_please_complete') }]}
        >
          <InputNumber max={100} min={1} />
        </Form.Item>
        <Form.Item
          name="templates"
          label="提示学习">
          <PromptTemplate project={project} tag />
        </Form.Item>
        <Modal.Footer>
          <Space align="end">
            <Button
              size="compact"
              onClick={(e) => { e.preventDefault(); close();}}
            >
              {t("Cancel")}
            </Button>
            <Button
              size="compact"
              look="primary"
              type="submit"
              waiting={loading}
            >
              {t("ceate_rightnow", "立即生成")}
            </Button>
          </Space>
        </Modal.Footer>
      </Form>
    </>
  );
};

export default ResponseGeneration;
