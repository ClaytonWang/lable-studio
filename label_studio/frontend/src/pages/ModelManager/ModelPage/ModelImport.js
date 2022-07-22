import React, { useCallback, useContext,useState } from 'react';
import { useHistory } from "react-router";
import { Modal } from '../../../components/Modal/Modal';
import { Form } from 'antd';
import { Button } from '../../../components';
import { Input, Select } from '../../../components/Form';
import { ApiContext } from '../../../providers/ApiProvider';

export const ModelImport = ({ onClose }) => {
  const api = useContext(ApiContext);
  const [form] = Form.useForm();
  const history = useHistory();
  const [waiting,setWaiting] = useState(false);

  const onHide = useCallback(async () => {
    history.replace("/model-manager");
    onClose?.();
  }, []);

  const layout = {
    labelCol: {
      span: 5,
    },
    wrapperCol: {
      span: 19,
    },
  };
  const tailLayout = {
    wrapperCol: {
      offset: 8,
      span: 16,
    },
  };

  const importModel = async (values) => {
    setWaiting(true);
    try {
      await api.callApi("importModel", {
        body: values,
        errorFilter: () => true,
      });
      onHide();
    } catch (e) {
      console.error(e);
    } finally {
      setWaiting(false);
    }
  };

  return (
    <Modal style={{ width: 500 }}
      onHide={onHide}
      visible
      closeOnClickOutside={false}
      allowClose={true}
      title={t("Import Model")}
    >
      <Form
        style={{ marginTop:20 }}
        initialValues={{ title: '', type: '', url: '' }}
        {...layout}
        form={form}
        layout="horizontal"
        name="form_in_modal"
        onFinish={ importModel}
      >
        <Form.Item
          name="title"
          label="模型名称"
          rules={[
            {
              required: true,
              message: '请输入模型名称,且不能超过20个字符。',
            },
          ]}
        >
          <Input style={{ width:300 }} placeholder="模型名称"/>
        </Form.Item>
        <Form.Item
          name="type"
          label="类型"
          rules={[{
            required: true,
            message: '请选择模型类型。',
          }]}>
          <div style={{ width: 300 }} >
            <Select
              options={[
                { label: '请选择模型类型', value: '' },
                { label: '对话意图分类', value: 'intention' },
                { label: '对话生成', value: 'generation' },
                { label: '清洗模型', value: 'clean' },
                { label: '其他', value: 'other' },
              ]}
              placeholder={t("Please select Model type")}
            />
          </div>
        </Form.Item>
        <Form.Item
          name="url"
          label="URL"
          rules={[
            {
              required: true,
              message: '请输入模型对应的URL。',
            },
          ]}
        >
          <Input style={{ width:300 }} placeholder="模型URL"/>
        </Form.Item>
        <Form.Item {...tailLayout}>
          <Button
            size="compact"
            style={{
              margin: '0 8px',
            }}
            onClick={onHide}
            waiting={waiting}
          >
              取消
          </Button>
          <Button size="compact" look="primary" type="submit" waiting={waiting}>
              立即导入
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  );
};
