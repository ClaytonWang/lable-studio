import { useCallback,useRef } from "react";
import { Form, InputNumber } from "antd";
import { Modal } from "@/components/Modal/Modal";
import { Space } from "@/components/Space/Space";
import { Button } from "@/components/Button/Button";
import { PromptTemplate } from "@/components/PromptTemplate/PromptTemplate";

const formItemLayout = {
  labelCol: { span: 4 },
  wrapperCol: { span: 20 },
};

const ResponseGeneration = ({ loading, close, project, request }) => {
  const [form] = Form.useForm();
  const comRef = useRef();
  const onFinish = useCallback(() => {
    form.validateFields()
      .then(values => {
        request({
          ...values,
          // tags,
        });
      });
  }, [request]);

  // const onChangeTag = useCallback((v) => {
  //   setTags(v);
  // }, []);

  return (
    <>
      <Modal.Header>对话生成(0样本)</Modal.Header>
      <Form {...formItemLayout} form={form}>
        <Form.Item
          name="generate_count"
          label="生成回答数量"
          rules={[{ required: true, message: t("tip_please_complete") }]}
        >
          <InputNumber max={100} min={1} />
        </Form.Item>
        <Form.Item label="提示学习">
          <PromptTemplate project={project} tag ref={ comRef } />
        </Form.Item>
      </Form>
      <Modal.Footer>
        <Space align="end">
          <Button size="compact" onClick={() => {
            close();
            console.log(comRef);
          }}>
            {t("Cancel")}
          </Button>
          <Button onClick={onFinish} size="compact" look="primary" waiting={loading}>
            {t("ceate_rightnow", "立即生成")}
          </Button>
        </Space>
      </Modal.Footer>
    </>
  );
};

export default ResponseGeneration;
